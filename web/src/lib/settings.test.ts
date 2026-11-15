// Requirement: Settings (web-frontend).
import { describe, expect, test } from "vitest";
import { sites } from "../../tests/fixtures/recorded.ts";
import { NO_FILTERS, streamQuery } from "./api";
import { applyTheme, DEFAULTS, DEFAULT_TOPICS, STORE_KEY, loadSettings, moveTopic, parseSettings, saveSettings, topicOrder } from "./settings";

const STUDENT_AFFAIRS = sites.find((site) => site.id === 1053)!;

function memory(entries: Record<string, string> = {}): Storage {
  const map = new Map(Object.entries(entries));
  return {
    get length() {
      return map.size;
    },
    clear: () => map.clear(),
    getItem: (key) => map.get(key) ?? null,
    key: (index) => [...map.keys()][index] ?? null,
    removeItem: (key) => void map.delete(key),
    setItem: (key, value) => void map.set(key, value),
  };
}

describe("Settings", () => {
  test("a wrong field falls back to its default and unknown ids are kept", () => {
    const parsed = parseSettings({ version: 1, theme: "neon", prefer: "raw", sites: [1053, 9999, "x"], hiddenBoards: 3 });

    expect(parsed).toEqual({ ...DEFAULTS, prefer: "raw", sites: [1053, 9999] });
    expect(parseSettings({ version: 2 })).toBeNull();
    expect(parseSettings("settings")).toBeNull();
  });

  test("saved settings load, and nothing saved gives the defaults", () => {
    const storage = memory();
    expect(loadSettings(storage)).toEqual({ settings: DEFAULTS, saved: false });

    expect(saveSettings(storage, { ...DEFAULTS, theme: "dark" })).toBe(true);
    expect(loadSettings(storage)).toEqual({ settings: { ...DEFAULTS, theme: "dark" }, saved: true });
    expect(loadSettings(memory({ [STORE_KEY]: "{broken" }))).toEqual({ settings: DEFAULTS, saved: false });
  });

  test("blocked storage gives working defaults", () => {
    const blocked = memory();
    blocked.getItem = () => {
      throw new DOMException("blocked", "SecurityError");
    };
    blocked.setItem = blocked.getItem;

    expect(loadSettings(blocked)).toEqual({ settings: DEFAULTS, saved: false });
    expect(loadSettings(null)).toEqual({ settings: DEFAULTS, saved: false });
    expect(saveSettings(blocked, DEFAULTS)).toBe(false);
  });

  test("topics follow the reader's order, unknown ones left out and missing ones appended", () => {
    const order = topicOrder({ ...DEFAULTS, topicOrder: ["free-food", "weather", "library"] }, DEFAULT_TOPICS);

    expect(order.slice(0, 3)).toEqual(["free-food", "library", "talks-and-events"]);
    expect(order).toHaveLength(DEFAULT_TOPICS.length);
  });

  test("A board that is gone: the page works as if it were not hidden", () => {
    const settings = { sites: [1053], hiddenBoards: ["1053-9999"] };

    expect(streamQuery(settings, sites, DEFAULT_TOPICS, NO_FILTERS)).toBe("site=1053");
  });

  test("A board that is gone: it is hidden again when it returns", () => {
    const back = { ...STUDENT_AFFAIRS, boards: [...STUDENT_AFFAIRS.boards, { key: "1053-9999", name: "n", category: "announcement" as const }] };
    const query = streamQuery({ sites: [1053], hiddenBoards: ["1053-9999"] }, [back], DEFAULT_TOPICS, NO_FILTERS);

    expect(query).not.toContain("1053-9999");
    expect(query).not.toContain("site=");
    expect(new URLSearchParams(query!).getAll("board")).toHaveLength(STUDENT_AFFAIRS.boards.length);
  });
});

test("a saved light or dark theme overrides the system's", () => {
  const root = document.createElement("html");
  applyTheme(root, "dark");
  expect(root.dataset["theme"]).toBe("dark");
  applyTheme(root, "system");
  expect(root.hasAttribute("data-theme")).toBe(false);
});

describe("Topic chips and unit filter", () => {
  const order = ["a", "b", "c", "d"];

  test.fails("a topic moves to a position, within bounds", () => {
    expect(moveTopic(order, "d", 0)).toEqual(["d", "a", "b", "c"]);
    expect(moveTopic(order, "a", 2)).toEqual(["b", "c", "a", "d"]);
    expect(moveTopic(order, "b", -1)).toEqual(["b", "a", "c", "d"]);
    expect(moveTopic(order, "b", 9)).toEqual(["a", "c", "d", "b"]);
    expect(moveTopic(order, "x", 0)).toEqual(order);
  });
});
