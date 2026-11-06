// HTTP response helpers for client stubbing: tests pass a vi.fn handler
// straight into `new PowerHubXClient(fetchMock)`, so no global fetch is
// touched and each test controls its own routing.

import { vi } from "vitest";

export type FetchHandler = (
  input: string | URL | Request,
  init?: RequestInit,
) => Promise<Response>;

export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export function htmlResponse(html: string, status = 200): Response {
  return new Response(html, {
    status,
    headers: { "Content-Type": "text/html" },
  });
}

export function mockFetch(handler: FetchHandler): ReturnType<typeof vi.fn> {
  return vi.fn((input: string | URL | Request, init?: RequestInit) =>
    handler(input, init),
  );
}

/** Request body of a stubbed call, parsed from JSON. */
export function requestBody(call: unknown[]): unknown {
  const init = call[1] as RequestInit | undefined;
  const raw = init?.body;
  return typeof raw === "string" ? (JSON.parse(raw) as unknown) : undefined;
}
