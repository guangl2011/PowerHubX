import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SensitivityPanel } from "./SensitivityPanel";
import { PowerHubXClient } from "../api/client";
import { sensitivityPayload } from "../test/fixtures";
import { jsonResponse, mockFetch } from "../test/http";

const PROJECT_ID = "p1";

const INITIAL_VALUES = {
  tariff_usd_kwh: 0.08,
  gpu_utilization: 1.0,
  equipment_lead_time_factor: 1.0,
};

function renderPanel(
  fetchMock = mockFetch(async () =>
    jsonResponse(sensitivityPayload("tariff_usd_kwh", 0.15)),
  ),
) {
  render(
    <SensitivityPanel
      client={new PowerHubXClient(fetchMock)}
      projectId={PROJECT_ID}
      initialValues={INITIAL_VALUES}
    />,
  );
  return fetchMock;
}

async function moveSlider(label: string, value: number) {
  await fireEvent.change(screen.getByRole("slider", { name: label }), {
    target: { value: String(value) },
  });
}

describe("SensitivityPanel", () => {
  it("starts idle with a hint instead of firing a request on mount", () => {
    const fetchMock = renderPanel();

    expect(
      screen.getByText(/Adjust a lever above/i),
    ).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("re-queries /sensitivity when a slider moves and updates the values", async () => {
    const fetchMock = renderPanel();

    await moveSlider("Electricity price ($/kWh)", 0.15);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe(`/api/projects/${PROJECT_ID}/sensitivity`);
    expect(JSON.parse(String(init?.body))).toEqual({
      param: "tariff_usd_kwh",
      range: [0.15],
    });

    // The swept table replaces the hint and names the swept value.
    const table = await screen.findByRole("table");
    const caption = table.querySelector("caption");
    expect(caption?.textContent ?? "").toMatch(/Swept tariff_usd_kwh = 0.15/);
    for (const architecture of [
      "islandable-microgrid",
      "mvdc-sst-hybrid",
      "grid+bess",
      "grid-only",
    ]) {
      expect(table.textContent).toContain(architecture);
    }
    expect(table.textContent).toContain("85.0%"); // swept chain_efficiency 0.85
  });

  it("debounces slider input into a single query", async () => {
    const fetchMock = renderPanel();

    await moveSlider("Equipment lead time factor", 1.5);
    await moveSlider("Equipment lead time factor", 1.6);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(String(init?.body))).toEqual({
      param: "equipment_lead_time_factor",
      range: [1.6],
    });
  });

  it("shows a loading state while the sweep runs", async () => {
    const fetchMock = mockFetch(() => new Promise<Response>(() => {}));
    renderPanel(fetchMock);

    await moveSlider("GPU utilization (fraction of nameplate IT load)", 0.75);

    // Not queried by role: <output> also has the implicit "status" role.
    expect(
      await screen.findByText(/Re-simulating at gpu_utilization = 0.75/),
    ).toBeInTheDocument();
  });

  it("surfaces sweep failures as an alert", async () => {
    const fetchMock = mockFetch(async () =>
      jsonResponse({ detail: "range values must be non-negative" }, 422),
    );
    renderPanel(fetchMock);

    await moveSlider("GPU utilization (fraction of nameplate IT load)", 0.75);

    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toContain(
      "Sensitivity query failed: range values must be non-negative",
    );
  });
});
