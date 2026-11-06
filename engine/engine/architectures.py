"""The four power architectures compared by the engine (spec art_Xihp9Qa2).

All four share one hourly pipeline (``_simulate_year``): a deterministic IT
load and PV profile, a binding grid import limit, BESS dispatch through
``dispatch_gpu_flexible_load``, and the architecture's documented loss chain
from grid to GPU. The architectures differ in which site DER assets they
build and which loss chain their energy traverses:

- ``grid-only``: no DER assets; the conventional chain.
- ``grid+bess``: BESS at the MV bus; the GPU conversion chain is unchanged —
  BESS creates resilience value, not conversion efficiency.
- ``mvdc-sst-hybrid``: the MV solid-state transformer chain; BESS on the
  hybrid bus. The product's core claim (R2) lives here.
- ``islandable-microgrid``: all site DER assets plus the conventional chain.

Every economic, resilience, and time-to-power figure is a documented
placeholder (assumptions.py); the loss chains are the tested core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Final, Protocol

import numpy as np
import numpy.typing as npt

from engine.assumptions import (
    BESS_CAPEX_USD_PER_KWH,
    BESS_CHARGE_EFFICIENCY,
    BESS_DISCHARGE_EFFICIENCY,
    BESS_DURATION_HOURS,
    BESS_MIN_SOC_FRACTION,
    BESS_USABLE_FRACTION,
    CAPEX_USD_PER_KW,
    DER_EQUIPMENT_LEAD_MONTHS,
    EPS,
    FIXED_OM_FRACTION_PER_YEAR,
    FOSSIL_FUEL_HOURS,
    GRID_CARBON_KG_PER_KWH,
    LOAD_SWING_BY_CRITICALITY,
    LOSS_CHAINS,
    PEAK_HOUR_OF_DAY,
    PV_DAYLENGTH_AMPLITUDE_HOURS,
    PV_DAYLENGTH_MEAN_HOURS,
    PV_DAYLENGTH_PEAK_DAY,
    RESILIENCE_TARGET_HOURS,
    SST_EQUIPMENT_LEAD_MONTHS,
    WEEKEND_FACTOR_BY_CRITICALITY,
    LossStage,
    capital_recovery_factor,
    chain_efficiency,
)
from engine.dispatch import dispatch_gpu_flexible_load
from engine.models import SiteProfile
from engine.results import HOURS_PER_YEAR, GpuDispatch, HourlySeries, ScenarioResult


class Architecture(Protocol):
    """Engine contract (spec art_Xihp9Qa2): simulate one site, once."""

    name: str

    def simulate(self, site: SiteProfile) -> ScenarioResult: ...


@dataclass(frozen=True)
class DerBuild:
    """The DER assets an architecture chooses to build from a site's assets."""

    bess_mwh: float = 0.0
    pv_mw: float = 0.0
    fuel_cell_mw: float = 0.0
    genset_mw: float = 0.0


ZERO_DER: Final[DerBuild] = DerBuild()


# ---------------------------------------------------------------------------
# Deterministic input profiles (placeholder shapes — see assumptions.py)
# ---------------------------------------------------------------------------


