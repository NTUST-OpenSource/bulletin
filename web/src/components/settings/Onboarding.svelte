<script lang="ts">
  import { onboarding as copy, units } from "../../lang/zh-TW";
  import type { Site } from "../../lib/api";
  import { unitGroups } from "../../lib/units";
  import { app, setSettings, ui } from "../../state.svelte";
  import Tiles from "./Tiles.svelte";

  let dialog: HTMLDialogElement;
  let body: HTMLDivElement;
  let step = $state(0);
  let picks = $state<number[]>([]);

  $effect(() => {
    if (ui.onboarding && !dialog.open) {
      step = 0;
      picks = [...app.settings.sites];
      dialog.showModal();
    }
    if (!ui.onboarding && dialog.open) dialog.close();
  });

  const departments = $derived(
    unitGroups(
      app.sites.filter((site) => site.kind === "academic"),
      "",
      units.school,
      units.other,
    ),
  );
  const others = $derived(app.sites.filter((site) => site.kind !== "academic"));

  const picked = (site: Site) => picks.includes(site.id);
  const pick = (site: Site) => (picks = picked(site) ? picks.filter((id) => id !== site.id) : [...picks, site.id]);

  function go(to: number): void {
    step = to;
    body.scrollTop = 0;
  }

  function done(): void {
    ui.onboarding = false;
    setSettings({ ...app.settings, sites: picks });
  }
</script>

<!-- Without a user activation Chromium closes on Esc without a cancelable event, so it reopens. -->
<dialog
  class="onboard"
  bind:this={dialog}
  aria-labelledby="ob-title"
  oncancel={(event) => event.preventDefault()}
  onclose={() => ui.onboarding && dialog.showModal()}
>
  <div class="ob-head">
    <span class="brand">bulletin<i>.</i></span>
    <span class="dots" aria-hidden="true"><i class:on={step === 0}></i><i class:on={step === 1}></i></span>
  </div>
  <div class="ob-body" bind:this={body}>
    <div class="ob-inner">
      <h1 id="ob-title">{step === 0 ? copy.department : copy.others}</h1>
      {#if step === 0}
        {#each departments as group (group.title)}
          <section>
            <h2>{group.title}</h2>
            <Tiles sites={group.sites} {picked} {pick} />
          </section>
        {/each}
      {:else}
        <section><Tiles sites={others} {picked} {pick} /></section>
      {/if}
    </div>
  </div>
  <div class="ob-foot">
    {#if step === 0}
      <button type="button" class="btn ghost" onclick={() => go(1)}>{copy.skip}</button>
      <button type="button" class="btn primary" onclick={() => go(1)}>{copy.next}</button>
    {:else}
      <button type="button" class="btn ghost" onclick={() => go(0)}>{copy.back}</button>
      <button type="button" class="btn primary" onclick={done}>{copy.done}</button>
    {/if}
  </div>
</dialog>

<style>
  .onboard {
    width: 100vw;
    max-width: none;
    height: 100%;
    max-height: none;
    margin: 0;
    background: var(--bg);
    box-shadow: none;
  }
  .onboard[open] {
    display: grid;
    grid-template-rows: auto 1fr auto;
  }
  .ob-head,
  .ob-foot {
    padding: 20px max(24px, env(safe-area-inset-right, 0px)) 20px max(24px, env(safe-area-inset-left, 0px));
  }
  .ob-head {
    padding-top: max(20px, env(safe-area-inset-top, 0px));
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .dots {
    display: flex;
    gap: 6px;
  }
  .dots i {
    width: 22px;
    height: 4px;
    border-radius: 2px;
    background: var(--line-2);
  }
  .dots i.on {
    background: var(--accent);
  }
  .ob-body {
    overflow: auto;
    padding: 8px max(24px, env(safe-area-inset-right, 0px)) 24px max(24px, env(safe-area-inset-left, 0px));
  }
  .ob-inner {
    max-width: 820px;
    margin: 0 auto;
    padding-top: clamp(8px, 4vh, 40px);
    display: grid;
    gap: 28px;
  }
  h1 {
    margin: 0;
    font-size: clamp(1.75rem, 1.3rem + 2vw, 2.5rem);
    letter-spacing: -0.02em;
    line-height: 1.25;
  }
  h2 {
    margin: 0 0 10px;
    font-size: var(--text-sm);
    color: var(--ink-3);
    font-weight: 600;
  }
  .ob-foot {
    padding-bottom: max(20px, env(safe-area-inset-bottom, 0px));
    border-top: 1px solid var(--line);
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
  .ob-foot .btn {
    padding: 10px 22px;
    font-size: var(--text-base);
  }
  .ob-foot .ghost {
    margin-right: auto;
  }
</style>
