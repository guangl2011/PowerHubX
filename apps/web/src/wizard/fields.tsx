// Plain-React form primitives for the wizard. The bootstrap scaffold ships no
// component library, so these stay deliberately minimal: a labeled text
// input and a labeled select, each surfacing a validation error.

import type { ChangeEvent } from "react";

interface TextFieldProps {
  label: string;
  value: string;
  error?: string;
  onChange: (value: string) => void;
}

export function TextField({ label, value, error, onChange }: TextFieldProps) {
  const errorId = error ? `${label}-error` : undefined;
  return (
    <div className="field">
      <label>
        <span>{label}</span>
        <input
          type="text"
          value={value}
          aria-invalid={error ? true : undefined}
          aria-describedby={errorId}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            onChange(e.target.value)
          }
        />
      </label>
      {error && (
        <p role="alert" id={errorId} className="field-error">
          {error}
        </p>
      )}
    </div>
  );
}

interface SelectFieldProps {
  label: string;
  value: string;
  error?: string;
  options: readonly string[];
  onChange: (value: string) => void;
}

export function SelectField({
  label,
  value,
  error,
  options,
  onChange,
}: SelectFieldProps) {
  const errorId = error ? `${label}-error` : undefined;
  return (
    <div className="field">
      <label>
        <span>{label}</span>
        <select
          value={value}
          aria-invalid={error ? true : undefined}
          aria-describedby={errorId}
          onChange={(e: ChangeEvent<HTMLSelectElement>) =>
            onChange(e.target.value)
          }
        >
          <option value="" disabled>
            Select…
          </option>
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
      {error && (
        <p role="alert" id={errorId} className="field-error">
          {error}
        </p>
      )}
    </div>
  );
}
