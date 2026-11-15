<script lang="ts">
  import Search from "@jis3r/icons/icons/search";
  import SlidersHorizontal from "@jis3r/icons/icons/sliders-horizontal";
  import Onboarding from "./components/settings/Onboarding.svelte";
  import Article from "./components/article/Article.svelte";
  import Settings from "./components/settings/Settings.svelte";
  import Stream from "./components/stream/Stream.svelte";
  import TopicChips from "./components/stream/TopicChips.svelte";
  import Confirm from "./components/ui/Confirm.svelte";
  import IconButton from "./components/ui/IconButton.svelte";
  import Menu from "./components/ui/Menu.svelte";
  import Toast from "./components/ui/Toast.svelte";
  import { brand, header } from "./lang/zh-TW";
  import { applyTheme, readImport } from "./lib/settings";
  import { follow } from "./article.svelte";
  import { app, loadLists, offerSettings, ui } from "./state.svelte";

  $effect(() => applyTheme(document.documentElement, app.settings.theme));
  void loadLists();

  // A settings link: read once, then dropped from the address so a reload does not ask again.
  function readLink(): void {
    if (!location.hash.startsWith("#s=")) return;
    const hash = location.hash;
    history.replaceState(history.state, "", location.pathname + location.search);
    try {
      void offerSettings(readImport(hash), "link");
    } catch {
      // An unreadable link changes nothing.
    }
  }
  readLink();

  // Day headings pin below the header, whose height changes with the search box.
  let top: HTMLElement;
  $effect(() => {
    const observer = new ResizeObserver(([entry]) => {
      const height = entry?.borderBoxSize[0]?.blockSize;
      if (height) document.documentElement.style.setProperty("--top-h", `${Math.round(height)}px`);
    });
    observer.observe(top);
    return () => observer.disconnect();
  });
  // A first visit starts with the unit picker; one through an article link shows the article first.
  if (!app.saved && !location.pathname.startsWith("/a/")) ui.onboarding = true;
  follow();
</script>

<svelte:window onhashchange={readLink} onpopstate={follow} />

<header class="top" bind:this={top}>
  <div class="wrap">
    <a class="brand" href="/" aria-label={brand.home}>bulletin<i>.</i></a>
    <IconButton label={header.search} icon={Search} />
    <IconButton label={header.settings} icon={SlidersHorizontal} onclick={() => (ui.sheet = "main")} />
  </div>
</header>

<main class="wrap stream">
  <TopicChips />
  <Stream />
</main>

<Article />
<Settings />
<Onboarding />
<Confirm />
<Menu />
<Toast />

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
    margin-right: auto;
  }
  .stream {
    padding-bottom: 96px;
  }
  @media (max-width: 639px) {
    .top .wrap {
      min-height: 56px;
    }
  }
</style>
