// TypeScript mirrors of the API's pydantic response contracts
// (apps/api/src/api/schemas.py). Field names stay snake_case to match the
// wire format, which itself mirrors the engine dataclasses.

import type { SiteProfile } from "../wizard/types";

export interface ProjectOut {
  id: string;
  name: string | null;
  location: string | null;
  site: SiteProfile | null;
  site_version: number;
  has_results: boolean;
  created_at: string;
  updated_at: string;
}

export interface DispatchSummary {
  curtailed_gpu_mwh: number;
  shed_mwh: number;
  curtailed_hours: number;
  shed_hours: number;
}

export interface ScenarioMetrics {
  architecture: string;
  chain_efficiency: number;
  annual_energy_mwh: number;
  loss_mwh: number;
  capex_usd: number;
  opex_usd_year: number;
  cost_per_mwh: number;
  time_to_power_months: number;
  resilience_score: number;
  /** Spec-mandated engine field name (art_Xihp9Qa2): kg CO2 per kWh. */
  carbon_kgCO2_kWh: number;
  dispatch: DispatchSummary;
}

export interface RankedScenario {
  architecture: string;
  score: number;
  axis_scores: Record<string, number>;
  metrics: ScenarioMetrics;
}

export interface ResultsPayload {
  site_version: number;
  /** The stored run predates the current site profile version. */
  stale: boolean;
  weights: Record<string, number>;
  ranking: RankedScenario[];
}

export interface SensitivityPoint {
  axis: string;
  value: number;
  architecture: string;
  chain_efficiency: number;
  annual_energy_mwh: number;
  capex_usd: number;
  opex_usd_year: number;
  cost_per_mwh: number;
  time_to_power_months: number;
  resilience_score: number;
  /** Spec-mandated engine field name (art_Xihp9Qa2): kg CO2 per kWh. */
  carbon_kgCO2_kWh: number;
}

export interface SensitivityPayload {
  param: string;
  values: number[];
  architectures: string[];
  points: SensitivityPoint[];
}
