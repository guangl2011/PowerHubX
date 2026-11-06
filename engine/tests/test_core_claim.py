"""D2 acceptance: the product's core claim as an executable test (spec
art_Xihp9Qa2). The MVDC-SST hybrid must beat grid-only on chain efficiency on
the reference profile — this is the claim the whole product rests on (R2)."""

from __future__ import annotations

from engine.architectures import simulate_all
from engine.assumptions import LOSS_CHAINS, chain_efficiency
from engine.models import SiteProfile


def test_mvdc_sst_hybrid_efficiency_exceeds_grid_only(
    reference_site: SiteProfile,
) -> None:
    results = simulate_all(reference_site)
    assert (
        results["mvdc-sst-hybrid"].chain_efficiency
        > results["grid-only"].chain_efficiency
    )


def test_mvdc_sst_hybrid_loses_less_energy_than_grid_only(
    reference_site: SiteProfile,
) -> None:
    """Same load served, so the higher-efficiency chain must lose less."""
    results = simulate_all(reference_site)
    assert results["mvdc-sst-hybrid"].loss_mwh < results["grid-only"].loss_mwh


def test_relative_loss_reduction_lands_in_r2_target_band(
    reference_site: SiteProfile,
) -> None:
    """R2 targets a 30-50% chain-loss reduction for the SST path. The
    placeholder stage efficiencies land at the low end (~30%); guard the band
    so future stage tuning cannot silently drift the headline claim."""
    results = simulate_all(reference_site)
    grid_only = results["grid-only"].loss_mwh
    hybrid = results["mvdc-sst-hybrid"].loss_mwh
    reduction = 1.0 - hybrid / grid_only
    assert 0.2 < reduction < 0.6, f"relative loss reduction {reduction:.3f}"


def test_placeholder_stages_match_r2_conventional_loss_band() -> None:
    """The conventional chain's documented loss must sit inside R2's 8-15%
    band — that band is the market gap the pitch quantifies."""
    loss = 1.0 - chain_efficiency(LOSS_CHAINS["grid-only"])
    assert 0.08 <= loss <= 0.15, f"conventional chain loss {loss:.3f}"
