<script lang="ts">
  import GripVertical from "@jis3r/icons/icons/grip-vertical";
  import { tick } from "svelte";
  import { settings as copy } from "../../lang/zh-TW";
  import { moveTopic } from "../../lib/settings";
  import { moveTo, topics } from "../../state.svelte";

  let list: HTMLOListElement;
  const shown = $derived(topics());
  let preview = $state<string[] | null>(null);
  const order = $derived(preview ? preview.map((id) => shown.find((t) => t.id === id)!) : shown);
  let dragging = $state<string | null>(null);

  async function focus(id: string): Promise<void> {
    await tick();
    list.querySelector<HTMLElement>(`[data-topic="${CSS.escape(id)}"] .handle`)?.focus();
  }

  function keys(event: KeyboardEvent, id: string, at: number): void {
    if (event.key !== "ArrowUp" && event.key !== "ArrowDown") return;
    event.preventDefault();
    moveTo(id, at + (event.key === "ArrowUp" ? -1 : 1));
    void focus(id);
  }

  // The window follows the pointer: reordering moves the row's node, which would drop a capture.
  function down(event: PointerEvent, id: string): void {
    event.preventDefault();
    dragging = id;
    preview = shown.map((t) => t.id);
    addEventListener("pointermove", move);
    addEventListener("pointerup", up);
    addEventListener("pointercancel", up);
  }

  /** Drop the dragged row before the first other row whose middle is below the pointer. */
  function move(event: PointerEvent): void {
    if (!dragging || !preview) return;
    const others = [...list.children].filter((row) => (row as HTMLElement).dataset["topic"] !== dragging);
    const at = others.findIndex((row) => {
      const box = row.getBoundingClientRect();
      return event.clientY < box.top + box.height / 2;
    });
    preview = moveTopic(preview, dragging, at === -1 ? others.length : at);
  }

  function up(): void {
    removeEventListener("pointermove", move);
    removeEventListener("pointerup", up);
    removeEventListener("pointercancel", up);
    if (dragging && preview) {
      const id = dragging;
      moveTo(id, preview.indexOf(id));
      void focus(id);
    }
    dragging = null;
    preview = null;
  }
</script>

<ol class="sort" bind:this={list}>
  {#each order as topic, at (topic.id)}
    <li data-topic={topic.id} class:dragging={dragging === topic.id}>
      <button
        type="button"
        class="handle"
        aria-label={copy.move(topic.label)}
        onkeydown={(event) => keys(event, topic.id, at)}
        onpointerdown={(event) => down(event, topic.id)}
      >
        <span class="icon" aria-hidden="true"><GripVertical size={18} /></span>
      </button>{topic.label}
    </li>
  {/each}
</ol>

<style>
  .sort {
    list-style: none;
    margin: 8px 0 0;
    padding: 0;
    display: grid;
    gap: 6px;
  }
  li {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg);
    border-radius: 10px;
    padding: 4px 14px 4px 4px;
    font-size: var(--text-base);
    transition: box-shadow 0.15s;
  }
  li.dragging {
    background: var(--paper);
    box-shadow: var(--shadow);
    position: relative;
    z-index: 1;
  }
  .handle {
    display: grid;
    place-items: center;
    width: 40px;
    height: 40px;
    border: 0;
    background: none;
    color: var(--ink-3);
    border-radius: 8px;
    touch-action: none;
    cursor: grab;
  }
  .handle:active {
    cursor: grabbing;
  }
  .handle :global(div) {
    display: grid;
  }
</style>
