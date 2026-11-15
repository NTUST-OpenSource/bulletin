<script lang="ts">
  import X from "@jis3r/icons/icons/x";
  import { closeArticle, reader } from "../../article.svelte";
  import { article as copy, days, menu as menuCopy } from "../../lang/zh-TW";
  import { markdown } from "../../lib/markdown";
  import { raw } from "../../lib/raw";
  import { heading, source, today } from "../../lib/stream";
  import { app, copyText, filters, openMenu, ui } from "../../state.svelte";
  import IconButton from "../ui/IconButton.svelte";
  import More from "../ui/More.svelte";

  let dialog: HTMLDialogElement;

  $effect(() => {
    if (reader.id !== null && !dialog.open) {
      dialog.showModal();
      dialog.focus(); // the reader scrolls with the keys at once; the close button stays unfocused
      dialog.scrollTop = 0;
    }
    if (reader.id === null && dialog.open) dialog.close();
  });

  const a = $derived(reader.article);
  const school = $derived(!a?.rendition || (reader.mode ?? app.settings.prefer) === "raw");
  const body = $derived(
    !a ? "" : school ? raw(a.body_html ?? "", a.url) : a.rendition ? markdown(a.rendition.markdown) : "",
  );
  const when = $derived.by(() => {
    if (!a) return "";
    const h = heading(a.day, today(new Date()));
    const unit = a.unit ?? app.sites.find((site) => site.id === a.site)?.unit;
    return [`${days.date(h.month, h.date, h.year)} ${days.weekday(h.weekday)}`, unit].filter(Boolean).join(" · ");
  });
  const labels = (dimension: string) =>
    new Map(app.tags.find((d) => d.id === dimension)?.tags.map((tag) => [tag.id, tag.label]) ?? []);
  const topics = $derived(a ? a.tags.topic.flatMap((id) => (labels("topic").has(id) ? [{ id, label: labels("topic").get(id)! }] : [])) : []);
  const audiences = $derived(a ? a.tags.audience.flatMap((id) => labels("audience").get(id) ?? []) : []);

  function more(event: MouseEvent): void {
    if (!a) return;
    const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
    const toggle = a.rendition
      ? [{ label: school ? copy.showRewrite : copy.showSchool, run: () => (reader.mode = school ? "rendition" : "raw") }]
      : [];
    openMenu(
      [
        ...toggle,
        { label: menuCopy.copyLink, run: () => copyText(`${location.origin}/a/${a.id}`, menuCopy.copied) },
        { label: menuCopy.openSchool, href: a.url },
      ],
      { x: box.right - 220, y: box.bottom + 4 },
      false,
    );
  }

  function byTopic(id: string): void {
    filters.topic = id;
    closeArticle();
    scrollTo({ top: 0 });
  }
</script>

<dialog
  class="article"
  tabindex="-1"
  bind:this={dialog}
  aria-labelledby="a-title"
  oncancel={(event) => {
    event.preventDefault();
    if (ui.menu) ui.menu = null;
    else closeArticle();
  }}
  onclose={closeArticle}
  onclick={(event) => event.target === dialog && closeArticle()}
