"""D2 acceptance: degenerate inputs return defined results, not exceptions
(spec art_Xihp9Qa2 — zero DER assets, zero flexible share, deficit exceeding
all resources)."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest

from engine.architectures import ARCHITECTURES
from engine.models import SiteProfile

RESULT_SCALARS = (
    "chain_efficiency",
    "annual_energy_mwh",
    "loss_mwh",
    "capex_usd",
    "opex_usd_year",
    "cost_per_mwh",
    "time_to_power_months",
    "resilience_score",
    "carbon_kgCO2_kWh",
)


def _assert_defined(result: object, name: str) -> None:
    for field in RESULT_SCALARS:
        value = getattr(result, field)
        assert np.isfinite(value), f"{name}.{field} not finite"


def test_zero_der_assets_defined_results(
    site_factory: Callable[..., SiteProfile],
) -> None:
    site = site_factory(bess_mwh=0.0, pv_mw=0.0, fuel_cell_mw=0.0, genset_mw=0.0)
    for name, arch in ARCHITECTURES.items():
        result = arch.simulate(site)
        _assert_defined(result, name)
        assert np.isfinite(result.hourly.gpu_delivered_mw).all()
        assert np.isfinite(result.hourly.bess_soc_mwh).all()


def test_zero_der_assets_score_zero_resilience_except_microgrid(
    site_factory: Callable[..., SiteProfile],
) -> None:
    """With no BESS and no fueled units there is nothing to island with. The
    microgrid's DER assets come from the site, so zero-asset sites make every
    architecture DER-less — and only its zero-critical-load convention could
    differ (not triggered at the reference load)."""
    site = site_factory(bess_mwh=0.0, pv_mw=0.0, fuel_cell_mw=0.0, genset_mw=0.0)
    for name in ("grid-only", "grid+bess", "mvdc-sst-hybrid"):
        assert ARCHITECTURES[name].simulate(site).resilience_score == 0.0, name


def test_zero_flexible_share_curtails_nothing_and_sheds_instead(
    site_factory: Callable[..., SiteProfile],
) -> None:
    site = site_factory(flexible_share=0.0, grid_limit_mw=10.0, it_load_mw=30.0)
    for name, arch in ARCHITECTURES.items():
        result = arch.simulate(site)
        assert float(result.hourly.curtailed_gpu_mw.sum()) == 0.0, name
        assert float(result.hourly.shed_mw.sum()) > 0.0, name


def test_deficit_beyond_all_resources_sheds(
    site_factory: Callable[..., SiteProfile],
) -> None:
    """A 1 MW limit against a ~30 MW load with no DERs: the surplus is shed,
    never an exception."""
    site = site_factory(
        grid_limit_mw=1.0,
        bess_mwh=0.0,
        pv_mw=0.0,
        fuel_cell_mw=0.0,
        genset_mw=0.0,
        flexible_share=0.0,
    )
    result = ARCHITECTURES["grid-only"].simulate(site)
    assert float(result.hourly.shed_mw.sum()) > 0.0
    # The limit binds every hour: 1 MW in, 1 MW x chain efficiency out.
    delivered = float(result.hourly.gpu_delivered_mw.sum())
    assert delivered == pytest.approx(8760.0 * result.chain_efficiency, rel=1e-6)


def test_zero_it_load_defined_results(
    site_factory: Callable[..., SiteProfile],
) -> None:
    site = site_factory(it_load_mw=0.0)
    for name, arch in ARCHITECTURES.items():
        result = arch.simulate(site)
        _assert_defined(result, name)
        assert result.annual_energy_mwh == 0.0
        assert result.cost_per_mwh == 0.0  # defined (no delivered energy)
        # No critical load to protect: defined as fully resilient.
        assert result.resilience_score == 1.0


def test_invalid_site_still_rejected(
    site_factory: Callable[..., SiteProfile],
) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        site_factory(pv_mw=-1.0)
