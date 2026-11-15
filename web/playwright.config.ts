import { defineConfig, devices } from "@playwright/test";

const PORT = 4173;

// The built page with its production policy, at desktop width and at 375 px.
export default defineConfig({
  testDir: "tests",
  forbidOnly: !!process.env["CI"],
  retries: process.env["CI"] ? 1 : 0,
  // Full Chromium: the default headless shell has no PDF viewer.
  // A missing element fails its action instead of timing the test out, so test.fail() holds.
  use: { baseURL: `http://localhost:${PORT}`, channel: "chromium", actionTimeout: 5_000 },
  webServer: {
    command: `bun run build && bun run preview --port ${PORT} --strictPort`,
    port: PORT,
    reuseExistingServer: !process.env["CI"],
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } } },
    {
      name: "phone",
      use: { ...devices["Desktop Chrome"], viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true },
    },
  ],
});
