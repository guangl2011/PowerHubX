// Typed fetch client for the seven MVP endpoints (spec art_Xihp9Qa2).
// Relative URLs keep the app same-origin: the Vite dev server proxies /api
// to the FastAPI backend (vite.config.ts), and tests inject a stub fetch
// instead of pointing this client at a real server.

import type { SiteProfile } from "../wizard/types";
import type { ProjectOut, ResultsPayload, SensitivityPayload } from "./types";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Unexpected error";
}

/** Extracts FastAPI's error detail: a string, or pydantic's 422 item list. */
export function detailFromBody(body: unknown): string | null {
  if (body === null || typeof body !== "object" || !("detail" in body)) {
    return null;
  }
  const detail = (body as { detail: unknown }).detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    const parts = detail
      .filter(
        (item): item is Record<string, unknown> =>
          item !== null && typeof item === "object",
      )
      .map((item) => {
        const loc = Array.isArray(item.loc) ? item.loc.join(".") : "";
        const msg = typeof item.msg === "string" ? item.msg : "";
        return [loc, msg].filter(Boolean).join(": ");
      })
      .filter(Boolean);
    if (parts.length > 0) {
      return parts.join("; ");
    }
  }
  return null;
}

async function parseErrorResponse(response: Response): Promise<ApiError> {
  let detail: string | null = null;
  try {
    detail = detailFromBody(await response.json());
  } catch {
    // Body was not JSON — the status line below still describes the failure.
  }
  return new ApiError(
    response.status,
    detail ?? `Request failed with status ${response.status}`,
  );
}

export class PowerHubXClient {
  constructor(
    private readonly fetchImpl: typeof fetch = globalThis.fetch.bind(globalThis),
    private readonly baseUrl = "",
  ) {}

  createProject(name: string | null): Promise<ProjectOut> {
    return this.sendJson<ProjectOut>("POST", "/api/projects", { name });
  }

  replaceSite(projectId: string, site: SiteProfile): Promise<ProjectOut> {
    return this.sendJson<ProjectOut>(
      "PUT",
      `/api/projects/${projectId}/site`,
      site,
    );
  }

  simulate(projectId: string): Promise<ResultsPayload> {
    // Empty body: SimulateIn.architectures omitted means "run all four".
    return this.sendJson<ResultsPayload>(
      "POST",
      `/api/projects/${projectId}/simulate`,
      {},
    );
  }

  /** Single-point sweep: one axis value re-simulated for every architecture. */
  sensitivity(
    projectId: string,
    param: string,
    value: number,
  ): Promise<SensitivityPayload> {
    return this.sendJson<SensitivityPayload>(
      "POST",
      `/api/projects/${projectId}/sensitivity`,
      { param, range: [value] },
    );
  }

  reportHtml(projectId: string): Promise<string> {
    return this.sendText("GET", `/api/projects/${projectId}/report`);
  }

  private async sendJson<T>(
    method: string,
    path: string,
    body: unknown,
  ): Promise<T> {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw await parseErrorResponse(response);
    }
    return (await response.json()) as T;
  }

  private async sendText(method: string, path: string): Promise<string> {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, { method });
    if (!response.ok) {
      throw await parseErrorResponse(response);
    }
    return response.text();
  }
}
