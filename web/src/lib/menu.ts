// What an item's context menu offers (design.md, "Context menu and long press").
import type { Board, Item, Site } from "./api";

export type Actions = {
  hide: Board[]; // each followed, visible board the item is shown through
  unfollow: Site[]; // each followed unit among those boards
  follow: Site | null; // the item's own unit, when it is not followed
};

export function actions(
  _item: Item,
  _sites: Site[],
  _settings: { sites: number[]; hiddenBoards: string[] },
): Actions {
  throw new Error("not implemented");
}
