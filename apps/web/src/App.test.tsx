import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { PowerHubXClient } from "./api/client";
import { resultsPayload, sensitivityPayload } from "./test/fixtures";
import { jsonResponse, mockFetch } from "./test/http";

// Full-wizard fill mirrors the profile from IntakeWizard.test.tsx so the two
// suites exercise the same valid input.
async function fillWizard() {
  const type = (label: string, value: string) =>
    userEvent.type(screen.getByLabelText(label), value);
  const next = () => userEvent.click(screen.getByRole("button", { name: "Next" }));

  await type("Site location", "Ashburn, VA");
  await type("Utility tariff (USD/kWh)", "0.08");
  await next();

  await type("IT load (MW)", "120");
  await type("Rack density (kW per rack)", "132");
  await next();

  await type("Flexible load share (0 to 1)", "0.4");
  await next();

  await userEvent.selectOptions(
    screen.getByLabelText("Reliability target (criticality)"),
    "tier4",
  );
  await next();

  await type("BESS capacity (MWh)", "80");
  await type("Solar PV (MW)", "10");
  await type("Fuel cell (MW)", "5");
  await type("Backup generator (MW)", "20");
  await next();

  await type("Grid interconnection limit (MW)", "150");
  await type("Interconnection wait (months)", "36");
  await next();

  await type("Target energization date (YYYY-MM-DD)", "2028-06-01");
  await userEvent.click(
    screen.getByRole("button", { name: "Generate site profile" }),
  );
}

function mockApi(reportHtml: string | null = null) {
  const project = {
    id: "p1",
    name: null,
    location: null,
    site: null,
    site_version: 1,
    has_results: false,
    created_at: "2026-11-06T00:00:00",
    updated_at: "2026-11-06T00:00:00",
  };
  return mockFetch(async (input, init) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    if (url.endsWith("/api/projects") && method === "POST") {
      return jsonResponse(project, 201);
    }
    if (url.endsWith("/api/projects/p1/site") && method === "PUT") {
      return jsonResponse({ ...project, site_version: 2 });
    }
    if (url.endsWith("/api/projects/p1/simulate") && method === "POST") {
      return jsonResponse(resultsPayload());
    }
    if (url.endsWith("/api/projects/p1/sensitivity")) {
      return jsonResponse(sensitivityPayload("tariff_usd_kwh", 0.15));
    }
    if (reportHtml !== null && url.endsWith("/api/projects/p1/report")) {
      return new Response(reportHtml, {
        status: 200,
        headers: { "Content-Type": "text/html" },
      });
    }
    throw new Error(`unexpected request ${method} ${url}`);
  });
}

function renderApp(fetchMock = mockApi()) {
  render(<App client={new PowerHubXClient(fetchMock)} />);
  return fetchMock;
}

describe("App flow", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("takes the wizard's profile through simulate to the ranked dashboard", async () => {
    renderApp();

    await fillWizard();

    expect(
      await screen.findByTestId("recommended-architecture"),
    ).toHaveTextContent("islandable-microgrid");
    expect(screen.getByRole("table")).toBeInTheDocument();
  });

  it("shows a bootstrap status while create/site/simulate run", async () => {
    // The wizard completed, create and site resolve, but simulate hangs —
    // deterministically freezing the bootstrap phase.
    const project = { id: "p1" };
    const fetchMock = mockFetch(async (input, init) => {
      const url = String(input);
      const method = init?.method ?? "GET";
      if (url.endsWith("/api/projects") && method === "POST") {
        return jsonResponse(project, 201);
      }
      if (url.endsWith("/api/projects/p1/site")) {
        return jsonResponse(project);
      }
      return new Promise<Response>(() => {}); // simulate never resolves
    });
    renderApp(fetchMock);

    await fillWizard();

    expect(
      screen.getByText(/Creating the project and simulating/),
    ).toBeInTheDocument();
  });

  it("surfaces API failures with a way back to the wizard", async () => {
    const fetchMock = mockFetch(async () =>
      jsonResponse({ detail: "backend exploded" }, 500),
    );
    renderApp(fetchMock);

    await fillWizard();

    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toContain("Something went wrong: backend exploded");

    await userEvent.click(screen.getByRole("button", { name: "Start over" }));
    expect(
      screen.getByRole("heading", { name: /Step 1 of 7/ }),
    ).toBeInTheDocument();
  });

  it("toggles to the report view, which embeds the fetched report", async () => {
    renderApp(mockApi("<html><body>Chain efficiency</body></html>"));

    await fillWizard();
    await screen.findByTestId("recommended-architecture");

    await userEvent.click(screen.getByRole("button", { name: "Report" }));

    const frame = await screen.findByTitle("Feasibility report");
    expect(frame.getAttribute("srcdoc")).toContain("Chain efficiency");
  });
});
