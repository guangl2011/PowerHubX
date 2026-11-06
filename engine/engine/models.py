"""Core site model shared by every architecture simulation.

The data model and validation from the MVP spec (art_Xihp9Qa2, engine
contract section). The Architecture protocol and the four implementations
live in engine.architectures; the loss chains they apply live in
engine.assumptions.
"""

from __future__ import annotations

import datetime
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
        if self.rack_density_kw < 0:
            raise ValueError("rack_density_kw must be non-negative")
        if self.criticality not in CRITICALITY_LEVELS:
            raise ValueError(f"criticality must be one of {CRITICALITY_LEVELS}")
        for field in ("bess_mwh", "pv_mw", "fuel_cell_mw", "genset_mw"):
            if getattr(self, field) < 0:
                raise ValueError(f"{field} must be non-negative")
        if self.tariff_usd_kwh < 0:
            raise ValueError("tariff_usd_kwh must be non-negative")
        if self.interconnection_wait_months < 0:
            raise ValueError("interconnection_wait_months must be non-negative")
        if not self.target_energization:
            raise ValueError("target_energization must be a non-empty ISO date")
        try:
            datetime.date.fromisoformat(self.target_energization)
        except ValueError as exc:
            raise ValueError(
                "target_energization must be an ISO date (YYYY-MM-DD)"
            ) from exc
