// Shared response builders for dashboard tests: fixtures shaped exactly like
// the API's pydantic contracts (apps/api/src/api/schemas.py).

import type {
  ResultsPayload,
  ScenarioMetrics,
  RankedScenario,
  SensitivityPayload,
  SensitivityPoint,
} from "../api/types";

// Ranked best-first, mirroring the API's sort order.
export const ARCHITECTURES = [
  "islandable-microgrid",
  "mvdc-sst-hybrid",
  "grid+bess",
  "grid-only",
] as const;

export function scenarioMetrics(architecture: string, rank: number): ScenarioMetrics {
  return {
    architecture,
    chain_efficiency: 0.9 - rank * 0.05,
    annual_energy_mwh: 1000,
    loss_mwh: 100,
    capex_usd: 1_000_000,
    opex_usd_year: 50_000,
    cost_per_mwh: 60 + rank * 10,
    time_to_power_months: 12 + rank * 6,
    resilience_score: 0.9 - rank * 0.1,
    carbon_kgCO2_kWh: 0.1 + rank * 0.05,
    dispatch: {
      curtailed_gpu_mwh: 10,
      shed_mwh: 0,
      curtailed_hours: 5,
      shed_hours: 0,
    },
  };
}

export function rankedScenario(architecture: string, rank: number): RankedScenario {
  return {
    architecture,
    score: 0.9 - rank * 0.1,
    axis_scores: {},
    metrics: scenarioMetrics(architecture, rank),
  };
}

export function resultsPayload(
  overrides: Partial<ResultsPayload> = {},
): ResultsPayload {
  return {
    site_version: 2,
    stale: false,
    weights: {
      chain_efficiency: 1,
      cost_per_mwh: 1,
      time_to_power_months: 1,
      resilience_score: 1,
      carbon_kgCO2_kWh: 1,
    },
    ranking: ARCHITECTURES.map((architecture, rank) =>
      rankedScenario(architecture, rank),
    ),
    ...overrides,
  };
}

export function sensitivityPoint(
  architecture: string,
  value: number,
): SensitivityPoint {
  return {
    axis: "tariff_usd_kwh",
    value,
    architecture,
    chain_efficiency: 0.85,
    annual_energy_mwh: 1000,
    capex_usd: 1_000_000,
    opex_usd_year: 50_000,
    cost_per_mwh: 75,
    time_to_power_months: 18,
    resilience_score: 0.7,
    carbon_kgCO2_kWh: 0.15,
  };
}

export function sensitivityPayload(
  param: string,
  value: number,
  architectures: readonly string[] = ARCHITECTURES,
): SensitivityPayload {
  return {
    param,
    values: [value],
    architectures: [...architectures],
    points: architectures.map((architecture) =>
      sensitivityPoint(architecture, value),
    ),
  };
}
