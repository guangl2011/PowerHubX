// Shared five-axis table for the comparison dashboard and the sensitivity
// sweep: one row per axis, one column per architecture.

import { AXIS_KEYS, AXIS_LABELS, formatAxis } from "./axes";
import type { AxesTableRow } from "./axes";

interface AxesTableProps {
  rows: AxesTableRow[];
  caption: string;
}

export function AxesTable({ rows, caption }: AxesTableProps) {
  return (
    <table>
      <caption>{caption}</caption>
      <thead>
        <tr>
          <th scope="col">Evaluation axis</th>
          {rows.map((row) => (
            <th scope="col" key={row.architecture}>
              {row.architecture}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {AXIS_KEYS.map((axis) => (
          <tr key={axis}>
            <th scope="row">{AXIS_LABELS[axis]}</th>
            {rows.map((row) => (
              <td key={row.architecture}>{formatAxis(axis, row.values[axis])}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
