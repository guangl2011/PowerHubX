// Intake wizard: a guided questionnaire that turns site facts into a typed
// SiteProfile (spec art_Xihp9Qa2, D3). Presentational only — the parent
// receives the completed profile via onComplete; no API calls from here yet.

import { useState } from "react";
import { SelectField, TextField } from "./fields";
import { CRITICALITY_LEVELS, emptyDraft } from "./types";
import type { SiteProfile, WizardDraft } from "./types";

interface WizardStep {
  title: string;
  description: string;
}

const STEPS: WizardStep[] = [
  {
    title: "Location & utility tariff",
    description: "Where the site is and what the utility charges per kWh.",
  },
  {
    title: "IT load & rack density",
    description: "Total IT load in MW and the power draw per AI rack in kW.",
  },
  {
    title: "Critical vs. flexible load share",
    description:
      "The fraction of IT load that can be curtailed during grid stress — GPU training and batch inference are typically flexible; tier-critical serving is not.",
  },
  {
    title: "Reliability target",
    description: "The criticality class the site must uphold.",
  },
  {
    title: "DER assets",
    description:
      "On-site generation and storage. Leave an asset at 0 if the site has none.",
  },
  {
    title: "Interconnection limit",
    description:
      "Maximum MW the grid will deliver and how long interconnection approval is expected to take.",
  },
  {
    title: "Desired energization date",
    description: "When the site needs to be powered on (YYYY-MM-DD).",
  },
];

interface IntakeWizardProps {
  /** Called once with the completed, validated SiteProfile. */
  onComplete: (profile: SiteProfile) => void;
}

