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

/** Settings from parsed JSON, a wrong field falling back to its default; null if not settings. */
export function parseSettings(_value: unknown): Settings | null {
  throw new Error("not implemented");
}

/** The saved settings, or the defaults when nothing readable is saved or storage is blocked. */
export function loadSettings(_storage: Storage | null): { settings: Settings; saved: boolean } {
  throw new Error("not implemented");
}

/** Save the settings; false when storage refuses them. */
export function saveSettings(_storage: Storage | null, _settings: Settings): boolean {
  throw new Error("not implemented");
}

/** The topics to show, in the reader's order: unknown ids left out, missing ones appended. */
export function topicOrder(_settings: Settings, _known: string[]): string[] {
  throw new Error("not implemented");
}
