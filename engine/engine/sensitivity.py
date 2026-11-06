"""Sensitivity sweep: one site, named axes, a comparable result matrix.

Three axes (spec art_Xihp9Qa2, evaluation dashboard):

- ``tariff_usd_kwh`` — electricity price, remapped on the SiteProfile.
- ``gpu_utilization`` — fraction of nameplate IT load actually drawn; MVP
  lever scales the load profile linearly (no separate workload telemetry).
- ``equipment_lead_time_factor`` — multiplier on the documented equipment
  lead times (assumptions.py). Lead times are assumptions, not site facts,
  so this threads through ``Architecture.simulate`` rather than the profile.

Every point is a pure re-simulation of the same site — no randomness, no
caching, no wall-clock input — so the same call always returns an identical
matrix. Points carry scalar metrics only (the hourly series behind a
sensitivity table would be a memory-times-value product nobody reads).
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from engine.architectures import ARCHITECTURES, Architecture
from engine.models import SiteProfile

AXIS_TARIFF: Final[str] = "tariff_usd_kwh"
AXIS_GPU_UTILIZATION: Final[str] = "gpu_utilization"
AXIS_EQUIPMENT_LEAD_TIME: Final[str] = "equipment_lead_time_factor"

# Canonical axis iteration order — the matrix layout is stable regardless of
# the caller's Mapping ordering.
AXIS_ORDER: Final[tuple[str, ...]] = (
    AXIS_TARIFF,
    AXIS_GPU_UTILIZATION,
    AXIS_EQUIPMENT_LEAD_TIME,
)


@dataclass(frozen=True)
class SensitivityPoint:
    """One (axis, value, architecture) cell of the sweep matrix."""

    axis: str
    value: float
    architecture: str
    chain_efficiency: float
    annual_energy_mwh: float
    capex_usd: float
    opex_usd_year: float
    cost_per_mwh: float
    time_to_power_months: float
    resilience_score: float
    # Spec-mandated field name (art_Xihp9Qa2 engine contract): kg CO2 per kWh,
    # mirroring ScenarioResult so downstream consumers map the fields 1:1.
    carbon_kgCO2_kWh: float  # noqa: N815


def _apply_axis(site: SiteProfile, axis: str, value: float) -> SiteProfile:
    """Remap the profile-level axes; the lead-time factor is not a site fact."""
    if axis == AXIS_TARIFF:
        return dataclasses.replace(site, tariff_usd_kwh=value)
    if axis == AXIS_GPU_UTILIZATION:
        return dataclasses.replace(site, it_load_mw=site.it_load_mw * value)
    raise ValueError(f"unknown axis {axis!r}; expected one of {AXIS_ORDER}")


def sweep(
    site: SiteProfile,
    axes: Mapping[str, Sequence[float]],
    architectures: Sequence[Architecture] | None = None,
) -> list[SensitivityPoint]:
    """Run every (axis value, architecture) pair on one site.

    The lead-time factor passes through to ``simulate``; tariff and GPU
    utilization rebuild the profile. Negative axis values are rejected up
    front — none of the three axes has a meaningful negative reading.
    """
    selected = list(ARCHITECTURES.values()) if architectures is None else list(architectures)
    unknown = set(axes) - set(AXIS_ORDER)
    if unknown:
        raise ValueError(f"unknown axis(es) {sorted(unknown)}; expected one of {AXIS_ORDER}")
    points: list[SensitivityPoint] = []
    for axis in AXIS_ORDER:
        if axis not in axes:
            continue
        for value in axes[axis]:
            if value < 0.0:
                raise ValueError(f"axis {axis} values must be non-negative, got {value}")
            lead_time_factor = value if axis == AXIS_EQUIPMENT_LEAD_TIME else 1.0
            swept_site = (
                site
                if axis == AXIS_EQUIPMENT_LEAD_TIME
                else _apply_axis(site, axis, value)
            )
            for architecture in selected:
                result = architecture.simulate(swept_site, lead_time_factor=lead_time_factor)
                points.append(
                    SensitivityPoint(
                        axis=axis,
                        value=value,
                        architecture=architecture.name,
                        chain_efficiency=result.chain_efficiency,
                        annual_energy_mwh=result.annual_energy_mwh,
                        capex_usd=result.capex_usd,
                        opex_usd_year=result.opex_usd_year,
                        cost_per_mwh=result.cost_per_mwh,
                        time_to_power_months=result.time_to_power_months,
                        resilience_score=result.resilience_score,
                        carbon_kgCO2_kWh=result.carbon_kgCO2_kWh,
                    )
                )
    return points
