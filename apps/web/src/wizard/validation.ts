// Pure validation for wizard drafts. UI-free so tests can exercise the rules
// without rendering; the wizard just renders whatever errors come back.
//
// Rules mirror the engine's SiteProfile.__post_init__ (engine/engine/models.py):
// no negative magnitudes, flexible_share within [0, 1], criticality from the
// known set. The wizard additionally requires required fields to be present —
// the engine receives only complete profiles.

import { CRITICALITY_LEVELS } from "./types";
import type { SiteProfile, WizardDraft } from "./types";

/** Field name -> error message. An empty record means valid. */
export type Errors = Record<string, string>;

export function required(raw: string, label: string): string | null {
  if (raw.trim() === "") {
    return `${label} is required.`;
  }
  return null;
}

function numberRule(raw: string, label: string, min: number): string | null {
  const missing = required(raw, label);
  if (missing) return missing;
  const value = Number(raw.trim());
  if (Number.isNaN(value) || !Number.isFinite(value)) {
    return `${label} must be a number.`;
  }
  if (value < min) {
    return `${label} must be at least ${min}.`;
  }
  return null;
}

function intRule(raw: string, label: string, min: number): string | null {
  const notNumber = numberRule(raw, label, min);
  if (notNumber) return notNumber;
  if (!Number.isInteger(Number(raw.trim()))) {
    return `${label} must be a whole number.`;
  }
  return null;
}

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

function dateRule(raw: string, label: string): string | null {
  const missing = required(raw, label);
  if (missing) return missing;
  const value = raw.trim();
  if (!ISO_DATE.test(value) || Number.isNaN(Date.parse(value))) {
    return `${label} must be a valid date in YYYY-MM-DD format.`;
  }
  return null;
}

/** Errors for one wizard step; empty means the step is valid. */
export function validateStep(stepIndex: number, draft: WizardDraft): Errors {
  const errors: Errors = {};
  const add = (field: string, error: string | null) => {
    if (error) errors[field] = error;
  };

  switch (stepIndex) {
    case 0:
      add("location", required(draft.location, "Site location"));
      add(
        "tariff_usd_kwh",
        numberRule(draft.tariff_usd_kwh, "Utility tariff (USD/kWh)", 0),
      );
      break;
    case 1:
      add("it_load_mw", numberRule(draft.it_load_mw, "IT load (MW)", 0));
      add(
        "rack_density_kw",
        numberRule(draft.rack_density_kw, "Rack density (kW per rack)", 0),
      );
      break;
    case 2: {
      const shareError = numberRule(
        draft.flexible_share,
        "Flexible load share",
        0,
      );
      if (shareError) {
        add("flexible_share", shareError);
      } else if (Number(draft.flexible_share.trim()) > 1) {
        add("flexible_share", "Flexible load share must be at most 1.");
      }
      break;
    }
    case 3:
      add(
        "criticality",
        draft.criticality === ""
          ? "Reliability target is required."
          : CRITICALITY_LEVELS.includes(draft.criticality)
            ? null
            : "Reliability target must be one of the listed criticality levels.",
      );
      break;
    case 4:
      add("bess_mwh", numberRule(draft.bess_mwh, "BESS capacity (MWh)", 0));
      add("pv_mw", numberRule(draft.pv_mw, "Solar PV (MW)", 0));
      add("fuel_cell_mw", numberRule(draft.fuel_cell_mw, "Fuel cell (MW)", 0));
      add("genset_mw", numberRule(draft.genset_mw, "Backup generator (MW)", 0));
      break;
    case 5:
      add(
        "grid_limit_mw",
        numberRule(draft.grid_limit_mw, "Grid interconnection limit (MW)", 0),
      );
      add(
        "interconnection_wait_months",
        intRule(
          draft.interconnection_wait_months,
          "Interconnection wait (months)",
          0,
        ),
      );
      break;
    case 6:
      add(
        "target_energization",
        dateRule(draft.target_energization, "Target energization date"),
      );
      break;
    default:
      throw new Error(`Unknown wizard step index: ${stepIndex}`);
  }

  return errors;
}

/** Validate all steps up to `stepCount`; the wizard passes STEPS.length. */
export function validateDraft(draft: WizardDraft, stepCount: number): Errors {
  const combined: Errors = {};
  for (let i = 0; i < stepCount; i += 1) {
    Object.assign(combined, validateStep(i, draft));
  }
  return combined;
}

/**
 * Convert a draft into the engine-shaped SiteProfile. Call only on a draft
 * whose steps all validated; the guard throws rather than silently produce
 * NaN fields. Numeric fields were held as strings purely to survive editing.
 */
export function toSiteProfile(
  draft: WizardDraft,
  stepCount: number,
): SiteProfile {
  const criticality = draft.criticality;
  if (criticality === "") {
    throw new Error("Cannot convert an invalid draft: criticality is required.");
  }
  const errors = validateDraft(draft, stepCount);
  const first = Object.values(errors)[0];
  if (first) {
    throw new Error(`Cannot convert an invalid draft: ${first}`);
  }
  return {
    grid_limit_mw: Number(draft.grid_limit_mw),
    it_load_mw: Number(draft.it_load_mw),
    flexible_share: Number(draft.flexible_share),
    rack_density_kw: Number(draft.rack_density_kw),
    criticality,
    bess_mwh: Number(draft.bess_mwh),
    pv_mw: Number(draft.pv_mw),
    fuel_cell_mw: Number(draft.fuel_cell_mw),
    genset_mw: Number(draft.genset_mw),
    tariff_usd_kwh: Number(draft.tariff_usd_kwh),
    interconnection_wait_months: Number(draft.interconnection_wait_months),
    target_energization: draft.target_energization.trim(),
  };
}
