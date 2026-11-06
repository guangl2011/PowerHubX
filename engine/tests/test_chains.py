"""D2 acceptance: each architecture's hourly loss chain sums to its documented
chain efficiency within +/- 0.5 pp (spec art_Xihp9Qa2).

The pipeline applies every documented stage to every GPU-bound MWh, so the
aggregate delivered/input ratio must equal the product of stage efficiencies.
A mismatch means implementation and documentation drifted apart.
"""

from __future__ import annotations

import pytest

from engine.architectures import ARCHITECTURES
from engine.assumptions import LOSS_CHAINS, chain_efficiency
from engine.models import SiteProfile
from engine.results import ScenarioResult

TOLERANCE_PP = 0.005  # +/- 0.5 percentage points


@pytest.mark.parametrize("name", list(ARCHITECTURES), ids=list(ARCHITECTURES))
def test_chain_sum_matches_documented_efficiency(
    name: str, reference_site: SiteProfile
) -> None:
    result: ScenarioResult = ARCHITECTURES[name].simulate(reference_site)

    chain_input_mwh = float(result.hourly.chain_input_mw.sum())
    delivered_mwh = float(result.hourly.gpu_delivered_mw.sum())
    computed = delivered_mwh / chain_input_mwh
    documented = chain_efficiency(LOSS_CHAINS[name])

    assert computed == pytest.approx(documented, abs=TOLERANCE_PP)
    assert result.chain_efficiency == pytest.approx(documented, abs=TOLERANCE_PP)


@pytest.mark.parametrize("name", list(ARCHITECTURES), ids=list(ARCHITECTURES))
def test_hourly_series_covers_full_year(
    name: str, reference_site: SiteProfile
) -> None:
    result = ARCHITECTURES[name].simulate(reference_site)
    assert result.hourly.hour.shape == (8760,)


def test_conventional_chain_architectures_share_documented_efficiency() -> None:
    """grid+bess and islandable intentionally keep grid-only's chain (BESS and
    DERs sit upstream of it); their documented efficiency must agree."""
    names = ("grid-only", "grid+bess", "islandable-microgrid")
    efficiencies = {chain_efficiency(LOSS_CHAINS[name]) for name in names}
    assert len(efficiencies) == 1
