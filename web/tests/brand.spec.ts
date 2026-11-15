// Requirement: The brand's intro (web-frontend).
import { expect, type Locator, type Page, test } from "@playwright/test";
import { answer, saved } from "./support/api.ts";

const brand = (page: Page) => page.getByRole("banner").getByRole("link", { name: "bulletin 首頁" });
type Frame = { ball: { x: number; y: number }; b: DOMRect; n: DOMRect; hidden: boolean; running: number };

/** Where the ball is against the word's first and last letters, with the intro held at `at` ms. */
function frame(link: Locator, at: number | "end" | "now"): Promise<Frame> {
  return link.evaluate((element, at) => {
    const animations = element.getAnimations({ subtree: true });
    for (const animation of animations) {
      if (at === "end") animation.finish();
      else if (at !== "now") {
        animation.pause();
        animation.currentTime = at;
      }
    }
    const letter = (node: Node, index: number): DOMRect => {
      const range = document.createRange();
      range.setStart(node, index);
      range.setEnd(node, index + 1);
      return range.getBoundingClientRect();
    };
    const rest = element.querySelector(".rest")!;
    const ball = element.querySelector("i")!.getBoundingClientRect();
    const clip = getComputedStyle(rest).clipPath;
    return {
      ball: { x: ball.left + ball.width / 2, y: ball.top + ball.height / 2 },
      b: letter(element.firstChild!, 0),
      n: letter(rest.firstChild!, rest.textContent!.length - 1),
      hidden: clip !== "none" && parseFloat(clip.split(" ")[1]!) >= 100,
      running: element.getAnimations({ subtree: true }).length,
    };
  }, at);
}

test("The intro: the brand starts as its b holding the ball, and ends with the ball as its period", async ({ page }) => {
  test.fail(true, "The brand's intro");
  await answer(page);
  await saved(page);
  await page.goto("/");
  const link = brand(page);
  await expect.poll(async () => (await frame(link, "now")).running, { timeout: 3000 }).toBeGreaterThan(0);

  const start = await frame(link, 0);
  expect(start.ball.x).toBeGreaterThan(start.b.left);
  expect(start.ball.x).toBeLessThan(start.b.right);
  expect(start.ball.y).toBeLessThan(start.b.bottom);
  expect(start.hidden).toBe(true);

  const end = await frame(link, "end");
  expect(end.ball.x).toBeGreaterThan(end.n.right);
  expect(end.hidden).toBe(false);
  await expect.poll(async () => (await frame(link, "now")).running).toBe(0);
  await expect(link).toHaveText("bulletin.");
});

test("Reduced motion: the brand shows at rest, without the intro", async ({ page }) => {
  test.fail(true, "The brand's intro");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await answer(page);
  await saved(page);
  await page.goto("/");
  await expect(page.locator("main .items > li").first()).toBeVisible();

  const now = await frame(brand(page), "now");
  expect(now.running).toBe(0);
  expect(now.hidden).toBe(false);
  expect(now.ball.x).toBeGreaterThan(now.n.right);
});
