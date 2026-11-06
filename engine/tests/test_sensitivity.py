"""D2 acceptance: the sensitivity sweep is deterministic and well-behaved
(spec art_Xihp9Qa2 — same input produces identical output; grid-only cost is
monotone in tariff)."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from engine.architectures import ARCHITECTURES, GridOnly, MvdcSstHybrid
from engine.assumptions import DER_EQUIPMENT_LEAD_MONTHS, SST_EQUIPMENT_LEAD_MONTHS
from engine.models import SiteProfile
from engine.sensitivity import (
    AXIS_EQUIPMENT_LEAD_TIME,
    AXIS_GPU_UTILIZATION,
    AXIS_TARIFF,
    sweep,
)

TARIFF_LADDER = (0.04, 0.08, 0.12, 0.20)


def test_sweep_is_deterministic(
    site_factory: Callable[..., SiteProfile],
) -> None:
    site = site_factory()
    axes = {
        AXIS_TARIFF: TARIFF_LADDER,
        AXIS_GPU_UTILIZATION: (0.5, 0.8, 1.0),
        AXIS_EQUIPMENT_LEAD_TIME: (0.5, 1.0, 2.0),
    }
    first = sweep(site, axes)
    second = sweep(site, axes)

    assert first == second
    assert len(first) == (4 + 3 + 3) * len(ARCHITECTURES)  # 10 values x 4 archs


def test_grid_only_cost_is_strictly_increasing_in_tariff(
    site_factory: Callable[..., SiteProfile],
) -> None:
    """Non-binding grid limit: import volume is tariff-independent (no price
    arbitrage), so the levelized cost rises strictly with the tariff."""
    site = site_factory()  # 50 MW limit vs 30 MW load: nothing binds
    points = sweep(site, {AXIS_TARIFF: TARIFF_LADDER}, architectures=[GridOnly()])

    costs = [point.cost_per_mwh for point in points]
    assert costs == sorted(costs)
    assert len(set(costs)) == len(costs)  # strictly, not merely non-decreasing


def test_gpu_utilization_scales_delivered_energy(
    site_factory: Callable[..., SiteProfile],
) -> None:
    site = site_factory()
    full = sweep(site, {AXIS_GPU_UTILIZATION: (1.0,)}, architectures=[GridOnly()])
    half = sweep(site, {AXIS_GPU_UTILIZATION: (0.5,)}, architectures=[GridOnly()])

    ratio = half[0].annual_energy_mwh / full[0].annual_energy_mwh
    assert ratio == pytest.approx(0.5, rel=1e-9)


def test_lead_time_factor_scales_equipment_timing(
    site_factory: Callable[..., SiteProfile],
) -> None:
    site = site_factory()  # 36-month interconnection wait
    points = sweep(
        site,
        {AXIS_EQUIPMENT_LEAD_TIME: (0.0, 1.0, 2.0)},
        architectures=[MvdcSstHybrid()],
    )
    by_value = {point.value: point.time_to_power_months for point in points}

    assert by_value[1.0] == pytest.approx(
        site.interconnection_wait_months + SST_EQUIPMENT_LEAD_MONTHS
    )
    assert by_value[2.0] == pytest.approx(
        site.interconnection_wait_months + 2.0 * SST_EQUIPMENT_LEAD_MONTHS
    )
    assert by_value[0.0] == float(site.interconnection_wait_months)


def test_lead_time_factor_can_pull_microgrid_ahead_of_the_queue(
    site_factory: Callable[..., SiteProfile],
) -> None:
    site = site_factory(interconnection_wait_months=36)
    points = sweep(
        site,
        {AXIS_EQUIPMENT_LEAD_TIME: (0.5,)},
        architectures=[ARCHITECTURES["islandable-microgrid"]],
    )

    assert points[0].time_to_power_months == pytest.approx(
        0.5 * DER_EQUIPMENT_LEAD_MONTHS
    )


def test_unknown_axis_rejected(site_factory: Callable[..., SiteProfile]) -> None:
    with pytest.raises(ValueError, match="unknown axis"):
        sweep(site_factory(), {"price": (0.08,)})


def test_negative_axis_value_rejected(site_factory: Callable[..., SiteProfile]) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        sweep(site_factory(), {AXIS_TARIFF: (-0.01,)})


def test_negative_lead_time_factor_rejected(
    site_factory: Callable[..., SiteProfile],
) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ARCHITECTURES["mvdc-sst-hybrid"].simulate(site_factory(), lead_time_factor=-1.0)
