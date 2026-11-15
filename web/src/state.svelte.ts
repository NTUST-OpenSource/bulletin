// The page's state: the settings, kept in localStorage, and the API's lists.
import { type Dimension, get, type Site } from "./lib/api";
import { loadSettings, type Settings, saveSettings } from "./lib/settings";

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
  listsFailed: false,
});

/** What the page shows over the stream. */
export const ui = $state({
  sheet: null as null | "main" | "units",
});

/** Change and keep the settings; storage is written only here. */
export function setSettings(next: Settings): void {
  app.settings = next;
  app.saved = true;
  saveSettings(storage(), next);
}

/** Load the sites and the tags; a failure leaves the settings as they are. */
export async function loadLists(): Promise<void> {
  try {
    [app.sites, app.tags] = await Promise.all([get<Site[]>("/sites"), get<Dimension[]>("/tags")]);
    app.listsFailed = false;
  } catch {
    app.listsFailed = true;
  }
}
