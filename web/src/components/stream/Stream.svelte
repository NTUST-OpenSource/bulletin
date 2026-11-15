<script lang="ts">
  import { stream as copy } from "../../lang/zh-TW";
  import { streamQuery } from "../../lib/api";
  import { byDay, today } from "../../lib/stream";
  import { tick } from "svelte";
  import { keepPlace } from "../../lib/anchor";
  import { app, filters, ui } from "../../state.svelte";
  import { CHECK_MS, checkNow, feed, more, open, setPlace } from "../../stream.svelte";
  import DaySection from "./DaySection.svelte";

  const topics = $derived(app.tags.find((dimension) => dimension.id === "topic")?.tags.map((tag) => tag.id) ?? []);
  const query = $derived(app.listsLoaded ? streamQuery(app.settings, app.sites, topics, filters) : undefined);
  const filtered = $derived(filters.topic !== null || filters.unit !== null);

  $effect(() => {
    if (query !== undefined) void open(query);
  });

  const days = $derived(byDay(feed.items));
  const now = today(new Date());

  let list: HTMLElement;
  let sentinel: HTMLElement;

  // Near the end, the next page loads; observing again reports a sentinel still in view.
  $effect(() => {
    const observer = new IntersectionObserver(
      async ([entry]) => {
        if (!entry?.isIntersecting || feed.next === null || feed.loading || feed.failed) return;
        await more();
        await tick();
        observer.unobserve(sentinel);
        observer.observe(sentinel);
      },
      { rootMargin: "800px 0px" },
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  });

  const header = () => document.querySelector("header")?.getBoundingClientRect().bottom ?? 0;
  setPlace((apply) =>
    keepPlace(list, header(), async () => {
      apply();
      await tick();
    }),
  );

  // Every 5 minutes while the tab is visible, and when it shows again after longer.
  $effect(() => {
    const visible = () => document.visibilityState === "visible";
    const timer = setInterval(() => visible() && void checkNow(), CHECK_MS);
    const shown = () => visible() && Date.now() - feed.checked >= CHECK_MS && void checkNow();
    document.addEventListener("visibilitychange", shown);
    return () => {
      clearInterval(timer);
      document.removeEventListener("visibilitychange", shown);
    };
  });

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
<div bind:this={list}>
  {#each days as day (day.day)}
    <DaySection {day} today={now} />
  {/each}
</div>
<div class="more" bind:this={sentinel}>
  {#if feed.loading}<span class="spinner" role="status" aria-label={copy.loading}></span>{/if}
</div>

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
</style>
