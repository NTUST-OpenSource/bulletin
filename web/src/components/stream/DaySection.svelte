<script lang="ts">
  import { days as copy } from "../../lang/zh-TW";
  import { type Day, heading } from "../../lib/stream";
  import ItemView from "./Item.svelte";

  let { day, today }: { day: Day; today: string } = $props();
  const h = $derived(heading(day.day, today));
  const relative = $derived(
    h.relative === "today" ? copy.today : h.relative === "yesterday" ? copy.yesterday : copy.weekday(h.weekday),
  );
</script>

<section class="daysec">
  <h2 class="day">
    <b>{h.date}</b>
    <span>
      <strong>{relative}</strong>{copy.month(h.month, h.year)}{h.relative ? ` · ${copy.weekday(h.weekday)}` : ""}
    </span>
  </h2>
  <ul class="items">
    {#each day.items as item (item.id)}
      <ItemView {item} />
    {/each}
  </ul>
</section>

<style>
  .daysec {
    content-visibility: auto;
    contain-intrinsic-size: auto 900px;
  }
  .day {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0;
    padding: 22px 0 6px;
    background: var(--bg);
    z-index: 2;
    font-weight: normal;
  }
  @media (min-height: 560px) {
    .day {
      position: sticky;
      top: calc(env(safe-area-inset-top, 0px) + var(--top-h));
    }
  }
  .day b {
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 2.75rem;
    line-height: 1;
    letter-spacing: -0.05em;
    font-variation-settings: "opsz" 96;
    font-variant-numeric: tabular-nums;
    min-width: 1.3ch;
    color: var(--accent);
  }
  .day span {
    display: grid;
    font-size: var(--text-xs);
    line-height: 1.35;
    color: var(--ink-3);
  }
  .day strong {
    color: var(--accent);
    font-size: var(--text-sm);
  }
  .day::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--line);
    margin-left: 8px;
  }
  .items {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
  }

  @media (max-width: 639px) {
    .day b {
      font-size: 2.25rem;
    }
  }
</style>
