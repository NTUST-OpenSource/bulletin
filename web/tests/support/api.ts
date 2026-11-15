// Answers /api/v1 from the recorded fixtures, in the public-api shapes.
import { readFileSync } from "node:fs";
import type { Page as Browser, Route } from "@playwright/test";
import type { Page } from "../../src/lib/api.ts";
import type { Settings } from "../../src/lib/settings.ts";
import { DEFAULTS, STORE_KEY } from "../../src/lib/settings.ts";
import { articles, sites, stream, tags } from "../fixtures/recorded.ts";

export const PDF = readFileSync(new URL("../fixtures/one-page.pdf", import.meta.url));
export const PNG = readFileSync(new URL("../fixtures/poster.png", import.meta.url));
export const DOCX = readFileSync(new URL("../fixtures/form.docx", import.meta.url));
const IMAGES = new Set(["png", "jpg", "jpeg", "gif", "webp"]);

/** When the fixtures were recorded: day headings and dates read relative to it. */
export const RECORDED = new Date("2026-11-15T12:00:00+08:00");

/** What a test changes: a status for a path, or the stream's pages. */
export type Answers = {
  fail?: Partial<Record<"sites" | "tags" | "announcements" | "article" | "files", number>>;
  pages?: (query: URLSearchParams) => Page;
  articles?: Record<number, unknown>; // answered before the recorded ones
};

/** The requests the page sent, as paths with their query strings. */
export type Sent = string[];

export async function answer(page: Browser, answers: Answers = {}): Promise<Sent> {
  const sent: Sent = [];
  // Nothing leaves the machine: other hosts, such as the school's images, answer with a fixture.
  await page.route((url) => url.hostname !== "localhost", (route) => route.fulfill({ contentType: "image/png", body: PNG }));
  const json = (route: Route, body: unknown, status = 200) =>
    route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
  await page.route("**/api/v1/**", async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname.slice("/api/v1".length);
    sent.push(`${path}${url.search}`);
    const article = /^\/announcements\/(\d+)$/.exec(path);
    const fail = answers.fail ?? {};
    if (path === "/sites") return json(route, sites, fail.sites);
    if (path === "/tags") return json(route, tags, fail.tags);
    if (path === "/announcements") {
      if (fail.announcements) return json(route, { detail: "failed" }, fail.announcements);
      const query = url.searchParams;
      const found = answers.pages?.(query) ?? (query.get("cursor") === stream.first.next ? stream.second : stream.first);
      return json(route, found);
    }
    if (article) {
      const found = answers.articles?.[Number(article[1])] ?? (articles as Record<string, unknown>)[article[1]!];
      if (fail.article || !found) return json(route, { detail: "Not Found" }, fail.article ?? 404);
      return json(route, found);
    }
    if (path.startsWith("/files/")) {
      if (fail.files) return json(route, { detail: "no file" }, fail.files);
      const extension = path.slice(path.lastIndexOf(".") + 1).toLowerCase();
      const [contentType, body] =
        extension === "docx" ? ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", DOCX]
        : IMAGES.has(extension) ? ["image/png", PNG]
        : ["application/pdf", PDF];
      return route.fulfill({ contentType, headers: { "Content-Disposition": "inline" }, body });
    }
    return json(route, { detail: "Not Found" }, 404);
  });
  return sent;
}

/** Start with saved settings, unless the page already saved others. */
export async function saved(page: Browser, settings: Partial<Settings> = {}): Promise<void> {
  await page.addInitScript(
    ([key, value]) => {
      if (localStorage.getItem(key) === null) localStorage.setItem(key, value);
    },
    [STORE_KEY, JSON.stringify({ ...DEFAULTS, ...settings })] as const,
  );
}

export const stored = (page: Browser) => page.evaluate((key) => localStorage.getItem(key), STORE_KEY);
