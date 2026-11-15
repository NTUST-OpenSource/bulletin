<script lang="ts">
  import type { IconProps } from "@jis3r/icons";
  import type { Component } from "svelte";

  type Props = {
    label: string;
    icon: Component<IconProps>;
    size?: number;
    onclick?: () => void;
  };
  let { label, icon: Icon, size = 20, onclick }: Props = $props();
  let active = $state(false); // the icon animates while the button is hovered or focused
</script>

<button
  type="button"
  class="icon-btn"
  aria-label={label}
  {onclick}
  onpointerenter={() => (active = true)}
  onpointerleave={() => (active = false)}
  onfocus={() => (active = true)}
  onblur={() => (active = false)}
>
  <Icon {size} strokeWidth={2.1} animate={active} />
</button>

<style>
  .icon-btn {
    flex: none;
    display: inline-grid;
    place-items: center;
    width: 40px;
    height: 40px;
    border: 0;
    background: none;
    border-radius: 999px;
    color: var(--ink-2);
  }
  .icon-btn:hover {
    background: var(--paper);
    color: var(--ink);
  }
  .icon-btn :global(div) {
    display: grid;
  }
</style>
