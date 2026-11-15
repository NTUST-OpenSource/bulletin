<script lang="ts">
  import { units } from "../../lang/zh-TW";
  import type { Site } from "../../lib/api";
  import { unitGroups } from "../../lib/units";
  import { app, setSettings } from "../../state.svelte";
  import Tiles from "./Tiles.svelte";

  let query = $state("");
  const groups = $derived(unitGroups(app.sites, query, units.school, units.other));

  function toggle(site: Site): void {
    const followed = app.settings.sites;
    const sites = followed.includes(site.id) ? followed.filter((id) => id !== site.id) : [...followed, site.id];
    setSettings({ ...app.settings, sites });
  }
</script>

<label class="sr" for="unit-q">{units.search}</label>
<input class="field" id="unit-q" type="search" placeholder={units.search} autocomplete="off" bind:value={query} />
<div class="picker">
  {#each groups as group (group.title)}
    <section class="group">
      <h4>{group.title}</h4>
      <Tiles sites={group.sites} picked={(site) => app.settings.sites.includes(site.id)} pick={toggle} />
    </section>
  {:else}
    <p class="note">{units.none}</p>
  {/each}
</div>

<style>
  .picker {
    display: grid;
    gap: 22px;
    padding-top: 8px;
  }
  h4 {
    margin: 0 0 10px;
    font-size: var(--text-sm);
    color: var(--ink-3);
    font-weight: 600;
  }
</style>
