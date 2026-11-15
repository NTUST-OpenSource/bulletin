// Requirement: The stream (web-frontend): days, headings and source lines.
import { describe, expect, test } from "vitest";
import { articles, sites, stream } from "../../tests/fixtures/recorded.ts";
import type { Item } from "./api";
import { byDay, heading, marked, source, today } from "./stream";

const item = (id: number, day: string): Item => ({ ...stream.first.items[0]!, id, day });

describe("byDay", () => {
  test("items group by day in order", () => {
    const days = byDay([item(3, "2026-11-15"), item(2, "2026-11-13"), item(1, "2026-11-13")]);

    expect(days.map((d) => [d.day, d.items.map((i) => i.id)])).toEqual([
      ["2026-11-15", [3]],
      ["2026-11-13", [2, 1]],
    ]);
  });

  test("the recorded pages make one group per day", () => {
    const days = byDay([...stream.first.items, ...stream.second.items]);

    expect(new Set(days.map((d) => d.day)).size).toBe(days.length);
  });
});

describe("heading", () => {
  test("today, yesterday and other days of this year", () => {
    expect(heading("2026-11-15", "2026-11-15")).toEqual({ date: 15, month: 11, year: null, weekday: 0, relative: "today" });
    expect(heading("2026-11-14", "2026-11-15")).toMatchObject({ relative: "yesterday", weekday: 6 });
    expect(heading("2026-11-13", "2026-11-15")).toMatchObject({ relative: null, weekday: 5, year: null });
  });

  test("another year adds the year", () => {
    expect(heading("2025-12-31", "2026-01-02")).toMatchObject({ year: 2025, month: 12, date: 31, weekday: 3 });
  });
});

describe("source", () => {
  const followed = { sites: [1045, 1049], hiddenBoards: [] };

  test("the publisher comes first", () => {
    expect(source(articles[1], sites, followed)).toBe(articles[1].publisher);
  });

  test("else the first followed board that is not hidden", () => {
    const on = { ...articles[16], publisher: null };
    const name = (key: string) => sites.flatMap((s) => s.boards).find((b) => b.key === key)!.name;

    expect(source(on, sites, followed)).toBe(name("1045-1391"));
    expect(source(on, sites, { ...followed, hiddenBoards: ["1045-1391"] })).toBe(name("1049-1"));
    expect(source(on, sites, { sites: [], hiddenBoards: [] })).toBe(name("1045-1391"));
  });

  test("a board the sites list does not hold names nothing", () => {
    expect(source({ ...articles[16], publisher: null, boards: ["9999-1"] }, sites, followed)).toBe("");
  });
});

test("today is counted in Taipei", () => {
  expect(today(new Date("2026-11-15T16:30:00Z"))).toBe("2026-11-16");
  expect(today(new Date("2026-11-15T15:30:00Z"))).toBe("2026-11-15");
});

describe("Search", () => {
  test("a result marks each word of the query, ignoring case", () => {
    expect(marked("Scholarship for AI students", "ai SCHOLARSHIP")).toEqual([
      { text: "Scholarship", mark: true },
      { text: " for ", mark: false },
      { text: "AI", mark: true },
      { text: " students", mark: false },
    ]);
    expect(marked("a+b (c)", "+b (c")).toEqual([
      { text: "a", mark: false },
      { text: "+b", mark: true },
      { text: " ", mark: false },
      { text: "(c", mark: true },
      { text: ")", mark: false },
    ]);
    expect(marked("text", "")).toEqual([{ text: "text", mark: false }]);
  });
});
