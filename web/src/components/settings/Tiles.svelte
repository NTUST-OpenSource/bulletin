<script lang="ts">
  import Check from "@jis3r/icons/icons/check";
  import type { Site } from "../../lib/api";

  type Props = { sites: Site[]; picked: (site: Site) => boolean; pick: (site: Site) => void };
  let { sites, picked, pick }: Props = $props();
</script>

<div class="tiles">
  {#each sites as site (site.id)}
    <button type="button" class="tile" aria-pressed={picked(site)} onclick={() => pick(site)}>
      <span class="check" aria-hidden="true"><Check size={14} strokeWidth={3} /></span>{site.unit}
    </button>
  {/each}
</div>

<style>
  .tiles {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .tile {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    max-width: 100%;
    border: 1px solid var(--line-2);
    background: var(--paper);
    border-radius: 999px;
    padding: 8px 16px;
    font-size: var(--text-base);
    color: var(--ink);
    text-align: left;
    overflow-wrap: anywhere;
  }
  .tile:hover {
    border-color: var(--ink-3);
  }
  .check {
    display: none;
  }
  .tile[aria-pressed="true"] {
    background: var(--accent);
    border-color: var(--accent);
    color: var(--accent-ink);
  }
  .tile[aria-pressed="true"] .check {
    display: grid;
  }
  .check :global(div) {
    display: grid;
  }
</style>
