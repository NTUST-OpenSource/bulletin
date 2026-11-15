// Requirement: Settings export and import (web-frontend).
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";
import { DEFAULTS, STORE_KEY } from "../src/lib/settings.ts";
import { answer, saved, stored } from "./support/api.ts";

const THEIRS = { ...DEFAULTS, theme: "dark" as const, sites: [1017, 1045] };
const MINE = { ...DEFAULTS, sites: [1049] };
const link = (settings: object) => `/#s=${Buffer.from(JSON.stringify(settings)).toString("base64url")}`;

test.beforeEach(async ({ page }) => {
  await answer(page);
});

test("A link for a new reader: the settings apply without the first-visit picker", async ({ page }) => {
  await page.goto(link(THEIRS));

  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  expect(JSON.parse((await stored(page))!)).toEqual(THEIRS);
  expect(new URL(page.url()).hash).toBe("");
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("A link for an existing reader: keeping theirs changes nothing, and a reload does not ask", async ({ page }) => {
  await saved(page, MINE);
  await page.goto(link(THEIRS));

  await page.getByRole("button", { name: "保留目前設定" }).click();
  expect(JSON.parse((await stored(page))!)).toEqual(MINE);
  await page.reload();

  await expect(page.getByText("覆蓋目前的設定？")).toHaveCount(0);
});

test("a link opened in a tab that shows the page asks too", async ({ page }) => {
  await saved(page, MINE);
  await page.goto("/");
  await page.goto(link(THEIRS));

  await expect(page.getByText("覆蓋目前的設定？")).toBeVisible();
});

test("a link for an existing reader overwrites when asked", async ({ page }) => {
  await saved(page, MINE);
  await page.goto(link(THEIRS));

  await page.getByRole("button", { name: "覆蓋", exact: true }).click();

  await expect.poll(async () => JSON.parse((await stored(page))!)).toEqual(THEIRS);
});

test("Unreadable input: an error is shown and the settings stay", async ({ page }) => {
  await saved(page, MINE);
  await page.goto("/");
  await page.getByRole("button", { name: "設定" }).click();

  await page.getByLabel("設定 JSON 或分享連結").fill("hello");
  await page.getByRole("button", { name: "匯入", exact: true }).click();

  await expect(page.getByRole("alert")).toHaveText("無法讀取：請貼上本站匯出的設定或分享連結。");
  expect(JSON.parse((await stored(page))!)).toEqual(MINE);
});

test("the settings export as copied JSON, a download and a copied link", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await saved(page, MINE);
  await page.goto("/");
  await page.getByRole("button", { name: "設定" }).click();
  const clipboard = () => page.evaluate(() => navigator.clipboard.readText());

  await page.getByRole("button", { name: "複製設定" }).click();
  expect(JSON.parse(await clipboard())).toEqual(MINE);
  await page.getByRole("button", { name: "複製分享連結" }).click();
  expect(await clipboard()).toBe(`${new URL(page.url()).origin}${link(MINE)}`);
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "下載 JSON" }).click();
  const file = await download;

  expect(file.suggestedFilename()).toBe("bulletin-settings.json");
  expect(JSON.parse(readFileSync((await file.path())!, "utf8"))).toEqual(MINE);
});

test("a JSON file imports for a reader who confirms", async ({ page }) => {
  await saved(page, MINE);
  await page.goto("/");
  await page.getByRole("button", { name: "設定" }).click();

  await page.locator("#import-file").setInputFiles({
    name: "bulletin-settings.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(THEIRS)),
  });
  await page.getByRole("button", { name: "覆蓋", exact: true }).click();

  await expect.poll(async () => JSON.parse((await stored(page))!)).toEqual(THEIRS);
  expect(await page.evaluate((key) => localStorage.getItem(key), STORE_KEY)).not.toBeNull();
});
