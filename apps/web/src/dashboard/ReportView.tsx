// One-page feasibility report (spec art_Xihp9Qa2, D3 report export): GET
// /report returns print-ready HTML. The view embeds it in a srcdoc iframe so
// the report's print styles stay isolated from the app, and "Print to PDF"
// opens the report URL in a new tab where the browser's print dialog saves
// it as PDF.

import { useEffect, useState } from "react";
import type { PowerHubXClient } from "../api/client";
import { errorMessage } from "../api/client";

export function reportUrl(projectId: string): string {
  return `/api/projects/${projectId}/report`;
}

type ReportState =
  | { kind: "loading" }
  | { kind: "loaded"; html: string }
  | { kind: "error"; message: string };

interface ReportViewProps {
  client: PowerHubXClient;
  projectId: string;
}

export function ReportView({ client, projectId }: ReportViewProps) {
  const [state, setState] = useState<ReportState>({ kind: "loading" });
  // Bumped by Retry: the fetch lives in the effect, keyed on the attempt.
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setState({ kind: "loading" });
    client
      .reportHtml(projectId)
      .then((html) => {
        if (!cancelled) {
          setState({ kind: "loaded", html });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setState({ kind: "error", message: errorMessage(error) });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [client, projectId, attempt]);

  if (state.kind === "loading") {
    return (
      <p role="status" aria-busy="true">
        Loading report…
      </p>
    );
  }
  if (state.kind === "error") {
    return (
      <div role="alert">
        <p>Report failed to load: {state.message}</p>
        <button type="button" onClick={() => setAttempt((a) => a + 1)}>
          Retry
        </button>
      </div>
    );
  }
  return (
    <section aria-label="Feasibility report">
      <p className="report-actions">
        <button
          type="button"
          onClick={() => window.open(reportUrl(projectId), "_blank")}
        >
          Print to PDF
        </button>
      </p>
      <iframe
        title="Feasibility report"
        srcDoc={state.html}
        className="report-frame"
      />
    </section>
  );
}
