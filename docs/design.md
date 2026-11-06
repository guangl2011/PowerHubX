# PowerHubX Design Document

Spec of record: PowerHubX MVP and DOE Pitch Spec (`art_Xihp9Qa2`). Companion
document: [Product development plan](product-plan.md) — market framing,
personas, and product flow.

## 1. System overview and data flow

One project record flows left to right; every stage reads and enriches the
same JSON project model. No re-keying between stages — that continuity is the
onboarding simplification.

```
apps/web (React)          apps/api (FastAPI)               engine/ (pure Python)
┌──────────────────┐      ┌─────────────────────────┐      ┌──────────────────┐
│ Intake wizard     │ POST │ Project store (SQLite)  │      │ SiteProfile      │
│ (SiteProfile form)│─────▶│ project { site, version}│      │      │           │
│                   │      │        │                 │ call │      ▼           │
│                   │      │        ▼                 │─────▶│ Architecture      │
│                   │ PUT  │ simulate(site)           │      │  × 4 impls        │
│                   │      │        │                 │      │  loss chains,     │
│ Comparison        │ GET  │        ▼                 │      │  dispatch,        │
│ dashboard         │◀─────│ ScenarioResults (ranked) │◀─────│  economics        │
│ + sensitivity     │      │        │                 │      │        │          │
│ sliders           │ POST │        ▼                 │      │        ▼          │
│                   │      │ report HTML              │◀─────│ HourlySeries,     │
│ Report view       │ GET  │ (print-to-PDF)           │      │ ScenarioResult    │
└──────────────────┘      └─────────────────────────┘      └──────────────────┘
```

Data flow, stage by stage:

1. The wizard builds a `SiteProfile` (§3.1) and `PUT`s it to the API, which
   stores it and bumps the project's profile version.
2. `POST /simulate` hands the stored `SiteProfile` to each selected
   `Architecture` implementation (§4). The API owns orchestration and
   persistence only; all modeling lives in the engine.
3. Each run returns a `ScenarioResult` (§3.2) with an `HourlySeries`
   (§3.3). The API persists results and serves them ranked (§6).
4. `POST /sensitivity` re-runs selected architectures across a parameter
   range, producing a result matrix (§6.2).
5. `GET /report` renders the one-page HTML feasibility report from stored
   results; the browser prints it to PDF.

## 2. Module responsibilities

| Module | Responsibility | Explicitly does NOT |
|---|---|---|
| `engine/` | Pure, UI-free Python package: `SiteProfile`, the `Architecture` protocol and its four implementations, hourly dispatch (including GPU flexible-load curtailment), loss chains, economics, sensitivity helpers | No web-framework imports, no I/O, no persistence, no external services — a later API or CLI drives the same functions |
| `apps/api/` | FastAPI backend: project store (SQLite), validation, versioning, simulation orchestration, sensitivity runs, report rendering | No modeling math — all computation is delegated to `engine/` |
| `apps/web/` | React 18 + Vite + TypeScript frontend: intake wizard (step validation), comparison dashboard (five axes, sensitivity sliders, ranked recommendation), report view | No computation — the web app only orchestrates API calls and renders results |

The engine stays importable and testable without the web app so coders can
test it in isolation; the API is a thin orchestration shell; the web app is a
thin rendering shell.

## 3. Data model

### 3.1 `SiteProfile` — the intake record

Shape (implemented in `engine/engine/models.py`; fields validated in
`__post_init__` — negative MW and out-of-range fractions raise `ValueError`,
surfaced by the API as 422 with field errors):

```python
@dataclass(frozen=True)
class SiteProfile:
    grid_limit_mw: float
    it_load_mw: float
    flexible_share: float          # fraction of IT load eligible for curtailment
    rack_density_kw: float
    criticality: str               # "tier3" | "tier4" | "inference" | "training"
    bess_mwh: float
    pv_mw: float
    fuel_cell_mw: float
    genset_mw: float
    tariff_usd_kwh: float
    interconnection_wait_months: int
    target_energization: str       # ISO date
```

Profiles are frozen; the API versions them at the project level on every
`PUT /site`. Each architecture treats the profile as immutable input.

### 3.2 `ScenarioResult` — one architecture's evaluation

```python
@dataclass(frozen=True)
class ScenarioResult:
    architecture: str            # "grid-only" | "grid+bess" | "mvdc-sst-hybrid" | "islandable-microgrid"
    chain_efficiency: float      # grid-to-GPU delivered energy fraction
    annual_energy_mwh: float
    loss_mwh: float
    capex_usd: float
    opex_usd_year: float
    cost_per_mwh: float          # levelized, delivered
    time_to_power_months: float
    resilience_score: float      # 0–1, islanding duration + backup coverage
    carbon_kgCO2_kWh: float
    hourly: HourlySeries         # flows, BESS SOC, curtailed GPU hours
```

Every field is traceable to a design section: the traceability table in §8.

