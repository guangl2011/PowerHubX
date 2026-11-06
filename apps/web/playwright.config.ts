import { defineConfig, devices } from "@playwright/test";

// D3 E2E (spec art_Xihp9Qa2): one webServer pair per run — the Vite dev
// server (which proxies /api) and the FastAPI backend it proxies to. The
// backend's SQLite file goes to a scratch path so runs never touch repo state.
const apiCommand =
  "POWERHUBX_DB_PATH=${POWERHUBX_DB_PATH:-/tmp/powerhubx-e2e.db} uvicorn api.main:app --port 8000";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: [
    {
      command: apiCommand,
      url: "http://localhost:8000/healthz",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: "npm run dev",
      url: "http://localhost:5173",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
});
