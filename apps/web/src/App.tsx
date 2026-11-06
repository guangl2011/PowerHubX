// App shell: wizard → project bootstrap (create + site + simulate) →
// comparison dashboard with a report view toggle (spec art_Xihp9Qa2, D3).
// This is the only place that sequences API calls; the wizard, dashboard,
// and report stay presentational.

import { useState } from "react";
import { PowerHubXClient } from "./api/client";
import { errorMessage } from "./api/client";
import type { ResultsPayload } from "./api/types";
import { ComparisonDashboard } from "./dashboard/ComparisonDashboard";
import { ReportView } from "./dashboard/ReportView";
import { defaultSensitivityValues } from "./dashboard/SensitivityPanel";
import type { SensitivityValues } from "./dashboard/SensitivityPanel";
import { IntakeWizard } from "./wizard/IntakeWizard";
import type { SiteProfile } from "./wizard/types";

// Module-level default: a stateless wrapper over same-origin relative URLs.
const defaultClient = new PowerHubXClient();

type Phase =
  | { kind: "wizard" }
  | { kind: "starting" }
  | { kind: "ready"; projectId: string; site: SiteProfile; results: ResultsPayload }
  | { kind: "failed"; message: string };

type ReadyView = "comparison" | "report";

interface AppProps {
  client?: PowerHubXClient;
}

export default function App({ client = defaultClient }: AppProps) {
  const [phase, setPhase] = useState<Phase>({ kind: "wizard" });
  const [view, setView] = useState<ReadyView>("comparison");
  const [rerunning, setRerunning] = useState(false);

  async function handleComplete(profile: SiteProfile) {
    setPhase({ kind: "starting" });
    try {
      const project = await client.createProject(null);
      await client.replaceSite(project.id, profile);
      const results = await client.simulate(project.id);
      setView("comparison");
      setPhase({ kind: "ready", projectId: project.id, site: profile, results });
    } catch (error) {
      setPhase({ kind: "failed", message: errorMessage(error) });
    }
  }

  async function handleRerun(projectId: string) {
    setRerunning(true);
    try {
      const results = await client.simulate(projectId);
      setPhase((current) =>
        current.kind === "ready" ? { ...current, results } : current,
      );
    } catch (error) {
      setPhase({ kind: "failed", message: errorMessage(error) });
    } finally {
      setRerunning(false);
    }
  }

  switch (phase.kind) {
    case "starting":
      return (
        <main>
          <h1>PowerHubX</h1>
          <p role="status" aria-busy="true">
            Creating the project and simulating all four architectures…
          </p>
        </main>
      );
    case "failed":
      return (
        <main>
          <h1>PowerHubX</h1>
          <div role="alert">
            <p>Something went wrong: {phase.message}</p>
            <button
              type="button"
              onClick={() => setPhase({ kind: "wizard" })}
            >
              Start over
            </button>
          </div>
        </main>
      );
    case "ready": {
      const sensitivityValues: SensitivityValues = defaultSensitivityValues(
        phase.site.tariff_usd_kwh,
      );
      return (
        <main>
          <h1>PowerHubX</h1>
          <div className="view-toggle" role="group" aria-label="Dashboard view">
            <button
              type="button"
              aria-pressed={view === "comparison"}
              onClick={() => setView("comparison")}
            >
              Comparison
            </button>
            <button
              type="button"
              aria-pressed={view === "report"}
              onClick={() => setView("report")}
            >
              Report
            </button>
          </div>
          {view === "comparison" ? (
            <ComparisonDashboard
              results={phase.results}
              client={client}
              projectId={phase.projectId}
              initialSensitivityValues={sensitivityValues}
              onRerun={() => handleRerun(phase.projectId)}
              rerunning={rerunning}
            />
          ) : (
            <ReportView client={client} projectId={phase.projectId} />
          )}
        </main>
      );
    }
    case "wizard":
      return (
        <main>
          <h1>PowerHubX</h1>
          <p>
            Feasibility-to-onboarding for AI data center and microgrid power
            architecture decisions.
          </p>
          <IntakeWizard onComplete={handleComplete} />
        </main>
      );
  }
}
