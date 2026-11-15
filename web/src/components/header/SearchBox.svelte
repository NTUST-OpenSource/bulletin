<script lang="ts">
  import Search from "@jis3r/icons/icons/search";
  import X from "@jis3r/icons/icons/x";
  import { tick } from "svelte";
  import { header as copy } from "../../lang/zh-TW";
  import { terms } from "../../lib/address";
  import { filters, ui } from "../../state.svelte";
  import IconButton from "../ui/IconButton.svelte";

  const WAIT = 300; // ms after the last keystroke
  const MAX_LENGTH = 100; // the API's limit

  let input = $state<HTMLInputElement>();
  let text = $state("");
  let timer: ReturnType<typeof setTimeout> | undefined;

  async function openBox(): Promise<void> {
    text = filters.q;
    ui.searching = true;
    await tick();
    input?.focus();
  }

  function search(): void {
    clearTimeout(timer);
    filters.q = terms(text);
  }

  function later(): void {
    clearTimeout(timer);
    timer = setTimeout(search, WAIT);
  }

  // An input method's keystrokes wait for the word; compositionend starts the wait.
  function typed(event: Event): void {
    if (!(event as InputEvent).isComposing) later();
  }

  function clear(): void {
    clearTimeout(timer);
    text = "";
    filters.q = "";
    ui.searching = false;
  }

  // The query stays applied when focus leaves the box.
  function left(event: FocusEvent): void {
    if (!(event.currentTarget as HTMLElement).contains(event.relatedTarget as Node | null)) ui.searching = false;
  }
</script>

{#if ui.searching}
  <!-- Pressing the box's buttons keeps focus in the input; Safari does not focus buttons on click,
       so the box would read the click as focus leaving it. -->
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <form
    class="search"
    role="search"
    onsubmit={(event) => {
      event.preventDefault();
      search();
    }}
    onfocusout={left}
    onmousedown={(event) => event.target !== input && event.preventDefault()}
  >
    <span class="glass" aria-hidden="true"><Search size={16} strokeWidth={2.2} /></span>
    <input
      bind:this={input}
      bind:value={text}
      type="search"
      aria-label={copy.search}
      placeholder={copy.search}
      maxlength={MAX_LENGTH}
      autocomplete="off"
      enterkeyhint="search"
      oninput={typed}
      oncompositionend={later}
      onkeydown={(event) => {
        if (event.key !== "Escape") return;
        event.preventDefault();
        clear();
      }}
    />
    <button type="button" class="scope" aria-pressed={filters.titleOnly} onclick={() => (filters.titleOnly = !filters.titleOnly)}>
      {copy.titleOnly}
    </button>
    <IconButton label={copy.closeSearch} icon={X} size={16} onclick={clear} />
  </form>
{:else}
  <IconButton label={copy.search} icon={Search} onclick={openBox} />
{/if}

<style>
  .search {
    box-sizing: border-box;
    display: flex;
    align-items: center;
    gap: 8px;
    height: 40px;
    width: 420px;
    max-width: 100%;
    padding: 0 0 0 14px;
    border-radius: 999px;
    background: var(--paper);
    border: 1px solid var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
    transform-origin: right center;
    animation: open-search 0.28s var(--ease);
  }
  @keyframes open-search {
    from {
      opacity: 0;
      transform: scaleX(0.6);
    }
  }
  .glass {
    display: grid;
    color: var(--ink-3);
  }
  input {
    flex: 1;
    min-width: 0;
    height: 100%;
    border: 0;
    background: none;
    outline: none;
    font: inherit;
    color: var(--ink);
  }
  input::-webkit-search-cancel-button {
    display: none;
  }
  .scope {
    flex: none;
    border: 0;
    border-radius: 999px;
    background: var(--bg);
    font-size: var(--text-xs);
    padding: 3px 10px;
    color: var(--ink-2);
  }
  .scope[aria-pressed="true"] {
    background: var(--accent-soft);
    color: var(--accent);
    font-weight: 600;
  }
  @media (max-width: 639px) {
    .search {
      flex: 1;
      width: auto;
    }
  }
</style>
