<script lang="ts">
  import Search from "@jis3r/icons/icons/search";
  import SlidersHorizontal from "@jis3r/icons/icons/sliders-horizontal";
  import IconButton from "./components/ui/IconButton.svelte";
  import { brand, header, stream } from "./lang/zh-TW";
</script>

<header class="top">
  <div class="wrap">
    <a class="brand" href="/" aria-label={brand.home}>bulletin<i>.</i></a>
    <IconButton label={header.search} icon={Search} />
    <IconButton label={header.settings} icon={SlidersHorizontal} />
  </div>
</header>

<main class="wrap stream">
  <div class="filters" role="toolbar" aria-label={stream.filters}></div>
</main>

<style>
  .top {
    position: sticky;
    top: env(safe-area-inset-top, 0px);
    z-index: 5;
    background: var(--bg);
  }
  .top .wrap {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
    min-height: 64px;
  }
  .brand {
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 1.5rem;
    letter-spacing: -0.035em;
    font-variation-settings: "opsz" 48;
    color: var(--ink);
    text-decoration: none;
    margin-right: auto;
  }
  .brand i {
    font-style: normal;
    color: var(--accent);
  }
  .stream {
    padding-bottom: 96px;
  }
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

  @media (max-width: 639px) {
    .top .wrap {
      min-height: 56px;
    }
  }
</style>
