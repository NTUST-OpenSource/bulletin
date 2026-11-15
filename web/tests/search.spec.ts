// Requirement: Search (web-frontend), and Context menu's follow entry for search results.
import { expect, type Page, test } from "@playwright/test";
import type { Item } from "../src/lib/api.ts";
import { sites, stream } from "./fixtures/recorded.ts";
import { answer, saved, type Sent, stored } from "./support/api.ts";

const OFFICE = sites.find((site) => site.id === 1000)!; // not among the default units
const elsewhere: Item = {
  ...stream.first.items[0]!,
  id: 9100,
  site: OFFICE.id,
  unit: OFFICE.unit,
  publisher: null,
  boards: [OFFICE.boards[1]!.key],
  title: "跨單位公告",
  rendition: null,
};
const found = { items: [elsewhere], next: null };
const searchButton = (page: Page) => page.getByRole("banner").getByRole("button", { name: "搜尋" });
const box = (page: Page) => page.getByRole("searchbox", { name: "搜尋" });
const item = (page: Page, id: number) => page.locator(`main .items > li[data-id="${id}"]`);
const searches = (sent: Sent) => sent.filter((path) => path.startsWith("/announcements?") && path.includes("q="));
const param = (path: string, name: string) => new URLSearchParams(path.split("?")[1]).getAll(name);

async function open(page: Page, pages = () => found): Promise<Sent> {
  const sent = await answer(page, { pages: (query) => (query.has("q") ? pages() : stream.first) });
  await saved(page);
  await page.goto("/");
  await expect(page.locator("main .items > li").first()).toBeVisible();
  await searchButton(page).click();
  return sent;
}

test("An unfollowed unit: a search lists an announcement found only there", async ({ page }) => {
  const sent = await open(page);

  await box(page).fill("跨單位");

  await expect(item(page, elsewhere.id)).toBeVisible();
  expect(searches(sent)).toHaveLength(1);
  expect(param(searches(sent)[0]!, "q")).toEqual(["跨單位"]);
  expect(param(searches(sent)[0]!, "site")).toEqual([]);
  expect(new URL(page.url()).searchParams.get("q")).toBe("跨單位");
});

test("a result marks the query in its title", async ({ page }) => {
  await open(page);

  await box(page).fill("單位");

  await expect(item(page, elsewhere.id).locator("mark")).toHaveText("單位");
});

test("Leaving the box: the box closes and the results stay with the query shown", async ({ page }) => {
  await open(page);
  await box(page).fill("跨單位");
  await expect(item(page, elsewhere.id)).toBeVisible();
  await page.keyboard.press("Tab"); // to the box's own titles-only toggle
  await expect(box(page)).toBeVisible();

  await page.getByRole("button", { name: "僅標題" }).blur();

  await expect(box(page)).toBeHidden();
  await expect(page.locator("main .results")).toContainText("跨單位");
  await expect(item(page, elsewhere.id)).toBeVisible();
  expect(new URL(page.url()).searchParams.get("q")).toBe("跨單位");
  await searchButton(page).click();
  await expect(box(page)).toHaveValue("跨單位");
});

test("Typing with an input method: one search after the word is committed, none while composing", async ({ page }) => {
  const sent = await open(page);
  await box(page).focus();
  const cdp = await page.context().newCDPSession(page);

  await cdp.send("Input.imeSetComposition", { text: "ㄓ", selectionStart: 1, selectionEnd: 1 });
  await cdp.send("Input.imeSetComposition", { text: "ㄓㄨㄥ", selectionStart: 3, selectionEnd: 3 });
  await page.waitForTimeout(700);
  expect(searches(sent)).toEqual([]);
  await cdp.send("Input.insertText", { text: "中" });

  await expect.poll(() => searches(sent).length).toBe(1);
  expect(param(searches(sent)[0]!, "q")).toEqual(["中"]);
  await page.waitForTimeout(700);
  expect(searches(sent)).toHaveLength(1);
});

