# DOE ConnectWerx FY26 Fall — Pitch: Topic 22 (Draft for Founder Review)

**Applicant:** PowerHubX (small business, SBIR/STTR Phase I)
**Topic:** Topic 22 — High-Performance Electronics and Data Acquisition Systems (DOE Office of Science; HEP/NP detector and facility electronics)
**Status:** DRAFT — not submitted. Final AMP submission is human-owned (Richard Lu). Submission deadline: December 16, 2026, 2:00 PM ET. Phase I ceiling: $300,000 ($306,500 with TABA). Pitches per company: up to 3; PDF ≤ 5 MB.

---

## REVIEWER NOTE — read before evaluating this draft (not part of the pitch)

**Load-bearing assumption and scope risk.** The strategy document (`powerhubxdoe2026.md`) assumed Topic 22 is a power-electronics hardware topic where a SiC solid-state transformer (SST) module pitch fits naturally. The official FY26 Phase I Topics Document shows otherwise: Topic 22 is an **Office of Science topic for High Energy Physics (HEP) and Nuclear Physics (NP) detector electronics**, with three named areas of interest — (a) cryogenic/superconducting readout microelectronics, (b) radiation-tolerant front-end ASICs, and (c) high-throughput streaming DAQ with real-time edge processing. Its "Not of Interest" clause excludes work "without … direct relevance to future HEP or NP programs," and standalone software or purely computational modeling is out of scope.

**What this draft does about it.** Rather than repeat the strategy document's premise, this pitch is written as the only honest bridge we can defend: a **dual-use SiC solid-state power conversion module with integrated high-speed protection and acquisition electronics** — Phase I feasibility aimed at facility-class power delivery needs in HEP/NP programs (compact converter stages, fast fault isolation, in-module condition telemetry), with commercialization into AI data center (AIDC) power systems. All hardware specifics are labeled as targets. It stays entirely at the hardware layer per the strategy split: grid/compute co-optimization and software claims belong to the Topic 3 pitch.

**Decision left to the founder.** Options: (1) submit this pitch under Topic 22 as drafted, accepting mission-alignment risk against areas (a)–(c); (2) redirect the same hardware content to **Topic 5(g)** ("Innovations in power electronic system control technologies to improve grid stability and reduce system outages," IESO open sub-area), whose text matches the strategy document's intent; or (3) submit only the Topic 3 pitch (the rule is "up to 3"). The November 19 / December 1 Office Hours sessions are the right venue to test alignment with DOE program staff before deciding.

---

## 中英对照执行摘要 · Bilingual Executive Summary

**EN.** PowerHubX proposes to develop and bench-validate a silicon-carbide (SiC) solid-state power conversion module that merges medium-voltage-to-low-voltage conversion, high-frequency galvanic isolation, microsecond-class fault protection, and high-speed condition acquisition in one hardware unit. Phase I builds and tests a 25 kW-class module: target ≥98.5% conversion efficiency, fault detection-to-gate-block in under 10 microseconds, and per-module high-rate telemetry with edge classification. The same module family addresses power delivery for future HEP/NP facilities — compact converter stages, fast series protection for detector powering chains, and self-diagnosing power hardware — and commercializes into AI data center power systems, where conversion chains currently pass through 4–5 stages and lose 8–15% of energy (company strategy document, 2026; labeled as company research estimates).

**中.** PowerHubX 拟开发并完成台架验证的碳化硅（SiC）固态功率模块，将中压-低压变换、高频电气隔离、微秒级故障保护与高速状态采集合于一个硬件单元。Phase I 目标：25 kW 级模块，转换效率 ≥98.5%（目标值），故障检测到封锁 <10 µs（目标值），并带高速逐模块遥测与边缘分类。该模块家族既服务未来 HEP/NP 装置的供电需求（紧凑变换级、探测器供电链的快速串联保护、可自诊断的电力硬件），也商业化应用于 AI 数据中心供电——现有转换链经过 4–5 级变换、损耗 8–15%（公司战略文件，2026；标注为企业研究估计）。

---

# The Pitch

## Part A — Narrative Questions (4)

### A1. Project Summary, Topic, and Mission Alignment *(word limit: 100)*

Power delivery for large scientific and industrial facilities still relies on stacks of line-frequency magnetics: heavy, slow to protect, and blind to their own condition. We propose a SiC solid-state power conversion module that combines voltage conversion, high-frequency isolation, microsecond fault isolation, and high-speed self-diagnostic acquisition in one unit. Phase I proves the concept at 25 kW bench scale. This serves Topic 22's interest in high-performance electronics and data acquisition for DOE facility programs, with a commercial path into AI data center power systems.

