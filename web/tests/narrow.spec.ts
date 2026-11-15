// Requirement: Narrow screens and long text (web-frontend), over every view at both widths.
import { expect, type Page, test } from "@playwright/test";
import type { Item, Page as Answer } from "../src/lib/api.ts";
import { extremePage, longArticle, longFile, longTitle, manyImages } from "./fixtures/extremes.ts";
import { stream } from "./fixtures/recorded.ts";
import { answer, saved } from "./support/api.ts";
import { settingsLink } from "../src/lib/settings.ts";

const FIVE_MINUTES = 5 * 60 * 1000;
const LONG_QUERY = "Announcement".repeat(8);
const LONG_UNITS = [1103, 1011, 1010]; // the longest unit names, and the longest board name
const LONG_BOARD = "1010-2177";
const docx = {
  name: `${"Form".repeat(30)}.docx`,
  url: "https://www.ntust.edu.tw/var/file/1/form.docx",
  size: 987_654_321,
  file: `/api/v1/files/${"d".repeat(64)}/form.docx`,
};
const articles = { [longArticle.id]: longArticle, [longFile.id]: { ...longFile, attachments: [...longFile.attachments, docx] }, [manyImages.id]: manyImages };
const dialog = (page: Page) => page.getByRole("dialog");
const item = (page: Page, id: number) => page.locator(`main .items > li[data-id="${id}"]`);

/** The page, open dialogs and menus that are wider than their box, so scroll sideways. */
async function flat(page: Page, view: string): Promise<void> {
  await page.waitForTimeout(350); // opening animations settle
  const wide = await page.evaluate(() =>
    [document.documentElement, ...document.querySelectorAll("dialog[open], [role=menu]:not([hidden])")]
      .filter((element) => element.scrollWidth > element.clientWidth + 1)
      .map((element) => `${element.tagName.toLowerCase()}.${element.className} ${element.scrollWidth} > ${element.clientWidth}`),
  );
  expect(wide, view).toEqual([]);
}

test("the stream, its menus and a long search do not scroll sideways", async ({ page }) => {
  const onLongBoard = { ...longTitle, boards: [LONG_BOARD, ...longTitle.boards] };
  const first = { ...extremePage, items: [onLongBoard, ...extremePage.items.slice(1)] };
  await answer(page, { pages: (query) => (query.has("q") ? { items: [onLongBoard], next: null } : first) });
  await saved(page, { sites: LONG_UNITS, hiddenBoards: [] });
  await page.goto("/");
  await expect(item(page, longTitle.id)).toBeVisible();
  await flat(page, "stream");

  await page.locator("main [aria-haspopup=menu]").click();
  await flat(page, "unit menu");
  await page.keyboard.press("Escape");
  await item(page, longTitle.id).click({ button: "right" });
  await flat(page, "item menu");
  await page.getByRole("menuitem", { name: /^隱藏「2024 ICMCMT/ }).click();
  await expect(page.locator("[role=status][aria-live=polite]")).toContainText("2024 ICMCMT");
  await flat(page, "notice");
  await page.getByRole("banner").getByRole("button", { name: "搜尋" }).click();
  await page.getByRole("searchbox", { name: "搜尋" }).fill(LONG_QUERY);
  await expect(page.locator("main .results")).toContainText(LONG_QUERY);
  await flat(page, "search");
});

test("the first visit, settings and their views do not scroll sideways", async ({ page }) => {
  await answer(page);
  await page.goto("/");
  await expect(dialog(page)).toBeVisible();
  await flat(page, "first visit");
  await dialog(page).getByRole("button", { name: "略過" }).click();
  await flat(page, "first visit, second step");
  await page.keyboard.press("Escape");

  await page.evaluate(
    ([units, board]) =>
      localStorage.setItem("bulletin.settings", JSON.stringify({ version: 1, theme: "system", prefer: "rendition", sites: units, hiddenBoards: [board], topicOrder: [] })),
    [LONG_UNITS, LONG_BOARD] as const,
  );
  await page.reload();
  await page.getByRole("banner").getByRole("button", { name: "設定" }).click();
  await flat(page, "settings");
  await dialog(page).getByRole("button", { name: "編輯" }).click();
  await flat(page, "followed units");
  await dialog(page).getByRole("button", { name: "返回" }).click();
  await dialog(page).getByRole("button", { name: "調整", exact: true }).click();
  await flat(page, "topic order");
  await page.keyboard.press("Escape");
  await expect(dialog(page)).toHaveCount(0);
  await page.goto(settingsLink("", { version: 1, theme: "dark", prefer: "raw", sites: LONG_UNITS, hiddenBoards: [], topicOrder: [] }));
  await expect(dialog(page)).toBeVisible(); // the question before overwriting saved settings
  await flat(page, "settings link question");
});

test("A long file name on a phone: articles, previews and failures do not scroll sideways", async ({ page }) => {
  await answer(page, { articles });
  await saved(page);

  await page.goto(`/a/${longArticle.id}`);
  await expect(dialog(page).getByRole("heading", { level: 1 })).toBeVisible();
  await flat(page, "rewrite");
  await dialog(page).getByRole("button", { name: "更多" }).click();
  await page.getByRole("menuitem", { name: "顯示原文" }).click();
  await flat(page, "school's version");

  await page.goto(`/a/${longFile.id}`);
  const name = dialog(page).locator(".files a", { hasText: longFile.attachments[0]!.name });
  await expect(name).toBeVisible();
  expect(await name.evaluate((link) => link.scrollWidth <= link.clientWidth)).toBe(true);
  await flat(page, "attachments");
  await dialog(page).locator(".files a", { hasText: docx.name }).click();
  await expect(page.locator("dialog.preview")).toContainText("Application form");
  await flat(page, "DOCX preview");
  await page.keyboard.press("Escape");

  await page.goto(`/a/${manyImages.id}`);
  await dialog(page).locator(".files a").last().click();
  await expect(page.locator("dialog.preview")).toContainText("120 / 120");
  await flat(page, "image preview");
  await page.route("**/api/v1/files/**", (route) => route.fulfill({ status: 404, body: "{}" }));
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("dialog.preview")).toContainText("無法預覽");
  await flat(page, "failed preview");

  await page.goto("/a/999999");
  await expect(dialog(page)).toContainText("找不到這則公告");
  await flat(page, "unknown article");
});

test("Reduced motion: a new announcement appears without animation", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.clock.install();
  const arriving: Item = { ...stream.first.items[0]!, id: 9002, title: "新公告", rendition: null, publisher: null };
  let checks = 0;
  await answer(page, {
    pages: (query): Answer =>
      query.has("cursor") ? stream.second : checks++ === 0 ? stream.first : { items: [arriving, ...stream.first.items], next: stream.first.next },
  });
  await saved(page);
  await page.goto("/");
  await expect(item(page, stream.first.items[0]!.id)).toBeVisible();

  await page.clock.fastForward(FIVE_MINUTES);

  await expect(item(page, arriving.id)).toHaveClass(/arrive/);
  expect(await item(page, arriving.id).evaluate((li) => li.getAnimations({ subtree: true }).length)).toBe(0);
});
