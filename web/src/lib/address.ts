// The search's limits, and the filters in the page's address.
import type { Filters } from "./api";

/** The query as sent: at most 100 characters, the first ten words, the API's limits. */
export function terms(text: string): string {
  throw new Error(`not implemented: ${text}`);
}

/** The filters as the page's query string. */
export function addressQuery(filters: Filters): string {
  throw new Error(`not implemented: ${filters.q}`);
}

/** The filters in the page's query string; unreadable ones read as unset. */
export function readAddress(search: string): Filters {
  throw new Error(`not implemented: ${search}`);
}
