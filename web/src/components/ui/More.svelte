<script lang="ts">
  // The icon set has no horizontal ellipsis; this one follows its props.
  import type { IconProps } from "@jis3r/icons";

  let { color = "currentColor", size = 24, class: className = "" }: IconProps = $props();
</script>

<div class={className} aria-hidden="true">
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill={color}>
    <circle cx="5" cy="12" r="1.8" /><circle cx="12" cy="12" r="1.8" /><circle cx="19" cy="12" r="1.8" />
  </svg>
</div>

<style>
  div {
    display: inline-block;
  }
</style>
