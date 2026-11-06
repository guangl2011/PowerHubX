# PowerHubX Product Development Plan

Spec of record: PowerHubX MVP and DOE Pitch Spec (`art_Xihp9Qa2`). Companion
document: [Design document](design.md) — the module-level view this plan refers to.

PowerHubX is a standard, productized feasibility-and-onboarding platform for AI
data center (AIDC) and microgrid power-architecture decisions. It takes a
customer from a guided 15-minute site intake to a defensible, side-by-side
comparison of four power architectures — grid-only, grid+BESS, hybrid AC/DC
with a medium-voltage solid-state transformer (MV SST), and an islandable
microgrid — evaluated on the same five axes, and carries that dataset forward
into a shareable feasibility report.

It is **not** a custom engineering consultancy and **not** a hardware vendor.
The MVP delivers software: simulation, evaluation, onboarding, and strategy
documents. Engineering-grade studies (ETAP/PSCAD-class), SST hardware, and
utility filings are downstream integration targets, not MVP scope.

**Load-bearing assumption:** customers (AIDC developers, colocation
operators, microgrid EPCs) will trust and act on a *standardized*
simulation-and-evaluation workflow instead of bespoke engineering studies.
Evidence that confirms it: onboarding time and study cost drop measurably in a
pilot. Evidence that breaks it: buyers insist on site-specific EMT/protection
studies per project, making standardization the wrong wedge — in that case the
MVP pivots to a pre-sales report generator only.

---

## 1. Market framing

AI data centers are colliding with a power system that cannot deliver capacity
at their pace. The consequences compound at every step of a project:

- **Time-to-power dominates every other constraint.** A data center can be
  built in roughly two years while grid interconnection in congested markets
  can take up to seven. Dominion, the utility at the center of "data center
  alley," reports ~70 GW of pending connection requests.
- **Equipment itself is scarce.** Lead times for transformers and switchgear
  run to years, with an estimated ~30% supply shortfall.
- **The conversion chain wastes what is already scarce.** The traditional
  13.8 kV → 480 V AC → UPS → 48/12 V DC → GPU VRM chain passes through 4–5
  conversions, losing 8–15% — a gap the SST/MVDC architecture attacks by
  merging stages.
- **AI racks concentrate load.** AI racks can draw up to ~40× the power
  density of conventional racks, stressing distribution and power quality
  beyond what the current chain was designed for.

> **Sourcing note:** the four figures above (7-year interconnection queues,
> ~30% equipment shortfall, 8–15% chain losses, ~40× rack density) are
> **research estimates** from the spec's findings log (R1: market research
> summarized 2026-11-06, citing Allianz Research 2026, S&P Global Market
> Intelligence 2026, Columbia Threadneedle 2026, POWER 2026). They set the
> product's evaluation axes and marketing narrative; no MVP acceptance
> criterion depends on their exact values. Product model assumptions that
> *do* drive computed results live in the design document, each numeric with
> a source or labeled `placeholder — tune before customer use`.

**The gap.** Every player in this market sells custom engineering. There is no
standard software product that takes a customer's site facts and returns a
defensible, comparable evaluation of grid-only vs. grid+BESS vs. hybrid AC/DC
with MV SST vs. islandable microgrid — with loss chains, economics,
resilience, and time-to-power side by side — and then carries that same
dataset forward into design and operations. Each project today starts from a
blank engineering study. Removing that onboarding friction is the product's
reason to exist.

**Positioning.** Standard feasibility-to-onboarding software. The competition
is not other software — it is the bespoke study. The wedge is speed and
comparability at the pre-feasibility stage, where decisions are made and
where a custom study has not yet been commissioned.

---

## 2. Personas

### 2.1 AIDC developer

- **Who:** a development team siting and financing a new AI data center
  (10–200 MW IT load), under pressure to lock an energization date.
- **Job to be done:** choose a power architecture early enough to influence
  land, interconnection requests, and capex models — with a defensible number
  for cost per delivered MWh and time-to-power.
- **Pain today:** the architecture comparison is a custom study with
  multi-week lead time; until it exists, financing conversations stall.
- **Success for them:** a ranked comparison with sensitivity ranges they can
  put in front of lenders and landowners within a day of knowing their site
  facts.
- **Key intake inputs they own:** IT load and rack density, criticality,
  target energization date, tariff, interconnection wait.

### 2.2 Colocation operator

- **Who:** an operator of existing or expanding colocation capacity facing
  AI-grade power density inside a fixed power envelope.
- **Job to be done:** decide whether to add BESS, upgrade the conversion
  chain, or pursue islanding capability — and what that does to delivered
  cost and resilience commitments in customer SLAs.
- **Pain today:** resilience and efficiency trade-offs are evaluated
  anecdotally per facility; there is no standard way to price flexibility
  (curtailable GPU load) into the offering.
- **Success for them:** scenario comparisons that show resilience score and
  chain efficiency against the existing baseline, plus the flexibility value
  of curtailable compute.
- **Key intake inputs they own:** existing DER assets (BESS, PV, fuel cell,
  genset), critical/flexible load split, reliability target.

### 2.3 Microgrid EPC

- **Who:** an engineering, procurement, and construction firm bidding
  microgrid projects that include compute loads (AIDC, edge AI, industrial).
