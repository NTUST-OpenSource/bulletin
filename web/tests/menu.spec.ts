// Requirement: Context menu (web-frontend).
import { expect, type Page, test } from "@playwright/test";
import { DEFAULTS } from "../src/lib/settings.ts";
import { articles, sites } from "./fixtures/recorded.ts";
import { answer, saved, stored } from "./support/api.ts";

const board = (key: string) => sites.flatMap((site) => site.boards).find((b) => b.key === key)!.name;
const unit = (id: number) => sites.find((site) => site.id === id)!.unit;
const item = (page: Page, id: number) => page.locator(`main .items > li[data-id="${id}"] a`);
const menu = (page: Page) => page.getByRole("menu");

test.beforeEach(async ({ page }) => {
  await answer(page);
  await saved(page);
});

test("An item on two followed boards: its menu offers to hide either board and unfollow either unit", async ({
  page,
}) => {
  test.fail(true, "Context menu");
  await page.goto("/");

  await item(page, 16).click({ button: "right" });

  await expect(menu(page).getByRole("menuitem")).toHaveText([
    `隱藏「${board("1045-1391")}」`,
    `隱藏「${board("1049-1")}」`,
    `不再關注「${unit(1045)}」`,
    `不再關注「${unit(1049)}」`,
    "複製連結",
    "開啟原網頁",
  ]);
  await expect(menu(page).getByRole("menuitem", { name: "開啟原網頁" })).toHaveAttribute("href", articles[16].url);
});

test("Unfollowing and undoing: the unit leaves the stream, then returns, and the settings match the start", async ({
  page,
}) => {
  test.fail(true, "Context menu");
  const sent = await answer(page);
  await page.goto("/");
  const start = await stored(page);

  await item(page, 16).click({ button: "right" });
  await menu(page).getByRole("menuitem", { name: `不再關注「${unit(1049)}」` }).click();
  await expect(page.getByRole("status")).toContainText(`已取消關注「${unit(1049)}」`);
  await expect.poll(() => sent.at(-1)).not.toContain("site=1049");
  await page.getByRole("button", { name: "復原" }).click();

  await expect.poll(() => sent.at(-1)).toContain("site=1049");
  expect(await stored(page)).toBe(start);
  expect(JSON.parse(start!).sites).toEqual(DEFAULTS.sites);
});

test("hiding a board applies at once with an undo", async ({ page }) => {
  test.fail(true, "Context menu");
  await page.goto("/");

  await item(page, 16).click({ button: "right" });
  await menu(page).getByRole("menuitem", { name: `隱藏「${board("1049-1")}」` }).click();

  await expect(page.getByRole("status")).toContainText(`已隱藏「${board("1049-1")}」`);
  expect(JSON.parse((await stored(page))!).hiddenBoards).toEqual(["1049-1"]);
});

test("the menu key opens the menu of a focused item, and copying its link works", async ({ page, context }) => {
  test.fail(true, "Context menu");
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.goto("/");

  await item(page, 16).focus();
  await page.keyboard.press("Shift+F10");
  await menu(page).getByRole("menuitem", { name: "複製連結" }).click();

  await expect(page.getByRole("status")).toContainText("已複製連結");
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(`${new URL(page.url()).origin}/a/16`);
});

test("a long press opens the menu as a bottom sheet on phones", async ({ page }, info) => {
  test.fail(true, "Context menu");
  test.skip(info.project.name !== "phone", "a touch hold");
  await page.goto("/");
  const target = item(page, 16);
  const box = (await target.boundingBox())!;
  const at = { clientX: box.x + 20, clientY: box.y + 20, pointerType: "touch", isPrimary: true, pointerId: 7 };

  await target.dispatchEvent("pointerdown", at);
  await expect(menu(page)).toBeVisible();
  await target.dispatchEvent("pointerup", at);
  await target.dispatchEvent("click", at);

  await expect(menu(page)).toBeVisible();
  expect(await menu(page).evaluate((element) => getComputedStyle(element).bottom)).toBe("0px");
  expect(new URL(page.url()).pathname).toBe("/");
});
