<script lang="ts">
  import { brand } from "../../lang/zh-TW";

  const FONT_WAIT = 1000; // ms the brand's font may take before the brand shows at rest

  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  // waiting: the b alone until the font is in; playing: the intro; still: at rest.
  let phase = $state<"waiting" | "playing" | "still">(reduced ? "still" : "waiting");

  // The intro's offsets are the font's own, so it plays only once the font is in.
  if (!reduced) {
    const late = new Promise<[]>((resolve) => setTimeout(resolve, FONT_WAIT, []));
    Promise.race([document.fonts.load('800 24px "Bricolage Grotesque"'), late]).then(
      (faces) => (phase = faces.length > 0 ? "playing" : "still"),
      () => (phase = "still"),
    );
  }
</script>

<!-- Ending the intro once keeps it from replaying when the phone's search box hides the brand. -->
<a class="brand {phase}" href="/" aria-label={brand.home}
  >b<span class="rest" onanimationend={() => (phase = "still")}>ulletin</span><i class="dot"
    ><span class="fall"><span class="squash">.</span></span></i
  ></a
>

<style>
  .rest {
    display: inline-block;
  }
  .dot,
  .dot span {
    display: inline-block;
    line-height: 1;
  }
  /* The period's ink centre and its foot, in Bricolage Grotesque at opsz 48. */
  .fall {
    transform-origin: 0.1247em 0.7525em;
  }
  .squash {
    transform-origin: 0.1247em 0.843em;
  }
  .waiting .rest {
    clip-path: inset(0 114.54% 0 0);
  }
  .waiting .dot {
    translate: -3.1024em 0;
  }
  .waiting .fall {
    translate: 0 -0.1852em;
    scale: 0;
  }
  .playing .dot {
    animation: hop-x 1279ms linear both;
  }
  .playing .fall {
    animation:
      hop-y 1279ms linear both,
      grow 1279ms linear both;
  }
  .playing .squash {
    animation: squash 1279ms linear both;
  }
  .playing .rest {
    animation: reveal 1279ms linear both;
  }

  /*
   * The ball starts in the b's counter, 3.1024em left of the period and 0.1852em above it, and
   * hops 0.42, 0.22, 0.11 and 0.05em high under 42em/s², keeping 82% of its speed through each
   * landing: x is linear within a hop, y eases out to each top and in to each landing. The word's
   * right inset is linear in the ball's x, trails it within a hop and catches up as it lands.
   */
  @keyframes hop-x {
    0%, 28.14% { translate: -3.1024em 0; }
    36.41% { translate: -2.5789em 0; }
    47.46% { translate: -1.8787em 0; }
    49.42% { translate: -1.7666em 0; }
    57.42% { translate: -1.3511em 0; }
    65.42% { translate: -0.9356em 0; }
    67.38% { translate: -0.8436em 0; }
    73.03% { translate: -0.6027em 0; }
    78.69% { translate: -0.3618em 0; }
    80.65% { translate: -0.2864em 0; }
    84.46% { translate: -0.1532em 0; }
    88.27% { translate: -0.02em 0; animation-timing-function: cubic-bezier(0.2, 0.6, 0.4, 1); }
    100% { translate: 0 0; }
  }
  @keyframes hop-y {
    0%, 28.14% { translate: 0 -0.1852em; animation-timing-function: cubic-bezier(0.333, 0.667, 0.667, 1); }
    36.41% { translate: 0 -0.42em; animation-timing-function: cubic-bezier(0.333, 0, 0.667, 0.333); }
    47.46% { translate: 0 0; }
    49.42% { translate: 0 0; animation-timing-function: cubic-bezier(0.333, 0.667, 0.667, 1); }
    57.42% { translate: 0 -0.22em; animation-timing-function: cubic-bezier(0.333, 0, 0.667, 0.333); }
    65.42% { translate: 0 0; }
    67.38% { translate: 0 0; animation-timing-function: cubic-bezier(0.333, 0.667, 0.667, 1); }
    73.03% { translate: 0 -0.11em; animation-timing-function: cubic-bezier(0.333, 0, 0.667, 0.333); }
    78.69% { translate: 0 0; }
    80.65% { translate: 0 0; animation-timing-function: cubic-bezier(0.333, 0.667, 0.667, 1); }
    84.46% { translate: 0 -0.05em; animation-timing-function: cubic-bezier(0.333, 0, 0.667, 0.333); }
    88.27%, 100% { translate: 0 0; }
  }
  @keyframes grow {
    0% { scale: 0; animation-timing-function: cubic-bezier(0.2, 0.8, 0.4, 1); }
    8.6% { scale: 0.72; animation-timing-function: ease-in-out; }
    12.51%, 28.14% { scale: 0.62; animation-timing-function: ease-out; }
    36.41%, 100% { scale: 1; }
  }
  @keyframes squash {
    0%, 21.11% { scale: 1 1; animation-timing-function: ease-out; }
    26.97% { scale: 1.12 0.86; animation-timing-function: ease-in; }
    31.27% { scale: 0.94 1.07; animation-timing-function: ease-out; }
    36.41% { scale: 1 1; animation-timing-function: ease-in; }
    44.73% { scale: 0.92 1.08; }
    47.46% { scale: 1.2 0.83; animation-timing-function: ease-out; }
    51.76% { scale: 0.96 1.04; animation-timing-function: ease-out; }
    57.42% { scale: 1 1; animation-timing-function: ease-in; }
    62.68% { scale: 0.95 1.05; }
    65.42% { scale: 1.13 0.89; animation-timing-function: ease-out; }
    69.72% { scale: 0.96 1.04; animation-timing-function: ease-out; }
    73.03% { scale: 1 1; animation-timing-function: ease-in; }
    75.95% { scale: 0.98 1.02; }
    78.69% { scale: 1.07 0.94; animation-timing-function: ease-out; }
    82.99% { scale: 0.96 1.04; animation-timing-function: ease-out; }
    84.46%, 85.54% { scale: 1 1; }
    88.27% { scale: 1.04 0.97; animation-timing-function: ease-out; }
    93.75% { scale: 0.97 1.03; animation-timing-function: ease-in-out; }
    100% { scale: 1 1; }
  }
  @keyframes reveal {
    0%, 28.14% { clip-path: inset(0 114.54% 0 0); animation-timing-function: cubic-bezier(0.55, 0, 0.85, 0.45); }
    47.46% { clip-path: inset(0 69.05% 0 0); }
    49.42% { clip-path: inset(0 64.89% 0 0); animation-timing-function: cubic-bezier(0.55, 0, 0.85, 0.45); }
    65.42% { clip-path: inset(0 34% 0 0); }
    67.38% { clip-path: inset(0 30.58% 0 0); animation-timing-function: cubic-bezier(0.55, 0, 0.85, 0.45); }
    78.69% { clip-path: inset(0 12.67% 0 0); }
    80.65% { clip-path: inset(0 9.87% 0 0); animation-timing-function: cubic-bezier(0.55, 0, 0.85, 0.45); }
    88.27%, 100% { clip-path: inset(0 0 0 0); }
  }
</style>