>
  <div class="a-bar">
    <IconButton label={copy.close} icon={X} onclick={closeArticle} />
    {#if a}<IconButton label={copy.more} icon={More} onclick={more} />{/if}
  </div>
  {#if a}
    <article class="doc">
      <span class="sec">{source(a, app.sites, app.settings)}</span>
      <h1 id="a-title">{school ? a.title : a.rendition?.title}</h1>
      <p class="when">
        {when}{#if a.withdrawn_at}{" · "}<span class="gone">{copy.withdrawn}</span>{/if}
      </p>
      {#if !school && a.rendition?.summary}<p class="lede">{a.rendition.summary}</p>{/if}
      <!-- eslint-disable-next-line svelte/no-at-html-tags -- escaped by lib/markdown.ts or sanitized by lib/raw.ts -->
      {#if body}<div class="body">{@html body}</div>{/if}
      {#if topics.length || audiences.length}
        <div class="tags">
          {#each topics as topic (topic.id)}
            <button type="button" class="chip" onclick={() => byTopic(topic.id)}>{topic.label}</button>
          {/each}
          {#each audiences as audience (audience)}<span class="chip">{audience}</span>{/each}
        </div>
      {/if}
    </article>
  {/if}
</dialog>

<style>
  .article {
    width: min(960px, calc(100vw - 64px));
    max-width: none;
    height: calc(100% - 48px);
    max-height: none;
    margin: 24px auto;
    border-radius: 16px;
    overflow: auto;
    overscroll-behavior: contain;
  }
  .article[open] {
    animation: fade 0.2s ease-out;
  }
  .doc {
    padding: 0 72px 80px;
    display: grid;
    gap: 20px;
    animation: rise 0.32s var(--ease);
  }
  @keyframes fade {
    from {
      opacity: 0;
    }
  }
  @keyframes rise {
    from {
      transform: translateY(24px);
      opacity: 0;
    }
  }
  .a-bar {
    position: sticky;
    top: 0;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    padding: 12px 14px;
    background: var(--paper);
  }
  .sec {
    font-size: var(--text-sm);
    color: var(--accent);
    overflow-wrap: anywhere;
  }
  h1 {
    margin: -14px 0 0;
    font-size: var(--text-xl);
    line-height: 1.35;
    letter-spacing: -0.01em;
    text-wrap: pretty;
    overflow-wrap: anywhere;
  }
  .when {
    margin: -10px 0 0;
    font-size: var(--text-sm);
    color: var(--ink-3);
  }
  .gone {
    color: var(--gone);
    font-weight: 600;
  }
  .lede {
    margin: 0;
    font-size: 1.125rem;
    line-height: 1.75;
    color: var(--ink);
    overflow-wrap: anywhere;
  }
  .body {
    font-size: var(--text-base);
    line-height: 1.85;
    overflow-wrap: anywhere;
    min-width: 0;
    color: var(--ink);
  }
  .body > :global(:first-child) {
    margin-top: 0;
  }
  .body :global(:is(h1, h2, h3, h4, h5, h6)) {
    margin: 1.5em 0 0.4em;
    line-height: 1.4;
  }
  /* The school's pages use h1 and h2 inside the body; they rank below the article's title. */
  .body :global(:is(h1, h2, h3)) {
    font-size: var(--text-lg);
  }
  .body :global(h4) {
    font-size: var(--text-md);
  }
  .body :global(:is(h5, h6)) {
    font-size: var(--text-base);
  }
  .body :global(hr) {
    border: 0;
    border-top: 1px solid var(--line);
    margin: 1.5em 0;
  }
  .body :global(p) {
    margin: 0 0 0.9em;
  }
  .body :global(:is(ul, ol)) {
    margin: 0 0 0.9em;
    padding-left: 1.4em;
  }
  .body :global(li) {
    margin: 0.2em 0;
  }
  .body :global(.sub) {
    font-size: var(--text-sm);
    color: var(--ink-3);
  }
  .body :global(blockquote) {
    margin: 0 0 0.9em;
    padding-left: 14px;
    border-left: 3px solid var(--line-2);
    color: var(--ink-2);
  }
  .body :global(code) {
    font-size: 0.9em;
    background: var(--bg);
    padding: 1px 4px;
    border-radius: 4px;
  }
  .body :global(img) {
    display: block;
    max-width: 100%;
    height: auto;
    border-radius: 10px;
    margin: 14px 0;
    background: var(--bg);
  }
  .body :global(.table-wrap) {
    overflow-x: auto;
    margin: 0 0 1em;
  }
  .body :global(table) {
    border-collapse: collapse;
    font-size: var(--text-sm);
    min-width: 100%;
  }
  .body :global(:is(td, th)) {
    border: 1px solid var(--line-2);
    padding: 6px 8px;
    vertical-align: top;
  }
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid var(--line);
  }
  .chip {
    display: inline-flex;
    align-items: center;
    border: 1px solid var(--line-2);
    background: transparent;
    border-radius: 999px;
    padding: 5px 14px;
    font-size: var(--text-sm);
    color: var(--ink-2);
  }
  button.chip:hover {
    border-color: var(--ink-3);
    color: var(--ink);
  }

  @media (max-width: 639px) {
    .article {
      width: 100vw;
      height: 100%;
      margin: 0;
      border-radius: 0;
    }
    .a-bar {
      padding-top: max(12px, env(safe-area-inset-top, 0px));
    }
    .doc {
      padding: 0 max(18px, env(safe-area-inset-right, 0px)) calc(56px + env(safe-area-inset-bottom, 0px))
        max(18px, env(safe-area-inset-left, 0px));
      gap: 18px;
    }
    h1 {
      font-size: 1.375rem;
      margin-top: -10px;
    }
  }
  @media (min-width: 640px) and (max-width: 1023px) {
    .doc {
      padding-inline: 48px;
    }
  }
</style>
