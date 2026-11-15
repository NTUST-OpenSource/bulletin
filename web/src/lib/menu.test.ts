// Requirement: Context menu (web-frontend).
import { expect, test } from "vitest";
import { articles, sites } from "../../tests/fixtures/recorded.ts";
import { actions } from "./menu";

const DEFAULT = { sites: [1045, 1049, 1053], hiddenBoards: [] };
const keys = (result: ReturnType<typeof actions>) => ({
  hide: result.hide.map((board) => board.key),
  unfollow: result.unfollow.map((site) => site.id),
  follow: result.follow?.id ?? null,
});

test.fails("An item on two followed boards: either board can be hidden and either unit unfollowed", () => {
  expect(keys(actions(articles[16], sites, DEFAULT))).toEqual({
    hide: ["1045-1391", "1049-1"],
    unfollow: [1045, 1049],
    follow: null,
  });
});

test.fails("hidden, unfollowed and unknown boards are not offered", () => {
  const item = { ...articles[16], boards: [...articles[16].boards, "1053-1435", "9999-1"] };

  expect(keys(actions(item, sites, { sites: [1045, 1053], hiddenBoards: ["1053-1435"] }))).toEqual({
    hide: ["1045-1391"],
    unfollow: [1045],
    follow: null,
  });
});

test.fails("an item of an unfollowed unit, as search shows it, offers to follow its unit", () => {
  expect(keys(actions(articles[1], sites, { sites: [1049], hiddenBoards: [] }))).toEqual({
    hide: [],
    unfollow: [],
    follow: 1045,
  });
});
