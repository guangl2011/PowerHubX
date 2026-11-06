"""API request/response contracts (pydantic).

Validation mirrors the engine's ``SiteProfile.__post_init__`` so clients get
422 responses with field-level errors instead of 500s from the engine. The
engine remains the source of truth: a model-level validator reconstructs the
engine object as a backstop, so a payload the API accepts is always one the
engine accepts. Field names stay snake_case to match the engine dataclass and
the web wizard's TS mirror (apps/web/src/wizard/types.ts).
"""

from __future__ import annotations

import dataclasses
import datetime
import math

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator, model_validator

from engine import ARCHITECTURES, CRITICALITY_LEVELS, ScenarioResult, SiteProfile
from engine.sensitivity import SensitivityPoint

_NON_NEGATIVE_FLOAT_FIELDS = (
    "grid_limit_mw",
    "it_load_mw",
    "rack_density_kw",
    "bess_mwh",
    "pv_mw",
    "fuel_cell_mw",
    "genset_mw",
    "tariff_usd_kwh",
)


class SiteProfileIn(BaseModel):
    """The intake record — field-for-field mirror of ``engine.SiteProfile``."""

    model_config = ConfigDict(extra="forbid")

    grid_limit_mw: float
    it_load_mw: float
    flexible_share: float
    rack_density_kw: float
    criticality: str
    bess_mwh: float
    pv_mw: float
    fuel_cell_mw: float
    genset_mw: float
    tariff_usd_kwh: float
    interconnection_wait_months: int
    target_energization: str

    @field_validator(*_NON_NEGATIVE_FLOAT_FIELDS)
    @classmethod
    def _finite(cls, value: float, info: ValidationInfo) -> float:
        # NaN/Infinity parse from JSON but are meaningless site facts.
        if not math.isfinite(value):
            raise ValueError(f"{info.field_name} must be a finite number")
        return value

    @field_validator(*_NON_NEGATIVE_FLOAT_FIELDS)
    @classmethod
    def _non_negative(cls, value: float, info: ValidationInfo) -> float:
        if value < 0.0:
            raise ValueError(f"{info.field_name} must be non-negative")
        return value

    @field_validator("interconnection_wait_months")
    @classmethod
    def _wait_months_non_negative(cls, value: int, info: ValidationInfo) -> int:
        if value < 0:
            raise ValueError(f"{info.field_name} must be non-negative")
        return value

    @field_validator("flexible_share")
    @classmethod
    def _share_in_range(cls, value: float) -> float:
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("flexible_share must be between 0 and 1")
        return value

    @field_validator("criticality")
    @classmethod
    def _criticality_known(cls, value: str) -> str:
        if value not in CRITICALITY_LEVELS:
            raise ValueError(f"criticality must be one of {CRITICALITY_LEVELS}")
        return value

    @field_validator("target_energization")
    @classmethod
    def _iso_date(cls, value: str) -> str:
        if not value:
            raise ValueError("target_energization must be a non-empty ISO date")
        try:
            datetime.date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                "target_energization must be an ISO date (YYYY-MM-DD)"
            ) from exc
        return value

    @model_validator(mode="after")
    def _engine_gate(self) -> SiteProfileIn:
        # Backstop: the field validators above mirror the engine rules; this
        # guarantees the API can never accept what the engine would reject.
        SiteProfile(**self.model_dump())
        return self

    def to_engine(self) -> SiteProfile:
        return SiteProfile(**self.model_dump())


