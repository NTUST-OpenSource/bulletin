<script lang="ts">
  import ChevronLeft from "@jis3r/icons/icons/chevron-left";
  import ChevronRight from "@jis3r/icons/icons/chevron-right";
  import Minus from "@jis3r/icons/icons/minus";
  import Plus from "@jis3r/icons/icons/plus";
  import X from "@jis3r/icons/icons/x";
  import { tick } from "svelte";
  import { type Shown, viewer } from "../../article.svelte";
  import { article as articleCopy, preview as copy, stream as streamCopy } from "../../lang/zh-TW";
  import { raw } from "../../lib/raw";
  import IconButton from "../ui/IconButton.svelte";

  const STEP = 1.5; // a zoom button's factor
  const MAX_ZOOM = STEP ** 4;
  const WHEEL = 300; // wheel delta that zooms by a factor of e

  let dialog: HTMLDialogElement;
  let stage = $state<HTMLElement>();
  let image = $state<HTMLImageElement>();
  let status = $state<"loading" | "ready" | "failed">("loading");
  let html = $state(""); // a DOCX's text, sanitized
  let zoom = $state(1);
  let fit = $state(0); // the image's width at zoom 1

  const shown = $derived(viewer.shown);
  const picture = $derived(shown?.kind === "images" ? shown.pictures[shown.index] : undefined);
  const file = $derived(shown?.kind === "images" ? (picture?.file ?? null) : (shown?.file ?? null));
  const label = $derived(shown?.kind === "images" ? (file?.name ?? (picture?.alt || shown.title)) : (file?.name ?? ""));
  const school = $derived(file?.url ?? picture?.src ?? null);
  const count = $derived(shown?.kind === "images" ? shown.pictures.length : 0);

  $effect(() => {
    if (shown && !dialog.open) {
      dialog.showModal();
      dialog.focus();
    }
    if (!shown && dialog.open) dialog.close();
  });

  // Each picture or file starts unzoomed; a PDF's or DOCX's stored copy is read first.
  $effect(() => {
    const current = viewer.shown;
    void (current?.kind === "images" && current.index);
    zoom = 1;
    html = "";
    status = current?.kind === "images" ? "ready" : "loading";
    if (current === null || current.kind === "images") return;
    let gone = false;
    read(current).then(
      (text) => {
        if (gone) return;
        html = text;
        status = "ready";
      },
      () => {
        if (!gone) status = "failed";
      },
    );
    return () => {
      gone = true;
    };
  });

  /** Check that a stored PDF is there, or turn a stored DOCX into sanitized HTML. */
  async function read(current: Exclude<Shown, { kind: "images" }>): Promise<string> {
    const answer = await fetch(current.file.file!);
    if (!answer.ok) throw new Error(`${answer.status}`);
    if (current.kind === "pdf") {
      void answer.body?.cancel(); // the frame reads it
      return "";
    }
    const { default: mammoth } = await import("mammoth");
    const converted = await mammoth.convertToHtml({ arrayBuffer: await answer.arrayBuffer() });
    return raw(converted.value, current.file.url);
  }

  function close(): void {
    viewer.shown = null;
  }

  function step(by: number): void {
    if (viewer.shown?.kind === "images") viewer.shown.index = (viewer.shown.index + by + count) % count;
  }

  /** Zoom to `next`, keeping the point at the stage's center where it is. */
  async function zoomTo(next: number): Promise<void> {
    if (!stage || !image) return;
    if (zoom === 1) fit = image.clientWidth;
    const x = (stage.scrollLeft + stage.clientWidth / 2) / stage.scrollWidth;
    const y = (stage.scrollTop + stage.clientHeight / 2) / stage.scrollHeight;
    zoom = Math.min(MAX_ZOOM, Math.max(1, next));
    await tick();
    stage.scrollLeft = x * stage.scrollWidth - stage.clientWidth / 2;
    stage.scrollTop = y * stage.scrollHeight - stage.clientHeight / 2;
  }

  // Svelte adds wheel listeners as passive; zooming has to stop the page's scroll.
  $effect(() => {
    const target = stage;
    if (!target) return;
    const wheel = (event: WheelEvent) => {
      event.preventDefault();
      void zoomTo(zoom * Math.exp(-event.deltaY / WHEEL));
    };
    target.addEventListener("wheel", wheel, { passive: false });
    return () => target.removeEventListener("wheel", wheel);
  });

  // One pointer drags the zoomed image, two pinch it.
  const pointers = new Map<number, { x: number; y: number }>();
  let spread = 0; // the fingers' distance at a pinch's start, per unit of zoom

  const distance = () => {
    const [a, b] = [...pointers.values()];
    return a && b ? Math.hypot(a.x - b.x, a.y - b.y) : 0;
  };

  function down(event: PointerEvent): void {
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    stage?.setPointerCapture(event.pointerId);
    if (pointers.size === 2) spread = distance() / zoom;
  }

  function move(event: PointerEvent): void {
    const last = pointers.get(event.pointerId);
    if (!last || !stage) return;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size === 2) void zoomTo(distance() / spread);
    else stage.scrollBy(last.x - event.clientX, last.y - event.clientY);
  }

  function up(event: PointerEvent): void {
    pointers.delete(event.pointerId);
  }

  function keys(event: KeyboardEvent): void {
    if (count < 2) return;
    if (event.key === "ArrowLeft") step(-1);
    else if (event.key === "ArrowRight") step(1);
  }
</script>

