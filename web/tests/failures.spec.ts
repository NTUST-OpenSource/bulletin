// Requirement: Failures (web-frontend).
import { expect, type Page, test } from "@playwright/test";
import { stream } from "./fixtures/recorded.ts";
import { answer, saved } from "./support/api.ts";

const items = (page: Page) => page.locator("main .items > li");
const retry = (page: Page) => page.getByRole("button", { name: "重試" });
const down = (page: Page, pattern: string) =>
  page.route(pattern, (route) => route.fulfill({ status: 503, contentType: "application/json", body: "{}" }));

test("The API is down: the loaded items stay and a retry button appears below them", async ({ page }) => {
  await answer(page);
  await down(page, "**/api/v1/announcements?*cursor=*");
  await saved(page);
  await page.goto("/");
  await expect(items(page)).toHaveCount(stream.first.items.length);

  await items(page).last().scrollIntoViewIfNeeded();

  await expect(page.getByText("無法載入公告")).toBeVisible();
  await expect(items(page)).toHaveCount(stream.first.items.length);
  const last = (await items(page).last().boundingBox())!;
  expect((await retry(page).boundingBox())!.y).toBeGreaterThan(last.y);
  await page.unroute("**/api/v1/announcements?*cursor=*");
  await retry(page).click();
  await expect(items(page)).toHaveCount(stream.first.items.length + stream.second.items.length);
  await expect(page.getByText("無法載入公告")).toHaveCount(0);
});

test("the first page or the lists failing say so, and a retry loads them", async ({ page }) => {
  await answer(page);
  await down(page, "**/api/v1/sites");
  await saved(page);
  await page.goto("/");

  await expect(page.getByText("無法載入公告")).toBeVisible();
  await page.unroute("**/api/v1/sites");
  await down(page, "**/api/v1/announcements?*");
  const refused = page.waitForResponse((answer) => answer.url().includes("/api/v1/announcements?") && answer.status() === 503);
  await retry(page).click();
  await refused;
  await expect(page.getByText("無法載入公告")).toBeVisible();
  await page.unroute("**/api/v1/announcements?*");
  await retry(page).click();

  await expect(items(page)).toHaveCount(stream.first.items.length);
});

test("Too many searches: the page says to try again shortly and keeps the query", async ({ page }) => {
  await answer(page);
  await page.route("**/api/v1/announcements?*q=*", (route) =>
    route.fulfill({ status: 429, contentType: "application/json", body: '{"detail":"too many searches"}' }),
  );
  await saved(page);
  await page.goto("/");
  await expect(items(page).first()).toBeVisible();
  await page.getByRole("banner").getByRole("button", { name: "搜尋" }).click();

  await page.getByRole("searchbox", { name: "搜尋" }).fill("獎學金");

  await expect(page.getByText("搜尋太頻繁，請稍後再試")).toBeVisible();
  await expect(page.getByRole("searchbox", { name: "搜尋" })).toHaveValue("獎學金");
  expect(new URL(page.url()).searchParams.get("q")).toBe("獎學金");
});

test("An unknown article: the page says it was not found, over the stream", async ({ page }) => {
  await answer(page);
  await saved(page);
  await page.goto("/a/999999");

  await expect(page.getByRole("dialog")).toContainText("找不到這則公告");
  await expect(items(page).first()).toBeAttached();
});

test("an article that cannot be loaded says so, and a retry loads it", async ({ page }) => {
  await answer(page);
  await down(page, "**/api/v1/announcements/1");
  await saved(page);
  await page.goto("/a/1");

  await expect(page.getByRole("dialog")).toContainText("無法載入公告");
  await page.unroute("**/api/v1/announcements/1");
  await page.getByRole("dialog").getByRole("button", { name: "重試" }).click();

  await expect(page.getByRole("dialog").getByRole("heading", { level: 1 })).toBeVisible();
});