### 3.3 `HourlySeries` — the time series behind the summary

Per-hour records (8760-hour profile, or representative-day acceleration per
§7) carrying: grid import MW, conversion losses MW, BESS state of charge MWh,
curtailed flexible-GPU MW, shed MW, and DER output (PV, fuel cell, genset) MW.
The dashboard reads summaries from `ScenarioResult`; the report and future
diagnostics read `HourlySeries` for the shape of dispatch over time.

## 4. The `Architecture` protocol — the extension seam

```python
class Architecture(Protocol):
    name: str
    def simulate(self, site: SiteProfile) -> ScenarioResult: ...
```

Every power architecture is a plugin behind this protocol. The API and the
dashboard never branch on which architecture they are showing — they render
`ScenarioResult` fields uniformly, so a new architecture is a new engine
class, nothing else. This is also the seam for the later integration targets
(EMT-grade model plugins, per the product plan's Phase 4).

Four MVP implementations, each with its own loss chain (§4.1) and dispatch
behavior (§5):

| `name` | Conversion chain (grid → GPU) | DER and islanding behavior |
|---|---|---|
| `grid-only` | MV transformer → AC UPS/rectifier → DC-DC → GPU VRM (4–5 stages, the baseline chain) | No on-site generation; deficit above `grid_limit_mw` is shed; resilience from grid alone |
| `grid+bess` | Same chain as `grid-only`, plus a BESS on the DC bus | BESS discharges into deficits and curtails GPU flexible load per §5; no intentional islanding |
| `mvdc-sst-hybrid` | MV SST (single stage: MV AC → MVDC → LVDC) → GPU VRM — merges what were 2–3 separate conversion stages into one SST stage | Same BESS/flexibility behavior as `grid+bess`, on the SST MVDC bus |
| `islandable-microgrid` | Baseline AC chain plus full DER set (BESS, PV, fuel cell, genset) with grid-forming control | Sustained intentional islanding: DER dispatch order and BESS `min_soc` reservation per §5 |

**Core-claim invariant (tested, D2):** on the same `SiteProfile`,
`mvdc-sst-hybrid` must show strictly higher `chain_efficiency` than
`grid-only`. The SST chain's merged stages mean fewer loss terms; the
per-stage assumptions in §4.1 make this structural, not incidental.

### 4.1 Loss-chain assumptions

Each architecture's chain efficiency is the product of its per-stage
efficiencies; unit tests assert the product reconciles with
`chain_efficiency` within ±0.5 percentage points.

| Stage | Assumption | Source / status |
|---|---|---|
| Traditional chain (4–5 conversions: MV transformer, AC UPS/rectifier, DC-DC, GPU VRM) | 8–15% total loss | Research estimate (spec findings log R1; user strategy doc `powerhubxdoe2026.md`) |
| MV transformer, traditional (standalone) | ≥98.5% efficient — the SST comparison must be made at system level, not against this stage alone | User strategy doc `powerhubxdoe2026.md` (reviewer-objection framing) |
| MV SST single-stage conversion (MV AC → LVDC, merging transformer + rectifier + PFC + DC-DC stages) | `placeholder — tune before customer use` | Placeholder pending component data |
| Grid+BESS additional AC-DC round trip | `placeholder — tune before customer use` | Placeholder pending component data |
| Per-stage efficiencies for the baseline chain (transformer, UPS, DC-DC, VRM individually) | `placeholder — tune before customer use` | Placeholder pending component data |
| PV, fuel cell, genset output efficiencies | `placeholder — tune before customer use` | Placeholder pending component data |

The 30–50% system-level chain-loss reduction claimed for the SST path (user
strategy doc) is a *target narrative* for the DOE pitches, not an engine
assumption; the engine computes chain efficiency from per-stage placeholders
and is calibrated against real data before customer use.

## 5. Dispatch model — GPU flexible load as a dispatchable resource

GPU load is modeled as dispatchable, not passive: during a grid-stress or
islanding event the engine serves load from, in order: (1) BESS discharge,
(2) flexible-load curtailment, (3) — only if still short — load shed.

```python
def dispatch_gpu_flexible_load(
    deficit_mw: float,
    flexible_gpu_mw: float,
    bess_discharge_mw: float,
    min_soc_mwh: float,
    soc_mwh: float,
) -> GpuDispatch:
    bess_used = min(bess_discharge_mw, max(soc_mwh - min_soc_mwh, 0.0) / 1.0)
    residual = deficit_mw - bess_used
    curtailed = min(residual, flexible_gpu_mw)
    shed = max(residual - curtailed, 0.0)
    return GpuDispatch(bess_mw=bess_used, curtailed_mw=curtailed, shed_mw=shed)
```

Invariants (property-tested with hypothesis, D2):

- **Never curtail the critical share.** Only `flexible_gpu_mw` (=
  `flexible_share × it_load_mw`) is ever curtailed.
- **Never discharge BESS below `min_soc`** — the reserve is held for
  grid-forming ride-through.
- Deficit exceeding all resources returns a defined `shed_mw` remainder, not
  an exception; edge cases (zero DER assets, zero flexible share) return
  defined results.

The dispatch split prices the flexibility value: the report states which GPUs
were curtailed and what that flexibility was worth to the architecture's
economics and resilience.

## 6. Evaluation axes — the five numbers

One vocabulary across engine, dashboard, and report. Each axis maps to
`ScenarioResult` fields (traceability: §8).

1. **Chain efficiency** (`chain_efficiency`) — fraction of energy drawn from
   the grid that reaches the GPU; the product of §4.1 stage efficiencies.
   Annual view: `annual_energy_mwh` (delivered) and `loss_mwh` (converted and
   lost in the chain).
2. **Cost per delivered MWh** (`cost_per_mwh`) — levelized:
   `(capex annualized + opex) / annual delivered MWh`. Capex and opex build
   from per-technology $/MW and $/MWh figures, all
   `placeholder — tune before customer use` pending market data.
3. **Time-to-power** (`time_to_power_months`) — months from today to usable
   capacity. For grid-dependent architectures this is dominated by
   `interconnection_wait_months` (site intake fact, up to years in congested
   markets per the research estimate in the product plan §1); on-site DER and
   equipment lead-time placeholders adjust it per architecture —
   `placeholder — tune before customer use`.
4. **Resilience score** (`resilience_score`, 0–1) — islanding duration plus
   backup coverage: from the hourly series, the fraction of a stress window
   the site can serve (critical load always; flexible load per §5 dispatch)
   without grid import, weighted by backup DER coverage.
5. **Carbon intensity** (`carbon_kgCO2_kWh`) — grid electricity emission
   factor times grid import share, net of on-site zero-carbon generation.
   Grid emission factor per site: `placeholder — tune before customer use`.

### 6.1 Ranking

The dashboard ranks the four scenarios and shows a recommendation. Ranking
weights across the five axes: `placeholder — tune before customer use` — the
MVP exposes the ranking with visible weights so a customer can re-rank by
their own priorities.

### 6.2 Sensitivity

`POST /sensitivity` varies one parameter across a range (electricity price,
GPU utilization, equipment lead time) and returns the result matrix. Each
architecture re-simulates deterministically; no interpolation or cached
approximation.

## 7. Simulation profile and performance

Full 8760-hour profile or representative-day acceleration; deterministic;
no external services. Performance criterion (D2): a full 8760-hour run on the
reference site profile completes in <5 s per architecture.

## 8. API shape and traceability

```
POST /api/projects                    # create project from wizard payload -> ProjectRecord
GET  /api/projects/{id}
PUT  /api/projects/{id}/site          # update SiteProfile (bumps version)
POST /api/projects/{id}/simulate      # run all 4 (or selected) architectures
GET  /api/projects/{id}/results       # ScenarioResults, ranked
POST /api/projects/{id}/sensitivity   # {param, range} -> result matrix
GET  /api/projects/{id}/report        # HTML feasibility report (print-to-PDF)
```

Error contract: invalid `SiteProfile` → 422 with field errors (from the
engine's validation); simulate on a project with no site → 409.

### Traceability table — every `ScenarioResult` field

| Field | Defined | Computed by | Assumptions governing it |
|---|---|---|---|
| `architecture` | §3.2 | §4 protocol | — |
| `chain_efficiency` | §3.2, §6.1 | §4.1 loss chains | §4.1 stage table |
| `annual_energy_mwh` | §3.2, §6.1 | §7 hourly profile | §3.3 series definition |
| `loss_mwh` | §3.2, §6.1 | §4.1 loss chains | §4.1 stage table |
| `capex_usd` | §3.2, §6.2 | §6.2 economics | per-technology $/MW — placeholder, §6.2 |
| `opex_usd_year` | §3.2, §6.2 | §6.2 economics | opex placeholders, §6.2 |
| `cost_per_mwh` | §3.2, §6.2 | §6.2 economics | tariff + capex/opex placeholders |
| `time_to_power_months` | §3.2, §6.3 | §6.3 | `interconnection_wait_months` + lead-time placeholders |
| `resilience_score` | §3.2, §6.4 | §5 + §6.4 | dispatch invariants §5 |
| `carbon_kgCO2_kWh` | §3.2, §6.5 | §6.5 | grid emission factor placeholder |
| `hourly` | §3.3 | §5, §7 | §3.3 series definition |

## 9. What is explicitly not modeled (MVP scope boundary)

No authentication or multi-tenancy; no persistence beyond a single project
record per browser session plus the server-side SQLite project store; no
EMT/protection-grade models; no utility filing formats. The `Architecture`
protocol (§4) is the extension seam for those later. The MVP is
pre-engineering feasibility, not an ETAP/PSCAD replacement — stated in the
product plan and in every report the product produces.