<dialog
  class="preview"
  tabindex="-1"
  aria-label={label}
  bind:this={dialog}
  oncancel={(event) => {
    event.preventDefault();
    close();
  }}
  onclose={close}
  onkeydown={keys}
>
  <div class="p-bar">
    <IconButton label={articleCopy.close} icon={X} onclick={close} />
    <span class="p-name">{label}</span>
    {#if count > 1}<span class="p-count">{(shown?.kind === "images" ? shown.index : 0) + 1} / {count}</span>{/if}
    {#if picture && status === "ready"}
      <IconButton label={copy.zoomOut} icon={Minus} onclick={() => zoomTo(zoom / STEP)} />
      <IconButton label={copy.zoomIn} icon={Plus} onclick={() => zoomTo(zoom * STEP)} />
    {/if}
    {#if file?.file && status !== "failed"}<a class="btn" href={file.file} download>{copy.download}</a>{/if}
  </div>
  {#if status === "failed"}
    <div class="p-failed">
      <p>{copy.failed}</p>
      {#if school}<a class="btn" href={school} target="_blank" rel="noopener noreferrer">{copy.school}</a>{/if}
    </div>
  {:else if picture}
    <div
      class="stage"
      role="presentation"
      bind:this={stage}
      onpointerdown={down}
      onpointermove={move}
      onpointerup={up}
      onpointercancel={up}
    >
      <img
        src={picture.src}
        alt={picture.alt || label}
        draggable="false"
        class:zoomed={zoom > 1}
        style:width={zoom > 1 ? `${fit * zoom}px` : null}
        bind:this={image}
        onerror={() => (status = "failed")}
      />
    </div>
    {#if count > 1}
      <div class="p-step prev"><IconButton label={copy.previous} icon={ChevronLeft} onclick={() => step(-1)} /></div>
      <div class="p-step next"><IconButton label={copy.next} icon={ChevronRight} onclick={() => step(1)} /></div>
    {/if}
  {:else if status === "loading"}
    <div class="p-wait"><span class="spinner" role="status" aria-label={streamCopy.loading}></span></div>
  {:else if shown?.kind === "pdf"}
    <iframe src={shown.file.file} title={shown.file.name}></iframe>
  {:else if shown?.kind === "docx"}
    <!-- Sanitized by lib/raw.ts. -->
    <div class="p-docx"><div class="doc">{@html html}</div></div>
  {/if}
</dialog>

<style>
  .preview {
    width: 100vw;
    height: 100%;
    max-width: none;
    max-height: none;
    margin: 0;
    padding: 0;
    border-radius: 0;
    display: none;
    grid-template-rows: auto minmax(0, 1fr);
    grid-template-columns: minmax(0, 1fr);
    background: var(--paper);
  }
  .preview[open] {
    display: grid;
    animation: fade 0.16s ease-out;
  }
  @keyframes fade {
    from {
      opacity: 0;
    }
  }
  .p-bar {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: max(10px, env(safe-area-inset-top, 0px)) 14px 10px;
    border-bottom: 1px solid var(--line);
  }
  .p-name {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-weight: 600;
    font-size: var(--text-sm);
  }
  .p-count {
    font-size: var(--text-sm);
    color: var(--ink-3);
    font-variant-numeric: tabular-nums;
    margin-right: 4px;
  }
  .p-bar .btn {
    text-decoration: none;
    margin-left: 4px;
  }
  .stage {
    display: flex;
    overflow: auto;
    touch-action: none;
    background: var(--bg);
    cursor: grab;
  }
  .stage img {
    margin: auto; /* centered, and every edge reachable when larger than the stage */
    max-width: 100%;
    max-height: 100%;
    user-select: none;
  }
  .stage img.zoomed {
    max-width: none;
    max-height: none;
    height: auto;
  }
  .p-step {
    position: absolute;
    top: 50%;
    translate: 0 -50%;
  }
  .p-step :global(.icon-btn) {
    background: var(--paper);
    box-shadow: 0 1px 6px rgb(0 0 0 / 0.18);
  }
  .prev {
    left: max(12px, env(safe-area-inset-left, 0px));
  }
  .next {
    right: max(12px, env(safe-area-inset-right, 0px));
  }
  .p-wait,
  .p-failed {
    display: grid;
    place-content: center;
    justify-items: center;
    gap: 14px;
    padding: 24px;
    text-align: center;
    color: var(--ink-2);
  }
  .p-failed p {
    margin: 0;
  }
  .p-failed .btn {
    text-decoration: none;
  }
  iframe {
    width: 100%;
    height: 100%;
    border: 0;
    background: var(--bg);
  }
  .p-docx {
    overflow: auto;
    background: var(--bg);
    padding: 24px 16px calc(24px + env(safe-area-inset-bottom, 0px));
  }
  .doc {
    box-sizing: border-box;
    max-width: 760px;
    margin: 0 auto;
    padding: 32px 40px;
    background: var(--paper);
    border-radius: 10px;
    line-height: 1.8;
    overflow-wrap: anywhere;
  }
  .doc :global(p) {
    margin: 0 0 0.8em;
  }
  .doc :global(:is(h1, h2, h3, h4, h5, h6)) {
    font-size: var(--text-md);
    margin: 1.2em 0 0.4em;
  }
  .doc :global(table) {
    display: block;
    overflow-x: auto;
    border-collapse: collapse;
    font-size: var(--text-sm);
  }
  .doc :global(:is(td, th)) {
    border: 1px solid var(--line-2);
    padding: 6px 8px;
    vertical-align: top;
  }

  @media (max-width: 639px) {
    .doc {
      padding: 20px 18px;
    }
  }
</style>
