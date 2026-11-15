// Requirement: Search (web-frontend): the query's limits, and the filters in the page's address.
import { describe, expect, test } from "vitest";
import { NO_FILTERS } from "./api";
import { addressQuery, readAddress, terms } from "./address";

describe("Search", () => {
  test("a query keeps its first ten words and at most 100 characters", () => {
    expect(terms("  scholarship   2026 ")).toBe("scholarship 2026");
    expect(terms("a b c d e f g h i j k l")).toBe("a b c d e f g h i j");
    expect(terms("x".repeat(150))).toBe("x".repeat(100));
    expect(terms("   ")).toBe("");
  });

  test("the query stays in the page's address until cleared, with the topic and unit", () => {
    const filters = { q: "scholarship 2026", titleOnly: true, topic: "scholarships", unit: 1053 };
    expect(new URLSearchParams(addressQuery(filters)).get("q")).toBe("scholarship 2026");
    expect(readAddress(`?${addressQuery(filters)}`)).toEqual(filters);
    expect(addressQuery({ ...NO_FILTERS, topic: "scholarships" })).toBe("topic=scholarships");
    expect(addressQuery(NO_FILTERS)).toBe("");
  });

  test("unreadable filters in the address read as unset", () => {
    expect(readAddress("?unit=abc&in=body&q=%20%20&topic=")).toEqual(NO_FILTERS);
    expect(readAddress("?unit=-3")).toEqual(NO_FILTERS);
    expect(readAddress("?in=title")).toEqual(NO_FILTERS); // titles only means nothing without a query
    expect(readAddress(`?q=${"w ".repeat(20)}`)).toEqual({ ...NO_FILTERS, q: "w w w w w w w w w w" });
  });
});
