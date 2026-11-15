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
