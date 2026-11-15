<script lang="ts">
  import ArrowLeft from "@jis3r/icons/icons/arrow-left";
  import X from "@jis3r/icons/icons/x";
  import { settings as copy } from "../../lang/zh-TW";
  import type { Prefer, Theme } from "../../lib/settings";
  import { app, setSettings, ui } from "../../state.svelte";
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
