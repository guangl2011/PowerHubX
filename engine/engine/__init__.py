"""PowerHubX simulation and evaluation engine.

A pure, UI-free Python package that turns a SiteProfile into a comparison of
power architectures (grid-only, grid+BESS, MVDC-SST hybrid, islandable
microgrid). The web app drives these functions through the API; nothing here
may import from apps/.
"""

from .architectures import (
    ARCHITECTURES,
    Architecture,
    GridOnly,
    GridPlusBess,
    IslandableMicrogrid,
    MvdcSstHybrid,
    simulate_all,
)
from .assumptions import LOSS_CHAINS, LossStage, chain_efficiency
from .dispatch import dispatch_gpu_flexible_load
from .models import CRITICALITY_LEVELS, SiteProfile
from .results import HOURS_PER_YEAR, GpuDispatch, HourlySeries, ScenarioResult

__version__ = "0.1.0"

__all__ = [
    "ARCHITECTURES",
    "CRITICALITY_LEVELS",
    "HOURS_PER_YEAR",
    "LOSS_CHAINS",
    "Architecture",
    "GpuDispatch",
    "GridOnly",
    "GridPlusBess",
    "HourlySeries",
    "IslandableMicrogrid",
    "LossStage",
    "MvdcSstHybrid",
    "ScenarioResult",
    "SiteProfile",
    "chain_efficiency",
    "dispatch_gpu_flexible_load",
    "simulate_all",
]
