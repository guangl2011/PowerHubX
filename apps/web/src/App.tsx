// Placeholder landing screen for the bootstrap PR. The intake wizard and
// comparison dashboard arrive in later PRs (spec art_Xihp9Qa2, D3).
import { IntakeWizard } from "./wizard/IntakeWizard";

export default function App() {
  return (
    <main>
      <h1>PowerHubX</h1>
      <p>
        Feasibility-to-onboarding for AI data center and microgrid power
        architecture decisions.
      </p>
      <IntakeWizard onComplete={() => {}} />
    </main>
  );
}
