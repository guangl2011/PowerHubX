// Sensitivity explorer (spec art_Xihp9Qa2, evaluation dashboard): three
// slider levers re-query POST /sensitivity and re-render the five-axis table
// at the swept value. Slider positions update instantly; queries are
// debounced so a drag does not fire a request per pixel.

import { useEffect, useRef, useState } from "react";
import type { PowerHubXClient } from "../api/client";
import { errorMessage } from "../api/client";
import type { SensitivityPayload } from "../api/types";
import { pointToRow } from "./axes";
import { AxesTable } from "./AxesTable";

export type SensitivityParam =
  | "tariff_usd_kwh"
  | "gpu_utilization"
  | "equipment_lead_time_factor";

export interface SensitivityAxisConfig {
  param: SensitivityParam;
  label: string;
  min: number;
  max: number;
  step: number;
}

// Lever ranges bracket realistic readings; engine axes reject negatives, and
// the API re-validates every swept value (422 otherwise).
export const SENSITIVITY_AXES: readonly SensitivityAxisConfig[] = [
  {
    param: "tariff_usd_kwh",
    label: "Electricity price ($/kWh)",
    min: 0.02,
    max: 0.3,
    step: 0.005,
  },
  {
    param: "gpu_utilization",
    label: "GPU utilization (fraction of nameplate IT load)",
    min: 0.25,
    max: 1.25,
    step: 0.05,
  },
  {
    param: "equipment_lead_time_factor",
    label: "Equipment lead time factor",
    min: 0.5,
    max: 2,
    step: 0.1,
  },
];

export type SensitivityValues = Record<SensitivityParam, number>;

export function defaultSensitivityValues(tariffUsdKwh: number): SensitivityValues {
  const tariffAxis = SENSITIVITY_AXES[0];
  const clamped = Math.min(Math.max(tariffUsdKwh, tariffAxis.min), tariffAxis.max);
  return {
    tariff_usd_kwh: clamped,
    gpu_utilization: 1.0,
    equipment_lead_time_factor: 1.0,
  };
}

export const SWEEP_DEBOUNCE_MS = 250;

type SweepState =
  | { kind: "idle" }
  | { kind: "loading"; param: SensitivityParam; value: number }
  | { kind: "loaded"; param: SensitivityParam; value: number; payload: SensitivityPayload }
  | { kind: "error"; param: SensitivityParam; value: number; message: string };

interface SensitivityPanelProps {
  client: PowerHubXClient;
  projectId: string;
  initialValues: SensitivityValues;
}

export function SensitivityPanel({
  client,
  projectId,
  initialValues,
}: SensitivityPanelProps) {
  const [values, setValues] = useState<SensitivityValues>(initialValues);
  const [sweep, setSweep] = useState<SweepState>({ kind: "idle" });
  const debounceRef = useRef<number | undefined>(undefined);
  const requestIdRef = useRef(0);

  // Only the latest request may write state: a slow response from a
  // superseded slider position must never land after a newer one.
  useEffect(() => {
    return () => {
      window.clearTimeout(debounceRef.current);
    };
  }, []);

  function requestSweep(param: SensitivityParam, value: number) {
    const requestId = ++requestIdRef.current;
    setSweep({ kind: "loading", param, value });
    client
      .sensitivity(projectId, param, value)
      .then((payload) => {
        if (requestId !== requestIdRef.current) return;
        setSweep({ kind: "loaded", param, value, payload });
      })
      .catch((error: unknown) => {
        if (requestId !== requestIdRef.current) return;
        setSweep({ kind: "error", param, value, message: errorMessage(error) });
      });
  }

  function handleChange(param: SensitivityParam, value: number) {
    setValues((current) => ({ ...current, [param]: value }));
    window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(
      () => requestSweep(param, value),
      SWEEP_DEBOUNCE_MS,
    );
  }

  return (
    <section aria-label="Sensitivity analysis">
      <h2>Sensitivity</h2>
      <p>Move a lever to re-simulate the site at a new value.</p>
      {SENSITIVITY_AXES.map((axis) => (
        <div className="field" key={axis.param}>
          <label>
            <span>{axis.label}</span>
            <input
              type="range"
              min={axis.min}
              max={axis.max}
              step={axis.step}
              value={values[axis.param]}
              aria-label={axis.label}
              onChange={(e) => handleChange(axis.param, Number(e.target.value))}
            />
          </label>
          <output>{values[axis.param]}</output>
        </div>
      ))}
      <SweepResult sweep={sweep} />
    </section>
  );
}

function SweepResult({ sweep }: { sweep: SweepState }) {
  if (sweep.kind === "idle") {
    return (
      <p role="status">
        Adjust a lever above to sweep its value across all architectures.
      </p>
    );
  }
  if (sweep.kind === "loading") {
    return (
      <p role="status" aria-busy="true">
        Re-simulating at {sweep.param} = {sweep.value}…
      </p>
    );
  }
  if (sweep.kind === "error") {
    return (
      <div role="alert">
        <p>Sensitivity query failed: {sweep.message}</p>
      </div>
    );
  }
  return (
    <AxesTable
      rows={sweep.payload.points.map(pointToRow)}
      caption={`Swept ${sweep.payload.param} = ${sweep.value}: the five evaluation axes re-simulated.`}
    />
  );
}
