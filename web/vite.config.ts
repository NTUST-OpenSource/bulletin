import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [svelte()],
  // Vitest runs in Node; components need Svelte's browser build to mount in jsdom.
  resolve: process.env["VITEST"] ? { conditions: ["browser"] } : {},
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.ts"],
    coverage: {
      include: ["src/lib/**/*.ts"],
      thresholds: { statements: 85, branches: 85, functions: 85, lines: 85 },
    },
  },
});