test("a search waits for a pause in typing, and Enter searches at once", async ({ page }) => {
  const sent = await open(page);

  await box(page).pressSequentially("abc", { delay: 60 });
  await expect.poll(() => searches(sent).length).toBe(1);
  expect(param(searches(sent)[0]!, "q")).toEqual(["abc"]);
  await box(page).press("d");
  await box(page).press("Enter");

  await expect.poll(() => searches(sent).length).toBe(2);
  expect(param(searches(sent)[1]!, "q")).toEqual(["abcd"]);
  await page.waitForTimeout(700);
  expect(searches(sent)).toHaveLength(2);
});

test("a query is capped at the API's limits, and titles only adds in=title", async ({ page }) => {
  const sent = await open(page);
  await expect(box(page)).toHaveAttribute("maxlength", "100");

  await box(page).fill("a b c d e f g h i j k l");
  await expect.poll(() => searches(sent).length).toBe(1);
  await page.getByRole("button", { name: "僅標題" }).click();

  await expect.poll(() => searches(sent).length).toBe(2);
  expect(param(searches(sent)[0]!, "q")).toEqual(["a b c d e f g h i j"]);
  expect(param(searches(sent)[1]!, "in")).toEqual(["title"]);
  await expect(page.getByRole("button", { name: "僅標題" })).toHaveAttribute("aria-pressed", "true");
});

test("the address's query, scope and topic apply on load", async ({ page }) => {
  const sent = await answer(page, { pages: () => found });
  await saved(page);
  await page.goto(`/?q=${encodeURIComponent("跨單位")}&in=title&topic=scholarships`);

  await expect(item(page, elsewhere.id)).toBeVisible();
  const first = sent.find((path) => path.startsWith("/announcements?"))!;
  expect(param(first, "q")).toEqual(["跨單位"]);
  expect(param(first, "in")).toEqual(["title"]);
  expect(param(first, "tag")).toEqual(["topic:scholarships"]);
  await expect(page.locator("main .results")).toContainText("跨單位");
  await expect(page.locator('main [data-topic="scholarships"]')).toHaveAttribute("aria-pressed", "true");
});

test("closing the box with its button or Esc clears the query", async ({ page }) => {
  const sent = await open(page);
  await box(page).fill("跨單位");
  await expect(item(page, elsewhere.id)).toBeVisible();

  await page.getByRole("button", { name: "關閉搜尋" }).click();

  await expect(box(page)).toBeHidden();
  await expect(item(page, elsewhere.id)).toHaveCount(0);
  expect(new URL(page.url()).searchParams.has("q")).toBe(false);
  await searchButton(page).click();
  await box(page).fill("跨單位");
  await expect(item(page, elsewhere.id)).toBeVisible();
  await box(page).press("Escape");
  await expect(box(page)).toBeHidden();
  await expect(item(page, elsewhere.id)).toHaveCount(0);
  expect(searches(sent)).toHaveLength(2);
});

test("no results: the stream says so, and offers to search the text too", async ({ page }) => {
  const sent = await open(page, () => ({ items: [], next: null }));
  await page.getByRole("button", { name: "僅標題" }).click();
  await box(page).fill("沒有這種公告");

  await expect(page.getByText("找不到相關公告")).toBeVisible();
  await page.getByRole("button", { name: "改搜內文" }).click();

  await expect.poll(() => searches(sent).at(-1) && param(searches(sent).at(-1)!, "in")).toEqual([]);
  await searchButton(page).click(); // the click outside closed the box
  await expect(page.getByRole("button", { name: "僅標題" })).toHaveAttribute("aria-pressed", "false");
});

test("a search result's menu follows its unit", async ({ page }) => {
  await open(page);
  await box(page).fill("跨單位");
  await expect(item(page, elsewhere.id)).toBeVisible();

  await item(page, elsewhere.id).click({ button: "right" });
  await page.getByRole("menuitem", { name: `關注「${OFFICE.unit}」` }).click();

  await expect.poll(async () => JSON.parse((await stored(page))!).sites).toContain(OFFICE.id);
});
