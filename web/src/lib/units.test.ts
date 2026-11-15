import { expect, test } from "vitest";
import { sites } from "../../tests/fixtures/recorded.ts";
import { unitGroups } from "./units";

test("school-wide and administrative units come first, then each college", () => {
  const groups = unitGroups(sites, "", "school", "other");

  expect(groups[0]!.title).toBe("school");
  expect(groups[0]!.sites.every((site) => site.kind !== "academic")).toBe(true);
  expect(groups.slice(1).every((group) => group.sites.every((site) => site.college === group.title))).toBe(true);
});

test("a query keeps the matching units and drops empty groups", () => {
  const unit = sites.find((site) => site.id === 1017)!.unit;
  const groups = unitGroups(sites, ` ${unit} `, "school", "other");

  expect(groups.map((group) => group.sites.map((site) => site.id))).toEqual([[1017]]);
  expect(unitGroups(sites, "no such unit", "school", "other")).toEqual([]);
});

test("an academic unit without a college goes under the other group", () => {
  const lone = { ...sites.find((site) => site.id === 1017)!, college: null };

  expect(unitGroups([lone], "", "school", "other")).toEqual([{ title: "other", sites: [lone] }]);
});
