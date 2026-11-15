// What an item's context menu offers (design.md, "Context menu and long press").
import type { Board, Item, Site } from "./api";

export type Actions = {
  hide: Board[]; // each followed, visible board the item is shown through
  unfollow: Site[]; // each followed unit among those boards
  follow: Site | null; // the item's own unit, when it is not followed
};

export function actions(
  item: Item,
  sites: Site[],
  settings: { sites: number[]; hiddenBoards: string[] },
): Actions {
  const hide: Board[] = [];
  const unfollow: Site[] = [];
  for (const key of item.boards) {
    const site = sites.find((s) => s.id === Number(key.split("-")[0]));
    const board = site?.boards.find((b) => b.key === key);
    if (!site || !board || !settings.sites.includes(site.id) || settings.hiddenBoards.includes(key)) continue;
    hide.push(board);
    if (!unfollow.includes(site)) unfollow.push(site);
  }
  const own = sites.find((site) => site.id === item.site);
  return { hide, unfollow, follow: own && !settings.sites.includes(own.id) ? own : null };
}
