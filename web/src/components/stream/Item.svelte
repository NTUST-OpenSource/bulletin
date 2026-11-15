<script lang="ts">
  import { stream as copy } from "../../lang/zh-TW";
  import type { Item } from "../../lib/api";
  import { source } from "../../lib/stream";
  import { app } from "../../state.svelte";
  import { feed } from "../../stream.svelte";

  let { item }: { item: Item } = $props();
  const rewrite = $derived(app.settings.prefer === "rendition" ? item.rendition : null);
  const unit = $derived(item.unit ?? app.sites.find((site) => site.id === item.site)?.unit ?? "");
</script>

<li data-id={item.id} class:arrive={feed.arrived.has(item.id)}>
  <a class="item" href="/a/{item.id}">
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
