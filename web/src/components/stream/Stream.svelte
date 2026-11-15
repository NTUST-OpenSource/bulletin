<script lang="ts">
  import { stream as copy } from "../../lang/zh-TW";
  import { streamQuery } from "../../lib/api";
  import { byDay, today } from "../../lib/stream";
  import { app, filters, ui } from "../../state.svelte";
  import { feed, open } from "../../stream.svelte";
  import DaySection from "./DaySection.svelte";

  const topics = $derived(app.tags.find((dimension) => dimension.id === "topic")?.tags.map((tag) => tag.id) ?? []);
  const query = $derived(app.listsLoaded ? streamQuery(app.settings, app.sites, topics, filters) : undefined);
  const filtered = $derived(filters.topic !== null || filters.unit !== null);

  $effect(() => {
    if (query !== undefined) void open(query);
  });

  const days = $derived(byDay(feed.items));
  const now = today(new Date());

  function clear(): void {
    filters.topic = null;
    filters.unit = null;
  }
</script>

{#if query === null && filters.q === ""}
  <div class="empty">
    <b>{copy.nothingFollowed}</b>
    <button type="button" class="btn primary" onclick={() => (ui.sheet = "units")}>{copy.pickUnits}</button>
  </div>
{:else if query !== undefined && !feed.loading && !feed.failed && feed.items.length === 0}
  <div class="empty">
    <b>{copy.nothingFound}</b>
    {#if filtered}<button type="button" class="btn" onclick={clear}>{copy.clearFilters}</button>{/if}
  </div>
{/if}
{#each days as day (day.day)}
  <DaySection {day} today={now} />
{/each}
{#if feed.loading}
  <div class="more"><span class="spinner" role="status" aria-label={copy.loading}></span></div>
{/if}

<style>
  .empty {
    display: grid;
    justify-items: center;
    gap: 12px;
    padding: 72px 16px;
    text-align: center;
    color: var(--ink-2);
  }
  .empty b {
    font-size: var(--text-md);
    color: var(--ink);
  }
  .more {
    display: grid;
    place-items: center;
    height: 72px;
  }
  .spinner {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 2.5px solid var(--line-2);
    border-top-color: var(--accent);
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(1turn);
    }
  }
</style>
