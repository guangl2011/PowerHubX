"""Ranked recommendation across the five evaluation axes (design doc §6.1).

Pure functions over ``ScenarioMetrics`` — no engine, no I/O — so the ranking
is trivially testable and the dashboard can re-rank client-side from the
exposed per-axis scores. Min-max normalization maps every axis to 0-1 with
its favor direction; an axis that ties across all scenarios scores 1.0 for
everyone (neutral, not penalized). Weights are the design doc's declared MVP
placeholder (equal) and ride in every results response so a customer can see
— and override client-side — the priority order they imply.
"""

from __future__ import annotations

from api.schemas import RankedScenario, ScenarioMetrics

# +1: higher is better. -1: lower is better. Key set IS the five-axis vocabulary.
AXIS_DIRECTION: dict[str, int] = {
    "chain_efficiency": 1,
    "cost_per_mwh": -1,
    "time_to_power_months": -1,
    "resilience_score": 1,
    "carbon_kgCO2_kWh": -1,
}

AXIS_LABELS: dict[str, str] = {
    "chain_efficiency": "Chain efficiency",
    "cost_per_mwh": "Cost per delivered MWh ($/MWh)",
    "time_to_power_months": "Time to power (months)",
    "resilience_score": "Resilience score (0-1)",
    "carbon_kgCO2_kWh": "Carbon intensity (kg CO2/kWh)",
}

DEFAULT_WEIGHTS: dict[str, float] = dict.fromkeys(AXIS_DIRECTION, 1.0)


def normalize_axes(metrics: list[ScenarioMetrics]) -> dict[str, dict[str, float]]:
    """Per-axis min-max scores in [0, 1], favoring each axis's better direction.

    Returns {axis: {architecture: score}}. A constant axis scores 1.0
    everywhere so tying on an axis never distorts the ranking.
    """
    scores: dict[str, dict[str, float]] = {}
    for axis in AXIS_DIRECTION:
        values = {m.architecture: float(getattr(m, axis)) for m in metrics}
        low, high = min(values.values()), max(values.values())
        if high == low:
            scores[axis] = dict.fromkeys(values, 1.0)
            continue
        maximize = AXIS_DIRECTION[axis] > 0
        scores[axis] = {
            arch: _scaled(value, low, high, maximize) for arch, value in values.items()
        }
    return scores


def _scaled(value: float, low: float, high: float, maximize: bool) -> float:
    """Map value to [0, 1] where the axis's better end maps to 1."""
    fraction = (value - low) / (high - low)
    return fraction if maximize else 1.0 - fraction


def rank_scenarios(
    metrics: list[ScenarioMetrics],
    weights: dict[str, float] | None = None,
) -> list[RankedScenario]:
    """Weighted-average ranking, best first; ties break by architecture name."""
    axes = normalize_axes(metrics)
    active_weights = weights if weights is not None else DEFAULT_WEIGHTS
    total_weight = sum(active_weights.get(axis, 0.0) for axis in AXIS_DIRECTION)
    ranked = [
        RankedScenario(
            architecture=m.architecture,
            score=(
                sum(
                    active_weights.get(axis, 0.0) * axes[axis][m.architecture]
                    for axis in AXIS_DIRECTION
                )
                / total_weight
                if total_weight > 0.0
                else 0.0
            ),
            axis_scores={axis: axes[axis][m.architecture] for axis in AXIS_DIRECTION},
            metrics=m,
        )
        for m in metrics
    ]
    ranked.sort(key=lambda r: (-r.score, r.architecture))
    return ranked