def _it_load_profile(site: SiteProfile) -> npt.NDArray[np.float64]:
    """Diurnal-sinusoid IT load trace, peaking 15:00 local.

    Placeholder workload model: no real telemetry in MVP scope. Swing and
    weekend behavior are keyed by criticality (assumptions.py); weekday
    alignment is a fixed cycle, not a calendar-accurate one.
    """
    swing = LOAD_SWING_BY_CRITICALITY[site.criticality]
    weekend_factor = WEEKEND_FACTOR_BY_CRITICALITY[site.criticality]
    hour = np.arange(HOURS_PER_YEAR, dtype=np.int32)
    hour_of_day = (hour % 24).astype(np.float64)
    weekend = ((hour // 24) % 7 >= 5).astype(np.float64)
    diurnal = 0.5 * (1.0 + np.cos(2.0 * np.pi * (hour_of_day - PEAK_HOUR_OF_DAY) / 24.0))
    factor = (1.0 - swing + swing * diurnal) * (1.0 - (1.0 - weekend_factor) * weekend)
    return site.it_load_mw * factor


def _pv_profile(pv_mw: float) -> npt.NDArray[np.float64]:
    """Clear-sky PV trace between sunrise and sunset (placeholder — no TMY).

    Daylength varies +/- 3 h seasonally around 12 h; output follows a sine
    between zero at the horizon and nameplate at solar noon.
    """
    if pv_mw == 0.0:
        return np.zeros(HOURS_PER_YEAR, dtype=np.float64)
    hour = np.arange(HOURS_PER_YEAR, dtype=np.int32)
    hour_of_day = (hour % 24).astype(np.float64)
    day = (hour // 24).astype(np.float64)
    daylength = PV_DAYLENGTH_MEAN_HOURS + PV_DAYLENGTH_AMPLITUDE_HOURS * np.sin(
        2.0 * np.pi * (day - PV_DAYLENGTH_PEAK_DAY) / 365.0
    )
    sunrise = 12.0 - daylength / 2.0
    fraction = (hour_of_day - sunrise) / daylength
    daylight = (fraction >= 0.0) & (fraction <= 1.0)
    output = np.sin(np.pi * np.clip(fraction, 0.0, 1.0))
    return pv_mw * np.where(daylight, output, 0.0)


# ---------------------------------------------------------------------------
# Shared hourly pipeline
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _YearTotals:
    """Scalar aggregates of one annual run (MWh throughout)."""

    grid_import_mwh: float
    gpu_delivered_mwh: float
    chain_loss_mwh: float
    storage_loss_mwh: float


def _simulate_year(
    site: SiteProfile,
    der: DerBuild,
    chain: tuple[LossStage, ...],
) -> tuple[HourlySeries, _YearTotals]:
    """Run the 8760-hour loop: serve load, dispatch BESS, apply loss stages.

    Semantics: the IT-load profile is GPU-side delivered demand — what the
    GPUs need after conversion — so it is identical across architectures and
    the scenarios stay comparable. Each hour draws
    ``demand / chain_efficiency`` through the documented stages: grid import
    is capped by the site limit, PV and BESS discharge feed the input bus,
    and shortfalls curtail flexible GPU load (then shed critical load) in
    GPU-delivered terms. BESS charging draws PV surplus first, then grid
    headroom; discharge only against deficits (no price arbitrage under a
    flat tariff — placeholder policy); recharge to full whenever headroom
    allows.
    """
    load_mw = _it_load_profile(site)
    pv_available = _pv_profile(der.pv_mw)
    eff = chain_efficiency(chain)

    capacity = der.bess_mwh
    bess_power = capacity / BESS_DURATION_HOURS if capacity > 0.0 else 0.0
    min_soc = capacity * BESS_MIN_SOC_FRACTION
    soc = capacity  # start full; placeholder policy keeps it topped up

    grid_import = np.zeros(HOURS_PER_YEAR, dtype=np.float64)
    pv_used_arr = np.zeros(HOURS_PER_YEAR, dtype=np.float64)
    bess_discharge_arr = np.zeros(HOURS_PER_YEAR, dtype=np.float64)
    bess_charge_arr = np.zeros(HOURS_PER_YEAR, dtype=np.float64)
    soc_arr = np.zeros(HOURS_PER_YEAR, dtype=np.float64)
    chain_input_arr = np.zeros(HOURS_PER_YEAR, dtype=np.float64)
    delivered_arr = np.zeros(HOURS_PER_YEAR, dtype=np.float64)
    curtailed_arr = np.zeros(HOURS_PER_YEAR, dtype=np.float64)
    shed_arr = np.zeros(HOURS_PER_YEAR, dtype=np.float64)

    stage_efficiencies = [stage.efficiency for stage in chain]
    storage_loss_mwh = 0.0

    for hour in range(HOURS_PER_YEAR):
        demand_h = float(load_mw[hour])  # GPU-side (delivered) MW
        pv_h = float(pv_available[hour])

        # To deliver the demand, the chain must be fed demand / efficiency.
        required_input = demand_h / eff
        pv_used = min(pv_h, required_input)
        grid_direct = min(site.grid_limit_mw, required_input - pv_used)
        deficit_input = required_input - pv_used - grid_direct

        bess_out = 0.0
        curtailed = 0.0
        shed = 0.0
        if deficit_input > EPS:
            # Dispatch runs in GPU-delivered terms; the BESS conversion back
            # to input-side MW happens on the way out.
            available_input = min(
                bess_power, max(0.0, soc - min_soc) * BESS_DISCHARGE_EFFICIENCY
            )
            dispatch: GpuDispatch = dispatch_gpu_flexible_load(
                deficit_input * eff,
                demand_h * site.flexible_share,
                available_input * eff,
                min_soc,
                soc,
            )
            bess_out = dispatch.bess_mw / eff
            curtailed = dispatch.curtailed_mw
            shed = dispatch.shed_mw
            soc = max(min_soc, soc - bess_out / BESS_DISCHARGE_EFFICIENCY)

        # Recharge (placeholder policy: no price arbitrage under a flat tariff):
        # PV surplus first, then grid headroom, toward full.
        stored_pv = 0.0
        grid_charge_draw = 0.0
        stored_grid = 0.0
        room = capacity - soc
        if deficit_input <= EPS and room > EPS and bess_power > 0.0:
            pv_surplus = pv_h - pv_used
            if pv_surplus > EPS:
                stored_pv = min(pv_surplus * BESS_CHARGE_EFFICIENCY, bess_power, room)
                soc += stored_pv
                room -= stored_pv
            headroom = site.grid_limit_mw - grid_direct
            if headroom > EPS and room > EPS:
                grid_charge_draw = min(bess_power, room / BESS_CHARGE_EFFICIENCY, headroom)
                stored_grid = grid_charge_draw * BESS_CHARGE_EFFICIENCY
                soc += stored_grid
            storage_loss_mwh += (pv_surplus - stored_pv) + (grid_charge_draw - stored_grid)

        chain_input = pv_used + grid_direct + bess_out
        delivered = chain_input
        for efficiency in stage_efficiencies:
            delivered *= efficiency

        grid_import[hour] = grid_direct + grid_charge_draw
        pv_used_arr[hour] = pv_used
        bess_discharge_arr[hour] = bess_out
        bess_charge_arr[hour] = stored_pv + stored_grid
        soc_arr[hour] = soc
        chain_input_arr[hour] = chain_input
        delivered_arr[hour] = delivered
        curtailed_arr[hour] = curtailed
        shed_arr[hour] = shed

    hourly = HourlySeries(
        hour=np.arange(HOURS_PER_YEAR, dtype=np.int32),
        it_load_mw=load_mw,
        grid_import_mw=grid_import,
        pv_mw=pv_used_arr,
        bess_discharge_mw=bess_discharge_arr,
        bess_charge_mw=bess_charge_arr,
        bess_soc_mwh=soc_arr,
        chain_input_mw=chain_input_arr,
        gpu_delivered_mw=delivered_arr,
        loss_mw=chain_input_arr - delivered_arr,
        curtailed_gpu_mw=curtailed_arr,
        shed_mw=shed_arr,
    )  # curtailed/shed are GPU-delivered MW; the rest are input-side MW.
    totals = _YearTotals(
        grid_import_mwh=float(grid_import.sum()),
        gpu_delivered_mwh=float(delivered_arr.sum()),
        chain_loss_mwh=float((chain_input_arr - delivered_arr).sum()),
        storage_loss_mwh=storage_loss_mwh,
    )
    return hourly, totals


# ---------------------------------------------------------------------------
# Architecture implementations
# ---------------------------------------------------------------------------


class _BaseArchitecture:
    """Shared evaluation pipeline; subclasses choose chain, DERs, and timing."""

    name: str
    equipment_key: ClassVar[str]

    def simulate(self, site: SiteProfile) -> ScenarioResult:
        chain = self._chain()
        der = self._der_build(site)
        hourly, totals = _simulate_year(site, der, chain)

        capex = self._capex_usd(site, der)
        opex = _opex_usd_year(totals.grid_import_mwh, site.tariff_usd_kwh, capex)
        delivered = totals.gpu_delivered_mwh
        annualized = capex * capital_recovery_factor() + opex
        cost_per_mwh = annualized / delivered if delivered > EPS else 0.0
        carbon_per_kwh = (
            totals.grid_import_mwh * GRID_CARBON_KG_PER_KWH / delivered
            if delivered > EPS
            else 0.0
        )

        return ScenarioResult(
            architecture=self.name,
            chain_efficiency=chain_efficiency(chain),
            annual_energy_mwh=delivered,
            loss_mwh=totals.chain_loss_mwh + totals.storage_loss_mwh,
            capex_usd=capex,
            opex_usd_year=opex,
            cost_per_mwh=cost_per_mwh,
            time_to_power_months=self._time_to_power_months(site),
            resilience_score=self._resilience_score(site, der),
            carbon_kgCO2_kWh=carbon_per_kwh,
            hourly=hourly,
        )

    def _chain(self) -> tuple[LossStage, ...]:
        return LOSS_CHAINS[self.name]

    def _der_build(self, site: SiteProfile) -> DerBuild:
        raise NotImplementedError

    def _time_to_power_months(self, site: SiteProfile) -> float:
        raise NotImplementedError

    def _capex_usd(self, site: SiteProfile, der: DerBuild) -> float:
        """Placeholder component costs (assumptions.py). BESS in $/kWh."""
        load_kw = site.it_load_mw * 1000.0
        parts = [
            load_kw * CAPEX_USD_PER_KW["interconnection"],
            load_kw * CAPEX_USD_PER_KW[self.equipment_key],
        ]
        if der.bess_mwh > 0.0:
            parts.append(der.bess_mwh * 1000.0 * BESS_CAPEX_USD_PER_KWH)
        if der.pv_mw > 0.0:
            parts.append(der.pv_mw * 1000.0 * CAPEX_USD_PER_KW["pv"])
        if der.fuel_cell_mw > 0.0:
            parts.append(der.fuel_cell_mw * 1000.0 * CAPEX_USD_PER_KW["fuel-cell"])
        if der.genset_mw > 0.0:
            parts.append(der.genset_mw * 1000.0 * CAPEX_USD_PER_KW["genset"])
        return float(sum(parts))

    def _resilience_score(self, site: SiteProfile, der: DerBuild) -> float:
        """power coverage x duration coverage of the critical load, 0-1.

        Computed from design capacity at full charge (not the operational SOC
        trace) — a design metric. Zero critical load defines full resilience.
        """
        critical_mw = site.it_load_mw * (1.0 - site.flexible_share)
        if critical_mw <= EPS:
            return 1.0
        bess_power = der.bess_mwh / BESS_DURATION_HOURS if der.bess_mwh > 0.0 else 0.0
        backup_power = bess_power + der.fuel_cell_mw + der.genset_mw
        backup_energy = (
            der.bess_mwh * BESS_USABLE_FRACTION * BESS_DISCHARGE_EFFICIENCY
            + (der.fuel_cell_mw + der.genset_mw) * FOSSIL_FUEL_HOURS
        )
        power_factor = min(1.0, backup_power / critical_mw)
        duration_factor = min(1.0, backup_energy / critical_mw / RESILIENCE_TARGET_HOURS)
        return power_factor * duration_factor


def _opex_usd_year(grid_import_mwh: float, tariff_usd_kwh: float, capex: float) -> float:
    """Energy bill plus fixed O&M (placeholder: 2% of capex per year)."""
    energy_usd = grid_import_mwh * 1000.0 * tariff_usd_kwh
    return energy_usd + capex * FIXED_OM_FRACTION_PER_YEAR


class GridOnly(_BaseArchitecture):
    """No DER assets built: utility service through the conventional chain.

    Site DER assets are deliberately not built in this scenario — that is the
    comparison the dashboard shows.
    """

    name = "grid-only"
    equipment_key = "conventional-chain"

    def _der_build(self, site: SiteProfile) -> DerBuild:
        return ZERO_DER

    def _time_to_power_months(self, site: SiteProfile) -> float:
        return float(site.interconnection_wait_months)


class GridPlusBess(_BaseArchitecture):
    """Grid-only chain plus BESS at the MV bus for peak shaving and backup.

    Same conversion chain as grid-only (assumptions.py); the BESS shows up in
    resilience and capex, and discharges only when the grid limit binds.
    """

    name = "grid+bess"
    equipment_key = "conventional-chain"

    def _der_build(self, site: SiteProfile) -> DerBuild:
        return DerBuild(bess_mwh=site.bess_mwh)

    def _time_to_power_months(self, site: SiteProfile) -> float:
        return float(site.interconnection_wait_months)


class MvdcSstHybrid(_BaseArchitecture):
    """MV solid-state transformer chain with BESS on the hybrid bus.

    The product's core claim (R2): merging the transformer, UPS, and PSU
    stages into SST + DC/DC raises grid-to-GPU efficiency strictly above the
    conventional chain. Ride-through comes from the BESS, not a UPS.
    """

    name = "mvdc-sst-hybrid"
    equipment_key = "sst-chain"

    def _der_build(self, site: SiteProfile) -> DerBuild:
        return DerBuild(bess_mwh=site.bess_mwh)

    def _time_to_power_months(self, site: SiteProfile) -> float:
        return float(site.interconnection_wait_months) + SST_EQUIPMENT_LEAD_MONTHS


class IslandableMicrogrid(_BaseArchitecture):
    """Grid-parallel microgrid: all site DER assets behind the same chain.

    Energizes critical load from DERs (PV first, BESS and fueled units for
    islanding) before full interconnection, so time to power is bounded by
    DER equipment lead time when that beats the queue.
    """

    name = "islandable-microgrid"
    equipment_key = "conventional-chain"

    def _der_build(self, site: SiteProfile) -> DerBuild:
        return DerBuild(
            bess_mwh=site.bess_mwh,
            pv_mw=site.pv_mw,
            fuel_cell_mw=site.fuel_cell_mw,
            genset_mw=site.genset_mw,
        )

    def _time_to_power_months(self, site: SiteProfile) -> float:
        return min(float(site.interconnection_wait_months), DER_EQUIPMENT_LEAD_MONTHS)


ARCHITECTURES: Final[dict[str, Architecture]] = {
    GridOnly.name: GridOnly(),
    GridPlusBess.name: GridPlusBess(),
    MvdcSstHybrid.name: MvdcSstHybrid(),
    IslandableMicrogrid.name: IslandableMicrogrid(),
}


def simulate_all(site: SiteProfile) -> dict[str, ScenarioResult]:
    """Run every architecture on one site — the API's simulate step."""
    return {name: arch.simulate(site) for name, arch in ARCHITECTURES.items()}
