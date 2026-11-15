import { expect, test } from "@playwright/test";

test("the built page mounts", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("a.brand")).toHaveText("bulletin.");
});