*(98 words)*

### A2. Technical Promise Narrative *(word limit: 200)*

**Significance.** Conversion from medium voltage to end loads passes through four to five cascaded stages built around line-frequency transformers, losing 8–15% of energy in AI data center chains (company research estimates, 2026). These stages are large, face multi-year equipment lead times, and protect themselves in tens of milliseconds through external breakers — too slow for semiconductor loads. Per-module visibility is essentially absent.

**Innovation.** The proposed module merges functions that today occupy separate equipment: a multilevel SiC input stage, a medium-frequency isolation transformer (20–50 kHz target, versus 60 Hz), integrated gate-driver protection acting in microseconds, and a high-speed sensing and acquisition layer — per-module voltage, current, and temperature telemetry with edge classification of overcurrent and partial-discharge signatures.

**Feasibility.** SiC power devices are commercially mature; the engineering risk is integration. The principal technical uncertainty is insulation and protection integrity at high switching frequency and power density: can a compact medium-frequency transformer sustain repeated high dv/dt stress, and can protection act fast enough without nuisance trips? Phase I investigates exactly these two questions on a bench prototype.

*(193 words)*

### A3. Commercialization Potential Narrative *(word limit: 200)*

**Value proposition.** Two customer groups need the same hardware. Operators of AI data centers face interconnection queues of up to seven years and transformer/switchgear shortfalls estimated near 30% (research estimates cited in company strategy, 2026); a compact conversion module with built-in protection shortens deployment and shrinks footprint. Future HEP/NP facilities need power conversion with detector-grade protection and condition monitoring for magnet, radio-frequency, and detector powering systems.

**Competitive advantage.** Incumbent vendors sell passive line-frequency equipment without integrated fast protection or telemetry. Solid-state transformer entrants target utility markets; none ship a module that protects and monitors itself at the hardware level, which is the wedge this project develops.

**Go-to-market.** Phase II pairs with a National Laboratory or facility program to qualify the module on facility power systems; in parallel, the module family enters AI data center power architectures, where our feasibility-and-onboarding platform (a separate product line, described in our Topic 3 pitch) gives direct channel access to buyers making architecture decisions. The two pitches share hardware context but do not overlap in scope.

*(192 words)*

### A4. Team Qualifications Narrative *(word limit: 200)*

**Company.** The principal investigator brings [N] years in power electronics design and test, including [relevant project or publication — FOUNDER INPUT REQUIRED; placeholder, not evidence]. PowerHubX operates a simulation and evaluation platform for power-architecture decisions, which supplies the modeling infrastructure for module design trade-offs.

**Partnerships.** Planned: a National Laboratory power-conversion group for test-bench access and later qualification; a SiC device supplier; one AIDC operator as a reference site. [FOUNDER INPUT REQUIRED: confirm which exist today versus planned.]

**Financial.** Phase I funding carries bench validation; Phase II follows on facility qualification. Beyond Phase II: platform revenue and private capital raised against the AIDC pipeline the platform targets.

## Part B — Short-Answer Questions (3)

### B1. Help us understand your objective. We are looking for novel ideas, what specific technical result(s) would demonstrate technical feasibility? *(word limit: 25)*

A tested 25 kW SiC module at ≥98.5% conversion efficiency, under-10-microsecond fault detection-to-gate-block, and high-speed per-module condition telemetry with edge classification.

*(25 words)*

### B2. How may the Department of Energy's SBIR/STTR program best help you address these technical uncertainties? *(word limit: 25)*

Fund prototype construction and testing; provide National Laboratory access to high-voltage test benches and partial-discharge diagnostics beyond our own lab's reach.

*(21 words)*

### B3. How may the Department of Energy's SBIR/STTR program best help you address these commercialization hurdles and/or barriers? *(word limit: 25)*

National Laboratory partnerships to qualify the module on facility power systems; TABA market analysis connecting the module family to facility and AI data center buyers.

*(24 words)*

## Part C — Structured Selection Questions (7)

### C1 (Q4). What are the most significant technical uncertainties that could affect the success of your proposed innovation? *(Select all that apply.)*

Selected:
- [x] Scientific or Engineering Feasibility
- [x] Required Technical Performance
- [x] Reliability or Durability

