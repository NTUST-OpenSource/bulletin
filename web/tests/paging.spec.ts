// Requirement: Paging and new announcements (web-frontend).
import { expect, type Page as Browser, test } from "@playwright/test";
import type { Item, Page } from "../src/lib/api.ts";
import { articles, stream } from "./fixtures/recorded.ts";
import { answer, saved } from "./support/api.ts";

const FIVE_MINUTES = 5 * 60 * 1000;
const ids = (page: Browser) => page.locator("main .items > li").evaluateAll((items) => items.map((li) => li.dataset["id"]));
const fresh = (id: number, title: string): Item => ({ ...stream.first.items[0]!, id, title, rendition: null, publisher: null });

/** The first page, then `polled` for every later check of the first page. */
async function answering(page: Browser, polled: (check: number) => Page) {
  let checks = -1;
  return answer(page, {
    pages: (query) => {
      if (query.get("cursor") === stream.first.next) return stream.second;
      if (query.has("cursor")) return polled(-1);
      checks += 1;
      return checks === 0 ? stream.first : polled(checks);
    },
  });
}

test("Reaching the end of a page: the next page loads below without a repeated item", async ({ page }) => {
  test.fail(true, "Paging and new announcements");
  await answer(page);
  await saved(page);
  await page.goto("/");
  await expect(page.locator("main .items > li")).toHaveCount(stream.first.items.length);

  await page.locator("main .items > li").last().scrollIntoViewIfNeeded();

  await expect(page.locator("main .items > li")).toHaveCount(stream.first.items.length + stream.second.items.length);
  const shown = await ids(page);
  expect(new Set(shown).size).toBe(shown.length);
});

test("A new announcement while reading: it appears in its place and the read item stays put", async ({ page }) => {
  test.fail(true, "Paging and new announcements");
  await page.clock.install();
  const arriving = fresh(9001, "新公告");
  await answering(page, () => ({ items: [arriving, ...stream.first.items.slice(0, 29)], next: stream.first.next }));
  await saved(page);
  await page.goto("/");
  const read = page.locator("main .items > li").nth(15);
  await read.scrollIntoViewIfNeeded();
  await page.mouse.wheel(0, 200);
  const before = (await read.boundingBox())!.y;

  await page.clock.fastForward(FIVE_MINUTES);

  await expect(page.locator('main .items > li[data-id="9001"]')).toBeAttached();
  expect((await ids(page))[0]).toBe("9001");
  await page.clock.fastForward(2000); // the arrival's animation
  expect(Math.abs((await read.boundingBox())!.y - before)).toBeLessThan(2);
});

test("A rewrite arrives: the check shows its rewritten title", async ({ page }) => {
  test.fail(true, "Paging and new announcements");
  await page.clock.install();
  const raw = stream.first.items.findIndex((i) => i.id === 10);
  const rewritten = { ...stream.first.items[raw]!, rendition: { title: "改寫後的標題", summary: "摘要", deadline: null } };
  await answering(page, () => ({ items: stream.first.items.with(raw, rewritten), next: stream.first.next }));
  await saved(page);
  await page.goto("/");
  await expect(page.locator('main .items > li[data-id="10"] .title')).toHaveText(articles[10].title);

  await page.clock.fastForward(FIVE_MINUTES);

  await expect(page.locator('main .items > li[data-id="10"] .title')).toHaveText("改寫後的標題");
});

test("Many new announcements: every one appears, without a gap before the shown ones", async ({ page }) => {
  test.fail(true, "Paging and new announcements");
  await page.clock.install();
  const many = Array.from({ length: 30 }, (_, n) => fresh(9100 - n, `新公告 ${n}`));
  const more = Array.from({ length: 5 }, (_, n) => fresh(9050 - n, `新公告 ${30 + n}`));
  let check = 0;
  await answer(page, {
    pages: (query) => {
      if (query.get("cursor") === "many") return { items: [...more, ...stream.first.items.slice(0, 25)], next: "after" };
      if (query.has("cursor")) return stream.second;
      check += 1;
      return check === 1 ? stream.first : { items: many, next: "many" };
    },
  });
  await saved(page);
  await page.goto("/");
  await expect(page.locator("main .items > li")).toHaveCount(30);

  await page.clock.fastForward(FIVE_MINUTES);

  await expect(page.locator("main .items > li")).toHaveCount(65);
  const shown = await ids(page);
  expect(shown.slice(0, 36)).toEqual([...many, ...more, stream.first.items[0]!].map((i) => String(i.id)));
});

test("A hidden tab: no check is sent until it is visible again", async ({ page }) => {
  test.fail(true, "Paging and new announcements");
  await page.clock.install();
  const sent = await answer(page);
  await saved(page);
  await page.goto("/");
  await expect(page.locator("main .items > li").first()).toBeVisible();
  const visibility = (state: "hidden" | "visible") =>
    page.evaluate((value) => {
      Object.defineProperty(document, "visibilityState", { value, configurable: true });
      document.dispatchEvent(new Event("visibilitychange"));
    }, state);
  const checks = () => sent.filter((path) => path.startsWith("/announcements?") && !path.includes("cursor")).length;

  await visibility("hidden");
  await page.clock.fastForward(3 * FIVE_MINUTES);
  expect(checks()).toBe(1);
  await visibility("visible");

  await expect.poll(checks).toBe(2);
});
