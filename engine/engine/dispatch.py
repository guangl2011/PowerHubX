"""GPU flexible-load dispatch: the spec's one-hour load-serving contract.

Pure function, no I/O — the hourly simulation calls it once per deficit hour
and the report prices the flexibility value from the returned split.
"""

from __future__ import annotations

from engine.results import GpuDispatch


def bess_available_discharge_mw(soc_mwh: float, min_soc_mwh: float) -> float:
    """Dischargeable BESS energy above the ride-through reservation, in MW.

    The min-SOC reservation rule (spec art_Xihp9Qa2): the band below
    ``min_soc_mwh`` is reserved for grid-forming ride-through and is never
    discharged. On the 1 h timestep, MWh of headroom is MW of discharge for
    one hour. SOC at or below the floor leaves zero.
    """
    return max(soc_mwh - min_soc_mwh, 0.0)


def dispatch_gpu_flexible_load(
    deficit_mw: float,
    flexible_gpu_mw: float,
    bess_discharge_mw: float,
    min_soc_mwh: float,
    soc_mwh: float,
) -> GpuDispatch:
    """Grid-stress or islanding event: serve a deficit for one hour.

    Resources in order: (1) BESS discharge, (2) flexible-load curtailment,
    (3) — only if still short — load shed. Rules (spec art_Xihp9Qa2): never
    curtail the critical share (curtailment is capped at the flexible load);
    never discharge the BESS below min_soc (reserved for grid-forming
    ride-through). Discharge is also capped at the deficit itself — no export
    market is modeled, so serving less than the deficit never makes sense.

    The 1 h timestep is why MWh of storage headroom converts 1:1 into MW of
    discharge for one hour.
    """
    bess_used = min(
        bess_discharge_mw,
        deficit_mw,
        max(soc_mwh - min_soc_mwh, 0.0) / 1.0,
    )
    residual = deficit_mw - bess_used
    curtailed = min(residual, flexible_gpu_mw)
    shed = max(residual - curtailed, 0.0)
    return GpuDispatch(bess_mw=bess_used, curtailed_mw=curtailed, shed_mw=shed)
