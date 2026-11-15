// Records the API fixtures from production: `bun scripts/record-fixtures.ts`.
// The output is TypeScript whose values `satisfies` the API's types, so `bun run check` verifies
// every recorded answer against them.
const API = "https://bulletin.ntust.org/api/v1";
const DEFAULT = "site=1045&site=1049&site=1051&site=1053&site=1060&site=1070&limit=30";
// Announcements with the cases the tests need: cross-posts (1, 4), a cross-post (794), an image (6),
// a stored PDF (8), no rendition (10), a file too large to store (11), two images (14), two
// followed boards (16), a withdrawal (615) and a link item (2533).
const ARTICLES = [1, 4, 6, 8, 10, 11, 14, 16, 615, 794, 2533];

async function get(path: string): Promise<unknown> {
  const answer = await fetch(`${API}${path}`, { headers: { "User-Agent": "bulletin-web-fixtures" } });
  if (!answer.ok) throw new Error(`${path}: ${answer.status}`);
  return answer.json();
}

const first = (await get(`/announcements?${DEFAULT}`)) as { next: string };
const second = await get(`/announcements?${DEFAULT}&cursor=${first.next}`);
const articles: Record<number, unknown> = {};
for (const id of ARTICLES) articles[id] = await get(`/announcements/${id}`);

const json = (value: unknown) => JSON.stringify(value, null, 2);
const source = `// Recorded from ${API} on ${new Date().toISOString().slice(0, 10)} by scripts/record-fixtures.ts.
import type { Article, Dimension, Page, Site } from "../../src/lib/api.ts";

export const sites = ${json(await get("/sites"))} satisfies Site[];

export const tags = ${json(await get("/tags"))} satisfies Dimension[];

/** The first two pages of the default units' stream. */
export const stream = ${json({ first, second })} satisfies Record<string, Page>;

export const articles = ${json(articles)} satisfies Record<number, Article>;
`;
await Bun.write(new URL("../tests/fixtures/recorded.ts", import.meta.url), source);
