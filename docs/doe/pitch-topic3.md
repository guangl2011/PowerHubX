# DOE ConnectWerx FY26 Fall Phase I Pitch — Topic 3 (Lead Pitch)

**Project title (working):** Compute–Power Co-Optimization for AI Data Centers: Medium-Voltage SST DC Architecture with SLA-Bounded Compute Flexibility

| Field | Value |
| --- | --- |
| Opportunity | DOE SBIR/STTR FY26 Fall Phase I (ConnectWerx / OTC), pitch-first process |
| Topic | Topic 3 — State-of-the-Art Technologies for Industrial Competitiveness (ITO Open Topic); area of interest (c): integration of data centers and other large loads — power systems, demand-side load flexibility |
| Estimated awards in topic | 3 (per FY26 opportunity topic table) |
| Phase I request | up to $300,000; $306,500 if TABA requested (TABA decision: open item for founder) |
| Deadline | December 16, 2026, 2:00 PM ET via AMP — **not submitted; final submission is human-owned (Richard Lu)** |
| Status | DRAFT v1 for founder review, prepared 2026-11-06 |

**Word-count verification (run at draft time with `python3 docs/doe/check_pitch_words.py`):** the four narrative answers total ≤500 words (self-imposed budget, tighter than the per-question caps below) and each answer is within its published cap — Summary ≤100, Technical Promise ≤200, Commercialization Potential ≤200, Team Qualifications ≤200 (caps per MNSBIR's 2026-11-05 summary of the Pitch Development Guide; verify per-question prompts inside AMP before entry). Re-run the checker after any edit.

---

## 中英对照摘要 / Bilingual executive summary (internal — not part of the AMP entry)

**中文：** 本申报以"算电协同"为主线：用中高压固态变压器（SST）构建的中压直流（MVDC）配电架构，把 AI 数据中心从"4–5 级串联变换、损耗 8–15%（内部策略文档数据）"的传统供电链，压缩为更少变换环节的一体化直流架构；同时把可灵活调度的 GPU 算力负荷当作一种"可调度的电力资源"，在保证服务水平协议（SLA）的前提下参与毫秒级功率调节。Phase I 以数字孪生与硬件在环（HIL）验证两项核心指标：系统级损耗降低 ≥30%（目标值）与 SLA 约束下的算力灵活性包络。差异化：SST 厂商只卖变流器，电网软件商把算力当固定负荷——无人把两者耦合协同优化，也无人把可行性评估标准化为软件产品。

**English:** Compute–power co-optimization: an MV solid-state-transformer (SST) DC architecture that replaces the traditional 4–5-stage, 8–15%-loss power chain (internal strategy analysis), plus a controller that treats SLA-bounded flexible GPU load as a dispatchable power resource. Phase I proves both in a digital twin with hardware-in-the-loop: ≥30% grid-to-GPU conversion-loss reduction (target) and a quantified compute-flexibility envelope. Differentiation: SST vendors sell converters, grid software treats compute as fixed load — no applicant couples them, and no standard feasibility-to-onboarding software exists for this decision (market research, spec art_Xihp9Qa2).

---

## Part 1 — Narrative answers (exactly 4, per the FY26 Fall pitch structure)

### Narrative 1 — Project summary, topic, and mission alignment (cap 100 words)

PowerHubX couples AI data centers to the grid through a medium-voltage solid-state-transformer (SST) DC architecture whose software treats flexible GPU compute as a dispatchable, SLA-bounded power resource — cutting grid-to-GPU energy losses and time-to-power while stabilizing the load the grid sees. It strengthens U.S. industrial competitiveness where it is bottlenecked: energy productivity of the fastest-growing industrial load class. Phase I delivers a validated digital twin and hardware-in-the-loop demonstration of the efficiency and flexibility claims, answering ITO's interest in data center power systems and demand-side load flexibility (Topic 3, area c).

### Narrative 2 — Technical promise (cap 200 words)

AI data centers draw power through four to five serial conversion stages — service transformer, UPS rectification, 48/12 V DC distribution, GPU voltage regulators — losing 8–15% of energy between grid and chip (internal strategy analysis). A single 60 Hz transformer is not the problem (98.5%+ efficiency); the serial chain is. Solid-state transformers merge step-down, rectification, power-factor correction, and battery integration into one medium-voltage DC architecture, cutting stages and footprint. Published SST work evaluates converters in isolation; none controls the coupled system where the GPU fleet itself is a dispatchable resource that absorbs or sheds megawatts in milliseconds under service-level constraints.

The proposed innovation is that co-design: an MVDC SST architecture plus a compute-flexibility controller coordinating GPU load modulation, battery discharge, and SST power flow. The principal technical uncertainty: whether merged-stage conversion and load flexibility together cut grid-to-GPU losses by 30–50% (internal analysis; Phase I target ≥30%) and damp load transients without breaching power-quality limits or compute SLAs. Phase I resolves this with a component-validated full-chain digital twin and hardware-in-the-loop controller tests against recorded AI training-load traces — measured evidence, not simulation alone.

### Narrative 3 — Commercialization potential (cap 200 words)

U.S. data center capacity is projected to grow from 62 GW (2026) to 152 GW (2030) (S&P Global Market Intelligence, 2026-06), while interconnection queues run up to seven years (Allianz Research, 2026-05) and transformer/switchgear supply is ~30% short of demand (Allianz Research, 2026; Columbia Threadneedle, 2026-10-20). Every operator must extract more compute per grid megawatt, sooner.

Customers: hyperscale and colocation AI data center developers and the EPCs serving them. Offering: the PowerHubX feasibility-to-onboarding platform (per-site architecture selection and sizing, sold as software subscriptions during Phase I), leading to the co-optimization controller and validated reference designs at Phase II. Demand evidence: [ADD pilot status — founder to insert; the Phase I commercialization milestone is ≥2 pilot commitments or LOIs by Month 12]. Financing beyond SBIR: Fast-Track Phase II, then equipment-partner co-development and strategic capital; sources, stages, timing, and amounts go in the full application, per Topic 3's requirements.

### Narrative 4 — Team qualifications (cap 200 words)

Richard Lu, founder — [ADD: bio; power-electronics and data-center-infrastructure background, prior roles, degrees]. [ADD: named engineering hires or advisors — SST power electronics, grid software]. Company: PowerHubX, [ADD: state and year founded]. Facilities/partners: [ADD: lab or university partner]; SBIR permits subcontracting up to 33% of Phase I research (ConnectWerx eligibility, 2026); [ADD: partner LOIs if any]. The founder owns the commercialization milestone (two pilot commitments) and [ADD: prior commercial track record].

---

## Part 2 — Short answers (exactly 3, per the FY26 Fall pitch structure)

Sourcing note for the section: one short answer is confirmed by Grant Engine's 2026-11-05 review of the FY26 Fall pitch — "the specific result that would demonstrate feasibility in 25 words or less." Caps for the other two are not public; verify in AMP.

### Short answer 1 — The specific result that would demonstrate feasibility (cap 25 words)

A hardware-in-the-loop-validated digital twin showing ≥30% grid-to-GPU loss reduction and ≥15% SLA-safe GPU load flexibility under recorded AI transients.

### Short answer 2 — Cost and thermal response (cap not public — verify in AMP; keep short)

Cost and thermal: SiC devices switch at kHz-to-tens-of-kHz frequencies, shrinking the magnetics and capacitors that dominate SST size and cost; direct-to-chip liquid cooling already planned for AI racks provides cold-plate infrastructure SST power modules can share, avoiding dedicated thermal capex (internal analysis). Phase I delivers a quantified $/kW system comparison against the traditional chain (target).

### Short answer 3 — Evidence of demand and the key commercialization barrier (cap not public — verify in AMP)

Demand: capacity growth 62 GW → 152 GW by 2030 (S&P Global Market Intelligence, 2026-06) against seven-year interconnection queues (Allianz Research, 2026-05). [ADD: founder-inserted pilot status]. Key barrier: operator confidence in SST reliability; mitigated by third-party-reviewable digital-twin evidence, phased pilots, and a hybrid fallback that retains the conventional transformer where SST value is unproven.

---

## Part 3 — Structured selection answers (exactly 7, per the FY26 Fall pitch structure)

The seven structured-selection questions are form selections inside AMP; their exact wording is not published outside the Pitch Development Guide. The table below is the recommended answer sheet — each row must be verified against the live AMP form before entry.

| # | Question slot (paraphrased) | Recommended answer | Verify in AMP |
| --- | --- | --- | --- |
| 1 | Topic selection | Topic 3 — State-of-the-Art Technologies for Industrial Competitiveness (ITO Open Topic) | [VERIFY] |
| 2 | Focus area within topic | Area (c): integration of data centers and other large loads — power systems and demand-side load flexibility | [VERIFY] |
| 3 | Program | SBIR (STTR election is made at the full-application stage, per Grant Engine 2026-11-05) | [VERIFY] |
| 4 | Phase I funding requested | $300,000 base; $306,500 with TABA — recommend requesting TABA (adds market-research assistance); founder decision | [VERIFY] |
| 5 | Period of performance | 12 months (within DOE's 6–12-month Phase I guidance; confirm schedule in full-application instructions — MNSBIR 2026-11-05) | [VERIFY] |
| 6 | Company and registrations | PowerHubX — requires active SAM.gov registration (UEI) and SBA Company Registry before award; SAM can take up to 8 weeks (MNSBIR, 2026-11-05) — start registration immediately | [VERIFY] |
| 7 | Generative AI / SI use disclosure | Disclose that AI drafting tools assisted preparation of responses; the company reviewed, edited, and takes full responsibility for accuracy and authorship (the guide requires this disclosure — MNSBIR, 2026-11-05) | [VERIFY] |

---

## Part 4 — Phase I work plan and budget (supporting detail — referenced by the narrative; expands into the full application's Work Plan)

**Research question.** Does coupling an MVDC SST distribution architecture with SLA-bounded compute-flexibility control deliver measured system-level efficiency and transient-stability gains that neither achieves alone, under realistic AI workloads?

**Tasks and measurable success criteria (all numeric targets are Phase I targets, not claims):**

| Task | Months | Deliverable | Success criterion |
| --- | --- | --- | --- |
| T1 — Baseline and reference models | 1–3 | Analytical grid-to-GPU loss-chain model for the traditional chain and the MVDC SST chain, per representative AIDC site profiles | Model reproduces the 8–15% traditional-chain loss envelope (internal analysis) within ±2 percentage points against datasheet-derived component efficiencies |
| T2 — Co-optimization controller v1 | 3–6 | Dispatch algorithm treating flexible GPU load as a dispatchable resource, with BESS and SST power-flow coordination; SLA constraint set (critical share never curtailed; bounded latency impact) | Flexibility envelope quantified in simulation: ≥15% of IT load dispatchable for ≥30 min without SLA breach under recorded AI load traces (target) |
| T3 — Digital twin + hardware-in-the-loop | 6–10 | Component-validated digital twin of both chains; HIL test of the controller against the simulated SST plant and GPU-cluster load models | HIL demonstration: ≥30% grid-to-GPU conversion-loss reduction vs. baseline chain (target); transient response ≤10 ms (target); zero critical-load curtailment events (hard constraint) |
| T4 — Techno-economics and market pull | 8–12 | Cost-per-delivered-MWh and time-to-power comparison across grid-only, grid+BESS, MVDC SST hybrid, islandable microgrid; commercialization plan | ≥2 pilot commitments or LOIs from AIDC operators/EPCs (target); full-application draft complete |

**Reliability work within T1–T3 (answers the "SST reliability" objection directly):** SiC module thermal-cycling stress analysis and redundancy architecture study in the digital twin; explicit comparison of expected service intervals vs. conventional transformer assets; documented hybrid-fallback design where the conventional transformer remains in circuit.

**Draft budget allocation (targets; final numbers set by founder):** personnel (PI + 2 technical) $180,000; HIL testbed and equipment $45,000; digital-twin compute/cloud $15,000; partner subcontracts $30,000; travel and materials $30,000 — base $300,000; plus TABA $6,500 → $306,500 if TABA is requested. Fixed-price, milestone-based Fast-Track award; Phase II funding subject to go/no-go (ConnectWerx FY26 Fall page, retrieved 2026-11-06).

---

## Part 5 — Reviewer checklist (internal QA — how this draft answers the predictable objections)

**Kill question 1 — "SST efficiency and reliability lose to a traditional transformer."**
Answered head-on in Narrative 2 and Short answer 2: the comparison is system-level, not device-level. A single 60 Hz transformer is 98.5%+ efficient, but the traditional chain passes through 4–5 conversion stages and loses 8–15% grid-to-GPU (internal strategy analysis). The SST architecture merges step-down, rectification, PFC, and battery DC-DC into fewer stages; internal analysis projects 30–50% system-level loss reduction, which Phase I validates to a ≥30% target with HIL evidence. Reliability is treated as the real risk it is: T1–T3 include cycling-stress analysis, redundancy design, and a hybrid fallback. Phase I claims are framed as targets the measurement program must hit.

**Kill question 2 — "SiC cost and thermal burden."**
Answered head-on in Short answer 2: SiC's high-frequency operation shrinks the magnetics and capacitors that dominate SST volume and cost (internal analysis: footprint reduction >50% vs. the traditional chain's transformer plant — target, to be quantified in T4); direct-to-chip liquid cooling already planned for AI racks is shared infrastructure the SST power modules attach to, avoiding a dedicated cooling system; and fewer conversion stages remove component count. T4 prices the whole system in $/kW against the traditional chain.

**Topic 3 "Not of Interest" compliance:**
- "Primarily relevant for non-industrial sector applications (e.g., power sector)": the pitch is framed from the data center as an industrial facility — energy productivity, cost per delivered MWh, time-to-power — with grid benefits secondary. Topic 3 area (c) names data center power systems and demand-side load flexibility explicitly.
- "Further development of technologies that are mature or commercially available" / "new system designs... that primarily incorporate commercially available or mature technologies": Phase I does not propose assembling commercially available parts into a system. The R&D is the co-optimization controller (compute-as-flexible-resource under SLA constraints), the component-validated full-chain digital twin, and the measured system-level efficiency and stability evidence — none of which exists in published SST work. The SST device itself is treated as a procurement article, not the invention.
- Carbon capture / hydrogen: not touched.

**Explicit differentiation (what no other applicant offers):**
1. **Compute as a dispatchable power resource.** SST/power-electronics vendors (e.g., the large electrical-equipment incumbents) sell converters with fixed control envelopes; grid-software vendors treat data center load as a fixed curve. No applicant couples SLA-bounded GPU load modulation with MVDC SST power-flow control as one system — this is the compute–power co-optimization thesis of the PowerHubX strategy document.
2. **System-level co-optimization with digital-twin and agent-based self-learning.** The same validated model that Phase I uses for evidence becomes the operational optimization layer (digital twin + equipment-agent self-learning, per the strategy document), carried forward by the PowerHubX platform from feasibility through operations.
3. **Standardized feasibility-to-onboarding software.** Market research in the approved spec (art_Xihp9Qa2, R1) found no standard software product for this architecture decision — every project today starts from a bespoke engineering study. The software is the commercialization wedge and the reason pilot customers stay.

**Screening criteria coverage (per the FY26 Fall evaluation order):** topic/mission alignment (N1), technical promise (N2 + SA1 + SA2), commercialization potential (N3 + SA3), team qualifications (N4) — all four dimensions have a dedicated answer, and the 7 structured rows are consistent with them.

---

## Part 6 — Bibliography & references cited (draft for the optional ≤5 MB PDF; every pitch claim maps here)

| Ref | Claim(s) used in the pitch | Source |
| --- | --- | --- |
| [1] | Traditional chain: 4–5 conversions, 8–15% losses; single 60 Hz transformer ≥98.5% efficient; system loss reduction 30–50%; SiC high-frequency benefits (footprint reduction >50% target); millisecond dynamic response; compute-as-flexible-resource strategy | Internal strategy document `powerhubxdoe2026.md` (Richard Lu, 2026) — internal engineering analysis, flagged for external validation in Phase I |
| [2] | U.S. data center capacity 62 GW (2026) → 152 GW (2030); AI racks up to ~40x conventional rack power density | S&P Global Market Intelligence, 2026-06 — as compiled in approved spec research findings (art_Xihp9Qa2, R1); research estimates, not independently validated |
| [3] | Interconnection queues up to 7 years; ~30% transformer/switchgear supply shortfall | Allianz Research, 2026-05 — via art_Xihp9Qa2 (R1); research estimate |
| [4] | Transformer/switchgear lead times of years; ~30% shortfall | Columbia Threadneedle, 2026-10-20 — via art_Xihp9Qa2 (R1); research estimate |
| [5] | ~70 GW pending connection requests (Dominion, "data center alley") | S&P Global, 2026-04-30 — via art_Xihp9Qa2 (R1) |
| [6] | Pitch structure (4 narrative / 3 short / 7 structured), deadline 2026-12-16 2:00 PM ET, Phase I cap $300,000 / $306,500 with TABA, ≤3 pitches per company, PDF ≤5 MB, evaluation criteria, eligibility (33% Phase I subcontract limit) | ConnectWerx FY26 Fall Opportunity page, retrieved 2026-11-06 |
| [7] | Topic 3 full language: ITO Open Topic; area (c) data centers and large loads — power systems, demand-side load flexibility; Not-of-Interest list; commercial-potential requirement (lab proof of concept + market pull; financing path) | DOE FY26 Phase I Topics Document (Oct 2026), Topic 3, pp. 8-9 |
| [8] | Narrative word caps (100/200/200/200); short-answer and structured composition; AI/SI-use disclosure requirement; SAM registration lead time up to 8 weeks | MNSBIR FY2026 Phase I summary, 2026-11-05 |
| [9] | Feasibility-result short answer ≤25 words; topic locked at pitch; STTR/SBIR election deferred to full application | Grant Engine, "DOE SBIR Fall 2026," 2026-11-05 |

Note for reviewers: market figures [2]–[5] are cited research estimates that set context; no Phase I acceptance criterion depends on their exact values. Internal-analysis figures [1] carry the "target" label wherever they appear in pitch answers.

---

## Part 7 — Open items for Richard (blocking submission; nothing here blocks the draft)

1. **Registrations first (deadline-critical):** SAM.gov (up to 8 weeks per MNSBIR), SBA Company Registry, AMP account request. The December 16 deadline is unforgiving.
2. **Fill the team placeholders** in Narrative 4: founder bio, hires/advisors, facilities, partner status, commercial track record. The drafting agent cannot invent these.
3. **Pilot/LOI status:** insert actual pilot-conversation status in Narrative 3 and Short answer 3; the ≥2-commitment milestone only works if outreach starts now.
4. **TABA decision:** $300,000 flat vs. $306,500 with TABA (recommend TABA).
5. **National-lab partnership (optional, strengthens Team score):** search Lab Partnering Service for relevant LIOs; FFRDC participation needs DOE Agreements Officer authorization — start early if pursued.
6. **Attend Office Hours:** November 19 and December 1, 2026 (3 PM ET) — use them to confirm the 3 short-answer prompts and 7 structured fields against this draft.
7. **Verify every [VERIFY] row** in Part 3 against the live AMP form and the Pitch Development Guide template before pasting anything.
8. **Language:** per the approved spec's default, the AMP submission is English-only; the bilingual executive summary above is internal.
9. **Companion pitch:** Topic 22 (hardware-layer SiC SST module pitch) is drafted separately and must stay non-overlapping: this pitch owns the system co-optimization claim; Topic 22 owns the hardware module claim.
