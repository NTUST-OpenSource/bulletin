// Requirement: Attachments (web-frontend).
import { expect, type Page, test } from "@playwright/test";
import type { Attachment } from "../src/lib/api.ts";
import { articles } from "./fixtures/recorded.ts";
import { answer, saved } from "./support/api.ts";

// Chromium's PDF viewer, which renders a framed PDF in a frame of its own.
const VIEWER = "chrome-extension://mhjfbmdgcfjbbpaeojofohoefgiehjai/";
const article = (page: Page) => page.locator("dialog.article");
const preview = (page: Page) => page.locator("dialog.preview");
const file = (page: Page, name: string) => article(page).locator(".files a", { hasText: name });
const stored = (name: string): Attachment => ({
  name,
  url: `https://bulletin.ntust.edu.tw/var/file/1/${encodeURIComponent(name)}`,
  size: 2048,
  file: `/api/v1/files/${"c".repeat(64)}/${encodeURIComponent(name)}`,
});
const pdf = articles[8].attachments[0]!;
const [poster12, poster16] = articles[14].attachments;

test("A stored PDF: it opens in an in-page preview with a download button", async ({ page }, info) => {
  test.skip(info.project.name !== "desktop", "touch screens open PDFs in a new tab");
  await answer(page);
  await saved(page);
  await page.goto("/a/8");
  expect(await page.evaluate(() => navigator.pdfViewerEnabled)).toBe(true);

  await file(page, pdf.name).click();

  await expect(preview(page).locator("iframe")).toHaveAttribute("src", pdf.file!);
  await expect(preview(page).getByRole("link", { name: "下載" })).toHaveAttribute("href", pdf.file!);
  await expect(preview(page).getByRole("link", { name: "下載" })).toHaveAttribute("download", "");
  await expect.poll(() => page.frames().some((frame) => frame.url().startsWith(VIEWER))).toBe(true);
  await page.keyboard.press("Escape");
  await expect(preview(page)).toBeHidden();
  await expect(article(page)).toBeVisible();
});

test("A stored PDF on a touch screen: it opens in a new tab", async ({ page }, info) => {
  test.fail(true, "Attachments: touch screens open stored PDFs in a new tab");
  test.skip(info.project.name !== "phone", "a touch screen");
  await answer(page);
  await saved(page);
  await page.goto("/a/8");
  expect(await page.evaluate(() => navigator.pdfViewerEnabled)).toBe(true);

  const popup = page.waitForEvent("popup", { timeout: 3000 });
  await file(page, pdf.name).click();

  expect(new URL((await popup).url()).pathname).toBe(pdf.file);
  await expect(preview(page)).toBeHidden();
});

test("where the browser shows no PDFs in a page, the stored PDF opens in a new tab", async ({ page }) => {
  await page.addInitScript(() => Object.defineProperty(Navigator.prototype, "pdfViewerEnabled", { get: () => false }));
  await answer(page);
  await saved(page);
  await page.goto("/a/8");

  const popup = page.waitForEvent("popup");
  await file(page, pdf.name).click();

  expect(new URL((await popup).url()).pathname).toBe(pdf.file);
  await expect(preview(page)).toBeHidden();
});

test("A file kept only at the school: the school's link opens in a new tab", async ({ page, context }) => {
  await context.route("https://bulletin.ntust.edu.tw/**", (route) => route.fulfill({ contentType: "text/plain", body: "school" }));
  const sheet = stored("list.xlsx");
  const kept = articles[11].attachments[0]!;
  await answer(page, { articles: { 11: { ...articles[11], attachments: [kept, sheet] } } });
  await saved(page);
  await page.goto("/a/11");

  for (const attachment of [kept, sheet]) {
    await expect(file(page, attachment.name)).toHaveAttribute("href", attachment.url);
    const popup = page.waitForEvent("popup");
    await file(page, attachment.name).click();
    expect((await popup).url()).toBe(attachment.url);
    await (await popup).close();
  }
  await expect(preview(page)).toBeHidden();
});

test("One image attachment: it shows at the article's end and all three are listed", async ({ page }) => {
  const image = articles[6].attachments[0]!;
  await answer(page, { articles: { 6: { ...articles[6], attachments: [image, pdf, stored("form.pdf")] } } });
  await saved(page);
  await page.goto("/a/6");

  await expect(article(page).locator(".files a")).toHaveCount(3);
  await expect(article(page).locator(".end img")).toHaveAttribute("src", image.file!);
});

test("an image previews with zoom and arrows across the article's images", async ({ page }) => {
  await answer(page);
  await saved(page);
  await page.goto("/a/14");
  await expect(article(page).locator(".end img")).toHaveCount(0); // two images: none at the end

  await file(page, poster12!.name).click();

  const image = preview(page).getByRole("img");
  await expect(image).toHaveAttribute("src", poster12!.file!);
  await expect(preview(page).getByRole("link", { name: "下載" })).toHaveAttribute("href", poster12!.file!);
  const width = (await image.boundingBox())!.width;
  await preview(page).getByRole("button", { name: "放大" }).click();
  await expect.poll(async () => (await image.boundingBox())!.width).toBeGreaterThan(width * 1.2);
  await preview(page).getByRole("button", { name: "縮小" }).click();
  await expect.poll(async () => Math.round((await image.boundingBox())!.width)).toBe(Math.round(width));
  await page.keyboard.press("ArrowRight");
  await expect(image).toHaveAttribute("src", poster16!.file!);
  await preview(page).getByRole("button", { name: "上一張" }).click();
  await expect(image).toHaveAttribute("src", poster12!.file!);
});

test("an image in the article's text opens the image preview", async ({ page }) => {
  await answer(page);
  await saved(page, { prefer: "raw" });
  await page.goto("/a/16");

  await article(page).locator(".body img").click();

  await expect(preview(page).getByRole("img")).toHaveAttribute("src", "https://bulletin.ntust.edu.tw/var/file/45/1045/img/2535/396338505.png");
});

test("a stored DOCX shows as text", async ({ page }) => {
  await answer(page, { articles: { 6: { ...articles[6], attachments: [stored("form.docx")] } } });
  await saved(page);
  await page.goto("/a/6");

  await file(page, "form.docx").click();

  await expect(preview(page)).toContainText("Application form");
  await expect(preview(page)).toContainText("Return it by December 10.");
});

test("A preview that fails: the preview says so and offers the school's link", async ({ page }) => {
  const broken = stored("broken.docx");
  await answer(page, { articles: { 6: { ...articles[6], attachments: [broken, poster12!, poster16!] } } });
  await page.route("**/broken.docx", (route) => route.fulfill({ contentType: "application/octet-stream", body: "not a document" }));
  await page.route(`**${poster12!.file!}`, (route) => route.fulfill({ status: 404, contentType: "application/json", body: "{}" }));
  await saved(page);
  await page.goto("/a/6");

  await file(page, broken.name).click();
  await expect(preview(page)).toContainText("無法預覽");
  await expect(preview(page).getByRole("link", { name: "開啟原檔" })).toHaveAttribute("href", broken.url);
  await page.keyboard.press("Escape");
  await file(page, poster12!.name).click(); // a pruned file

  await expect(preview(page)).toContainText("無法預覽");
  await expect(preview(page).getByRole("link", { name: "開啟原檔" })).toHaveAttribute("href", poster12!.url);
});
