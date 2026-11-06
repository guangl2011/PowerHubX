"""Smoke tests for the bootstrap: package imports, model validation, and a
hypothesis property test proving the property-testing toolchain runs in CI."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

import engine
from engine.models import CRITICALITY_LEVELS, SiteProfile


def test_package_imports() -> None:
    assert engine.__version__ == "0.1.0"


def _site(**overrides: object) -> SiteProfile:
    base: dict[str, object] = {
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
    base.update(overrides)
    return SiteProfile(**base)  # type: ignore[arg-type]


def test_valid_site_profile_constructs() -> None:
    site = _site()
    assert site.it_load_mw == 30.0


@pytest.mark.parametrize("field", ["grid_limit_mw", "it_load_mw"])
def test_negative_mw_rejected(field: str) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        _site(**{field: -1.0})


def test_invalid_criticality_rejected() -> None:
    with pytest.raises(ValueError, match="criticality"):
        _site(criticality="not-a-tier")


@given(
    share=st.floats(min_value=0.0, max_value=1.0),
    criticality=st.sampled_from(CRITICALITY_LEVELS),
)
def test_flexible_share_and_criticality_domain(share: float, criticality: str) -> None:
    site = _site(flexible_share=share, criticality=criticality)
    assert 0.0 <= site.flexible_share <= 1.0
    assert site.criticality in CRITICALITY_LEVELS
