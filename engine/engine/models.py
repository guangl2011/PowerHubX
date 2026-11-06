"""Core site model shared by every architecture simulation.

Placeholder scaffold from the MVP spec (art_Xihp9Qa2, engine contract section).
The four Architecture implementations arrive in a later PR; only the data
model and validation live here for now.
"""

from __future__ import annotations

from dataclasses import dataclass

CRITICALITY_LEVELS = ("tier3", "tier4", "inference", "training")


@dataclass(frozen=True)
class SiteProfile:
    """Site facts captured by the intake wizard.

    Versions of this model are versioned at the project level by the API; the
    engine treats each profile as immutable input.
    """

    grid_limit_mw: float
    it_load_mw: float
    flexible_share: float  # fraction of IT load eligible for curtailment
    rack_density_kw: float
    criticality: str  # one of CRITICALITY_LEVELS
    bess_mwh: float
    pv_mw: float
    fuel_cell_mw: float
    genset_mw: float
    tariff_usd_kwh: float
    interconnection_wait_months: int
    target_energization: str  # ISO date

    def __post_init__(self) -> None:
        if self.grid_limit_mw < 0:
            raise ValueError("grid_limit_mw must be non-negative")
        if self.it_load_mw < 0:
            raise ValueError("it_load_mw must be non-negative")
        if not 0.0 <= self.flexible_share <= 1.0:
            raise ValueError("flexible_share must be between 0 and 1")
        if self.criticality not in CRITICALITY_LEVELS:
            raise ValueError(f"criticality must be one of {CRITICALITY_LEVELS}")
