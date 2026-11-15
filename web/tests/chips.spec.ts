// Requirement: Topic chips and unit filter (web-frontend).
import { expect, type Page, test } from "@playwright/test";
import { answer, saved, stored } from "./support/api.ts";

const lastQuery = async (sent: string[]) => {
  await expect.poll(() => sent.filter((path) => path.startsWith("/announcements?")).length).toBeGreaterThan(0);
  return new URLSearchParams(sent.filter((path) => path.startsWith("/announcements?")).at(-1)!.split("?")[1]);
};
const chips = (page: Page) => page.getByRole("toolbar", { name: "篩選" }).locator("[data-topic]");

test("Filtering by topic: only that topic is asked for, one at a time", async ({ page }) => {
  test.fail(true, "Topic chips and unit filter");
  const sent = await answer(page);
  await saved(page);
  await page.goto("/");

  await page.getByRole("button", { name: "獎助學金" }).click();
  await expect(page.getByRole("button", { name: "獎助學金" })).toHaveAttribute("aria-pressed", "true");
  await expect.poll(async () => (await lastQuery(sent)).getAll("tag")).toEqual(["topic:scholarships"]);
  await page.getByRole("button", { name: "繳費" }).click();
  await expect.poll(async () => (await lastQuery(sent)).getAll("tag")).toEqual(["topic:fees"]);
  await page.getByRole("button", { name: "全部", exact: true }).click();

  await expect.poll(async () => (await lastQuery(sent)).getAll("tag")).toEqual([]);
});

test("every topic shows, in the reader's order", async ({ page }) => {
  test.fail(true, "Topic chips and unit filter");
  await answer(page);
  await saved(page, { topicOrder: ["free-food", "library"] });
  await page.goto("/");

  await expect(chips(page)).toHaveCount(21);
  await expect(chips(page).nth(0)).toHaveText("免費餐點");
  await expect(chips(page).nth(1)).toHaveText("圖書館");
  await expect(chips(page).nth(2)).toHaveText("講座活動");
});

test("Reordering topics: a dragged chip stays first after a reload, in the stream and in the settings", async ({
  page,
}, info) => {
  test.fail(true, "Topic chips and unit filter");
  test.skip(info.project.name !== "desktop", "a mouse drag");
  await answer(page);
  await saved(page);
  await page.goto("/");
  const food = page.getByRole("button", { name: "免費餐點" });
  await food.scrollIntoViewIfNeeded();
  await page.getByRole("button", { name: "講座活動" }).scrollIntoViewIfNeeded();

  await food.hover();
  await page.mouse.down();
  const first = (await page.getByRole("button", { name: "講座活動" }).boundingBox())!;
  await page.mouse.move(first.x + 10, first.y + first.height / 2, { steps: 12 });
  await page.mouse.up();
  await page.reload();

  await expect(chips(page).first()).toHaveText("免費餐點");
  await expect(page.getByRole("button", { name: "免費餐點" })).toHaveAttribute("aria-pressed", "false");
  await page.getByRole("button", { name: "設定" }).click();
  await page.getByRole("button", { name: "調整" }).click();
  await expect(page.getByRole("dialog").getByRole("listitem").first()).toHaveText("免費餐點");
});

test("Alt+Left and Alt+Right move a focused chip", async ({ page }) => {
  test.fail(true, "Topic chips and unit filter");
  await answer(page);
  await saved(page);
  await page.goto("/");

  await page.getByRole("button", { name: "獎助學金" }).focus();
  await page.keyboard.press("Alt+ArrowLeft");
  await expect(chips(page).first()).toHaveText("獎助學金");
  await expect(page.getByRole("button", { name: "獎助學金" })).toBeFocused();
  await page.keyboard.press("Alt+ArrowRight");

  await expect(chips(page).nth(1)).toHaveText("獎助學金");
  expect(JSON.parse((await stored(page))!).topicOrder.slice(0, 2)).toEqual(["talks-and-events", "scholarships"]);
});

test("the settings reorder topics with the arrow keys", async ({ page }) => {
  test.fail(true, "Topic chips and unit filter");
  await answer(page);
  await saved(page);
  await page.goto("/");
  await page.getByRole("button", { name: "設定" }).click();
  await page.getByRole("button", { name: "調整" }).click();

  await page.getByRole("button", { name: "移動「獎助學金」" }).focus();
  await page.keyboard.press("ArrowUp");

  await expect(page.getByRole("dialog").getByRole("listitem").first()).toHaveText("獎助學金");
  await expect(page.getByRole("button", { name: "移動「獎助學金」" })).toBeFocused();
  await page.getByRole("button", { name: "關閉" }).click();
  await expect(chips(page).first()).toHaveText("獎助學金");
});

test("One unit with a hidden board: its boards stay out", async ({ page }) => {
  test.fail(true, "Topic chips and unit filter");
  const sent = await answer(page);
  await saved(page, { sites: [1045, 1049], hiddenBoards: ["1049-203"] });
  await page.goto("/");

  await page.getByRole("button", { name: "所有單位" }).click();
  await page.getByRole("menuitem", { name: "圖書館" }).click();

  await expect(page.getByRole("button", { name: "圖書館" })).toHaveAttribute("aria-pressed", "true");
  await expect.poll(async () => (await lastQuery(sent)).toString()).toBe("board=1049-1&board=1049-204");
  await page.getByRole("button", { name: "圖書館" }).click();
  await page.getByRole("menuitem", { name: "所有單位" }).click();
  await expect.poll(async () => (await lastQuery(sent)).toString()).toBe("board=1049-1&board=1049-204&site=1045");
});
