# PowerHubX Testing Plan (Spec Deliverable D4)

Spec: **PowerHubX MVP and DOE Pitch Spec** (`art_Xihp9Qa2`), deliverable D4.
This plan maps every test in the repository to the spec requirement it
verifies, defines the CI merge gate, and states explicitly what is **not**
tested per the spec's scope boundary.

## 1. Suite inventory and how to run it

| Suite | Location | Command (repo root unless noted) |
|---|---|---|
| Engine + API unit/property tests | `engine/tests/`, `apps/api/tests/` | `pytest` (root `pyproject.toml` sets `testpaths`) |
| Lint | all Python trees | `ruff check .` |
| Type check | `engine`, `apps/api/src` | `mypy .` |
| Frontend unit + type check | `apps/web/src` | `cd apps/web && npm run build && npm test` (vitest run) |
| End-to-end | `apps/web/e2e/` | `cd apps/web && npm run test:e2e` (Playwright; boots Vite dev server + FastAPI backend via `webServer`) |
| DOE pitch structure | `docs/doe/` | `python3 docs/doe/check_pitch_words.py` |

Python suite coverage of both test trees is enforced: the root
`[tool.pytest.ini_options]` sets `testpaths = ["engine/tests", "apps/api/tests"]`,
so a bare `pytest` cannot silently skip either package.

## 2. Spec → test traceability (D2: simulation & evaluation engine)

Every D2 acceptance criterion in the spec has at least one named test.
"Spec" column quotes the criterion's operative language.

| Spec acceptance criterion (D2) | Verifying tests |
|---|---|
| "each architecture's loss chain sums to the documented chain efficiency within ±0.5 pp" | `engine/tests/test_chains.py::test_chain_sum_matches_documented_efficiency` — asserts per-architecture chain efficiency within 0.5 pp of `assumptions.py`; `test_conventional_chain_architectures_share_documented_efficiency` pins the shared conventional chain |
| "`dispatch_gpu_flexible_load` never curtails the critical share and never discharges BESS below `min_soc` (property-based via hypothesis, ≥200 examples)" | `engine/tests/test_dispatch.py::test_dispatch_never_violates_bess_floor_or_critical_share`, `::test_bess_never_discharges_below_min_soc_from_any_starting_soc`, `::test_bess_reservation_rule_leaves_the_floor_intact` — all `@settings(max_examples=200)` |
| Dispatch priority (BESS → curtailment → shed) | `engine/tests/test_dispatch.py::test_dispatch_priority_is_bess_then_curtailment_then_shed`, `::test_zero_flexible_share_curtails_nothing` |
| "LCOE math reproduces a hand-computed fixture" | `engine/tests/test_economics.py::test_lcoe_reproduces_hand_computed_fixture`, `::test_lcoe_uses_capital_recovery_not_raw_capex` |
| "edge cases — zero DER assets, zero flexible share, deficit exceeding all resources — return defined results, not exceptions" | `engine/tests/test_edge_cases.py::test_zero_der_assets_defined_results`, `::test_zero_der_assets_score_zero_resilience_except_microgrid`, `::test_zero_flexible_share_curtails_nothing_and_sheds_instead`, `::test_deficit_beyond_all_resources_sheds`, `::test_zero_it_load_defined_results`, `::test_invalid_site_still_rejected` |
| "Full 8760-hour run on the reference site profile completes in <5 s per architecture (deterministic)" | `engine/tests/test_performance.py::test_full_year_under_five_seconds` — runs all four architectures, asserts per-architecture wall clock < 5 s and run-to-run determinism; hourly coverage pinned by `test_chains.py::test_hourly_series_covers_full_year` |
| "MVDC-SST hybrid result shows a strictly higher `chain_efficiency` than grid-only on the same profile" | `engine/tests/test_core_claim.py::test_mvdc_sst_hybrid_efficiency_exceeds_grid_only`, `::test_mvdc_sst_hybrid_loses_less_energy_than_grid_only`, `::test_relative_loss_reduction_lands_in_r2_target_band`, `::test_placeholder_stages_match_r2_conventional_loss_band` |

Supporting D2 coverage (not spec-named, guards regressions in the same area):
`test_smoke.py` — `SiteProfile` construction and rejection of negative MW /
invalid criticality, with hypothesis-generated invalid fields;
`test_sensitivity.py` — sweep determinism, tariff monotonicity, GPU-utilization
scaling, lead-time effects, and axis validation (unknown axis, negative values).

## 3. Spec → test traceability (D3: MVP web application)

### API (`apps/api/tests/`, pytest + httpx `TestClient`)

| Spec acceptance criterion (D3) | Verifying tests |
|---|---|
| "create/simulate/results/report happy path" | `apps/api/tests/test_api_flow.py::test_full_happy_path` — create → site → simulate → ranked results → sensitivity → report in one flow; per-endpoint round-trips in `test_api_projects.py::test_get_project_roundtrip`, `test_api_simulate.py::test_results_roundtrip_ranked`, `test_api_report.py::test_report_happy_html` |
| "invalid `SiteProfile` (negative MW, missing fields) → 422 with field errors" | `test_api_projects.py::test_put_site_rejects_negative_mw`, `::test_put_site_rejects_missing_fields`, plus bad criticality / bad date / out-of-range share / non-finite numbers; sensitivity-parameter 422s in `test_api_sensitivity.py::test_sensitivity_unknown_param_422`, `::test_sensitivity_negative_value_422`, `::test_sensitivity_oversized_range_422`; unknown-architecture 422 in `test_api_simulate.py::test_simulate_unknown_architecture_422` |
| "simulate on a project with no site → 409" | `test_api_simulate.py::test_simulate_without_site_409`; sibling 409s: `::test_results_before_simulate_409`, `test_api_report.py::test_report_before_simulate_409`, `test_api_sensitivity.py::test_sensitivity_without_site_409` |
| Supporting contracts | 404 on every endpoint for a missing project (`test_api_flow.py::test_unknown_project_404_on_every_endpoint`); site update bumps version (`test_api_projects.py::test_put_site_bumps_version`); results go stale after site change (`test_api_flow.py::test_site_change_marks_results_stale_until_resimulated`, `test_api_simulate.py::test_results_stale_after_site_change`); deterministic ranking (`test_api_simulate.py::test_ranking_deterministic`); report escapes user input (`test_api_report.py::test_report_escapes_user_input`); core claim visible through the API (`test_api_simulate.py::test_core_claim_visible_through_api`) |

