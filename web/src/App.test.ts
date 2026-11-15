import { mount, unmount } from "svelte";
import { expect, test } from "vitest";
import App from "./App.svelte";

test("the app mounts", () => {
  const app = mount(App, { target: document.body });
  expect(document.querySelector("a.brand")?.textContent).toBe("bulletin.");
  void unmount(app);
});
