// The search's limits, and the filters in the page's address.
import type { Filters } from "./api";

const MAX_LENGTH = 100; // the API's limits on q
const MAX_WORDS = 10;

/** The query as sent: the first ten words, at most 100 characters, the API's limits. */
export function terms(text: string): string {
  return text.trim().split(/\s+/).slice(0, MAX_WORDS).join(" ").slice(0, MAX_LENGTH).trim();
}

/** The filters as the page's query string. */
export function addressQuery(filters: Filters): string {
  const params = new URLSearchParams();
  if (filters.q) {
    params.set("q", filters.q);
    if (filters.titleOnly) params.set("in", "title");
  }
  if (filters.topic) params.set("topic", filters.topic);
  if (filters.unit !== null) params.set("unit", String(filters.unit));
  return params.toString();
}

/** The filters in the page's query string; unreadable ones read as unset. */
export function readAddress(search: string): Filters {
  const params = new URLSearchParams(search);
  const q = terms(params.get("q") ?? "");
  const unit = Number(params.get("unit"));
  return {
    q,
    titleOnly: q !== "" && params.get("in") === "title",
    topic: params.get("topic") || null,
    unit: Number.isSafeInteger(unit) && unit > 0 ? unit : null,
  };
}
