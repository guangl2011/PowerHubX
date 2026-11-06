// TypeScript mirror of the engine's SiteProfile (engine/engine/models.py).
// The intake wizard produces this object; the API serializes it verbatim,
// so field names stay snake_case to match the Python dataclass.

export const CRITICALITY_LEVELS = [
  "tier3",
  "tier4",
  "inference",
  "training",
] as const;

export type Criticality = (typeof CRITICALITY_LEVELS)[number];

export interface SiteProfile {
  grid_limit_mw: number;
  it_load_mw: number;
  /** Fraction of IT load eligible for curtailment (0–1). */
  flexible_share: number;
  rack_density_kw: number;
  criticality: Criticality;
  bess_mwh: number;
  pv_mw: number;
  fuel_cell_mw: number;
  genset_mw: number;
  tariff_usd_kwh: number;
  interconnection_wait_months: number;
  /** ISO date (YYYY-MM-DD). */
  target_energization: string;
}

// The wizard holds every numeric input as its raw string so that partially
// typed or invalid values ("1.", "-3", "abc") survive editing. Parsing and
// validation happen in validation.ts; only complete drafts become a
// SiteProfile. `location` labels the site for humans but is not part of the
// engine contract, so toSiteProfile strips it.
export interface WizardDraft {
  location: string;
  tariff_usd_kwh: string;
  it_load_mw: string;
  rack_density_kw: string;
  flexible_share: string;
  criticality: Criticality | "";
  bess_mwh: string;
  pv_mw: string;
  fuel_cell_mw: string;
  genset_mw: string;
  grid_limit_mw: string;
  interconnection_wait_months: string;
  target_energization: string;
}

export function emptyDraft(): WizardDraft {
  return {
    location: "",
    tariff_usd_kwh: "",
    it_load_mw: "",
    rack_density_kw: "",
    flexible_share: "",
    criticality: "",
    bess_mwh: "",
    pv_mw: "",
    fuel_cell_mw: "",
    genset_mw: "",
    grid_limit_mw: "",
    interconnection_wait_months: "",
    target_energization: "",
  };
}
