"""D2 acceptance: the levelized-cost math reproduces a hand-computed example.

The worked example (spec art_Xihp9Qa2, D2: "LCOE math reproduces a
hand-computed fixture"):

    Site: grid-only, it_load 30 MW, grid limit 1 MW (binds every hour),
    zero DER assets, zero flexible share, tariff $0.08/kWh.

    Grid import is then exactly 1 MW every hour -> 8,760 MWh/yr, and GPU
    delivery is exactly chain efficiency per hour.

    chain efficiency = 0.990 x 0.970 x 0.995 x 0.960 x 0.935 = 0.8576554536
    delivered        = 8,760 x 0.8576554536             = 7,513.0617... MWh
    capex            = 30,000 kW x ($200 + $350)/kW     = $16,500,000
    opex             = 8,760 x 1,000 x $0.08 + 2% capex = $700,800 + $330,000
    CRF              = 0.08 x 1.08^30 / (1.08^30 - 1)   = 0.088827...
    LCOE             = (capex x CRF + opex) / delivered
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from engine.architectures import ARCHITECTURES
from engine.models import SiteProfile

# The five conventional-chain stage efficiencies, in documented order
# (assumptions.py). Written as literals so the fixture is independent of the
# engine's own chain code.
STAGE_EFFICIENCIES = (0.990, 0.970, 0.995, 0.960, 0.935)


def test_lcoe_reproduces_hand_computed_fixture(
    site_factory: Callable[..., SiteProfile],
) -> None:
    site = site_factory(
        it_load_mw=30.0,
        grid_limit_mw=1.0,
        bess_mwh=0.0,
        pv_mw=0.0,
        fuel_cell_mw=0.0,
        genset_mw=0.0,
        flexible_share=0.0,
        tariff_usd_kwh=0.08,
    )
    result = ARCHITECTURES["grid-only"].simulate(site)

    chain_efficiency = 1.0
    for stage in STAGE_EFFICIENCIES:
        chain_efficiency *= stage

    # Hand-computed expected values (worked example in the module docstring).
    capex = 30_000.0 * (200.0 + 350.0)
    opex = 8_760.0 * 1_000.0 * 0.08 + 0.02 * capex
    crf = 0.08 * (1.08**30) / ((1.08**30) - 1.0)
    delivered = 8_760.0 * chain_efficiency
    expected_lcoe = (capex * crf + opex) / delivered

    assert result.chain_efficiency == pytest.approx(chain_efficiency, rel=1e-12)
    assert result.capex_usd == pytest.approx(capex, rel=1e-12)
    assert result.opex_usd_year == pytest.approx(opex, rel=1e-12)
    assert result.annual_energy_mwh == pytest.approx(delivered, rel=1e-9)
    assert result.cost_per_mwh == pytest.approx(expected_lcoe, rel=1e-9)

    # Cross-checks on the same fixture: carbon from grid imports only, and
    # zero-DER grid-only has no islanding capability. Carbon follows the
    # ScenarioResult convention: grid_import_mwh x intensity / delivered_mwh.
    assert result.carbon_kgCO2_kWh == pytest.approx(
        8_760.0 * 0.38 / delivered, rel=1e-9
    )
    assert result.resilience_score == 0.0


def test_lcoe_uses_capital_recovery_not_raw_capex(
    site_factory: Callable[..., SiteProfile],
) -> None:
    """The levelized cost must annualize capex (CRF < 1/1 at 8%/30y), not
    divide raw capex in — a 1/30 mistake would roughly double the tariff share."""
    site = site_factory()
    result = ARCHITECTURES["grid-only"].simulate(site)

    crf = 0.08 * (1.08**30) / ((1.08**30) - 1.0)
    assert crf < 0.1
    expected = (result.capex_usd * crf + result.opex_usd_year) / result.annual_energy_mwh
    assert result.cost_per_mwh == pytest.approx(expected, rel=1e-12)
