"""D2 acceptance: a full 8760-hour reference run completes < 5 s per
architecture (spec art_Xihp9Qa2). The run is deterministic with no external
services, so no representative-day acceleration is needed."""

from __future__ import annotations

import time

import pytest

from engine.architectures import ARCHITECTURES
from engine.models import SiteProfile

LIMIT_SECONDS = 5.0


@pytest.mark.parametrize("name", list(ARCHITECTURES), ids=list(ARCHITECTURES))
def test_full_year_under_five_seconds(name: str, reference_site: SiteProfile) -> None:
    start = time.perf_counter()
    ARCHITECTURES[name].simulate(reference_site)
    elapsed = time.perf_counter() - start
    assert elapsed < LIMIT_SECONDS, f"{name} took {elapsed:.2f}s"
