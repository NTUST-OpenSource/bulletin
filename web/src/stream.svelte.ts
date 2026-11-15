// The stream: the pages of the current query, paged by cursor and checked for news.
import { get, type Item, type Page } from "./lib/api";
import { appended, merged } from "./lib/stream";

export const CHECK_MS = 5 * 60 * 1000;
const FOLLOW = 5; // pages a check follows to reach the shown items before starting over

export const feed = $state({
  query: null as string | null, // null asks for nothing
  items: [] as Item[],
  next: null as string | null,
  loading: false,
  failed: false,
  arrived: new Set<number>(), // inserted by a check, shown with an animation
  checked: 0, // when the first page was last read, by Date.now()
});

const path = (query: string, cursor: string | null) =>
  `/announcements?${query}${cursor === null ? "" : `&cursor=${encodeURIComponent(cursor)}`}`;

/** Show the first page of `query`; an answer for an older query is dropped. */
export async function open(query: string | null): Promise<void> {
  Object.assign(feed, { query, items: [], next: null, failed: false, arrived: new Set() });
  if (query === null) return;
  feed.loading = true;
  feed.checked = Date.now();
  try {
    const page = await get<Page>(path(query, null));
    if (feed.query !== query) return;
    feed.items = page.items;
    feed.next = page.next;
  } catch {
    if (feed.query === query) feed.failed = true;
  } finally {
    if (feed.query === query) feed.loading = false;
  }
}

/** Load the page after the shown items, skipping ids already shown. */
export async function more(): Promise<void> {
  const { query, next } = feed;
  if (query === null || next === null || feed.loading) return;
  feed.loading = true;
  feed.failed = false;
  try {
    const page = await get<Page>(path(query, next));
    if (feed.query !== query) return;
    feed.items = appended(feed.items, page.items);
    feed.next = page.next;
  } catch {
    if (feed.query === query) feed.failed = true;
  } finally {
    if (feed.query === query) feed.loading = false;
  }
}

type Insert = (apply: () => void) => Promise<void>;
let place: Insert = async (apply) => apply();

/** How the stream inserts a check's items while keeping the reader's place; the stream sets it. */
export function setPlace(insert: Insert): void {
  place = insert;
}

/** Check now, as on opening an article. */
export const checkNow = (): Promise<void> => check(place);

/**
 * Check for new and changed announcements, bypassing cached answers. The check follows the
 * cursor until it reaches the shown items, so nothing is skipped; `insert` applies the result.
 */
export async function check(insert: (apply: () => void) => Promise<void>): Promise<void> {
  const query = feed.query;
  if (query === null || feed.loading) return;
  feed.checked = Date.now();
  let polled: Item[] = [];
  let cursor: string | null = null;
  try {
    for (let page = 0; page < FOLLOW; page++) {
      const answer: Page = await get<Page>(path(query, cursor), true);
      if (feed.query !== query) return;
      polled = [...polled, ...answer.items];
      const result = merged(feed.items, polled, feed.next === null);
      if (result.overlap || answer.next === null) {
        await insert(() => {
          feed.items = result.items;
          feed.arrived = new Set([...feed.arrived, ...result.added]);
        });
        return;
      }
      cursor = answer.next;
    }
  } catch {
    return; // the next check tries again
  }
  await open(query);
}
