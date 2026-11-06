// Intake wizard: a guided questionnaire that turns site facts into a typed
// SiteProfile (spec art_Xihp9Qa2, D3). Presentational only — the parent
// receives the completed profile via onComplete; no API calls from here yet.

import { useState } from "react";
import { SelectField, TextField } from "./fields";
import { CRITICALITY_LEVELS, emptyDraft } from "./types";
import type { SiteProfile, WizardDraft } from "./types";
import { toSiteProfile, validateStep } from "./validation";
import type { Errors } from "./validation";

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
  const [errors, setErrors] = useState<Errors>({});
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
    // Gate progression on the current step: invalid values block the wizard
    // and surface per-field errors instead of reaching a later step.
    const stepErrors = validateStep(stepIndex, draft);
    if (Object.keys(stepErrors).length > 0) {
      setErrors(stepErrors);
      return;
    }
    if (isLastStep) {
      const profile = toSiteProfile(draft, STEPS.length);
      setCompleted(profile);
      onComplete(profile);
      return;
    }
    setErrors({});
    setStepIndex((i) => Math.min(i + 1, STEPS.length - 1));
  }

  function handleBack() {
    setErrors({});
    setStepIndex((i) => Math.max(i - 1, 0));
  }

  function reset() {
    setDraft(emptyDraft());
    setStepIndex(0);
    setErrors({});
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

      <StepFields stepIndex={stepIndex} draft={draft} errors={errors} update={update} />

      <div className="wizard-actions">
        <button type="button" onClick={handleBack} disabled={stepIndex === 0}>
          Back
        </button>
        <button type="button" onClick={handleNext}>
          {isLastStep ? "Generate site profile" : "Next"}
        </button>
        <button type="button" onClick={reset}>Reset</button>
      </div>
    </section>
  );
}

interface StepFieldsProps {
  stepIndex: number;
  draft: WizardDraft;
  errors: Errors;
  update: <K extends keyof WizardDraft>(key: K, value: WizardDraft[K]) => void;
}

function StepFields({ stepIndex, draft, errors, update }: StepFieldsProps) {
  const text = (label: string, field: keyof WizardDraft) => (
    <TextField
      label={label}
      value={draft[field]}
      error={errors[field]}
      onChange={(v) => update(field, v as string)}
    />
  );

  switch (stepIndex) {
    case 0:
      return (
        <>
          {text("Site location", "location")}
          {text("Utility tariff (USD/kWh)", "tariff_usd_kwh")}
        </>
      );
    case 1:
      return (
        <>
          {text("IT load (MW)", "it_load_mw")}
          {text("Rack density (kW per rack)", "rack_density_kw")}
        </>
      );
    case 2:
      return text("Flexible load share (0 to 1)", "flexible_share");
    case 3:
      return (
        <SelectField
          label="Reliability target (criticality)"
          value={draft.criticality}
          error={errors.criticality}
          options={CRITICALITY_LEVELS}
          onChange={(v) => update("criticality", v as WizardDraft["criticality"])}
        />
      );
    case 4:
      return (
        <>
          {text("BESS capacity (MWh)", "bess_mwh")}
          {text("Solar PV (MW)", "pv_mw")}
          {text("Fuel cell (MW)", "fuel_cell_mw")}
          {text("Backup generator (MW)", "genset_mw")}
        </>
      );
    case 5:
      return (
        <>
          {text("Grid interconnection limit (MW)", "grid_limit_mw")}
          {text("Interconnection wait (months)", "interconnection_wait_months")}
        </>
      );
    case 6:
      return text("Target energization date (YYYY-MM-DD)", "target_energization");
    default:
      throw new Error(`Unknown wizard step index: ${stepIndex}`);
  }
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
