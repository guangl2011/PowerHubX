"""Documented model assumptions for the PowerHubX engine.

Every number carries a source or an explicit placeholder label, per the MVP
spec (art_Xihp9Qa2, D1 acceptance criteria): nothing is silently guessed.

Labels in use:

- ``R2: powerhubxdoe2026.md`` — the user's DOE strategy document (project
  artifact art_kNeuMqU8), the doctrinal source for the SST/MVDC story: the
  conventional 13.8 kV -> 480 V AC -> UPS -> 48/12 V DC -> GPU VRM chain loses
  8-15% through 4-5 conversions, and the SST/MVDC path attacks that gap by
  merging stages (30-50% chain-loss reduction target).
- ``placeholder — tune before customer use`` — an engineering estimate chosen
  to be defensible for an MVP; no published source was attached this session.

Chain efficiencies: an architecture's chain efficiency is the product of its
stage efficiencies. The placeholder stages below put the conventional chain at
~14.2% loss (85.8% efficient — inside R2's 8-15% band) and the SST chain at
~10.0% (90.0% efficient) — a ~30% relative loss reduction, the low end of R2's
30-50% target. A power engineer should re-derive every stage before customer
use; the loss-chain tests exist so such re-derivation cannot drift silently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# ---------------------------------------------------------------------------
# Loss chains (grid to GPU)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LossStage:
    """One conversion stage: a fraction of the energy entering it is lost."""

    name: str
    efficiency: float
    source: str


CONVENTIONAL_CHAIN: Final[tuple[LossStage, ...]] = (
    LossStage(
        "MV-LV distribution transformer (13.8 kV AC -> 480 V AC)",
        0.990,
        "placeholder — tune before customer use",
    ),
    LossStage(
        "UPS double conversion (AC -> DC -> AC)",
        0.970,
        "placeholder — tune before customer use",
    ),
    LossStage(
        "PDU and branch wiring",
        0.995,
        "placeholder — tune before customer use",
    ),
    LossStage(
        "Server PSU (AC -> 48 V DC)",
        0.960,
        "placeholder — 80 PLUS Titanium-class PSU at typical load; tune before "
        "customer use",
    ),
    LossStage(
        "GPU board VRM (48 V DC -> <1 V DC)",
        0.935,
        "placeholder — tune before customer use",
    ),
)

MVDC_SST_CHAIN: Final[tuple[LossStage, ...]] = (
    LossStage(
        "MV solid-state transformer (13.8 kV AC -> 800 V DC, SiC)",
        0.985,
        "placeholder — SiC SST stage target consistent with R2 SST/SSPS "
        "positioning; tune before customer use",
    ),
    LossStage(
        "MVDC -> 48 V rack DC/DC",
        0.980,
        "placeholder — tune before customer use",
    ),
    LossStage(
        "Rack DC bus wiring",
        0.997,
        "placeholder — tune before customer use",
    ),
    LossStage(
        "GPU board VRM (48 V DC -> <1 V DC)",
        0.935,
        "placeholder — same stage as the conventional chain",
    ),
)

# The SST chain merges the transformer + UPS + PSU stages (R2: 4-5 conversions
# down to 2 on the GPU supply path); ride-through that the UPS provided comes
# from the BESS on the hybrid bus instead.

LOSS_CHAINS: Final[dict[str, tuple[LossStage, ...]]] = {
    "grid-only": CONVENTIONAL_CHAIN,
    # BESS sits at the MV bus with its own charger (AC-coupled for MVP): it
    # does not alter the GPU conversion chain, so its grid-to-GPU chain is
    # grid-only's. Its value shows in resilience and economics, not losses.
    "grid+bess": CONVENTIONAL_CHAIN,
    "mvdc-sst-hybrid": MVDC_SST_CHAIN,
    # Grid-parallel microgrid with all site DERs upstream of the chain.
    "islandable-microgrid": CONVENTIONAL_CHAIN,
}

ARCHITECTURE_NAMES: Final[tuple[str, ...]] = tuple(LOSS_CHAINS)


def chain_efficiency(chain: tuple[LossStage, ...]) -> float:
    """Product of stage efficiencies — the documented grid-to-GPU fraction."""
    efficiency = 1.0
    for stage in chain:
        efficiency *= stage.efficiency
    return efficiency


# ---------------------------------------------------------------------------
# IT load and PV profiles (deterministic placeholders — no TMY weather or
# workload telemetry in MVP scope)
# ---------------------------------------------------------------------------

# Peak-to-trough diurnal swing as a fraction of IT load — placeholder — tune
# before customer use.
LOAD_SWING_BY_CRITICALITY: Final[dict[str, float]] = {
    "tier3": 0.15,
    "tier4": 0.10,
    "inference": 0.20,
    "training": 0.30,
}

# Enterprise tiers dip on weekends; GPU clusters do not — placeholder.
WEEKEND_FACTOR_BY_CRITICALITY: Final[dict[str, float]] = {
    "tier3": 0.95,
    "tier4": 0.95,
    "inference": 1.00,
    "training": 1.00,
}

PEAK_HOUR_OF_DAY: Final[float] = 15.0  # diurnal peak, local time — placeholder

PV_DAYLENGTH_MEAN_HOURS: Final[float] = 12.0  # placeholder (clear-sky)
PV_DAYLENGTH_AMPLITUDE_HOURS: Final[float] = 3.0  # seasonal swing — placeholder
PV_DAYLENGTH_PEAK_DAY: Final[int] = 81  # ~Mar 21, northern mid-latitude


# ---------------------------------------------------------------------------
# BESS (AC-coupled at the MV bus for MVP; DC-coupling is a refinement)
# ---------------------------------------------------------------------------

BESS_DURATION_HOURS: Final[float] = 4.0  # power rating = energy / duration
BESS_CHARGE_EFFICIENCY: Final[float] = 0.933  # round trip ~87%
BESS_DISCHARGE_EFFICIENCY: Final[float] = 0.933
# Reserved for grid-forming ride-through (spec dispatch contract).
BESS_MIN_SOC_FRACTION: Final[float] = 0.10
# Of nameplate, for resilience math at full charge.
BESS_USABLE_FRACTION: Final[float] = 0.90


# ---------------------------------------------------------------------------
# Grid, carbon, economics (all placeholder — tune before customer use)
# ---------------------------------------------------------------------------

GRID_CARBON_KG_PER_KWH: Final[float] = 0.38  # US-average intensity

# Component capex, USD per kW of IT load (chain equipment) or per kW/kWh of
# the named asset. The SST path replaces the transformer + UPS chain, so its
# equipment figure is not additive with the conventional one.
CAPEX_USD_PER_KW: Final[dict[str, float]] = {
    "interconnection": 200.0,
    "conventional-chain": 350.0,
    "sst-chain": 600.0,
    "pv": 1200.0,
    "fuel-cell": 3000.0,
    "genset": 800.0,
}
BESS_CAPEX_USD_PER_KWH: Final[float] = 350.0  # NREL-class ATB range midpoint
FIXED_OM_FRACTION_PER_YEAR: Final[float] = 0.02
WACC: Final[float] = 0.08
ECONOMIC_LIFE_YEARS: Final[int] = 30


def capital_recovery_factor() -> float:
    """CRF = r(1+r)^n / ((1+r)^n - 1) — annualizes capex at WACC over life."""
    factor = (1.0 + WACC) ** ECONOMIC_LIFE_YEARS
    return WACC * factor / (factor - 1.0)


# ---------------------------------------------------------------------------
# Time to power and resilience
# ---------------------------------------------------------------------------

# R1 (market research, this project's spec): transformer/switchgear lead times
# run to years. SST supply chains are immature — placeholder.
SST_EQUIPMENT_LEAD_MONTHS: Final[float] = 18.0
DER_EQUIPMENT_LEAD_MONTHS: Final[float] = 12.0  # FC/genset/PV procurement

RESILIENCE_TARGET_HOURS: Final[float] = 24.0  # islanding duration for full score
FOSSIL_FUEL_HOURS: Final[float] = 48.0  # on-site fuel for FC + genset


# ---------------------------------------------------------------------------
# Numerical tolerance
# ---------------------------------------------------------------------------

EPS: Final[float] = 1e-9
