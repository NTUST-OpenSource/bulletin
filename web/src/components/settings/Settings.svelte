<script lang="ts">
  import ArrowLeft from "@jis3r/icons/icons/arrow-left";
  import X from "@jis3r/icons/icons/x";
  import { settings as copy, transfer } from "../../lang/zh-TW";
  import { type Prefer, readImport, settingsLink, type Theme } from "../../lib/settings";
  import { app, ask, clearSettings, notify, offerSettings, setSettings, ui } from "../../state.svelte";
  import IconButton from "../ui/IconButton.svelte";
  import UnitPicker from "./UnitPicker.svelte";

  let dialog: HTMLDialogElement;

  $effect(() => {
    if (ui.sheet && !dialog.open) dialog.showModal();
    if (!ui.sheet && dialog.open) dialog.close();
  });

  const themes: Theme[] = ["system", "light", "dark"];
  const prefers: Prefer[] = ["rendition", "raw"];
  const followed = $derived(app.sites.filter((site) => app.settings.sites.includes(site.id)));
  const hidden = $derived(
    app.sites.flatMap((site) =>
      site.boards.filter((board) => app.settings.hiddenBoards.includes(board.key)).map((board) => ({ site, board })),
    ),
  );

  function unhide(key: string): void {
    setSettings({ ...app.settings, hiddenBoards: app.settings.hiddenBoards.filter((k) => k !== key) });
  }

  let pasted = $state("");
  let importError = $state("");
  const json = () => JSON.stringify(app.settings, null, 2);

  async function copyText(text: string, done: string): Promise<void> {
    try {
      await navigator.clipboard.writeText(text);
      notify(done);
    } catch {
      notify(transfer.noClipboard);
    }
  }

  function download(): void {
    const url = URL.createObjectURL(new Blob([json()], { type: "application/json" }));
    const link = Object.assign(document.createElement("a"), { href: url, download: "bulletin-settings.json" });
    link.click();
    setTimeout(() => URL.revokeObjectURL(url));
  }

  /** Offer what was read, or say why it cannot be; the sheet closes first, as the offer may ask. */
  function offer(text: string, unreadable: string): void {
    try {
      const next = readImport(text);
      importError = "";
      ui.sheet = null;
      void offerSettings(next, "import");
    } catch {
      importError = unreadable;
    }
  }

  async function pickFile(event: Event): Promise<void> {
    const input = event.currentTarget as HTMLInputElement;
    const file = input.files?.[0];
    input.value = "";
    if (file) offer(await file.text(), copy.unreadableFile);
  }

  async function reset(): Promise<void> {
    ui.sheet = null;
    if (await ask(copy.resetAsk)) clearSettings();
  }

  $effect(() => {
    if (!ui.sheet) importError = pasted = "";
  });
</script>

