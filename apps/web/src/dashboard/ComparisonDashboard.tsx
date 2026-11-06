// Side-by-side comparison of the simulated architectures (spec art_Xihp9Qa2,
// D3): ranked recommendation, the five-axis table, and the sensitivity
// explorer. Presentation only — data comes in as the API's ResultsPayload.

import { metricsToRow } from "./axes";
import { AxesTable } from "./AxesTable";
import { SensitivityPanel } from "./SensitivityPanel";
import type { SensitivityValues } from "./SensitivityPanel";
import type { PowerHubXClient } from "../api/client";
import type { ResultsPayload } from "../api/types";

interface ComparisonDashboardProps {
  results: ResultsPayload;
  client: PowerHubXClient;
  projectId: string;
  initialSensitivityValues: SensitivityValues;
  onRerun: () => void;
  rerunning: boolean;
}

export function ComparisonDashboard({
  results,
  client,
  projectId,
  initialSensitivityValues,
  onRerun,
  rerunning,
}: ComparisonDashboardProps) {
  if (results.ranking.length === 0) {
    return (
      <p role="status">
        No scenarios to compare yet. Run a simulation from the intake wizard to
        populate this dashboard.
      </p>
    );
  }

  const best = results.ranking[0];

  return (
    <section aria-label="Comparison dashboard">
      {results.stale && (
        <div role="alert" className="stale-banner">
          <p>
            The site profile changed after this simulation ran — these results
            are stale.
          </p>
          <button type="button" onClick={onRerun} disabled={rerunning}>
            {rerunning ? "Re-running…" : "Re-run simulation"}
          </button>
        </div>
      )}

      <section aria-label="Recommendation">
        <h2>Recommendation</h2>
        <p>
          Recommended architecture:{" "}
          <strong data-testid="recommended-architecture">
            {best.architecture}
          </strong>{" "}
          (score {best.score.toFixed(2)})
        </p>
        <ol aria-label="Ranked architectures">
          {results.ranking.map((ranked) => (
            <li key={ranked.architecture}>
              {ranked.architecture} — score {ranked.score.toFixed(2)}
            </li>
          ))}
        </ol>
      </section>

      <section aria-label="Architecture comparison">
        <h2>Comparison</h2>
        <AxesTable
          rows={results.ranking.map((ranked) => metricsToRow(ranked.metrics))}
          caption="The five evaluation axes across all simulated architectures, best-ranked first."
        />
      </section>

      <SensitivityPanel
        client={client}
        projectId={projectId}
        initialValues={initialSensitivityValues}
      />
    </section>
  );
}