- **Job to be done:** produce a credible pre-feasibility comparison across
  architecture options in the sales cycle, before committing engineering
  hours.
- **Pain today:** every bid starts from a blank study; the cost of
  pre-feasibility either eats margin or gets skipped, weakening bids.
- **Success for them:** a one-page feasibility report per bid, produced same-
  day from the intake questionnaire, that narrows the option space before
  detailed design.
- **Key intake inputs they own:** grid limit, DER asset mix, tariff
  structure, interconnection timeline.

All three personas share one need: **a defensible comparison, fast**. None of
them needs the MVP to produce a utility-submittable study — they need it to
tell them which architecture deserves the study.

---

## 3. Product flow

One project record flows through four stages; every stage reads and enriches
the same JSON project model. No re-keying between stages — that continuity is
the onboarding simplification.

```
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
│ Intake wizard │──▶│ Simulation   │──▶│ Comparison       │──▶│ Report       │
│ (~15 minutes) │   │ engine       │   │ dashboard        │   │ export       │
│ SiteProfile   │   │ 4 × simulate │   │ ranked + sliders │   │ HTML → PDF   │
└──────────────┘   └──────────────┘   └──────────────────┘   └──────────────┘
```

1. **Intake wizard (~15 minutes, apps/web).** A guided questionnaire:
   location and utility tariff, IT load and GPU rack density, critical vs.
   flexible load share, reliability target, DER assets (BESS, PV, fuel cell,
   genset), interconnection limit, desired energization date. Produces a
   versioned `SiteProfile` (shape in the design document, §3.1). Each step
   validates and blocks progression on invalid input.
2. **Simulation engine (engine/).** Deterministic models turn one
   `SiteProfile` into a comparison of the four architectures. Each run yields
   an hourly (8760-style, or representative-day accelerated) profile of power
   flow, conversion losses, BESS dispatch — including GPU load as a
   dispatchable resource — and the cost model. Full specification of each
   architecture's loss chain and dispatch rules: design document, §4–§6.
3. **Comparison dashboard (apps/web).** Side-by-side scenario comparison
   across the five evaluation axes with sensitivity sliders (electricity
   price, GPU utilization, equipment lead time) and a ranked recommendation.
4. **Report export.** A one-page feasibility report (HTML → PDF) the customer
   hands to their own stakeholders — lenders, landowners, boards. This is the
   onboarding artifact and the end of the MVP flow.

MVP boundaries: no authentication or multi-tenancy; persistence is a single
project record per browser session plus a server-side project store (SQLite).

---

## 4. Evaluation axes

The same five axes appear in the engine, the dashboard, and the report — one
vocabulary end to end. Definitions and computation: design document, §5.

| Axis | What it answers |
|---|---|
| Chain efficiency | What fraction of energy drawn from the grid reaches the GPU |
| Cost per delivered MWh | Levelized cost normalized to delivered, not purchased, energy |
| Time-to-power | Months from today to usable capacity |
| Resilience score | 0–1: islanding duration plus backup coverage |
| Carbon intensity | kg CO₂ per kWh delivered |

Modeling GPU flexible load as a dispatchable resource — not passive load — is
the differentiator across all five axes: it is what lets the comparison price
curtailment as capacity rather than treat AI load as fixed.

---

## 5. Roadmap beyond MVP

- **Phase 1 (MVP, this build):** intake → simulation → comparison → report;
  four architectures; SQLite project store; sensitivity analysis; DOE pitch
  drafts (Topic 3 lead, Topic 22 hardware — documents delivered in-repo; final
  submission is human-owned).
- **Phase 2 — credibility hardening:** calibrate model assumptions against
  real projects and published component data; add utility-tariff library
  coverage; external review of loss-chain models by a power engineer; extend
  the hourly model to full 8760 profiles with weather-driven PV.
- **Phase 3 — persistence and teams:** authentication, multi-tenancy, project
  history and versioning across a team, shared scenario libraries.
- **Phase 4 — engineering-grade integration:** import/export paths toward
  ETAP/PSCAD-class studies and utility workflows; the `Architecture` protocol
  is the extension seam for site-specific model plugins (design document, §4).
- **Phase 5 — operations carry-through:** carry the validated architecture
  dataset into design and operations — digital-twin hooks and agent-based
  optimization of compute-power dispatch, per the compute–power
  co-optimization strategy.

Sequencing rule: nothing in Phase 2+ ships ahead of pilot validation of the
load-bearing assumption. If pilot buyers insist on per-project custom studies,
the product pivots to a pre-sales report generator and Phases 3–5 are
re-scoped accordingly.

---

## 6. Success metrics

- **Onboarding time:** from first wizard step to a complete four-architecture
  comparison — target under one working session (~15 minutes intake + seconds
  of simulation, per the D2 performance criterion: a full 8760-hour run in
  <5 s per architecture).
- **Comparison defensibility:** every number in a report traceable to a
  documented model assumption (design document traceability table, §8) — no
  unsourced figures.
- **Study cost reduction:** measurable in a pilot against the customer's
  prior bespoke-study spend (confirming evidence for the load-bearing
  assumption).
- **MVP engineering quality:** all CI suites green (ruff, mypy strict,
  pytest, vitest, Playwright E2E) on every PR to `main`.
