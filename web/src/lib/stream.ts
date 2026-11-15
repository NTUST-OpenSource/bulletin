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
export function byDay(items: Item[]): Day[] {
  const days: Day[] = [];
  for (const item of items) {
    const last = days.at(-1);
    if (last?.day === item.day) last.items.push(item);
    else days.push({ day: item.day, items: [item] });
  }
  return days;
}

const DAY_MS = 86_400_000;
const dayNumber = (day: string): number =>
  Date.UTC(Number(day.slice(0, 4)), Number(day.slice(5, 7)) - 1, Number(day.slice(8, 10))) / DAY_MS;

/** The heading of `day`, seen on `today`; both `YYYY-MM-DD`. */
export function heading(day: string, today: string): Heading {
  const offset = dayNumber(day) - dayNumber(today);
  const year = Number(day.slice(0, 4));
  return {
    date: Number(day.slice(8, 10)),
    month: Number(day.slice(5, 7)),
    year: day.slice(0, 4) === today.slice(0, 4) ? null : year,
    weekday: new Date(dayNumber(day) * DAY_MS).getUTCDay(),
    relative: offset === 0 ? "today" : offset === -1 ? "yesterday" : null,
  };
}

/** The item's source line: its publisher, else its first followed visible board, else its first. */
export function source(
  item: Item,
  sites: Site[],
  settings: { sites: number[]; hiddenBoards: string[] },
): string {
  if (item.publisher) return item.publisher;
  const names = new Map(sites.flatMap((site) => site.boards.map((board) => [board.key, board.name] as const)));
  const shown = item.boards.find(
    (key) =>
      names.has(key) && settings.sites.includes(Number(key.split("-")[0])) && !settings.hiddenBoards.includes(key),
  );
  return names.get(shown ?? item.boards[0] ?? "") ?? "";
}

const TAIPEI = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Taipei" });

/** Today in Taipei, where the stream's days are counted, as `YYYY-MM-DD`. */
export function today(now: Date): string {
  return TAIPEI.format(now);
}
