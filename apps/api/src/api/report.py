"""One-page HTML feasibility report (design doc §8, GET /report).

Pure renderer: strings in, HTML out — the route owns persistence. The page is
print-to-PDF ready (browser print CSS targets A4 portrait, one page). Every
dynamic value passes through ``html.escape``; project names and locations are
user input. All economics are placeholder assumptions (assumptions.py) and
the report says so — it is pre-engineering feasibility, not a
utility-submittable study.
"""

from __future__ import annotations

import datetime
from html import escape

from api.ranking import AXIS_LABELS
from api.schemas import ResultsPayload, ScenarioMetrics, SiteProfileIn

_SITE_FIELD_LABELS: dict[str, str] = {
    "grid_limit_mw": "Grid interconnection limit (MW)",
    "it_load_mw": "IT load (MW)",
    "flexible_share": "Flexible GPU load share",
    "rack_density_kw": "Rack density (kW)",
    "criticality": "Criticality class",
    "bess_mwh": "BESS capacity (MWh)",
    "pv_mw": "PV capacity (MW)",
    "fuel_cell_mw": "Fuel cell capacity (MW)",
    "genset_mw": "Genset capacity (MW)",
    "tariff_usd_kwh": "Electricity tariff ($/kWh)",
    "interconnection_wait_months": "Interconnection wait (months)",
    "target_energization": "Target energization",
}

_SCOPING_NOTE = (
    "Pre-engineering feasibility based on documented placeholder assumptions "
    "(tune before customer use) — not a utility-submittable EMT/protection study."
)

_STALE_NOTE = (
    "Warning: the site profile changed after this simulation ran — "
    "re-run simulate to refresh these results."
)


def _fmt(value: float) -> str:
    return f"{value:,.2f}"


def _site_rows(site: SiteProfileIn) -> str:
    data = site.model_dump()
    rows = "\n".join(
        f"<tr><th>{escape(label)}</th><td>{escape(str(data[field]))}</td></tr>"
        for field, label in _SITE_FIELD_LABELS.items()
    )
    return f"<table>{rows}</table>"


def _axis_table(metrics: list[ScenarioMetrics]) -> str:
    header = "<tr><th>Evaluation axis</th>" + "".join(
        f"<th>{escape(m.architecture)}</th>" for m in metrics
    ) + "</tr>"
    rows = []
    for axis, label in AXIS_LABELS.items():
        cells = "".join(f"<td>{_fmt(float(getattr(m, axis)))}</td>" for m in metrics)
        rows.append(f"<tr><th>{escape(label)}</th>{cells}</tr>")
    rows.append(
        "<tr><th>Flexible GPU curtailed (MWh / hours)</th>"
        + "".join(
            f"<td>{_fmt(m.dispatch.curtailed_gpu_mwh)} / {m.dispatch.curtailed_hours}</td>"
            for m in metrics
        )
        + "</tr>"
    )
    rows.append(
        "<tr><th>Critical load shed (MWh / hours)</th>"
        + "".join(
            f"<td>{_fmt(m.dispatch.shed_mwh)} / {m.dispatch.shed_hours}</td>" for m in metrics
        )
        + "</tr>"
    )
    body = "\n".join(rows)
    return f"<table>{header}\n{body}</table>"


def render_report(
    *,
    project_id: str,
    name: str | None,
    location: str | None,
    site: SiteProfileIn,
    payload: ResultsPayload,
) -> str:
    """Render the one-page feasibility report from a stored simulate run."""
    ranking = payload.ranking
    winner = ranking[0].architecture if ranking else "n/a"
    title_bits = [bit for bit in (name, location) if bit]
    title = escape(" — ".join(title_bits)) if title_bits else escape(project_id)
    generated = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
    stale_note = (
        f'<p class="stale">{escape(_STALE_NOTE)}</p>' if payload.stale else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>PowerHubX feasibility report — {title}</title>
<style>
  body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; margin: 1.5cm; color: #111; }}
  h1 {{ font-size: 16pt; margin-bottom: 0; }}
  h2 {{ font-size: 12pt; margin-top: 1.1em; border-bottom: 1px solid #999; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #bbb; padding: 3px 6px; text-align: left; }}
  thead th, tr th:first-child {{ background: #f0f0f0; }}
  .recommendation {{ background: #eef7ee; border: 1px solid #7c7; padding: 6px 10px; }}
  .stale {{ background: #fdf3d0; border: 1px solid #c90; padding: 6px 10px; }}
  .note {{ font-size: 9pt; color: #444; }}
  @page {{ size: A4 portrait; margin: 1cm; }}
  @media print {{ .noprint {{ display: none; }} }}
</style>
</head>
<body>
<h1>PowerHubX feasibility report</h1>
<p><strong>{title}</strong> · project <code>{escape(project_id)}</code> · generated {generated}</p>
{stale_note}
<h2>Recommended architecture</h2>
<p class="recommendation"><strong>{escape(winner)}</strong>
 (score {_fmt(ranking[0].score) if ranking else "n/a"}, equal-axis placeholder weights —
 re-rank by your own priorities in the dashboard)</p>
<h2>Site profile</h2>
{_site_rows(site)}
<h2>Architecture comparison</h2>
{_axis_table([r.metrics for r in ranking])}
<h2>Assumptions &amp; scope</h2>
<p class="note">{escape(_SCOPING_NOTE)}</p>
<p class="note noprint">Print this page (Ctrl/Cmd+P) to produce the PDF deliverable.</p>
</body>
</html>
"""
