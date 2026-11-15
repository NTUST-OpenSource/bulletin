// The reader's settings, kept in the browser (design.md, "Settings").

export type Theme = "system" | "light" | "dark";
export type Prefer = "rendition" | "raw";

export type Settings = {
  version: 1;
  theme: Theme;
  prefer: Prefer;
  sites: number[]; // followed, by site id
  hiddenBoards: string[]; // board keys
  topicOrder: string[]; // topic ids
};

export const STORE_KEY = "bulletin.settings";

// The six P1 units: the school-wide board, student affairs, international affairs, the library,
// the language center and the center for teaching and learning development.
export const DEFAULT_SITES = [1045, 1053, 1060, 1049, 1070, 1051];

// The prototype's order, with the library after IT systems.
export const DEFAULT_TOPICS = [
  "talks-and-events",
  "scholarships",
  "competitions-and-calls",
  "internships-and-jobs",
  "international-exchange",
  "courses",
  "enrolment-and-grades",
  "exams-and-certification",
  "fees",
  "housing",
  "research-projects",
  "admissions",
  "venue-and-service-changes",
  "safety-and-health",
  "it-systems",
  "library",
  "military-service",
  "clubs-and-volunteering",
  "rules-and-policy",
  "honours",
  "free-food",
];

export const DEFAULTS: Settings = {
  version: 1,
  theme: "system",
  prefer: "rendition",
  sites: DEFAULT_SITES,
  hiddenBoards: [],
  topicOrder: DEFAULT_TOPICS,
};

const THEMES: readonly Theme[] = ["system", "light", "dark"];
const PREFERS: readonly Prefer[] = ["rendition", "raw"];

const isObject = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

/** The items of `value` that pass `keep`, once each; `fallback` when it is not a list. */
function list<T>(value: unknown, keep: (item: unknown) => item is T, fallback: T[]): T[] {
  return Array.isArray(value) ? [...new Set(value.filter(keep))] : fallback;
}

const isId = (item: unknown): item is number => Number.isSafeInteger(item);
const isText = (item: unknown): item is string => typeof item === "string";

/** Settings from parsed JSON, a wrong field falling back to its default; null if not settings. */
export function parseSettings(value: unknown): Settings | null {
  if (!isObject(value) || value["version"] !== 1) return null;
  const theme = THEMES.find((t) => t === value["theme"]) ?? DEFAULTS.theme;
  const prefer = PREFERS.find((p) => p === value["prefer"]) ?? DEFAULTS.prefer;
  return {
    version: 1,
    theme,
    prefer,
    sites: list(value["sites"], isId, DEFAULTS.sites),
    hiddenBoards: list(value["hiddenBoards"], isText, DEFAULTS.hiddenBoards),
    topicOrder: list(value["topicOrder"], isText, DEFAULTS.topicOrder),
  };
}

/** The saved settings, or the defaults when nothing readable is saved or storage is blocked. */
export function loadSettings(storage: Storage | null): { settings: Settings; saved: boolean } {
  try {
    const raw = storage?.getItem(STORE_KEY);
    const settings = raw ? parseSettings(JSON.parse(raw)) : null;
    if (settings) return { settings, saved: true };
  } catch {
    // Blocked storage or broken JSON: the defaults, not kept.
  }
  return { settings: DEFAULTS, saved: false };
}

/** Save the settings; false when storage refuses them. */
export function saveSettings(storage: Storage | null, settings: Settings): boolean {
  try {
    storage?.setItem(STORE_KEY, JSON.stringify(settings));
    return storage !== null;
  } catch {
    return false;
  }
}

/** The topics to show, in the reader's order: unknown ids left out, missing ones appended. */
export function topicOrder(settings: Settings, known: string[]): string[] {
  const ordered = settings.topicOrder.filter((topic) => known.includes(topic));
  const rest = DEFAULT_TOPICS.filter((topic) => known.includes(topic) && !ordered.includes(topic));
  return [...ordered, ...rest, ...known.filter((topic) => !ordered.includes(topic) && !rest.includes(topic))];
}

/** Show `theme` on the page: a saved light or dark theme overrides the system's. */
export function applyTheme(root: HTMLElement, theme: Theme): void {
  if (theme === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", theme);
}

/** Input that is neither settings JSON nor a settings link. */
export class UnreadableSettings extends Error {}

const toBase64Url = (text: string): string =>
  btoa(String.fromCharCode(...new TextEncoder().encode(text)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");

const fromBase64Url = (text: string): string =>
  new TextDecoder("utf-8", { fatal: true }).decode(
    Uint8Array.from(atob(text.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0)),
  );

/** A link that applies `settings` when opened: the page's address with `#s=<base64url JSON>`. */
export function settingsLink(origin: string, settings: Settings): string {
  return `${origin}/#s=${toBase64Url(JSON.stringify(settings))}`;
}

/** The settings in pasted JSON, a pasted link or a file's text; UnreadableSettings otherwise. */
export function readImport(text: string): Settings {
  const trimmed = text.trim();
  const link = /#s=([\w-]+)$/.exec(trimmed);
  try {
    const settings = parseSettings(JSON.parse(link ? fromBase64Url(link[1]!) : trimmed));
    if (settings) return settings;
  } catch {
    // Not JSON, not base64url or not UTF-8.
  }
  throw new UnreadableSettings();
}
