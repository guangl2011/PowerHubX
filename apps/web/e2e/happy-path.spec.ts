// D3 happy-path E2E (spec art_Xihp9Qa2): fill the intake wizard, run the
// simulation of all four architectures, see the ranked comparison on the
// dashboard, then open the feasibility report. Runs against the Vite dev
// server whose /api proxy reaches the FastAPI backend (playwright.config.ts).

import { expect, test } from "@playwright/test";

// A small but non-trivial reference site: grid limit below IT load so
// time-to-power and curtailment matter, a flexible share above zero so GPU
// dispatch is exercised, and some DER so the microgrid scenarios differ.
const REFERENCE_SITE = {
  location: "Northern Virginia",
  tariff_usd_kwh: "0.08",
  it_load_mw: "120",
  rack_density_kw: "132",
  flexible_share: "0.4",
  criticality: "training",
  bess_mwh: "240",
  pv_mw: "0",
  fuel_cell_mw: "0",
  genset_mw: "20",
  grid_limit_mw: "90",
  interconnection_wait_months: "48",
  target_energization: "2028-06-01",
} as const;

const ARCHITECTURES = [
  "grid-only",
  "grid+bess",
  "mvdc-sst-hybrid",
  "islandable-microgrid",
] as const;

test("intake wizard to four-architecture comparison to report", async ({
  page,
}) => {
  await page.goto("/");

  // --- Wizard: seven steps, gated progression -----------------------------
  await expect(
    page.getByRole("heading", { name: "Step 1 of 7" }),
  ).toBeVisible();
  await page.getByLabel("Site location").fill(REFERENCE_SITE.location);
  await page
    .getByLabel("Utility tariff (USD/kWh)")
    .fill(REFERENCE_SITE.tariff_usd_kwh);
  await page.getByRole("button", { name: "Next" }).click();

  await expect(
    page.getByRole("heading", { name: "Step 2 of 7" }),
  ).toBeVisible();
  await page.getByLabel("IT load (MW)").fill(REFERENCE_SITE.it_load_mw);
  await page
    .getByLabel("Rack density (kW per rack)")
    .fill(REFERENCE_SITE.rack_density_kw);
  await page.getByRole("button", { name: "Next" }).click();

  await expect(
    page.getByRole("heading", { name: "Step 3 of 7" }),
  ).toBeVisible();
  await page
    .getByLabel("Flexible load share (0 to 1)")
    .fill(REFERENCE_SITE.flexible_share);
  await page.getByRole("button", { name: "Next" }).click();

  await expect(
    page.getByRole("heading", { name: "Step 4 of 7" }),
  ).toBeVisible();
  await page
    .getByLabel("Reliability target (criticality)")
    .selectOption(REFERENCE_SITE.criticality);
  await page.getByRole("button", { name: "Next" }).click();

  await expect(
    page.getByRole("heading", { name: "Step 5 of 7" }),
  ).toBeVisible();
  await page.getByLabel("BESS capacity (MWh)").fill(REFERENCE_SITE.bess_mwh);
  await page.getByLabel("Solar PV (MW)").fill(REFERENCE_SITE.pv_mw);
  await page.getByLabel("Fuel cell (MW)").fill(REFERENCE_SITE.fuel_cell_mw);
  await page
    .getByLabel("Backup generator (MW)")
    .fill(REFERENCE_SITE.genset_mw);
  await page.getByRole("button", { name: "Next" }).click();

  await expect(
    page.getByRole("heading", { name: "Step 6 of 7" }),
  ).toBeVisible();
  await page
    .getByLabel("Grid interconnection limit (MW)")
    .fill(REFERENCE_SITE.grid_limit_mw);
  await page
    .getByLabel("Interconnection wait (months)")
    .fill(REFERENCE_SITE.interconnection_wait_months);
  await page.getByRole("button", { name: "Next" }).click();

  await expect(
    page.getByRole("heading", { name: "Step 7 of 7" }),
  ).toBeVisible();
  await page
    .getByLabel("Target energization date (YYYY-MM-DD)")
    .fill(REFERENCE_SITE.target_energization);
  await page.getByRole("button", { name: "Generate site profile" }).click();

  // --- Bootstrap: create + site + simulate --------------------------------
  // The "starting" status can flash by when simulate is fast, so the first
  // durable readiness signal is the dashboard's ranked recommendation.
  const recommended = page.getByTestId("recommended-architecture");
  await expect(recommended).toBeVisible({ timeout: 30_000 });
  await expect(recommended).not.toHaveText("");

  const ranked = page.getByRole("list", { name: "Ranked architectures" });
  await expect(ranked.getByRole("listitem")).toHaveCount(4);
  for (const architecture of ARCHITECTURES) {
    await expect(ranked).toContainText(architecture);
  }

  // The five evaluation axes run across all four simulated architectures.
  const table = page.getByRole("table");
  await expect(table.getByRole("row")).toHaveCount(6); // header + five axes
  for (const architecture of ARCHITECTURES) {
    await expect(table.locator("thead")).toContainText(architecture);
  }

  // --- Report: print-ready feasibility report in the isolated frame ------
  await page.getByRole("button", { name: "Report" }).click();
  const reportFrame = page.frameLocator('iframe[title="Feasibility report"]');
  await expect(
    reportFrame.getByRole("heading", {
      name: "PowerHubX feasibility report",
    }),
  ).toBeVisible({ timeout: 15_000 });
  await expect(
    reportFrame.getByRole("heading", { name: "Recommended architecture" }),
  ).toBeVisible();
  await expect(
    reportFrame.getByRole("heading", { name: "Architecture comparison" }),
  ).toBeVisible();
  await expect(
    reportFrame.getByRole("heading", { name: "Assumptions & scope" }),
  ).toBeVisible();
});
