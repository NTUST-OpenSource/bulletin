<script lang="ts">
  import { ui } from "../../state.svelte";

  const SHORT = 2200;
  const WITH_ACTION = 5000;

  let node: HTMLDivElement;
  let shown = $state(false);

  // A modal dialog makes the rest of the page inert, so the notice moves into the open one.
  function host(): HTMLElement {
    const open = [...document.querySelectorAll<HTMLDialogElement>("dialog[open]")].filter(
      (dialog) => !dialog.classList.contains("confirm"),
    );
    return open.at(-1) ?? document.body;
  }

  $effect(() => {
    const notice = ui.notice;
    if (!notice) return;
    host().append(node);
    const frame = requestAnimationFrame(() => (shown = true));
    const timer = setTimeout(() => (ui.notice = null), notice.action ? WITH_ACTION : SHORT);
    return () => {
      cancelAnimationFrame(frame);
      clearTimeout(timer);
      shown = false;
    };
  });

  function act(): void {
    ui.notice?.action?.run();
    ui.notice = null;
  }
</script>

<div class="toast" class:show={shown && ui.notice} role="status" aria-live="polite" bind:this={node}>
  <span>{ui.notice?.message ?? ""}</span>
  {#if ui.notice?.action}
    <button type="button" onclick={act}>{ui.notice.action.label}</button>
  {/if}
</div>

<style>
  .toast {
    position: fixed;
    left: 50%;
    bottom: calc(24px + env(safe-area-inset-bottom, 0px));
    transform: translate(-50%, 16px);
    display: flex;
    align-items: center;
    gap: 14px;
    background: var(--ink);
    color: var(--bg);
    padding: 10px 12px 10px 18px;
    border-radius: 999px;
    font-size: var(--text-sm);
    box-shadow: var(--shadow);
    opacity: 0;
    pointer-events: none;
    transition:
      opacity 0.2s,
      transform 0.3s var(--ease);
    z-index: 50;
    max-width: calc(100vw - 32px);
    box-sizing: border-box;
    overflow-wrap: anywhere;
  }
  .toast.show {
    opacity: 1;
    transform: translate(-50%, 0);
    pointer-events: auto;
  }
  button {
    flex: none;
    border: 0;
    background: none;
    color: var(--accent);
    font-weight: 700;
    font-size: var(--text-sm);
    padding: 2px 6px;
  }
</style>