export function IntakeWizard({ onComplete }: IntakeWizardProps) {
  const [draft, setDraft] = useState<WizardDraft>(emptyDraft);
  const [stepIndex, setStepIndex] = useState(0);
  const [completed, setCompleted] = useState<SiteProfile | null>(null);

  if (completed) {
    return (
      <CompletionScreen
        profile={completed}
        onStartOver={() => {
          setDraft(emptyDraft());
          setStepIndex(0);
          setCompleted(null);
        }}
      />
    );
  }

  const step = STEPS[stepIndex];
  const isLastStep = stepIndex === STEPS.length - 1;

  function update<K extends keyof WizardDraft>(key: K, value: WizardDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  function handleNext() {
    // Validation is wired in the next commit (site profile validation).
    if (isLastStep) {
      const profile = toSiteProfile(draft);
      setCompleted(profile);
      onComplete(profile);
      return;
    }
    setStepIndex((i) => Math.min(i + 1, STEPS.length - 1));
  }

  function handleBack() {
    setStepIndex((i) => Math.max(i - 1, 0));
  }

  return (
    <section aria-label="Intake wizard">
      <ol className="wizard-progress" aria-label="Wizard progress">
        {STEPS.map((s, i) => (
          <li
            key={s.title}
            aria-current={i === stepIndex ? "step" : undefined}
            data-active={i === stepIndex || undefined}
          >
            {s.title}
          </li>
        ))}
      </ol>

      <h2>{`Step ${stepIndex + 1} of ${STEPS.length}: ${step.title}`}</h2>
      <p>{step.description}</p>

      <StepFields stepIndex={stepIndex} draft={draft} update={update} />

      <div className="wizard-actions">
        <button type="button" onClick={handleBack} disabled={stepIndex === 0}>
          Back
        </button>
        <button type="button" onClick={handleNext}>
          {isLastStep ? "Generate site profile" : "Next"}
        </button>
        <button
          type="button"
          onClick={() => {
            setDraft(emptyDraft());
            setStepIndex(0);
          }}
        >
          Reset
        </button>
      </div>
    </section>
  );
}

interface StepFieldsProps {
  stepIndex: number;
  draft: WizardDraft;
  update: <K extends keyof WizardDraft>(key: K, value: WizardDraft[K]) => void;
}

function StepFields({ stepIndex, draft, update }: StepFieldsProps) {
  switch (stepIndex) {
    case 0:
      return (
        <>
          <TextField
            label="Site location"
            value={draft.location}
            onChange={(v) => update("location", v)}
          />
          <TextField
            label="Utility tariff (USD/kWh)"
            value={draft.tariff_usd_kwh}
            onChange={(v) => update("tariff_usd_kwh", v)}
          />
        </>
      );
    case 1:
      return (
        <>
          <TextField
            label="IT load (MW)"
            value={draft.it_load_mw}
            onChange={(v) => update("it_load_mw", v)}
          />
          <TextField
            label="Rack density (kW per rack)"
            value={draft.rack_density_kw}
            onChange={(v) => update("rack_density_kw", v)}
          />
        </>
      );
    case 2:
      return (
        <TextField
          label="Flexible load share (0 to 1)"
          value={draft.flexible_share}
          onChange={(v) => update("flexible_share", v)}
        />
      );
    case 3:
      return (
        <SelectField
          label="Reliability target (criticality)"
          value={draft.criticality}
          options={CRITICALITY_LEVELS}
          onChange={(v) => update("criticality", v as WizardDraft["criticality"])}
        />
      );
    case 4:
      return (
        <>
          <TextField
            label="BESS capacity (MWh)"
            value={draft.bess_mwh}
            onChange={(v) => update("bess_mwh", v)}
          />
          <TextField
            label="Solar PV (MW)"
            value={draft.pv_mw}
            onChange={(v) => update("pv_mw", v)}
          />
          <TextField
            label="Fuel cell (MW)"
            value={draft.fuel_cell_mw}
            onChange={(v) => update("fuel_cell_mw", v)}
          />
          <TextField
            label="Backup generator (MW)"
            value={draft.genset_mw}
            onChange={(v) => update("genset_mw", v)}
          />
        </>
      );
    case 5:
      return (
        <>
          <TextField
            label="Grid interconnection limit (MW)"
            value={draft.grid_limit_mw}
            onChange={(v) => update("grid_limit_mw", v)}
          />
          <TextField
            label="Interconnection wait (months)"
            value={draft.interconnection_wait_months}
            onChange={(v) => update("interconnection_wait_months", v)}
          />
        </>
      );
    case 6:
      return (
        <TextField
          label="Target energization date (YYYY-MM-DD)"
          value={draft.target_energization}
          onChange={(v) => update("target_energization", v)}
        />
      );
    default:
      throw new Error(`Unknown wizard step index: ${stepIndex}`);
  }
}

// Temporary draft-to-profile conversion; numeric parsing and validation land
// in the next commit (validation.ts).
function toSiteProfile(draft: WizardDraft): SiteProfile {
  return {
    grid_limit_mw: Number(draft.grid_limit_mw),
    it_load_mw: Number(draft.it_load_mw),
    flexible_share: Number(draft.flexible_share),
    rack_density_kw: Number(draft.rack_density_kw),
    criticality: draft.criticality as SiteProfile["criticality"],
    bess_mwh: Number(draft.bess_mwh),
    pv_mw: Number(draft.pv_mw),
    fuel_cell_mw: Number(draft.fuel_cell_mw),
    genset_mw: Number(draft.genset_mw),
    tariff_usd_kwh: Number(draft.tariff_usd_kwh),
    interconnection_wait_months: Number(draft.interconnection_wait_months),
    target_energization: draft.target_energization,
  };
}

interface CompletionScreenProps {
  profile: SiteProfile;
  onStartOver: () => void;
}

function CompletionScreen({ profile, onStartOver }: CompletionScreenProps) {
  return (
    <section aria-label="Site profile complete">
      <h2>Site profile complete</h2>
      <p>
        The site profile below is ready for architecture simulation (arriving
        in a later release).
      </p>
      <pre data-testid="site-profile-json">
        {JSON.stringify(profile, null, 2)}
      </pre>
      <button type="button" onClick={onStartOver}>
        Start over
      </button>
    </section>
  );
}
