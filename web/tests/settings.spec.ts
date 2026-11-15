// Requirement: Settings (web-frontend).
import { expect, test } from "@playwright/test";
import { answer, saved, stored } from "./support/api.ts";

const NOTE = "內容轉寫自國立臺灣科技大學各單位網站，以原網頁內容為準";

test("Dark theme: the page stays dark after a reload", async ({ page }) => {
  test.fail(true, "Settings");
  await page.emulateMedia({ colorScheme: "light" });
  await answer(page);
  await saved(page);
  await page.goto("/");

  await page.getByRole("button", { name: "設定" }).click();
  await page.getByRole("button", { name: "深色" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.reload();

  await expect(page.locator("body")).toHaveCSS("background-color", "rgb(13, 16, 21)");
});

test("the settings sheet ends with the note on the source", async ({ page }) => {
  test.fail(true, "Settings");
  await answer(page);
  await saved(page);
  await page.goto("/");

  await page.getByRole("button", { name: "設定" }).click();

  await expect(page.getByRole("dialog").getByText(NOTE)).toBeVisible();
});

test("The sites list fails: the saved settings stay as they are", async ({ page }) => {
  test.fail(true, "Settings");
  await answer(page, { fail: { sites: 503 } });
  await saved(page, { theme: "dark", sites: [1053, 9999], hiddenBoards: ["1053-9999"] });
  await page.goto("/");
  const before = await stored(page);

  await page.getByRole("button", { name: "設定" }).click();

  await expect(page.getByRole("button", { name: "深色" })).toHaveAttribute("aria-pressed", "true");
  expect(await stored(page)).toBe(before);
});
