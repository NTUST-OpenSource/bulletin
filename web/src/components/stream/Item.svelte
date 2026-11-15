<script lang="ts">
  import { stream as copy } from "../../lang/zh-TW";
  import type { Item } from "../../lib/api";
  import { source } from "../../lib/stream";
  import { app } from "../../state.svelte";
  import { feed } from "../../stream.svelte";
  import { openItem } from "../../article.svelte";
  import { itemMenu } from "./itemMenu";

  const HOLD = 500; // milliseconds a finger holds before the menu opens
  const SLOP = 10; // pixels a finger moves before the hold is a scroll

  let { item }: { item: Item } = $props();
  const rewrite = $derived(app.settings.prefer === "rendition" ? item.rendition : null);
  const unit = $derived(item.unit ?? app.sites.find((site) => site.id === item.site)?.unit ?? "");

  let press: { x: number; y: number; timer: number } | null = null;
  let held = false; // the hold opened the menu, so the click that follows does not open the item

  function context(event: MouseEvent): void {
    event.preventDefault();
    if (held) return;
    const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
    const keyboard = event.clientX === 0 && event.clientY === 0;
    itemMenu(item, keyboard ? { x: box.left + 16, y: box.top + 24 } : { x: event.clientX, y: event.clientY });
  }

  function keys(event: KeyboardEvent): void {
    if (event.key !== "ContextMenu" && !(event.shiftKey && event.key === "F10")) return;
    event.preventDefault();
    const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
    itemMenu(item, { x: box.left + 16, y: box.top + 24 });
  }

  function down(event: PointerEvent): void {
    if (event.pointerType !== "touch") return;
    held = false;
    const at = { x: event.clientX, y: event.clientY };
    press = {
      ...at,
      timer: window.setTimeout(() => {
        held = true;
        navigator.vibrate?.(8);
        itemMenu(item, at, true);
      }, HOLD),
    };
  }

  function move(event: PointerEvent): void {
    if (press && Math.hypot(event.clientX - press.x, event.clientY - press.y) >= SLOP) release();
  }

  function release(): void {
    if (press) clearTimeout(press.timer);
    press = null;
  }

  function click(event: MouseEvent): void {
    if (held) {
      event.preventDefault();
      held = false;
    } else if (!item.link_item && event.button === 0 && !(event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)) {
      event.preventDefault(); // the article opens over the stream; other clicks keep the browser's tabs
      openItem(item.id);
    }
  }
</script>

<li data-id={item.id} class:arrive={feed.arrived.has(item.id)}>
  <a
    class="item"
    href={item.link_item ? item.url : `/a/${item.id}`}
    target={item.link_item ? "_blank" : null}
    rel={item.link_item ? "noopener noreferrer" : null}
    oncontextmenu={context}
    onkeydown={keys}
    onpointerdown={down}
    onpointermove={move}
    onpointerup={release}
    onpointercancel={release}
    onclick={click}
  >
    <span class="sec">{source(item, app.sites, app.settings)}</span>
    <span class="title">{rewrite?.title ?? item.title}</span>
    {#if rewrite?.summary}<span class="sum">{rewrite.summary}</span>{/if}
    <span class="foot">
      {#if item.withdrawn_at}<span class="gone">{copy.withdrawn}</span>{/if}
      <span class="pri">{unit}</span>
    </span>
  </a>
</li>

<style>
  li {
    display: grid;
    grid-template-rows: 1fr;
  }
  li.arrive {
    clip-path: inset(0 -24px);
    animation: arrive 0.7s var(--ease) both;
  }
  li.arrive > .item {
    min-height: 0;
    animation: glow 2.6s ease-out 0.3s both;
  }
  @keyframes arrive {
    from {
      grid-template-rows: 0fr;
      opacity: 0;
    }
  }
  @keyframes glow {
    from {
      background: var(--accent-soft);
    }
    to {
      background: transparent;
    }
  }
  .item {
    display: grid;
    gap: 3px;
    padding: 16px 16px 14px;
    margin: 0 -16px;
    border-radius: 12px;
    text-decoration: none;
    color: inherit;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    user-select: none;
    transition: background 0.15s;
  }
  .item:hover {
    background: var(--paper);
  }
  .item:hover .title {
    color: var(--accent);
  }
  .sec {
    font-size: var(--text-xs);
    color: var(--ink-3);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .title {
    font-size: var(--text-md);
    font-weight: 650;
    line-height: 1.45;
    overflow-wrap: anywhere;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    transition: color 0.15s;
  }
  .sum {
    font-size: var(--text-sm);
    color: var(--ink-2);
    overflow-wrap: anywhere;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .foot {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-top: 3px;
    font-size: var(--text-xs);
  }
  .gone {
    color: var(--gone);
    font-weight: 600;
  }
  .pri {
    margin-left: auto;
    color: var(--ink-3);
    text-align: right;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

  @media (max-width: 639px) {
    .item {
      margin: 0 -10px;
      padding: 14px 10px 12px;
    }
  }
</style>
