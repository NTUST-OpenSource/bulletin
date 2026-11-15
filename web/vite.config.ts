import { svelte } from "@sveltejs/vite-plugin-svelte";
import type { Plugin } from "vite";
import { defineConfig } from "vitest/config";
import { NO_FRAMES, POLICY } from "./src/lib/csp.ts";

// Development keeps Vite's inline client working, so only the build carries the policy.
const policy: Plugin = {
  name: "bulletin-policy",
  apply: "build",
  transformIndexHtml: () => [
    { tag: "meta", attrs: { "http-equiv": "Content-Security-Policy", content: POLICY }, injectTo: "head-prepend" },
  ],
};

// BULLETIN_API, such as https://bulletin.ntust.org or a local `bulletin serve`, answers /api for
// `vite` and `vite preview`; without it, as in the tests, nothing leaves the machine.
const api = process.env["BULLETIN_API"];

export default defineConfig({
  plugins: [svelte(), policy],
  server: api ? { proxy: { "/api": { target: api, changeOrigin: true } } } : {},
  preview: { headers: { "Content-Security-Policy": NO_FRAMES } },
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
