// The stream query from settings (design.md) and the API's fetches.
import { afterEach, describe, expect, test, vi } from "vitest";
import { sites } from "../../tests/fixtures/recorded.ts";
import { ApiError, type Filters, get, NO_FILTERS, streamQuery } from "./api";
import { DEFAULT_SITES, DEFAULT_TOPICS } from "./settings";

const DEFAULTS: { sites: number[]; hiddenBoards: string[] } = { sites: DEFAULT_SITES, hiddenBoards: [] };
const query = (settings = DEFAULTS, filters: Partial<Filters> = {}) =>
  streamQuery(settings, sites, DEFAULT_TOPICS, { ...NO_FILTERS, ...filters });

describe("streamQuery", () => {
  test("the default units, sorted", () => {
    expect(query()).toBe("site=1045&site=1049&site=1051&site=1053&site=1060&site=1070");
  });

  test("a hidden board lists the site's other boards instead of the site", () => {
    const params = new URLSearchParams(query({ sites: [1049], hiddenBoards: ["1049-203"] })!);

    expect(params.getAll("board")).toEqual(["1049-1", "1049-204"]);
    expect(params.has("site")).toBe(false);
  });

  test("units the API does not list are left out, and none left asks for nothing", () => {
    expect(query({ sites: [1049, 9999], hiddenBoards: [] })).toBe("site=1049");
    expect(query({ sites: [9999], hiddenBoards: [] })).toBeNull();
    expect(query({ sites: [1049], hiddenBoards: ["1049-1", "1049-203", "1049-204"] })).toBeNull();
  });

  test("the unit menu narrows to one unit, its hidden boards still out", () => {
    const params = new URLSearchParams(query({ sites: [1045, 1049], hiddenBoards: ["1049-203"] }, { unit: 1049 })!);

    expect(params.getAll("board")).toEqual(["1049-1", "1049-204"]);
    expect(params.has("site")).toBe(false);
  });

  test("a topic chip adds its tag; an unknown topic is left out", () => {
    expect(query({ sites: [1049], hiddenBoards: [] }, { topic: "scholarships" })).toBe(
      "site=1049&tag=topic%3Ascholarships",
    );
    expect(query({ sites: [1049], hiddenBoards: [] }, { topic: "weather" })).toBe("site=1049");
  });

  test("search drops the followed units and keeps the chip and the unit menu", () => {
    expect(query(DEFAULTS, { q: "113-1 (OR", titleOnly: true, topic: "fees" })).toBe(
      "tag=topic%3Afees&q=113-1+%28OR&in=title",
    );
    expect(query(DEFAULTS, { q: "x", unit: 1049 })).toBe("site=1049&q=x");
    expect(query({ sites: [], hiddenBoards: [] }, { q: "x" })).toBe("q=x");
  });
});

describe("get", () => {
  afterEach(() => vi.unstubAllGlobals());

  test("answers parse as JSON; a fresh read revalidates", async () => {
    const fetch = vi.fn(async () => new Response('{"ok":true}'));
    vi.stubGlobal("fetch", fetch);

    expect(await get("/sites", true)).toEqual({ ok: true });
    expect(fetch).toHaveBeenCalledWith("/api/v1/sites", { cache: "no-cache" });
  });

  test("a status other than 200, or no answer, is an ApiError", async () => {
    vi.stubGlobal("fetch", async () => new Response("", { status: 429 }));
    await expect(get("/announcements")).rejects.toEqual(new ApiError(429));

    vi.stubGlobal("fetch", async () => {
      throw new TypeError("offline");
    });
    await expect(get("/announcements")).rejects.toMatchObject({ status: 0 });
  });
});
