import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ReportView, reportUrl } from "./ReportView";
import { PowerHubXClient } from "../api/client";
import { htmlResponse, jsonResponse, mockFetch } from "../test/http";

const PROJECT_ID = "p1";

// The API renders the axes into this HTML (apps/api/src/api/report.py); the
// view must hand the same document to the iframe.
const REPORT_HTML = `
  <!doctype html><html><body>
    <h1>Feasibility report</h1>
    <table><tr><th>Chain efficiency</th><th>Cost per delivered MWh</th>
    <th>Time to power</th><th>Resilience</th><th>Carbon intensity</th></tr></table>
  </body></html>
`;

describe("ReportView", () => {
  it("shows a loading state while the report is fetched", () => {
    render(
      <ReportView
        client={new PowerHubXClient(mockFetch(() => new Promise<Response>(() => {})))}
        projectId={PROJECT_ID}
      />,
    );

    expect(screen.getByRole("status")).toHaveTextContent(/Loading report…/);
  });

  it("renders the report axes inside the embedded frame", async () => {
    render(
      <ReportView
        client={new PowerHubXClient(
          mockFetch(async () => htmlResponse(REPORT_HTML)),
        )}
        projectId={PROJECT_ID}
      />,
    );

    const frame = await screen.findByTitle("Feasibility report");
    for (const axis of [
      "Chain efficiency",
      "Cost per delivered MWh",
      "Time to power",
      "Resilience",
      "Carbon intensity",
    ]) {
      expect(frame.getAttribute("srcdoc")).toContain(axis);
    }
  });

  it("surfaces load failures with a retry that re-requests the report", async () => {
    const fetchMock = mockFetch(async () =>
      jsonResponse({ detail: "project has no results yet" }, 409),
    );
    render(
      <ReportView client={new PowerHubXClient(fetchMock)} projectId={PROJECT_ID} />,
    );

    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toContain(
      "Report failed to load: project has no results yet",
    );

    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  });

  it("opens the printable report URL for print-to-PDF", async () => {
    const open = vi.fn();
    vi.spyOn(window, "open").mockImplementation(open);
    render(
      <ReportView
        client={new PowerHubXClient(
          mockFetch(async () => htmlResponse(REPORT_HTML)),
        )}
        projectId={PROJECT_ID}
      />,
    );

    await screen.findByTitle("Feasibility report");
    await userEvent.click(screen.getByRole("button", { name: "Print to PDF" }));
    expect(open).toHaveBeenCalledTimes(1);
    expect(open).toHaveBeenCalledWith(reportUrl(PROJECT_ID), "_blank");
  });
});
