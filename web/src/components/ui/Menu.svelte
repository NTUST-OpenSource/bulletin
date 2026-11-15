<script lang="ts">
  import { tick } from "svelte";
  import { ui } from "../../state.svelte";

  const EDGE = 8;
  let menu: HTMLDivElement;
  let scrim: HTMLDivElement;

  // A modal dialog makes the rest of the page inert, so the menu moves into the open one.
  $effect(() => {
    const open = ui.menu;
    if (!open) return;
    const dialogs = [...document.querySelectorAll<HTMLDialogElement>("dialog[open]")];
    (dialogs.at(-1) ?? document.body).append(scrim, menu);
    void tick().then(() => {
      if (!open.sheet) {
        menu.style.left = `${Math.max(EDGE, Math.min(open.at.x, innerWidth - menu.offsetWidth - EDGE))}px`;
        menu.style.top = `${Math.max(EDGE, Math.min(open.at.y, innerHeight - menu.offsetHeight - EDGE))}px`;
      }
      menu.querySelector<HTMLElement>("[role=menuitem]")?.focus({ preventScroll: true });
    });
  });

  const close = () => (ui.menu = null);

  function keys(event: KeyboardEvent): void {
    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      close();
    } else if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const items = [...menu.querySelectorAll<HTMLElement>("[role=menuitem]")];
      const at = items.indexOf(document.activeElement as HTMLElement);
      const next = (at + (event.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
      items[next]?.focus();
    }
  }
</script>

<div class="menu-scrim" class:dim={ui.menu?.sheet} hidden={!ui.menu} bind:this={scrim} onclick={close} role="presentation"></div>
<div class="menu" class:sheet={ui.menu?.sheet} role="menu" tabindex="-1" hidden={!ui.menu} bind:this={menu} onkeydown={keys}>
  {#each ui.menu?.entries ?? [] as entry, index (index)}
    {#if entry === "-"}
      <hr />
    {:else if "href" in entry}
      <a role="menuitem" href={entry.href} target="_blank" rel="noopener noreferrer" onclick={close}>{entry.label}</a>
    {:else}
      <button
        type="button"
        role="menuitem"
        onclick={() => {
          close();
          entry.run();
        }}>{entry.label}</button
      >
    {/if}
  {/each}
</div>

<style>
  .menu {
    position: fixed;
    z-index: 40;
    min-width: 220px;
    max-width: min(320px, calc(100vw - 32px));
    box-sizing: border-box;
    padding: 6px;
    border-radius: 12px;
    background: var(--paper);
    box-shadow: var(--shadow);
    border: 1px solid var(--line);
    display: grid;
  }
  .menu[hidden],
  .menu-scrim[hidden] {
    display: none;
  }
  .menu button,
  .menu a {
    display: block;
    text-align: left;
    border: 0;
    background: none;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: var(--text-sm);
    color: var(--ink);
    text-decoration: none;
    overflow-wrap: anywhere;
  }
  .menu button:hover,
  .menu a:hover,
  .menu :focus-visible {
    background: var(--bg);
    outline: none;
  }
  hr {
    border: 0;
    height: 1px;
    background: var(--line);
    margin: 4px 6px;
  }
  .menu.sheet {
    left: 0 !important;
    right: 0;
    top: auto !important;
    bottom: 0;
    max-width: none;
    border-radius: 16px 16px 0 0;
    padding: 10px max(10px, env(safe-area-inset-right, 0px)) calc(10px + env(safe-area-inset-bottom, 0px))
      max(10px, env(safe-area-inset-left, 0px));
    animation: rise 0.25s var(--ease);
  }
  .menu.sheet button,
  .menu.sheet a {
    padding: 14px 16px;
    font-size: var(--text-base);
  }
  .menu-scrim {
    position: fixed;
    inset: 0;
    z-index: 39;
    background: transparent;
  }
  .menu-scrim.dim {
    background: var(--scrim);
  }
  @keyframes rise {
    from {
      transform: translateY(24px);
      opacity: 0;
    }
  }
</style>