### Frontend (`apps/web/src`, vitest + Testing Library)

| Spec acceptance criterion (D3) | Verifying tests |
|---|---|
| "wizard validates each step and blocks progression on invalid input" | `src/wizard/IntakeWizard.test.tsx` — blocks empty step 1, non-numeric tariff, negative MW, missing criticality, missing date; `src/wizard/validation.test.ts` — per-field validation table, `toSiteProfile` shape, never emits NaN, throws on invalid draft |
| "dashboard renders all four scenarios with ranked recommendation" | `src/dashboard/ComparisonDashboard.test.tsx::renders all four architectures and the ranked recommendation` and `::renders the five evaluation axes for every architecture` |
| "empty state (no project) is reachable and actionable" | `ComparisonDashboard.test.tsx::shows an actionable empty state when no scenarios exist`; reachable-from-anywhere via `IntakeWizard.test.tsx::returns to an empty, actionable wizard from the Start over button` (and the Reset-path test) |

Additional component coverage: `SensitivityPanel.test.tsx` (slider-driven
re-query, debouncing, loading/error states), `ReportView.test.tsx` (loading,
retry on failure, opens printable report URL), `App.test.tsx` (wizard →
simulate → ranked dashboard → report integration, API-failure surfacing).

### E2E (Playwright)

| Spec acceptance criterion (D3) | Verifying test |
|---|---|
| "one happy path — fill wizard, run simulate, see comparison, open report — runs in CI against a dev server" | `apps/web/e2e/happy-path.spec.ts`, executed by the CI `e2e` job; `playwright.config.ts` `webServer` boots the Vite dev server and the FastAPI backend (on Python 3.11 with the engine/API packages installed) |

## 4. Spec → test traceability (D5: DOE pitch structure)

The pitch word-count gate is `docs/doe/check_pitch_words.py`, run in CI
(job `pitches`). It enforces the publicly verifiable ConnectWerx FY26 Fall
caps — Narrative 1 ≤ 100, Narratives 2–4 ≤ 200 each, Short answer 1 ≤ 25,
narrative total ≤ 500 — and reports unenforceable counts (caps only stated
inside AMP) as informational. The checker matches both pitch heading styles:
Topic 3 (`### Narrative N` / `### Short answer N`) and Topic 22
(`### A1.`–`A4.` / `### B1.`–`B3.`), so both documents are actually counted.

## 5. CI gate — all suites green = mergeable

`.github/workflows/ci.yml` runs on every pull request to `main` and on
pushes to `main`:

| Job | Runs |
|---|---|
| `python` | ruff → mypy (strict) → pytest, on Python 3.11 and 3.13 |
| `web` | `tsc -b && vite build` → vitest run |
| `e2e` | Playwright against dev-server + FastAPI backend |
| `pitches` | `check_pitch_words.py` over `docs/doe/pitch-*.md` |
| `merge-gate` | aggregate: `needs: [python, web, e2e, pitches]`; succeeds only when every suite above is green |

**Merge rule:** a PR to `main` is mergeable only when the `merge-gate` check
is green. Branch protection should mark `merge-gate` required (one check
stands in for the full matrix, so a new suite can be added to the workflow
without reconfiguring branch protection). Local runs are the primary gate —
run the suites above before pushing; CI is the final gate.

Note the Python matrix: `pytest`/`mypy`/`ruff` run on both Python 3.11 (the
spec's stack floor) and 3.13; a failure on either version blocks the gate.

## 6. What is NOT tested (spec scope boundary)

Per the spec, the MVP is **pre-engineering feasibility** — it deliberately
does not cover:

- **EMT/protection-grade validation.** No electromagnetic-transient or
  protection-coordination modeling, and nothing here is validated against
  PSCAD/ETAP-class studies. Loss chains and dispatch are deterministic
  engineering-arithmetic models, not utility-submittable analysis.
- **Utility-grade studies or filings.** No interconnection-application,
  tariff-filing, or regulatory format is generated or checked.
- **Authentication, multi-tenancy, or concurrency.** The SQLite store is
  single-project-per-session MVP scope; no access control is tested because
  none exists.
- **Performance beyond the one spec number.** The < 5 s / 8760 h per
  architecture budget is the only latency criterion; API latency, load, and
  scale are untested.
- **Real-world model calibration.** Assumptions in
  `engine/engine/assumptions.py` are sourced or labeled
  *placeholder — tune before customer use* (per D1); tests assert internal
  consistency of those numbers, not their empirical accuracy.
- **Browser matrix beyond Chromium.** Playwright runs one browser on one
  viewport in CI; cross-browser rendering is out of MVP scope.
- **PDF rendering.** The report is HTML with print-to-PDF left to the
  browser; the print output itself is not asserted.

These gaps are the spec's intended boundary, not deferred defects; closing
any of them is downstream scope via the `Architecture` protocol extension
seam named in `docs/design.md`.
