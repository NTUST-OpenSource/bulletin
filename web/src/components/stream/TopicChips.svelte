<script lang="ts">
  import ArrowLeftRight from "@jis3r/icons/icons/arrow-left-right";
  import ChevronDown from "@jis3r/icons/icons/chevron-down";
  import { tick } from "svelte";
  import { stream as copy } from "../../lang/zh-TW";
  import { moveTopic } from "../../lib/settings";
  import { app, filters, moveTo, openMenu, phone, topics, ui } from "../../state.svelte";

  const MOUSE_SLOP = 6; // pixels a mouse moves before a press becomes a drag
  const TOUCH_SLOP = 10; // pixels a finger moves before a press becomes a scroll
  const HOLD = 400; // milliseconds a finger holds before a press becomes a drag
  const EDGE = 40; // pixels from the row's ends where a drag scrolls it
  const SPEED = 8;

  let row: HTMLDivElement;
  const shown = $derived(topics());
  let preview = $state<string[] | null>(null); // the order while a chip is dragged
  const order = $derived(preview ? preview.map((id) => shown.find((t) => t.id === id)!) : shown);
  const followed = $derived(app.sites.filter((site) => app.settings.sites.includes(site.id)));
  const unit = $derived(followed.find((site) => site.id === filters.unit));

  $effect(() => {
    if (filters.unit !== null && app.sites.length && !unit) filters.unit = null; // unfollowed meanwhile
  });

  function unitMenu(event: MouseEvent): void {
    const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
    openMenu(
      [
        { label: copy.allUnits, run: () => (filters.unit = null) },
        "-",
        ...followed.map((site) => ({ label: site.unit, run: () => (filters.unit = site.id) })),
      ],
      { x: box.left, y: box.bottom + 6 },
      phone(),
    );
  }

  async function focusTopic(id: string): Promise<void> {
    await tick();
    row.querySelector<HTMLElement>(`[data-topic="${CSS.escape(id)}"]`)?.focus();
  }

  function keys(event: KeyboardEvent, id: string, at: number): void {
    if (!event.altKey || (event.key !== "ArrowLeft" && event.key !== "ArrowRight")) return;
    event.preventDefault();
    moveTo(id, at + (event.key === "ArrowLeft" ? -1 : 1));
    void focusTopic(id);
  }

  type Press = { id: string; x: number; y: number; pointer: number; touch: boolean; timer?: number };
  let press: Press | null = null;
  let dragging = $state<string | null>(null);
  let pointerX = 0;
  let frame = 0;
  let swallowClick = false;

  // The window follows the pointer: reordering moves the chip's node, which would drop a capture.
  function down(event: PointerEvent, id: string): void {
    if (event.button !== 0) return;
    press = { id, x: event.clientX, y: event.clientY, pointer: event.pointerId, touch: event.pointerType === "touch" };
    if (press.touch) press.timer = window.setTimeout(start, HOLD);
    addEventListener("pointermove", move);
    addEventListener("pointerup", up);
    addEventListener("pointercancel", cancel);
  }

  function start(): void {
    if (!press) return;
    dragging = press.id;
    preview = shown.map((t) => t.id);
    navigator.vibrate?.(8);
    frame = requestAnimationFrame(scroll);
  }

  function move(event: PointerEvent): void {
    if (!press || event.pointerId !== press.pointer) return;
    pointerX = event.clientX;
    const moved = Math.hypot(event.clientX - press.x, event.clientY - press.y);
    if (!dragging) {
      if (press.touch && moved >= TOUCH_SLOP) cancel();
      else if (!press.touch && moved >= MOUSE_SLOP) start();
      return;
    }
    place();
  }

  /** Drop the dragged chip before the first other chip whose middle is right of the pointer. */
  function place(): void {
    if (!dragging || !preview) return;
    const others = [...row.querySelectorAll<HTMLElement>("[data-topic]")].filter((c) => c.dataset["topic"] !== dragging);
    const at = others.findIndex((chip) => {
      const box = chip.getBoundingClientRect();
      return pointerX < box.left + box.width / 2;
    });
    preview = moveTopic(preview, dragging, at === -1 ? others.length : at);
  }

  function scroll(): void {
    const box = row.getBoundingClientRect();
    if (pointerX < box.left + EDGE) row.scrollLeft -= SPEED;
    else if (pointerX > box.right - EDGE) row.scrollLeft += SPEED;
    place();
    frame = requestAnimationFrame(scroll);
  }

  function up(event: PointerEvent): void {
    if (!press || event.pointerId !== press.pointer) return;
    if (dragging && preview) {
      moveTo(dragging, preview.indexOf(dragging));
      swallowClick = true;
    }
    cancel();
  }

  function cancel(): void {
    removeEventListener("pointermove", move);
    removeEventListener("pointerup", up);
    removeEventListener("pointercancel", cancel);
    clearTimeout(press?.timer);
    cancelAnimationFrame(frame);
    press = null;
    dragging = null;
    preview = null;
  }

  function pick(id: string): void {
    if (swallowClick) swallowClick = false;
    else filters.topic = id;
  }

  // A finger that holds a chip drags it instead of scrolling the row.
  function holdScroll(event: TouchEvent): void {
    if (dragging) event.preventDefault();
  }

  $effect(() => {
    row.addEventListener("touchmove", holdScroll, { passive: false });
    return () => row.removeEventListener("touchmove", holdScroll);
  });
