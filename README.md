# PowerHubX

Feasibility-to-onboarding software for AI data center (AIDC) and microgrid
power-architecture decisions. PowerHubX takes a customer from a guided site
intake to a defensible comparison of four architectures — grid-only,
grid+BESS, hybrid AC/DC with MV solid-state transformer, and islandable
microgrid — evaluated on chain efficiency, cost per delivered MWh,
time-to-power, resilience, and carbon intensity.

Spec of record: `art_Xihp9Qa2` (PowerHubX MVP and DOE Pitch Spec, in the
Obvious project).

## Repository layout

```
engine/          Pure Python simulation/evaluation package (numpy, pandas;
                 pytest + hypothesis). No web-framework imports.
apps/api/        FastAPI backend: project store (SQLite), simulation
                 orchestration, report export.
apps/web/        React 18 + Vite + TypeScript frontend: intake wizard,
                 comparison dashboard, report view. Vitest + Testing Library
                 for components; Playwright config ships now, E2E tests arrive
                 in a later PR.
docs/            Product plan, design document, testing plan, DOE pitches
                 (populated by later PRs).
```

## Development

Python side (ruff + mypy + pytest read their config from the root
`pyproject.toml`, which is not itself an install target):

```bash
python3 -m venv .venv && .venv/bin/pip install -e "engine[dev]" -e "apps/api[dev]"
.venv/bin/ruff check .
.venv/bin/mypy .
.venv/bin/pytest

# API dev server
.venv/bin/uvicorn api.main:app --reload --app-dir apps/api/src
```

Web side:

```bash
cd apps/web
npm install
npm run dev     # Vite dev server, proxies /api to localhost:8000
npm test        # vitest + RTL
npm run build   # tsc -b && vite build
npm run test:e2e  # Playwright (tests arrive in a later PR)
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every PR to `main`:

- **python** — ruff, mypy (strict), pytest across Python 3.11 and 3.13.
- **web** — type-check + build, then vitest.

The workflow has marked extension points for a Playwright E2E job and a DOE
pitch word-count check; both land with the PRs that introduce those tests.
