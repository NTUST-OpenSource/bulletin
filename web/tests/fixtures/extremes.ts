// The cases of design.md that production does not hold, built from recorded answers.
import type { Article, Item, Page } from "../../src/lib/api.ts";
import { articles, stream } from "./recorded.ts";

const LONG_WORD = "Announcement".repeat(17); // 204 characters without a break
const LONG_URL = `https://www.ntust.edu.tw/var/file/0/1000/img/${"a1b2c3d4".repeat(16)}.pdf`;

const recorded = stream.first.items[0]!;

/** A 200-character title without spaces, also in the rewrite and the summary. */
export const longTitle = {
  ...recorded,
  id: 900001,
  title: LONG_WORD,
  rendition: { title: LONG_WORD, summary: `${LONG_WORD} ${LONG_URL}`, deadline: null },
} satisfies Item;

/** A 120-character file name, a long school URL and a three-digit size in megabytes. */
export const longFile = {
  ...articles[8],
  id: 900002,
  attachments: [
    { name: `${"Attachment".repeat(12)}.pdf`, url: LONG_URL, size: 987_654_321, file: null },
    ...articles[8].attachments,
  ],
} satisfies Article;

/** A first page with the extreme item and a link item on top of the recorded one. */
export const extremePage = {
  items: [longTitle, articles[2533], ...stream.first.items],
  next: stream.first.next,
} satisfies Page;

/** Recorded announcements by the case they stand for. */
export const cases = {
  crossPosted: 1, // its cross-post is 794
  crossPost: 794,
  image: 6,
  twoImages: 14,
  storedPdf: 8,
  unstoredFile: 11,
  noRendition: 10,
  twoFollowedBoards: 16, // 1045-1391 and 1049-1, both followed by default
  withdrawn: 615,
  linkItem: 2533,
} as const;
