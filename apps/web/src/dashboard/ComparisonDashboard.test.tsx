import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ComparisonDashboard } from "./ComparisonDashboard";
import { PowerHubXClient } from "../api/client";
import {
  resultsPayload,
  ARCHITECTURES,
} from "../test/fixtures";
import { jsonResponse, mockFetch } from "../test/http";

const PROJECT_ID = "p1";

function renderDashboard(
  results = resultsPayload(),
  onRerun = vi.fn(),
  rerunning = false,
) {
  return render(
    <ComparisonDashboard
      results={results}
      client={new PowerHubXClient(mockFetch(async () => jsonResponse({})))}
      projectId={PROJECT_ID}
      initialSensitivityValues={{
        tariff_usd_kwh: 0.08,
        gpu_utilization: 1.0,
        equipment_lead_time_factor: 1.0,
      }}
      onRerun={onRerun}
      rerunning={rerunning}
    />,
  );
}

describe("ComparisonDashboard", () => {
  it("renders all four architectures and the ranked recommendation", () => {
    renderDashboard();

    expect(screen.getByTestId("recommended-architecture")).toHaveTextContent(
      "islandable-microgrid",
    );
    const ranked = screen.getByRole("list", { name: "Ranked architectures" });
    const items = ranked.querySelectorAll("li");
    expect(items).toHaveLength(4);
    // API order is best-first and the list must preserve it.
    expect(Array.from(items).map((li) => li.textContent)).toEqual([
      "islandable-microgrid — score 0.90",
      "mvdc-sst-hybrid — score 0.80",
      "grid+bess — score 0.70",
      "grid-only — score 0.60",
    ]);
  });

  it("renders the five evaluation axes for every architecture", () => {
    renderDashboard();

    const table = screen.getByRole("table", { name: /five evaluation axes/i });
    for (const axis of [
      "Chain efficiency",
      "Cost per delivered MWh",
      "Time to power",
      "Resilience",
      "Carbon intensity",
    ]) {
      expect(
        withinRowHeaders(table).some((header) => header === axis),
        `axis row ${axis}`,
      ).toBe(true);
    }
    // Every architecture appears as a column header.
    for (const architecture of ARCHITECTURES) {
      expect(
        withinColumnHeaders(table).some((header) => header === architecture),
        `column ${architecture}`,
      ).toBe(true);
    }
  });

  it("formats axis values in their natural units", () => {
    renderDashboard();

    // Rank 0 metrics: chain_efficiency 0.9, cost_per_mwh 60, ttp 12 months.
    const table = screen.getByRole("table", { name: /five evaluation axes/i });
    expect(table.textContent).toContain("90.0%");
    expect(table.textContent).toContain("$60/MWh");
    expect(table.textContent).toContain("12.0 months");
  });

  it("warns and offers a re-run when results are stale", async () => {
    const onRerun = vi.fn();
    renderDashboard(resultsPayload({ stale: true }), onRerun);

    expect(screen.getByRole("alert").textContent).toMatch(/results are stale/i);
    await userEvent.click(screen.getByRole("button", { name: "Re-run simulation" }));
    expect(onRerun).toHaveBeenCalledOnce();
  });

  it("shows an actionable empty state when no scenarios exist", () => {
    renderDashboard(resultsPayload({ ranking: [] }));

    expect(screen.getByRole("status").textContent).toMatch(
      /No scenarios to compare yet/i,
    );
  });
});

function withinRowHeaders(table: HTMLElement): string[] {
  return Array.from(table.querySelectorAll("tbody th")).map(
    (th) => th.textContent ?? "",
  );
}

function withinColumnHeaders(table: HTMLElement): string[] {
  return Array.from(table.querySelectorAll("thead th")).map(
    (th) => th.textContent ?? "",
  );
}
