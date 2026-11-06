"""Property tests for the spec's dispatch contract (D2: hypothesis, 200
examples — spec art_Xihp9Qa2: never curtail the critical share, never
discharge the BESS below min_soc, shed only after both are exhausted)."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.dispatch import bess_available_discharge_mw, dispatch_gpu_flexible_load

EPS = 1e-9


def test_bess_reservation_rule_leaves_the_floor_intact() -> None:
    """Min-SOC reservation: only energy above the floor is dischargeable."""
    assert bess_available_discharge_mw(soc_mwh=50.0, min_soc_mwh=10.0) == 40.0
    assert bess_available_discharge_mw(soc_mwh=10.0, min_soc_mwh=10.0) == 0.0
    # Already below the floor (e.g. after a harder event than planned for):
    # the reservation holds — nothing is dischargeable.
    assert bess_available_discharge_mw(soc_mwh=5.0, min_soc_mwh=10.0) == 0.0


@settings(max_examples=200)
@given(
    deficit=st.floats(min_value=0.0, max_value=500.0),
    flexible=st.floats(min_value=0.0, max_value=200.0),
    available=st.floats(min_value=0.0, max_value=100.0),
    headroom=st.floats(min_value=0.0, max_value=80.0),
    min_soc=st.floats(min_value=0.0, max_value=20.0),
)
def test_dispatch_never_violates_bess_floor_or_critical_share(
    deficit: float,
    flexible: float,
    available: float,
    headroom: float,
    min_soc: float,
) -> None:
    soc = min_soc + headroom
    dispatch = dispatch_gpu_flexible_load(deficit, flexible, available, min_soc, soc)

    # BESS never discharged below min_soc, never beyond availability.
    assert -EPS <= dispatch.bess_mw <= min(headroom, available) + EPS
    # Critical share never curtailed: only the flexible load is.
    assert -EPS <= dispatch.curtailed_mw <= flexible + EPS
    # Shed exists only after BESS and curtailment are exhausted, and the
    # split conserves the deficit.
    assert dispatch.shed_mw >= -EPS
    total = dispatch.bess_mw + dispatch.curtailed_mw + dispatch.shed_mw
    assert total == pytest.approx(deficit, abs=EPS)
    # When resources cover the deficit, nothing is shed.
    if deficit <= min(available, headroom) + flexible + EPS:
        assert dispatch.shed_mw <= EPS
