// Requirement: Settings export and import (web-frontend).
import { expect, test } from "vitest";
import { DEFAULTS, readImport, settingsLink, UnreadableSettings } from "./settings";

const MINE = { ...DEFAULTS, theme: "dark" as const, sites: [1017, 1045], hiddenBoards: ["1049-203"] };

test.fails("a settings link carries the settings after #s=", () => {
  const link = settingsLink("https://bulletin.ntust.org", MINE);

  expect(link).toMatch(/^https:\/\/bulletin\.ntust\.org\/#s=[\w-]+$/);
  expect(readImport(link)).toEqual(MINE);
});

test.fails("pasted JSON imports, as copied or hand-edited", () => {
  expect(readImport(JSON.stringify(MINE, null, 2))).toEqual(MINE);
  expect(readImport(`  {"version": 1, "theme": "light"}\n`)).toEqual({ ...DEFAULTS, theme: "light" });
});

test.fails("Unreadable input: an error, and nothing to apply", () => {
  for (const text of ["hello", "{broken", '{"version": 2}', "[1, 2]", "https://bulletin.ntust.org/#s=%%%", "#s=bm90IGpzb24"]) {
    expect(() => readImport(text), text).toThrow(UnreadableSettings);
  }
});
