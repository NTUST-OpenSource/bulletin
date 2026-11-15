// The page's state: the settings, kept in localStorage, and the API's lists.
import { transfer } from "./lang/zh-TW";
import { type Dimension, type Filters, get, NO_FILTERS, type Site } from "./lib/api";
import { DEFAULTS, loadSettings, STORE_KEY, type Settings, saveSettings } from "./lib/settings";

function storage(): Storage | null {
  try {
    return localStorage;
  } catch {
    return null; // blocked storage: settings work but are not kept
  }
}

const loaded = loadSettings(storage());

export const app = $state({
  settings: loaded.settings,
  saved: loaded.saved, // the reader has saved settings
  sites: [] as Site[],
  tags: [] as Dimension[],
  listsLoaded: false,
  listsFailed: false,
});

/** The search, the topic chip and the unit menu. */
export const filters: Filters = $state({ ...NO_FILTERS });

export type Question = { title: string; text: string; yes: string; no: string; answer: (yes: boolean) => void };
export type Notice = { message: string; action?: { label: string; run: () => void } };

/** What the page shows over the stream. */
export const ui = $state({
  sheet: null as null | "main" | "units",
  onboarding: false,
  question: null as Question | null,
  notice: null as Notice | null,
});

/** Ask a yes-or-no question in a dialog. */
export function ask(question: Omit<Question, "answer">): Promise<boolean> {
  return new Promise((answer) => (ui.question = { ...question, answer }));
}

/** Show a notice, with an action such as undo. */
export function notify(message: string, action?: Notice["action"]): void {
  ui.notice = action ? { message, action } : { message };
}

/** Apply imported or linked settings: at once for a reader who never saved any, else on yes. */
export async function offerSettings(next: Settings, how: "link" | "import"): Promise<void> {
  if (!app.saved) {
    setSettings(next);
    notify(how === "link" ? transfer.linkApplied : transfer.imported);
  } else if (await ask(transfer.overwrite)) {
    setSettings(next);
    notify(transfer.overwritten);
  }
}

/** Change and keep the settings; storage is written only here. */
export function setSettings(next: Settings): void {
  app.settings = next;
  app.saved = true;
  saveSettings(storage(), next);
}

/** Forget the saved settings: the defaults apply, and the unit picker starts again. */
export function clearSettings(): void {
  try {
    storage()?.removeItem(STORE_KEY);
  } catch {
    // Blocked storage kept nothing.
  }
  app.settings = DEFAULTS;
  app.saved = false;
  ui.onboarding = true;
}

/** Load the sites and the tags; a failure leaves the settings as they are. */
export async function loadLists(): Promise<void> {
  try {
    [app.sites, app.tags] = await Promise.all([get<Site[]>("/sites"), get<Dimension[]>("/tags")]);
    app.listsLoaded = true;
    app.listsFailed = false;
  } catch {
    app.listsFailed = true;
  }
}
