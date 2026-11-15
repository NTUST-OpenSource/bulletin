import { mount, unmount } from "svelte";
import { expect, test, vi } from "vitest";
import App from "./App.svelte";

test("the app mounts", () => {
  // jsdom has no matchMedia; a reader who prefers reduced motion gets the brand at rest.
  vi.stubGlobal("matchMedia", () => ({ matches: true }));
  const app = mount(App, { target: document.body });
  expect(document.querySelector("a.brand")?.textContent).toBe("bulletin.");
  void unmount(app);
  vi.unstubAllGlobals();
});
