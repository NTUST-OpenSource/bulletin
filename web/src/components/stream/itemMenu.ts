// An item's context menu: hide its boards, unfollow or follow its units, copy or open it.
import { menu as copy } from "../../lang/zh-TW";
import type { Item } from "../../lib/api";
import { actions } from "../../lib/menu";
import { app, copyText, type Entry, openMenu, phone, withUndo } from "../../state.svelte";

export function itemMenu(item: Item, at: { x: number; y: number }, sheet = phone()): void {
  const settings = app.settings;
  const { hide, unfollow, follow } = actions(item, app.sites, settings);
  const changes: Entry[] = [
    ...hide.map((board) => ({
      label: copy.hide(board.name),
      run: () => withUndo({ ...settings, hiddenBoards: [...settings.hiddenBoards, board.key] }, copy.hidden(board.name)),
    })),
    ...unfollow.map((site) => ({
      label: copy.unfollow(site.unit),
      run: () => withUndo({ ...settings, sites: settings.sites.filter((id) => id !== site.id) }, copy.unfollowed(site.unit)),
    })),
    ...(follow
      ? [
          {
            label: copy.follow(follow.unit),
            run: () => withUndo({ ...settings, sites: [...settings.sites, follow.id] }, copy.followed(follow.unit)),
          },
        ]
      : []),
  ];
  openMenu(
    [
      ...changes,
      ...(changes.length ? (["-"] as const) : []),
      { label: copy.copyLink, run: () => copyText(`${location.origin}/a/${item.id}`, copy.copied) },
      { label: copy.openSchool, href: item.url },
    ],
    at,
    sheet,
  );
}
