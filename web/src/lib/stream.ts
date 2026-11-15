// The stream's days and items (design.md, "Day headings and items").
import type { Item, Site } from "./api";

export type Day = { day: string; items: Item[] };

/** What a day heading shows; the component words it. */
export type Heading = {
  date: number;
  month: number;
  year: number | null; // only for another year than today's
  weekday: number; // 0 is Sunday
  relative: "today" | "yesterday" | null;
};

/** Items grouped by their day, in order; a group continues when the next item has its day. */
export function byDay(_items: Item[]): Day[] {
  throw new Error("not implemented");
}

/** The heading of `day`, seen on `today`; both `YYYY-MM-DD`. */
export function heading(_day: string, _today: string): Heading {
  throw new Error("not implemented");
}

/** The item's source line: its publisher, else its first followed visible board, else its first. */
export function source(
  _item: Item,
  _sites: Site[],
  _settings: { sites: number[]; hiddenBoards: string[] },
): string {
  throw new Error("not implemented");
}

/** Today in Taipei, where the stream's days are counted, as `YYYY-MM-DD`. */
export function today(_now: Date): string {
  throw new Error("not implemented");
}