class ProjectCreate(BaseModel):
    """POST /api/projects payload. ``site`` may arrive later via PUT /site."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    location: str | None = None
    site: SiteProfileIn | None = None


class ProjectOut(BaseModel):
    id: str
    name: str | None
    location: str | None
    site: SiteProfileIn | None
    site_version: int
    has_results: bool
    # Naive UTC datetimes — SQLite has no timezone column support in MVP.
    created_at: datetime.datetime
    updated_at: datetime.datetime


class DispatchSummary(BaseModel):
    """Aggregates of the hourly dispatch behind one scenario.

    Prices the flexible-load lever (design doc §5): what curtailment and
    shedding were worth over the year.
    """

    curtailed_gpu_mwh: float
    shed_mwh: float
    curtailed_hours: int
    shed_hours: int


class ScenarioMetrics(BaseModel):
    """Scalar evaluation of one architecture — ``ScenarioResult`` minus hourly.

    The five evaluation axes (design doc §6) plus the economics behind them;
    the full 8760-hour series stays in the engine and is not persisted or
    serialized in the MVP.
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
    dispatch: DispatchSummary

    @classmethod
    def from_engine(cls, result: ScenarioResult) -> ScenarioMetrics:
        hourly = result.hourly
        curtailed_mw = hourly.curtailed_gpu_mw
        shed_mw = hourly.shed_mw
        return cls(
            architecture=result.architecture,
            chain_efficiency=result.chain_efficiency,
            annual_energy_mwh=result.annual_energy_mwh,
            loss_mwh=result.loss_mwh,
            capex_usd=result.capex_usd,
            opex_usd_year=result.opex_usd_year,
            cost_per_mwh=result.cost_per_mwh,
            time_to_power_months=result.time_to_power_months,
            resilience_score=result.resilience_score,
            carbon_kgCO2_kWh=result.carbon_kgCO2_kWh,
            dispatch=DispatchSummary(
                curtailed_gpu_mwh=float(curtailed_mw.sum()),  # 1 h steps: MW·1 h = MWh
                shed_mwh=float(shed_mw.sum()),
                curtailed_hours=int((curtailed_mw > 0.0).sum()),
                shed_hours=int((shed_mw > 0.0).sum()),
            ),
        )


class StoredResults(BaseModel):
    """What POST /simulate persists: metrics plus the profile version they ran on."""

    site_version: int
    metrics: list[ScenarioMetrics]


class SimulateIn(BaseModel):
    """POST /simulate body. Omitted (or null) means run all four architectures."""

    architectures: list[str] | None = None

    @field_validator("architectures")
    @classmethod
    def _known_architectures(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        unknown = set(value) - set(ARCHITECTURES)
        if unknown:
            raise ValueError(
                f"unknown architecture(s) {sorted(unknown)}; "
                f"expected one of {sorted(ARCHITECTURES)}"
            )
        return list(dict.fromkeys(value))  # dedupe, preserve order


class RankedScenario(BaseModel):
    architecture: str
    score: float
    axis_scores: dict[str, float]
    metrics: ScenarioMetrics


class ResultsPayload(BaseModel):
    """GET /results and POST /simulate response: ranking plus visible weights."""

    site_version: int
    stale: bool  # the stored run predates the current site profile version
    weights: dict[str, float]
    ranking: list[RankedScenario]


class SensitivityIn(BaseModel):
    """POST /sensitivity body: one parameter axis swept over a range."""

    model_config = ConfigDict(extra="forbid")

    param: str
    range: list[float]
    architectures: list[str] | None = None

    @field_validator("param")
    @classmethod
    def _known_axis(cls, value: str) -> str:
        from engine.sensitivity import AXIS_ORDER  # local: keeps engine import lazy

        if value not in AXIS_ORDER:
            raise ValueError(f"unknown param {value!r}; expected one of {list(AXIS_ORDER)}")
        return value

    @field_validator("range")
    @classmethod
    def _sane_range(cls, value: list[float]) -> list[float]:
        if not value:
            raise ValueError("range must contain at least one value")
        if len(value) > 100:
            # Sensitivity points are full re-simulations; bound the payload.
            raise ValueError("range must contain at most 100 values")
        bad = [v for v in value if not math.isfinite(v) or v < 0.0]
        if bad:
            raise ValueError(f"range values must be non-negative finite numbers, got {bad[:3]}")
        return value

    @field_validator("architectures")
    @classmethod
    def _known_architectures(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        unknown = set(value) - set(ARCHITECTURES)
        if unknown:
            raise ValueError(
                f"unknown architecture(s) {sorted(unknown)}; "
                f"expected one of {sorted(ARCHITECTURES)}"
            )
        return list(dict.fromkeys(value))


class SensitivityPointOut(BaseModel):
    """One (value, architecture) cell of the sweep matrix — mirrors the engine dataclass."""

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
    # Spec-mandated field name (art_Xihp9Qa2 engine contract): kg CO2 per kWh.
    carbon_kgCO2_kWh: float  # noqa: N815

    @classmethod
    def from_engine(cls, point: SensitivityPoint) -> SensitivityPointOut:
        return cls(**{f.name: getattr(point, f.name) for f in dataclasses.fields(point)})


class SensitivityPayload(BaseModel):
    """POST /sensitivity response: the swept matrix with its axes echoed."""

    param: str
    values: list[float]
    architectures: list[str]
    points: list[SensitivityPointOut]
