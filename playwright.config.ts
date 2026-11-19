import { defineConfig, devices } from "@playwright/test";

// E2E landing statis hermes-monitor-kuliah — HANYA di CI (JANGAN jalankan
// di VM dev: Chromium lokal tidak bisa start di sandbox VM ini).
// Server statis disajikan job CI dengan `python3 -m http.server`.
export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: true,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:8461",
    trace: "off",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
  webServer: {
    command: "python3 -m http.server 8461 --bind 127.0.0.1",
    url: "http://127.0.0.1:8461/",
    reuseExistingServer: true,
    timeout: 20_000,
  },
});
