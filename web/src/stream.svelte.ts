// The stream: the pages of the current query.
import { get, type Item, type Page } from "./lib/api";

export const feed = $state({
  query: null as string | null, // null asks for nothing
  items: [] as Item[],
  next: null as string | null,
  loading: false,
  failed: false,
});

/** Show the first page of `query`; an answer for an older query is dropped. */
export async function open(query: string | null): Promise<void> {
  feed.query = query;
  feed.items = [];
  feed.next = null;
  feed.failed = false;
  if (query === null) return;
  feed.loading = true;
  try {
    const page = await get<Page>(`/announcements?${query}`);
    if (feed.query !== query) return;
    feed.items = page.items;
    feed.next = page.next;
  } catch {
    if (feed.query === query) feed.failed = true;
  } finally {
    if (feed.query === query) feed.loading = false;
  }
}
