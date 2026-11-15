<script lang="ts">
  import { brand, notFound as copy } from "./lang/zh-TW";
  import { applyTheme } from "./lib/settings";
  import { app } from "./state.svelte";

  $effect(() => applyTheme(document.documentElement, app.settings.theme));
</script>

<header class="top">
  <div class="wrap">
    <a class="brand" href="/" aria-label={brand.home}>bulletin<i>.</i></a>
  </div>
</header>

<main class="wrap lost">
  <!-- The 0 is the brand's ball, dropping in; the heading says it in words. -->
  <p class="code" aria-hidden="true">
    4<span class="slot"><span class="shadow"></span><span class="ball"><span class="squash"></span></span></span>4
  </p>
  <h1>{copy.title}</h1>
  <a class="btn primary home" href="/">{copy.home}</a>
</main>

<style>
  .top .wrap {
    display: flex;
    align-items: center;
    min-height: 64px;
  }
  .lost {
    box-sizing: border-box;
    min-height: calc(100dvh - 64px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding-bottom: 72px;
  }
  .code {
    margin: 0;
    font-family: var(--font-display);
    font-weight: 800;
    font-size: clamp(7.5rem, 4rem + 12vw, 11.5rem);
    font-variation-settings: "opsz" 96;
    letter-spacing: -0.04em;
    line-height: 1;
    color: var(--ink);
  }
  .slot {
    display: inline-block;
    position: relative;
    width: 0.62em;
    height: 0.62em;
    margin: 0 0.05em 0 0.03em;
  }
  .shadow {
    position: absolute;
    left: 8%;
    right: 8%;
    bottom: -0.07em;
    height: 0.08em;
    border-radius: 50%;
    background: var(--ink);
    opacity: 0.14;
    animation: shadow 1.2s linear 0.2s both;
  }
  .ball {
    position: absolute;
    inset: 0;
    animation: drop 1.2s linear 0.2s both;
  }
  .squash {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: var(--accent);
    transform-origin: 50% 100%;
    animation: squash 1.2s linear 0.2s both;
  }
  h1 {
    margin: 20px 0 0;
    font-size: var(--text-lg);
    font-weight: 600;
    letter-spacing: 0.01em;
  }
  .home {
    box-sizing: border-box;
    margin-top: 28px;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    padding: 0 24px;
    font-size: var(--text-base);
    text-decoration: none;
  }
  @media (max-width: 639px) {
    .top .wrap {
      min-height: 56px;
    }
    .lost {
      min-height: calc(100dvh - 56px);
    }
    h1 {
      font-size: 1.125rem;
    }
  }

  /* Gravity: falls speed up into each landing and slow to each top; the ball squashes as it lands. */
  @keyframes drop {
    0% {
      translate: 0 -2.4em;
      opacity: 0;
      animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
    }
    10% {
      opacity: 1;
    }
    36% {
      translate: 0 0;
      animation-timing-function: cubic-bezier(0, 0.55, 0.45, 1);
    }
    56% {
      translate: 0 -0.42em;
      animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
    }
    72% {
      translate: 0 0;
      animation-timing-function: cubic-bezier(0, 0.55, 0.45, 1);
    }
    83% {
      translate: 0 -0.1em;
      animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
    }
    91%,
    100% {
      translate: 0 0;
      opacity: 1;
    }
  }
  @keyframes squash {
    0%,
    24% {
      scale: 1 1;
      animation-timing-function: ease-in;
    }
    33% {
      scale: 0.88 1.14;
    }
    36% {
      scale: 1.3 0.72;
      animation-timing-function: ease-out;
    }
    44% {
      scale: 0.95 1.06;
      animation-timing-function: ease-in-out;
    }
    54%,
    68% {
      scale: 1 1;
    }
    72% {
      scale: 1.14 0.86;
      animation-timing-function: ease-out;
    }
    78%,
    88% {
      scale: 1 1;
    }
    91% {
      scale: 1.05 0.95;
      animation-timing-function: ease-out;
    }
    96%,
    100% {
      scale: 1 1;
    }
  }
  @keyframes shadow {
    0% {
      scale: 0.2 0.2;
      opacity: 0;
      animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
    }
    36% {
      scale: 1 1;
      opacity: 0.16;
      animation-timing-function: cubic-bezier(0, 0.55, 0.45, 1);
    }
    56% {
      scale: 0.7 0.7;
      opacity: 0.08;
      animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
    }
    72% {
      scale: 1 1;
      opacity: 0.16;
      animation-timing-function: cubic-bezier(0, 0.55, 0.45, 1);
    }
    83% {
      scale: 0.9 0.9;
      opacity: 0.12;
      animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
    }
    91%,
    100% {
      scale: 1 1;
      opacity: 0.14;
    }
  }
</style>
