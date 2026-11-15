// Requirement: The stream (web-frontend).
import { expect, test } from "@playwright/test";
import { DEFAULT_SITES } from "../src/lib/settings.ts";
import { articles, stream } from "./fixtures/recorded.ts";
import { answer, saved } from "./support/api.ts";

const announcements = (sent: string[]) => sent.filter((path) => path.startsWith("/announcements?") || path === "/announcements");

test("the followed units' announcements, newest day first, under pinned day headings", async ({ page }) => {
  const sent = await answer(page);
  await saved(page);
  await page.goto("/");

  const items = page.locator("main .items > li");
  await expect(items).toHaveCount(stream.first.items.length);
  await expect(page.locator("main h2.day").first()).toContainText("15");
  await expect(page.locator("main h2.day").first()).toContainText("今天");
  await expect(page.locator("main h2.day").first()).toHaveCSS("position", "sticky");
  expect(announcements(sent)).toEqual([`/announcements?${DEFAULT_SITES.toSorted().map((id) => `site=${id}`).join("&")}`]);
  const first = items.first();
  await expect(first.locator(".sec")).toHaveText(articles[1].publisher!);
  await expect(first.locator(".title")).toHaveText(articles[1].rendition!.title);
  await expect(first.locator(".sum")).toHaveText(articles[1].rendition!.summary!);
  await expect(first.locator(".pri")).toHaveText(articles[1].unit!);
});

test("A hidden board: its announcements are not asked for", async ({ page }) => {
  const sent = await answer(page);
  await saved(page, { sites: [1049], hiddenBoards: ["1049-203"] });
  await page.goto("/");

  await expect(page.locator("main .items > li").first()).toBeVisible();
  expect(announcements(sent)).toEqual(["/announcements?board=1049-1&board=1049-204"]);
});

test("A withdrawn announcement stays with the 已刪除 mark", async ({ page }) => {
  const withdrawn = { ...stream.first.items[1]!, id: 615, withdrawn_at: articles[615].withdrawn_at };
  await answer(page, { pages: () => ({ items: [stream.first.items[0]!, withdrawn], next: null }) });
  await saved(page);
  await page.goto("/");

  await expect(page.locator("main .items > li").nth(1).locator(".gone")).toHaveText("已刪除");
  await expect(page.locator("main .items > li").first().locator(".gone")).toHaveCount(0);
});

test("No rewrite yet: the school's title and no summary", async ({ page }) => {
  await answer(page);
  await saved(page);
  await page.goto("/");

  const raw = page.locator("main .items > li", { hasText: articles[10].title });
  await expect(raw.locator(".title")).toHaveText(articles[10].title);
  await expect(raw.locator(".sum")).toHaveCount(0);
});

test("a reader who prefers the school's version sees its titles", async ({ page }) => {
  await answer(page);
  await saved(page, { prefer: "raw" });
  await page.goto("/");

  await expect(page.locator("main .items > li").first().locator(".title")).toHaveText(articles[1].title);
  await expect(page.locator("main .sum")).toHaveCount(0);
});

test("Nothing followed: the stream asks for units and requests no announcements", async ({ page }) => {
  const sent = await answer(page);
  await saved(page, { sites: [] });
  await page.goto("/");

  await expect(page.getByText("還沒有關注的單位")).toBeVisible();
  await page.getByRole("button", { name: "選擇單位" }).click();
  await expect(page.getByRole("dialog", { name: "關注的單位" })).toBeVisible();
  expect(announcements(sent)).toEqual([]);
});

test("after the first visit the stream shows the picked units", async ({ page }) => {
  const sent = await answer(page);
  await page.goto("/");

  await page.getByRole("button", { name: "電子工程系" }).click();
  await page.getByRole("button", { name: "下一步" }).click();
  await page.getByRole("button", { name: "開始使用" }).click();

  await expect(page.locator("main .items > li").first()).toBeVisible();
  expect(announcements(sent).at(-1)).toContain("site=1017");
});