</script>

<div class="filters" role="toolbar" aria-label={copy.filters} bind:this={row}>
  <button type="button" class="chip unit-chip" aria-haspopup="menu" aria-pressed={!!unit} onclick={unitMenu}>
    {unit?.unit ?? copy.allUnits}<span class="icon" aria-hidden="true"><ChevronDown size={12} strokeWidth={2.6} /></span>
  </button>
  <button type="button" class="chip" aria-pressed={filters.topic === null} onclick={() => (filters.topic = null)}
    >{copy.allTopics}</button
  >
  {#each order as topic, at (topic.id)}
    <button
      type="button"
      class="chip"
      class:dragging={dragging === topic.id}
      data-topic={topic.id}
      aria-pressed={filters.topic === topic.id}
      onclick={() => pick(topic.id)}
      onkeydown={(event) => keys(event, topic.id, at)}
      onpointerdown={(event) => down(event, topic.id)}>{topic.label}</button
    >
  {/each}
  <button type="button" class="chip edit" aria-label={copy.reorder} onclick={() => (ui.sheet = "topics")}>
    <span class="icon" aria-hidden="true"><ArrowLeftRight size={16} strokeWidth={2.2} /></span>
  </button>
</div>

<style>
  .filters {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    scrollbar-width: none;
    padding: 4px 40px 10px 2px;
    margin: 0 -2px;
    mask-image: linear-gradient(90deg, #000 calc(100% - 48px), transparent);
  }
  .filters::-webkit-scrollbar {
    display: none;
  }
  .chip {
    flex: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1px solid var(--line-2);
    background: transparent;
    border-radius: 999px;
    padding: 5px 14px;
    font-size: var(--text-sm);
    color: var(--ink-2);
    white-space: nowrap;
    -webkit-user-select: none;
    user-select: none;
    -webkit-touch-callout: none;
  }
  .chip:hover {
    border-color: var(--ink-3);
    color: var(--ink);
  }
  .chip[aria-pressed="true"] {
    background: var(--ink);
    border-color: var(--ink);
    color: var(--bg);
  }
  .chip.dragging {
    box-shadow: var(--shadow);
    background: var(--paper);
    color: var(--ink);
    cursor: grabbing;
  }
  .unit-chip {
    border-style: dashed;
  }
  .unit-chip[aria-pressed="true"] {
    border-style: solid;
  }
  .edit {
    padding: 5px 10px;
    border-color: transparent;
    color: var(--ink-3);
  }
  .chip :global(div) {
    display: grid;
  }
</style>
