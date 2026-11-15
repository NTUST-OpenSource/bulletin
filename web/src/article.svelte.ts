// The open article: its path, its answer and the version shown.
import { ApiError, type Article, type Attachment, get } from "./lib/api";
import type { Prefer } from "./lib/settings";
import { app, ui } from "./state.svelte";
import { checkNow } from "./stream.svelte";

export const PATH = /^\/a\/(\d+)$/;

export type Picture = { src: string; alt: string; file: Attachment | null };
export type Shown =
  | { kind: "images"; pictures: Picture[]; index: number; title: string }
  | { kind: "pdf" | "docx"; file: Attachment };

/** The preview over the article: its images, or one stored PDF or DOCX. */
export const viewer = $state({ shown: null as Shown | null });

export const reader = $state({
  id: null as number | null,
  article: null as Article | null,
  missing: false,
  failed: false,
  mode: null as Prefer | null, // the reader's choice from the article's menu
});

/** Show the article of `id`: a cross-post shows its original, a link item opens its link. */
export async function show(id: number): Promise<void> {
  Object.assign(reader, { id, article: null, missing: false, failed: false, mode: null });
  viewer.shown = null;
  void checkNow();
  try {
    const article = await get<Article>(`/announcements/${id}`);
    if (reader.id !== id) return;
    if (article.link_item) {
      location.replace(article.url);
    } else if (article.cross_post_of !== null) {
      const original = article.cross_post_of;
      history.replaceState(history.state === null ? null : { article: original }, "", `/a/${original}${location.search}`);
      await show(original);
    } else {
      reader.article = article;
    }
  } catch (error) {
    if (reader.id !== id) return;
    if (error instanceof ApiError && error.status === 404) reader.missing = true;
    else reader.failed = true;
  }
}

/** Follow the address: an article path shows it, any other closes it. */
export function follow(): void {
  const path = PATH.exec(location.pathname);
  if (path) void show(Number(path[1]));
  else if (reader.id !== null) closed();
}

/** Open an item from the stream under its own path. */
export function openItem(id: number): void {
  history.pushState({ article: id }, "", `/a/${id}${location.search}`);
  void show(id);
}

/** Close the article: back to the stream, or, when the page was entered at it, to the stream's path. */
export function closeArticle(): void {
  if (reader.id === null) return;
  if (history.state?.article) {
    history.back();
  } else {
    history.replaceState(null, "", `/${location.search}`);
    closed();
  }
}

function closed(): void {
  Object.assign(reader, { id: null, article: null, missing: false, failed: false, mode: null });
  viewer.shown = null;
  if (!app.saved) ui.onboarding = true; // a first visit through an article link picks units now
}
