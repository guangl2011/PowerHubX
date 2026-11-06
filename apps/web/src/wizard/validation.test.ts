import { describe, expect, it } from "vitest";
import { emptyDraft } from "./types";
import type { WizardDraft } from "./types";
import { toSiteProfile, validateDraft, validateStep } from "./validation";

function draftWith(overrides: Partial<WizardDraft>): WizardDraft {
  return { ...emptyDraft(), ...overrides };
}

describe("validateStep", () => {
  it("returns no errors for a valid step 1", () => {
    const draft = draftWith({ location: "Ashburn, VA", tariff_usd_kwh: "0.08" });
    expect(validateStep(0, draft)).toEqual({});
  });

  it("blocks step 1 when fields are missing", () => {
    expect(Object.keys(validateStep(0, emptyDraft()))).toEqual([
      "location",
      "tariff_usd_kwh",
    ]);
  });

  it("blocks a non-numeric tariff", () => {
    const draft = draftWith({ location: "X", tariff_usd_kwh: "eight cents" });
    expect(validateStep(0, draft)["tariff_usd_kwh"]).toMatch(/must be a number/i);
  });

  it("blocks negative MW on the IT load step", () => {
    const draft = draftWith({ it_load_mw: "-5", rack_density_kw: "130" });
    expect(validateStep(1, draft)["it_load_mw"]).toMatch(/at least 0/i);
  });

  it("blocks negative rack density", () => {
    const draft = draftWith({ it_load_mw: "50", rack_density_kw: "-1" });
    expect(validateStep(1, draft)["rack_density_kw"]).toMatch(/at least 0/i);
  });

  it("accepts a flexible share of 0 and 1 but rejects out-of-range values", () => {
    expect(validateStep(2, draftWith({ flexible_share: "0" }))).toEqual({});
    expect(validateStep(2, draftWith({ flexible_share: "1" }))).toEqual({});
    expect(
      validateStep(2, draftWith({ flexible_share: "1.5" }))["flexible_share"],
    ).toMatch(/at most 1/i);
    expect(
      validateStep(2, draftWith({ flexible_share: "-0.1" }))["flexible_share"],
    ).toMatch(/at least 0/i);
  });

  it("requires a known criticality level", () => {
    expect(validateStep(3, draftWith({ criticality: "" }))["criticality"]).toBeDefined();
  });

  it("accepts zero for every DER asset but rejects negative ones", () => {
    const zeros = draftWith({
      bess_mwh: "0",
      pv_mw: "0",
      fuel_cell_mw: "0",
      genset_mw: "0",
    });
    expect(validateStep(4, zeros)).toEqual({});
    expect(
      validateStep(4, draftWith({ ...zeros, bess_mwh: "-2" }))["bess_mwh"],
    ).toMatch(/at least 0/i);
  });

  it("requires a whole number of interconnection months", () => {
    const draft = draftWith({ grid_limit_mw: "100", interconnection_wait_months: "2.5" });
    expect(validateStep(5, draft)["interconnection_wait_months"]).toMatch(
      /whole number/i,
    );
  });

  it("rejects malformed energization dates", () => {
    expect(
      validateStep(6, draftWith({ target_energization: "2027-13-40" }))[
        "target_energization"
      ],
    ).toBeDefined();
    expect(
      validateStep(6, draftWith({ target_energization: "next spring" }))[
        "target_energization"
      ],
    ).toMatch(/YYYY-MM-DD/i);
  });
});

describe("validateDraft", () => {
  it("collects errors across every step", () => {
    const errors = validateDraft(emptyDraft(), 7);
    expect(Object.keys(errors)).toEqual([
      "location",
      "tariff_usd_kwh",
      "it_load_mw",
      "rack_density_kw",
      "flexible_share",
      "criticality",
      "bess_mwh",
      "pv_mw",
      "fuel_cell_mw",
      "genset_mw",
      "grid_limit_mw",
      "interconnection_wait_months",
      "target_energization",
    ]);
  });
});

describe("toSiteProfile", () => {
  const valid = draftWith({
    location: "Ashburn, VA",
    tariff_usd_kwh: "0.08",
    it_load_mw: "120",
    rack_density_kw: "132",
    flexible_share: "0.4",
    criticality: "tier4",
    bess_mwh: "80",
    pv_mw: "10",
    fuel_cell_mw: "5",
    genset_mw: "20",
    grid_limit_mw: "150",
    interconnection_wait_months: "36",
    target_energization: "2028-06-01",
  });

  it("produces the engine-shaped SiteProfile", () => {
    expect(toSiteProfile(valid, 7)).toEqual({
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
    });
  });

  it("never emits NaN fields", () => {
    const profile = toSiteProfile(valid, 7);
    for (const [key, value] of Object.entries(profile)) {
      if (typeof value === "number") {
        expect(value, key).not.toBeNaN();
      }
    }
  });

  it("throws instead of converting an invalid draft", () => {
    expect(() => toSiteProfile(emptyDraft(), 7)).toThrow(/invalid draft/i);
  });
});
