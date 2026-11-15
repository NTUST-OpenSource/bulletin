// Requirement: The page (web-frontend).
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";
import { POLICY } from "../src/lib/csp.ts";

const PDF = readFileSync(new URL("fixtures/one-page.pdf", import.meta.url));
// Chromium's PDF viewer, which renders a framed PDF in a frame of its own.
const VIEWER = "chrome-extension://mhjfbmdgcfjbbpaeojofohoefgiehjai/";
const STORED = "/api/v1/files/0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a69788796a5b4c3d2e1f0/one-page.pdf";

test("the tab title", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle("bulletin. | 臺科公布欄");
});

test("The site's icon: the page links its icons, and each is served", async ({ page, request }) => {
  test.fail(true, "The site's icon");
  await page.goto("/");
  const links = page.locator('link[rel="icon"], link[rel="apple-touch-icon"]');
  const hrefs = await links.evaluateAll((all) => all.map((link) => link.getAttribute("href") ?? ""));

  expect(hrefs.toSorted()).toEqual(["/apple-touch-icon.png", "/favicon.ico", "/favicon.svg"]);
  for (const href of hrefs) expect((await request.get(href)).ok(), href).toBe(true);
});

test.describe("a stored PDF under the page's policy", () => {
  test("the PDF shows without a policy violation", async ({ page }, info) => {
    test.skip(info.project.name !== "desktop", "phones open PDFs in a new tab");
    await page.route(`**${STORED}`, (route) =>
      route.fulfill({ contentType: "application/pdf", headers: { "Content-Disposition": "inline" }, body: PDF }),
    );
    await page.addInitScript(() => {
      const seen: string[] = [];
      (window as unknown as { violations: string[] }).violations = seen;
      document.addEventListener("securitypolicyviolation", (event) => seen.push(event.violatedDirective));
    });
    await page.goto("/");

    expect(await page.evaluate(() => navigator.pdfViewerEnabled)).toBe(true);
    const policy = page.locator('meta[http-equiv="Content-Security-Policy"]');
    await expect(policy).toHaveAttribute("content", POLICY);
    await page.evaluate((src) => {
      const frame = document.createElement("iframe");
      frame.src = src;
      document.body.append(frame);
    }, STORED);
    await expect.poll(() => page.frames().some((frame) => frame.url().startsWith(VIEWER))).toBe(true);
    expect(await page.evaluate(() => (window as unknown as { violations: string[] }).violations)).toEqual([]);
  });
});
