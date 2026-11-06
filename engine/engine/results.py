"""Result models: the hourly series and per-architecture scenario result.

Shapes follow the engine contract in the MVP spec (art_Xihp9Qa2): one
ScenarioResult per architecture, carrying the five evaluation axes (chain
efficiency, cost per delivered MWh, time-to-power, resilience, carbon) plus
the full hourly series behind them.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

HOURS_PER_YEAR = 8760


@dataclass(frozen=True)
class GpuDispatch:
    """One-hour dispatch split when a binding grid limit creates a deficit.

    ``bess_mw`` is delivered at the facility bus, ``curtailed_mw`` is flexible
    GPU load left unserved (the dispatchable-resource lever), and ``shed_mw``
    is critical load that could not be served after all resources ran out.
    """

    bess_mw: float
    curtailed_mw: float
    shed_mw: float


@dataclass(frozen=True)
class HourlySeries:
    """8760-hour traces behind a scenario result.

    Power values are MW averaged over the hour, so on the 1 h timestep energy
    and power are numerically equal; BESS state of charge is MWh. ``pv_mw``
    records PV consumed behind the meter; surplus above load (and above BESS
    charging room) is curtailed — no export market is modeled (placeholder,
    see assumptions.py).
    """

    hour: npt.NDArray[np.int32]
    it_load_mw: npt.NDArray[np.float64]
    grid_import_mw: npt.NDArray[np.float64]
    pv_mw: npt.NDArray[np.float64]
    bess_discharge_mw: npt.NDArray[np.float64]
    bess_charge_mw: npt.NDArray[np.float64]
    bess_soc_mwh: npt.NDArray[np.float64]
    chain_input_mw: npt.NDArray[np.float64]
    gpu_delivered_mw: npt.NDArray[np.float64]
    loss_mw: npt.NDArray[np.float64]
    curtailed_gpu_mw: npt.NDArray[np.float64]
    shed_mw: npt.NDArray[np.float64]

    def __post_init__(self) -> None:
        lengths = {np.size(getattr(self, f.name)) for f in dataclasses.fields(self)}
        if len(lengths) > 1:
            raise ValueError("HourlySeries arrays must all have the same length")


@dataclass(frozen=True)
class ScenarioResult:
    """One architecture's annual evaluation of one SiteProfile.

    Field semantics (spec art_Xihp9Qa2, engine contract):

    - ``chain_efficiency``: documented grid-to-GPU conversion efficiency — the
      product of the architecture's loss-chain stages (assumptions.py). Every
      unit of energy traversing the chain emerges GPU-delivered at exactly
      this fraction, hour by hour.
    - ``annual_energy_mwh``: GPU-delivered energy for the year.
    - ``loss_mwh``: conversion-chain losses plus BESS round-trip losses.
    - ``capex_usd`` / ``opex_usd_year`` / ``cost_per_mwh``: placeholder
      economics (assumptions.py); cost is levelized over delivered MWh via a
      capital recovery factor.
    - ``time_to_power_months``: energization estimate including interconnection
      wait and, where applicable, equipment lead time.
    - ``resilience_score``: 0-1 islanding capability, computed from design
      capacity at full charge (not the operational SOC trace).
    - ``carbon_kgCO2_kWh``: kg CO2 per delivered kWh from grid imports.
    """

    architecture: str
    chain_efficiency: float
    annual_energy_mwh: float
    loss_mwh: float
    capex_usd: float
    opex_usd_year: float
    cost_per_mwh: float
    time_to_power_months: float
    resilience_score: float
    # Spec-mandated field name (art_Xihp9Qa2 engine contract): kg CO2 per kWh.
    carbon_kgCO2_kWh: float  # noqa: N815
    hourly: HourlySeries

    def __post_init__(self) -> None:
        if not 0.0 < self.chain_efficiency <= 1.0:
            raise ValueError("chain_efficiency must be in (0, 1]")
        if not 0.0 <= self.resilience_score <= 1.0:
            raise ValueError("resilience_score must be in [0, 1]")
