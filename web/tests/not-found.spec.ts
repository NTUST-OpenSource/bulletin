// Requirement: Unknown paths (web-frontend).
import { expect, test } from "@playwright/test";
import { answer, saved } from "./support/api.ts";

test("An unknown path: the page says it is not found and links back to the stream", async ({ page }) => {
  const sent = await answer(page);
  await saved(page);
  await page.goto("/notices");

  await expect(page.getByRole("heading", { name: "找不到這個頁面" })).toBeVisible({ timeout: 3000 });
  await expect(page.getByRole("dialog")).toBeHidden();
  expect(sent.filter((path) => path.startsWith("/announcements"))).toEqual([]);

  await page.getByRole("link", { name: "回到公布欄" }).click();
  await expect(page).toHaveURL("/");
  await expect(page.locator("main .items > li").first()).toBeVisible();
});