<dialog class="sheet" bind:this={dialog} aria-labelledby="settings-title" onclose={() => (ui.sheet = null)}>
  <div class="sheet-head" class:sub={ui.sheet === "units"}>
    {#if ui.sheet === "units"}
      <IconButton label={copy.back} icon={ArrowLeft} onclick={() => (ui.sheet = "main")} />
    {/if}
    <h2 id="settings-title">{ui.sheet === "units" ? copy.units : copy.title}</h2>
    <IconButton label={copy.close} icon={X} onclick={() => (ui.sheet = null)} />
  </div>
  <div class="sheet-body">
    {#if ui.sheet === "units"}
      <UnitPicker />
    {:else}
      <section class="set">
        <h3>{copy.appearance}</h3>
        <div class="seg" role="group" aria-label={copy.appearance}>
          {#each themes as theme (theme)}
            <button
              type="button"
              aria-pressed={app.settings.theme === theme}
              onclick={() => setSettings({ ...app.settings, theme })}>{copy.themes[theme]}</button
            >
          {/each}
        </div>
      </section>
      <section class="set">
        <h3>{copy.display}</h3>
        <div class="seg" role="group" aria-label={copy.display}>
          {#each prefers as prefer (prefer)}
            <button
              type="button"
              aria-pressed={app.settings.prefer === prefer}
              onclick={() => setSettings({ ...app.settings, prefer })}>{copy.prefers[prefer]}</button
            >
          {/each}
        </div>
      </section>
      <section class="set">
        <div class="set-head">
          <h3>{copy.units}</h3>
          <button type="button" class="link-btn" onclick={() => (ui.sheet = "units")}>{copy.edit}</button>
        </div>
        {#if followed.length}
          <div class="mini">
            {#each followed as site (site.id)}<span>{site.unit}</span>{/each}
          </div>
        {/if}
      </section>
      {#if hidden.length}
        <section class="set">
          <h3>{copy.hidden}</h3>
          <div class="rows">
            {#each hidden as { site, board } (board.key)}
              <div>
                <span>{site.unit} · {board.name}</span>
                <button type="button" class="link-btn" onclick={() => unhide(board.key)}>{copy.show}</button>
              </div>
            {/each}
          </div>
        </section>
      {/if}
      <section class="set">
        <h3>{copy.export}</h3>
        <div class="row-btns">
          <button type="button" class="btn" onclick={() => copyText(json(), transfer.copiedJson)}>{copy.copyJson}</button>
          <button type="button" class="btn" onclick={download}>{copy.download}</button>
          <button
            type="button"
            class="btn"
            onclick={() => copyText(settingsLink(location.origin, app.settings), transfer.copiedLink)}
            >{copy.copyLink}</button
          >
        </div>
      </section>
      <section class="set">
        <h3>{copy.import}</h3>
        <label class="sr" for="import-text">{copy.importLabel}</label>
        <textarea class="field" id="import-text" rows="3" placeholder={copy.importPlaceholder} bind:value={pasted}
        ></textarea>
        {#if importError}<p class="err" role="alert">{importError}</p>{/if}
        <div class="row-btns">
          <button type="button" class="btn primary" onclick={() => offer(pasted, copy.unreadablePaste)}>{copy.import}</button>
          <label class="btn" for="import-file">{copy.chooseFile}</label>
          <input id="import-file" type="file" accept=".json,application/json" hidden onchange={pickFile} />
        </div>
      </section>
      <section class="set">
        <div class="row-btns">
          <button type="button" class="btn danger" onclick={reset}>{copy.reset}</button>
        </div>
        <p class="note">{copy.note}</p>
      </section>
    {/if}
  </div>
</dialog>

<style>
  .sheet {
    width: min(480px, 100vw);
    max-width: 100vw;
    height: 100%;
    max-height: 100%;
    margin: 0 0 0 auto;
    border-radius: 0;
  }
  .sheet[open] {
    display: flex;
    flex-direction: column;
  }
  .sheet-head {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: max(14px, env(safe-area-inset-top, 0px)) 14px 10px 24px;
  }
  .sheet-head.sub {
    padding-left: 12px;
  }
  .sheet-head h2 {
    margin: 0 auto 0 0;
    font-size: var(--text-lg);
  }
  .sheet-body {
    overflow: auto;
    padding: 0 max(24px, env(safe-area-inset-right, 0px)) 40px 24px;
    display: grid;
    align-content: start;
  }
  .set {
    padding: 20px 0;
    border-top: 1px solid var(--line);
    display: grid;
    gap: 12px;
  }
  .set-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .set h3 {
    margin: 0;
    font-size: var(--text-sm);
  }
  .seg {
    display: inline-flex;
    justify-self: start;
    background: var(--bg);
    border-radius: 999px;
    padding: 3px;
    gap: 2px;
  }
  .seg button {
    border: 0;
    background: none;
    border-radius: 999px;
    padding: 5px 16px;
    font-size: var(--text-sm);
    color: var(--ink-2);
  }
  .seg button[aria-pressed="true"] {
    background: var(--paper);
    color: var(--ink);
    font-weight: 600;
    box-shadow: 0 1px 3px rgb(0 0 0 / 0.14);
  }
  .mini {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .mini span {
    font-size: var(--text-sm);
    background: var(--bg);
    border-radius: 999px;
    padding: 3px 12px;
    overflow-wrap: anywhere;
  }
  .rows {
    display: grid;
  }
  .rows div {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-height: 40px;
    font-size: var(--text-sm);
  }
  .rows span {
    min-width: 0;
    overflow-wrap: anywhere;
  }
  .err {
    color: var(--gone);
    font-size: var(--text-xs);
    margin: 0;
  }
  label.btn {
    cursor: pointer;
  }
  .note {
    margin: 8px 0 0;
    font-size: var(--text-xs);
    color: var(--ink-3);
    line-height: 1.6;
  }

  @media (max-width: 639px) {
    .sheet {
      width: 100vw;
    }
  }
</style>
