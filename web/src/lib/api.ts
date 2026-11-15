// The public API's answers (openspec/specs/public-api), as the frontend reads them.

/** Tag ids by dimension, in the taxonomy's order. */
export type Tags = {
  topic: string[];
  audience: string[];
  nature: string[];
  source: string[];
};

/** A rendition's title, summary and deadline (a date); null without one or with a fallback. */
export type Rendition = {
  title: string;
  summary: string | null;
  deadline: string | null;
};

/** A stream item. Days are `YYYY-MM-DD`, times ISO 8601 with an offset. */
export type Item = {
  id: number;
  site: number;
  unit: string | null;
  url: string;
  link_item: boolean;
  title: string;
  publisher: string | null;
  day: string;
  listed_on: string | null;
  first_seen_at: string;
  withdrawn_at: string | null;
  boards: string[]; // `<site>-<board>`, its own and its cross-posts'
  tags: Tags;
  rendition: Rendition | null;
};

export type Page = {
  items: Item[];
  next: string | null;
};

/** `file` is the stored copy's path under the API, null when not stored or pruned. */
export type Attachment = {
  name: string;
  url: string;
  size: number | null;
  file: string | null;
};

export type CrossPost = {
  id: number;
  site: number;
  url: string;
};

/** One announcement: the item's fields, its text and its files. */
export type Article = Omit<Item, "rendition"> & {
  rendition: (Rendition & { markdown: string }) | null;
  body_html: string | null;
  attachments: Attachment[];
  revisions: { fetched_at: string }[];
  cross_posts: CrossPost[];
  cross_post_of: number | null;
};

export type Board = {
  key: string;
  name: string;
  category: "announcement" | "news" | "regulation" | "course";
};

export type Site = {
  id: number;
  host: string;
  unit: string;
  kind: "all" | "admin" | "academic";
  college: string | null;
  boards: Board[];
};

export type Dimension = {
  id: string;
  several: boolean;
  tags: { id: string; label: string }[];
};

/** The stream's filters besides the settings: the search, the topic chip and the unit menu. */
export type Filters = {
  q: string;
  titleOnly: boolean;
  topic: string | null;
  unit: number | null;
};

export const NO_FILTERS: Filters = { q: "", titleOnly: false, topic: null, unit: null };

/** A site's part of the query: the site when none of its boards is hidden, else its visible boards. */
function placement(site: Site, hidden: Set<string>, params: [string, string][]): void {
  const visible = site.boards.filter((board) => !hidden.has(board.key));
  if (visible.length === site.boards.length) params.push(["site", String(site.id)]);
  else for (const board of visible) params.push(["board", board.key]);
}

/**
 * The stream's query string, each list sorted so equal settings share Cloudflare's cache; null
 * when there is nothing to ask for. Units, boards and topics the API does not list are left out.
 */
export function streamQuery(
  settings: { sites: number[]; hiddenBoards: string[] },
  sites: Site[],
  topics: string[],
  filters: Filters,
): string | null {
  const hidden = new Set(settings.hiddenBoards);
  const followed = sites.filter((site) => settings.sites.includes(site.id));
  const unit = filters.unit === null ? null : sites.find((site) => site.id === filters.unit);
  const searching = filters.q !== "";
  const params: [string, string][] = [];
  if (unit) placement(unit, hidden, params);
  else if (!searching) for (const site of followed) placement(site, hidden, params);
  if (params.length === 0 && (unit || !searching)) return null;
  params.sort(([a, x], [b, y]) => a.localeCompare(b) || x.localeCompare(y, "en", { numeric: true }));
  if (filters.topic && topics.includes(filters.topic)) params.push(["tag", `topic:${filters.topic}`]);
  if (searching) {
    params.push(["q", filters.q]);
    if (filters.titleOnly) params.push(["in", "title"]);
  }
  return new URLSearchParams(params).toString();
}

export const API = "/api/v1";

/** An answer other than 200; `status` 0 when the API could not be reached. */
export class ApiError extends Error {
  constructor(readonly status: number) {
    super(`the API answered ${status}`);
  }
}

/** GET a path of the API; `fresh` revalidates instead of taking a cached copy. */
export async function get<T>(path: string, fresh = false): Promise<T> {
  let answer: Response;
  try {
    answer = await fetch(`${API}${path}`, fresh ? { cache: "no-cache" } : {});
  } catch {
    throw new ApiError(0);
  }
  if (!answer.ok) throw new ApiError(answer.status);
  return (await answer.json()) as T;
}
