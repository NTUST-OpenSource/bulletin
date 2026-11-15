// Requirement: First visit (web-frontend). "A new reader opens an article link" is in
// article.spec.ts, with the article view it needs.
import { expect, test } from "@playwright/test";
import { DEFAULT_SITES } from "../src/lib/settings.ts";
import { answer, saved, stored } from "./support/api.ts";

const DEPARTMENT = "你在哪個系所？";
const OTHERS = "還想看哪些單位的公告？";
const EE = 1017; // 電子工程系

test.beforeEach(async ({ page }) => {
  await answer(page);
});

test("Picking a department: the department and the six preselected units are saved", async ({ page }) => {
  await page.goto("/");
  const picker = page.getByRole("dialog", { name: DEPARTMENT });

  await picker.getByRole("button", { name: "電子工程系" }).click();
  await picker.getByRole("button", { name: "下一步" }).click();
  const others = page.getByRole("dialog", { name: OTHERS });
  await expect(others.getByRole("button", { name: "全校公佈欄" })).toHaveAttribute("aria-pressed", "true");
  await expect(others.getByRole("button", { name: "電子工程系" })).toHaveCount(0);
  await others.getByRole("button", { name: "開始使用" }).click();

  await expect(page.getByRole("dialog")).toHaveCount(0);
  expect(JSON.parse((await stored(page))!).sites).toEqual([...DEFAULT_SITES, EE]);
});

test("skipping the department keeps the six, and Esc does not close the picker", async ({ page }) => {
  await page.goto("/");

  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "略過" }).click();
  await page.getByRole("button", { name: "上一步" }).click();
  await page.getByRole("button", { name: "略過" }).click();
  await page.getByRole("button", { name: "開始使用" }).click();

  expect(JSON.parse((await stored(page))!).sites).toEqual(DEFAULT_SITES);
});

test("a reader with saved settings sees no picker", async ({ page }) => {
  await saved(page);
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "bulletin" })).toHaveCount(0);
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("clearing all settings starts the picker again", async ({ page }) => {
  await saved(page, { theme: "dark" });
  await page.goto("/");
  await page.getByRole("button", { name: "設定" }).click();

  await page.getByRole("button", { name: "清除所有設定" }).click();
  await page.getByRole("button", { name: "清除", exact: true }).click();

  await expect(page.getByRole("dialog", { name: DEPARTMENT })).toBeVisible();
  expect(await stored(page)).toBeNull();
  await expect(page.locator("html")).not.toHaveAttribute("data-theme", "dark");
});