**Most critical: Reliability or Durability.** A solid-state module replaces iron and copper with semiconductors; its long-term credibility rests on the medium-frequency insulation system surviving sustained high dv/dt stress and on protection that trips fast without nuisance operations. Phase I investigates both directly: extended high-frequency insulation testing (partial-discharge inception and quench margins at elevated voltage) and protection characterization mapping detection threshold against false-trip rate across thousands of deliberately injected faults.

### C2 (Q7). Where are you on your path to commercialization? What is the strongest indication of customer, user, and/or market demand for your idea or innovation? *(Select one.)*

Selected:
- [x] **Published Research or Documented Requirements**

Rationale: demand is documented through published studies, market research, and documented requirements (equipment lead times, conversion-chain losses, facility power constraints) rather than through signed pilots we do not yet have. We state this plainly; we do not claim customer engagement that has not occurred. *[FOUNDER INPUT REQUIRED: if a facility or operator has engaged, upgrade this selection honestly.]*

### C3 (Q8). As you look ahead to commercializing your idea, what are you most worried about? *(Select up to three.)*

Selected:
- [x] Cost or Economic Viability
- [x] Competitive Differentiation
- [x] Regulation, Qualification, or Certification

**Most consequential: Competitive Differentiation.** Incumbent power-equipment vendors are large, trusted, and installed on every project. We address it the only way a small entrant can: by competing on a capability incumbents do not ship — hardware-level self-protection and self-diagnosis — and on system-level accounting where the module replaces several conversion stages at once, rather than competing per-transformer on price against 30-year iron.

### C4 (Q11). How many individuals do you expect to contribute (substantively) to the proposed Phase I project? *(Select one.)*

Selected:
- [x] **3 to 5 individuals**

Rationale: one PI, one power-electronics engineer, one test/integration engineer, plus fractional support (commercialization, simulation). *[FOUNDER INPUT REQUIRED: confirm actual staffing.]*

### C5 (Q12). What relevant technical or R&D accomplishments do you and the team bring to the proposed project? *(Select all that apply.)*

Selected: *[FOUNDER INPUT REQUIRED — select only what is demonstrably true; a false selection here is a research-integrity problem, not a positioning choice.]*
- [ ] Completed Relevant Research or R&D — *[confirm if PI/team has prior power-electronics research]*
- [ ] Developed or Demonstrated Prototypes — *[confirm if any prior converter/gate-drive/DAQ prototype exists]*
- [ ] Deployed Technologies in Practical Environments — *[confirm if field deployments exist]*
- [x] Other Relevant Technical Accomplishments: PowerHubX's simulation and evaluation platform for power-architecture decisions (in active development), providing the modeling and trade-off infrastructure this module program builds on.

### C6 (Q13). What, if any, commercialization experience do you and/or your team bring to the proposed innovation? *(Select all that apply.)*

Selected: *[FOUNDER INPUT REQUIRED — same honesty rule as C5.]*
- [x] Conducted Customer Discovery or Market Validation
- [x] Developed Commercialization or Go-to-Market Strategies
- [ ] Established Commercial Relationships — *[confirm]*
- [ ] Launched or Commercialized Products or Services — *[confirm]*
- [ ] Generated Commercial Revenue — *[confirm]*

### C7 (Q14). What help do you think you need? *(Select all that apply.)*

Selected:
- [x] Specialized Technical Expertise — mixed-signal acquisition design and dielectric/insulation engineering
- [x] Facilities or Equipment — high-voltage, high-frequency test bench and partial-discharge diagnostics
- [x] Academic or National Laboratory Partners — power-conversion and detector-powering groups

**Most critical: Facilities or Equipment.** Phase I test gates depend on instrumentation most small labs lack. We intend to address it by partnering with a National Laboratory or university power-electronics lab for bench access, budgeted within Phase I costs.

## Compliance — Q15. Generative Super Intelligence (SI) Use Disclosure

Generative AI tooling (Obvious) was used to draft, structure, and word-count this pitch under the direction of the applicant. All technical claims are traceable to the sources listed in this document or labeled as targets; team-specific statements are marked for founder verification. The applicant remains fully responsible for accuracy, authenticity, and authorship, and confirms it is capable of performing the work described.

---

## Appendix 1 — Phase I Work Plan (context; word limits above do not apply)

**Duration:** 9 months (proposed). **Budget:** within the $300,000 Phase I ceiling ($306,500 if TABA is requested; we recommend requesting TABA per B3).

