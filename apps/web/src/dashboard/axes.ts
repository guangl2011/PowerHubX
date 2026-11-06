// The five evaluation axes (spec art_Xihp9Qa2): the same vocabulary as the
// backend's ranking module (apps/api/src/api/ranking.py). Pure mapping and
// formatting only — no React.

import type { ScenarioMetrics, SensitivityPoint } from "../api/types";

export type AxisKey =
  | "chain_efficiency"
  | "cost_per_mwh"
  | "time_to_power_months"
  | "resilience_score"
  | "carbon_kgCO2_kWh";

export const AXIS_KEYS: readonly AxisKey[] = [
  "chain_efficiency",
  "cost_per_mwh",
  "time_to_power_months",
  "resilience_score",
  "carbon_kgCO2_kWh",
];

export const AXIS_LABELS: Record<AxisKey, string> = {
  chain_efficiency: "Chain efficiency",
  cost_per_mwh: "Cost per delivered MWh",
  time_to_power_months: "Time to power",
  resilience_score: "Resilience",
  carbon_kgCO2_kWh: "Carbon intensity",
};

export function formatAxis(key: AxisKey, value: number): string {
  switch (key) {
    case "chain_efficiency":
      return `${(value * 100).toFixed(1)}%`;
    case "cost_per_mwh":
      return `$${Math.round(value).toLocaleString("en-US")}/MWh`;
    case "time_to_power_months":
      return `${value.toFixed(1)} months`;
    case "resilience_score":
      return value.toFixed(2);
    case "carbon_kgCO2_kWh":
      return `${value.toFixed(3)} kg CO2/kWh`;
  }
}

export interface AxesTableRow {
  architecture: string;
  values: Record<AxisKey, number>;
}

// Explicit field mapping — both API shapes carry the five axis fields, but
// under different interfaces, and an honest projection beats a cast.
function axisValues(
  source: ScenarioMetrics | SensitivityPoint,
): Record<AxisKey, number> {
  return {
    chain_efficiency: source.chain_efficiency,
    cost_per_mwh: source.cost_per_mwh,
    time_to_power_months: source.time_to_power_months,
    resilience_score: source.resilience_score,
    carbon_kgCO2_kWh: source.carbon_kgCO2_kWh,
  };
}

export function metricsToRow(metrics: ScenarioMetrics): AxesTableRow {
  return { architecture: metrics.architecture, values: axisValues(metrics) };
}

export function pointToRow(point: SensitivityPoint): AxesTableRow {
  return { architecture: point.architecture, values: axisValues(point) };
}
