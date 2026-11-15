// Requirement: Paging and new announcements (web-frontend).
import { expect, test } from "vitest";
import { stream } from "../../tests/fixtures/recorded.ts";
import type { Item } from "./api";
import { appended, merged } from "./stream";

const item = (id: number, day: string, title = `t${id}`): Item => ({ ...stream.first.items[0]!, id, day, title });
const ids = (items: Item[]) => items.map((i) => i.id);

const SHOWN = [item(9, "2026-11-15"), item(7, "2026-11-14"), item(5, "2026-11-13")];

test("Reaching the end of a page: the next page adds no item twice", () => {
  expect(ids(appended(SHOWN, [item(5, "2026-11-13"), item(4, "2026-11-13"), item(3, "2026-11-12")]))).toEqual([
    9, 7, 5, 4, 3,
  ]);
});

test("A new announcement goes in its place, and a rewrite replaces the shown copy", () => {
  const result = merged(SHOWN, [item(10, "2026-11-15"), item(9, "2026-11-15", "rewritten"), item(8, "2026-11-14")], false);

  expect(ids(result.items)).toEqual([10, 9, 8, 7, 5]);
  expect(result.items[1]!.title).toBe("rewritten");
  expect(result).toMatchObject({ overlap: true, added: [10, 8] });
});

test("unseen items past the last shown one wait for its page, unless every page is shown", () => {
  expect(ids(merged(SHOWN, [item(6, "2026-11-14"), item(2, "2026-11-12")], false).items)).toEqual([9, 7, 6, 5]);
  expect(ids(merged(SHOWN, [item(6, "2026-11-14"), item(2, "2026-11-12")], true).items)).toEqual([9, 7, 6, 5, 2]);
});

test("a page of new items alone does not overlap", () => {
  const result = merged(SHOWN, [item(12, "2026-11-16"), item(11, "2026-11-16")], false);

  expect(result.overlap).toBe(false);
  expect(ids(result.items)).toEqual([12, 11, 9, 7, 5]);
});
