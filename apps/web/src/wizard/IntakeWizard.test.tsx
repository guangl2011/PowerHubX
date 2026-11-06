import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { IntakeWizard } from "./IntakeWizard";
import type { SiteProfile } from "./types";

const EXPECTED_PROFILE: SiteProfile = {
  grid_limit_mw: 150,
  it_load_mw: 120,
  flexible_share: 0.4,
  rack_density_kw: 132,
  criticality: "tier4",
  bess_mwh: 80,
  pv_mw: 10,
  fuel_cell_mw: 5,
  genset_mw: 20,
  tariff_usd_kwh: 0.08,
  interconnection_wait_months: 36,
  target_energization: "2028-06-01",
};

async function fillField(label: string, value: string) {
  await userEvent.type(screen.getByLabelText(label), value);
}

async function selectOption(label: string, value: string) {
  await userEvent.selectOptions(screen.getByLabelText(label), value);
}

async function clickNext() {
  await userEvent.click(screen.getByRole("button", { name: "Next" }));
}

async function advanceValidSteps() {
  await fillField("Site location", "Ashburn, VA");
  await fillField("Utility tariff (USD/kWh)", "0.08");
  await clickNext();

  await fillField("IT load (MW)", "120");
  await fillField("Rack density (kW per rack)", "132");
  await clickNext();

  await fillField("Flexible load share (0 to 1)", "0.4");
  await clickNext();

  await selectOption("Reliability target (criticality)", "tier4");
  await clickNext();

  await fillField("BESS capacity (MWh)", "80");
  await fillField("Solar PV (MW)", "10");
  await fillField("Fuel cell (MW)", "5");
  await fillField("Backup generator (MW)", "20");
  await clickNext();

  await fillField("Grid interconnection limit (MW)", "150");
  await fillField("Interconnection wait (months)", "36");
  await clickNext();
}

describe("IntakeWizard step validation", () => {
  it("blocks progression on the empty initial state and shows required errors", async () => {
    render(<IntakeWizard onComplete={() => {}} />);
    await clickNext();
    expect(screen.getByText("Site location is required.")).toBeInTheDocument();
    expect(
      screen.getByText("Utility tariff (USD/kWh) is required."),
    ).toBeInTheDocument();
    // Still on step 1.
    expect(
      screen.getByRole("heading", { name: /Step 1 of 7/ }),
    ).toBeInTheDocument();
  });

  it("blocks a non-numeric tariff and stays on step 1", async () => {
    render(<IntakeWizard onComplete={() => {}} />);
    await fillField("Site location", "Ashburn, VA");
    await fillField("Utility tariff (USD/kWh)", "eight cents");
    await clickNext();
    expect(
      screen.getByText("Utility tariff (USD/kWh) must be a number."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Step 1 of 7/ }),
    ).toBeInTheDocument();
  });

  it("blocks negative MW on the IT load step", async () => {
    render(<IntakeWizard onComplete={() => {}} />);
    await fillField("Site location", "Ashburn, VA");
    await fillField("Utility tariff (USD/kWh)", "0.08");
    await clickNext();

    await fillField("IT load (MW)", "-5");
    await fillField("Rack density (kW per rack)", "132");
    await clickNext();
    expect(screen.getByText("IT load (MW) must be at least 0.")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Step 2 of 7/ }),
    ).toBeInTheDocument();
  });

  it("blocks a missing criticality selection", async () => {
    render(<IntakeWizard onComplete={() => {}} />);
    await fillField("Site location", "Ashburn, VA");
    await fillField("Utility tariff (USD/kWh)", "0.08");
    await clickNext();
    await fillField("IT load (MW)", "120");
    await fillField("Rack density (kW per rack)", "132");
    await clickNext();
    await fillField("Flexible load share (0 to 1)", "0.4");
    await clickNext();

    await clickNext();
    expect(
      screen.getByText("Reliability target is required."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Step 4 of 7/ }),
    ).toBeInTheDocument();
  });

  it("blocks progression past step 1 when only the date is missing", async () => {
    render(<IntakeWizard onComplete={() => {}} />);
    await advanceValidSteps();

    // Last step: date still empty — completion is blocked.
    await userEvent.click(
      screen.getByRole("button", { name: "Generate site profile" }),
    );
    expect(
      screen.getByText("Target energization date is required."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Step 7 of 7/ }),
    ).toBeInTheDocument();
  });
});

describe("IntakeWizard completion", () => {
  it("produces the correctly shaped SiteProfile on completion", async () => {
    const onComplete = vi.fn();
    render(<IntakeWizard onComplete={onComplete} />);
    await advanceValidSteps();

    await fillField("Target energization date (YYYY-MM-DD)", "2028-06-01");
    await userEvent.click(
      screen.getByRole("button", { name: "Generate site profile" }),
    );

    expect(onComplete).toHaveBeenCalledOnce();
    expect(onComplete).toHaveBeenCalledWith(EXPECTED_PROFILE);
    expect(screen.getByTestId("site-profile-json")).toHaveTextContent(
      '"criticality": "tier4"',
    );
    expect(
      screen.getByRole("heading", { name: "Site profile complete" }),
    ).toBeInTheDocument();
  });

  it("returns to an empty, actionable wizard from the Start over button", async () => {
    const onComplete = vi.fn();
    render(<IntakeWizard onComplete={onComplete} />);
    await advanceValidSteps();
    await fillField("Target energization date (YYYY-MM-DD)", "2028-06-01");
    await userEvent.click(
      screen.getByRole("button", { name: "Generate site profile" }),
    );

    await userEvent.click(screen.getByRole("button", { name: "Start over" }));
    expect(
      screen.getByRole("heading", { name: /Step 1 of 7/ }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Site location")).toHaveValue("");
    // The empty state is actionable: validation errors surface on demand.
    await clickNext();
    expect(screen.getByText("Site location is required.")).toBeInTheDocument();
  });
});

describe("IntakeWizard reset", () => {
  it("reaches the empty state via Reset and blocks progression there", async () => {
    render(<IntakeWizard onComplete={() => {}} />);
    await fillField("Site location", "Ashburn, VA");
    await fillField("Utility tariff (USD/kWh)", "0.08");
    await userEvent.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByLabelText("Site location")).toHaveValue("");
    expect(screen.getByLabelText("Utility tariff (USD/kWh)")).toHaveValue("");
    expect(
      screen.getByRole("heading", { name: /Step 1 of 7/ }),
    ).toBeInTheDocument();
  });
});