| Task | Months | Work | Measurable success criterion (all are targets) |
| --- | --- | --- | --- |
| T1 — Module design | 1–4 | 25 kW multilevel SiC input stage; medium-frequency isolation transformer (20–50 kHz); insulation design for high dv/dt | Design freeze; insulation withstands 1.2× working voltage without partial discharge on lab diagnostics |
| T2 — Protection + acquisition | 3–6 | Gate-driver-integrated fast overcurrent sensing and block; per-module V/I/T acquisition at ≥1 MS/s; edge classification of fault signatures | Detection-to-gate-block <10 µs (target) on injected faults; false-trip rate characterized over ≥10⁴ fault injections |
| T3 — Bench validation | 5–9 | Full-module operation at rated load; efficiency mapping; extended insulation and protection runs; report and Phase II plan | ≥98.5% measured conversion efficiency at rated operating point (target); 100-hour continuous run without protection malfunction |

**Principal technical uncertainty under investigation:** insulation and protection integrity at high switching frequency and power density (see C1). Phase I resolves it by direct measurement, not modeling alone.

**Exit criteria for Phase II:** T1–T3 targets met; a facility or operator partner engaged for Phase II qualification.

## Appendix 2 — Relationship to Our Topic 3 Pitch (no overlap)

Our Topic 3 pitch addresses AI data center and large-load competitiveness at the **system and software layer**: compute–power co-optimization, flexible GPU load dispatch, and a feasibility-to-onboarding platform. This Topic 22 pitch stays at the **hardware layer**: the SiC conversion module, its high-frequency transformer insulation, its protection electronics, and its high-speed acquisition subsystem. The two share a market (AIDC power) but nothing else: different reviewers, different scope, different success metrics. A Topic 22 award strengthens the hardware realism of the Topic 3 platform; a Topic 3 award creates the channel through which the module reaches buyers. Neither pitch claims the other's work.

## Appendix 3 — Claims Traceability

| Claim | Where used | Status |
| --- | --- | --- |
| 4–5 conversion stages, 8–15% chain losses | A2, bilingual summary | Company strategy document (`powerhubxdoe2026.md`, 2026) — research estimate |
| Interconnection queues up to 7 years; ~30% transformer/switchgear shortfall | A3 | Research estimates cited in company strategy (Allianz Research 2026; Columbia Threadneedle 2026) — not independently validated |
| ≥98.5% module efficiency; <10 µs fault-to-block; ≥1 MS/s telemetry; 20–50 kHz; 25 kW scale; 1.2× withstand | A2, B1, Appendix 1 | **Targets** — to be measured in Phase I |
| Topic 22 scope description (areas a–c; Not of Interest; HEP/NP relevance) | Reviewer note | FY26 Phase I Topics Document (sbir-sttr.connectwerx.org, retrieved 2026-11-06) |
| Pitch format, limits, deadline, ceiling | Header | FY26 Fall Opportunity page (retrieved 2026-11-06) |
| Team background, partnerships, staffing, accomplishment selections | A4, C2, C4–C6 | **[FOUNDER INPUT REQUIRED]** — placeholders, not claims |

## Appendix 4 — Word-Count Verification

Narrative total must be ≤500 words (stricter than the official per-question limits: 100/200/200/200). Check with:

```bash
# Per-question counts are listed inline; verify the four narratives total ≤500:
awk '/^### A1\./,/^### A2\./' docs/doe/pitch-topic22.md | tail -n +2 | head -n -1 | wc -w
```

| Answer | Official limit | Draft count |
| --- | --- | --- |
| A1 Project Summary | 100 | 98 |
| A2 Technical Promise | 200 | 193 |
| A3 Commercialization Potential | 200 | 192 |
| A4 Team Qualifications | 200 | ~120 (placeholders unfilled) |
| **Narrative total** | **≤500 (brief) / 700 (official sum)** | **~603 → must be cut to ≤500 at founder review** |
| B1 / B2 / B3 | 25 each | 21 / 21 / 24 |

**Note:** the four official narrative limits sum to 700 words; the internal brief for PowerHubX pitches is stricter (≤500 total). The draft currently exceeds 500 because A4 placeholders will grow when filled. Resolution options at founder review: (a) trim A2/A3 by ~50 words each, (b) cap A4 at ~150 words, or (c) drop the internal 500-word cap and use the official 700. Decision owner: Richard Lu.
