"""Shared fixtures: the reference site profile and an override factory."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from engine.models import SiteProfile

REFERENCE_PROFILE: dict[str, Any] = {
    "grid_limit_mw": 50.0,
    "it_load_mw": 30.0,
    "flexible_share": 0.3,
    "rack_density_kw": 132.0,
    "criticality": "tier3",
    "bess_mwh": 100.0,
    "pv_mw": 10.0,
    "fuel_cell_mw": 5.0,
    "genset_mw": 5.0,
    "tariff_usd_kwh": 0.08,
    "interconnection_wait_months": 36,
    "target_energization": "2027-06-01",
}


def make_site(**overrides: Any) -> SiteProfile:
    """The reference site with named overrides."""
    base = dict(REFERENCE_PROFILE)
    base.update(overrides)
    return SiteProfile(**base)


@pytest.fixture
def site_factory() -> Callable[..., SiteProfile]:
    return make_site


@pytest.fixture
def reference_site() -> SiteProfile:
    return make_site()
