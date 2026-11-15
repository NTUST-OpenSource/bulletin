// Requirement: Article view (web-frontend), and First visit's "A new reader opens an article link".
import { expect, type Page, test } from "@playwright/test";
import { articles, sites, stream } from "./fixtures/recorded.ts";
import { answer, RECORDED, saved } from "./support/api.ts";

const dialog = (page: Page) => page.getByRole("dialog");
const item = (page: Page, id: number) => page.locator(`main .items > li[data-id="${id}"] a`);

test("opening an item shows the rewrite over the stream under its own path", async ({ page }) => {
  await page.clock.setFixedTime(RECORDED);
  await answer(page);
  await saved(page);
  await page.goto("/");

  await item(page, 1).click();

  await expect(dialog(page).getByRole("heading", { level: 1 })).toHaveText(articles[1].rendition!.title);
  await expect(dialog(page).locator(".lede")).toHaveText(articles[1].rendition!.summary!);
  await expect(dialog(page).locator(".body").getByRole("heading", { name: "招生說明會資訊" })).toBeVisible();
  await expect(dialog(page).locator(".when")).toContainText("11月15日 週日");
  expect(new URL(page.url()).pathname).toBe("/a/1");
});

test("Back to the stream: the article closes and the stream is where it was", async ({ page }) => {
  await answer(page);
  await saved(page);
  await page.goto("/");
  await item(page, 16).scrollIntoViewIfNeeded();
  await expect(page.locator("main .items > li")).toHaveCount(stream.first.items.length + stream.second.items.length);
  await item(page, 16).scrollIntoViewIfNeeded(); // the second page made room below it
  const y = await page.evaluate(() => scrollY);

  await item(page, 16).click();
  await expect(dialog(page)).toBeVisible();
  await page.goBack();

  await expect(dialog(page)).toHaveCount(0);
  expect(await page.evaluate(() => scrollY)).toBe(y);
  expect(new URL(page.url()).pathname).toBe("/");
});

test("Esc and the close button close the article", async ({ page }) => {
  await answer(page);
  await saved(page);
  await page.goto("/");

  await item(page, 1).click();
  await expect(dialog(page)).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog(page)).toHaveCount(0);
  await item(page, 1).click();
  await dialog(page).getByRole("button", { name: "關閉" }).click();

  await expect(dialog(page)).toHaveCount(0);
  expect(new URL(page.url()).pathname).toBe("/");
});

test("Closing after a direct link: the stream shows and the reader stays on bulletin", async ({ page }) => {
  await answer(page);
  await saved(page);
  await page.goto("/a/1");

  await dialog(page).getByRole("button", { name: "關閉" }).click();

  await expect(page.locator("main .items > li").first()).toBeVisible();
  expect(new URL(page.url()).pathname).toBe("/");
});

test("The school's version: the school's text and images, sanitized, from the article's menu", async ({ page }) => {
  const school = {
    ...articles[6],
    body_html:
      '<style>p{color:red}</style><p style="color:red">學校原文</p><img data-src="/var/file/a.jpg" alt="海報">' +
      "<script>window.hacked = true</script>",
  };
  await answer(page, { articles: { 6: school } });
  await page.route("https://*.ntust.edu.tw/var/file/**", (route) => route.fulfill({ status: 404 }));
  await saved(page);
  await page.goto("/a/6");

  await dialog(page).getByRole("button", { name: "更多" }).click();
  await page.getByRole("menuitem", { name: "顯示原文" }).click();

  await expect(dialog(page).locator(".body p")).toHaveText("學校原文");
  await expect(dialog(page).locator(".body p")).not.toHaveAttribute("style");
  await expect(dialog(page).locator(".body img")).toHaveAttribute("src", /^https:\/\/.*\/var\/file\/a\.jpg$/);
  expect(await page.evaluate(() => "hacked" in window)).toBe(false);
  await dialog(page).getByRole("button", { name: "更多" }).click();
  await expect(page.getByRole("menuitem", { name: "顯示改寫" })).toBeVisible();
});

test("a reader who prefers the school's version gets it first", async ({ page }) => {
  await answer(page, { articles: { 6: { ...articles[6], body_html: "<p>學校原文</p>" } } });
  await saved(page, { prefer: "raw" });
  await page.goto("/a/6");

  await expect(dialog(page).locator(".body p")).toHaveText("學校原文");
  await expect(dialog(page).getByRole("heading", { level: 1 })).toHaveText(articles[6].title);
});

test("a withdrawn article says so after its day and unit", async ({ page }) => {
  await page.clock.setFixedTime(RECORDED);
  await answer(page);
  await saved(page);
  await page.goto("/a/615");

  await expect(dialog(page).locator(".when")).toHaveText(/^2月10日 週二 · \S+ · 已刪除$/);
});

test("A plain-text URL: the article shows it as a link", async ({ page }) => {
  await answer(page, { articles: { 6: { ...articles[6], body_html: "<p>詳見 https://www.ntust.edu.tw/x</p>" } } });
  await saved(page, { prefer: "raw" });
  await page.goto("/a/6");

  await expect(dialog(page).getByRole("link", { name: "https://www.ntust.edu.tw/x" })).toHaveAttribute(
    "href",
    "https://www.ntust.edu.tw/x",
  );
});

test("A cross-post's link: the announcement it copies opens under its own path", async ({ page }) => {
  await answer(page);
  await saved(page);
  await page.goto("/a/794");

  await expect(dialog(page).getByRole("heading", { level: 1 })).toHaveText(articles[1].rendition!.title);
  expect(new URL(page.url()).pathname).toBe("/a/1");
});

test("A link item: its link opens and no empty article is shown", async ({ page }) => {
  const link = articles[2533];
  await answer(page, { pages: () => ({ items: [{ ...stream.first.items[0]!, ...link }], next: null }) });
  await page.route(link.url, (route) => route.fulfill({ contentType: "text/html", body: "<title>school</title>" }));
  await saved(page);
  await page.goto("/");

  await expect(item(page, 2533)).toHaveAttribute("href", link.url);
  await expect(item(page, 2533)).toHaveAttribute("target", "_blank");
  await page.goto("/a/2533");

  await expect(page).toHaveURL(link.url);
});

test("a topic chip closes the article and filters the stream", async ({ page }) => {
  const sent = await answer(page, {});
  await saved(page);
  await page.goto("/a/1");

  await dialog(page).getByRole("button", { name: "招生" }).click();

  await expect(dialog(page)).toHaveCount(0);
  await expect.poll(() => sent.at(-1)).toContain("tag=topic%3Aadmissions");
  expect(articles[1].tags.topic).toContain("admissions");
});

test("A new reader opens an article link: the article shows first and the unit picker follows", async ({ page }) => {
  await answer(page);
  await page.goto("/a/1");

  await expect(dialog(page).getByRole("heading", { level: 1 })).toHaveText(articles[1].rendition!.title);
  await dialog(page).getByRole("button", { name: "關閉" }).click();

  await expect(page.getByRole("dialog", { name: "你在哪個系所？" })).toBeVisible();
  expect(sites.length).toBeGreaterThan(0);
});
