// Keeping the reader's place while items are inserted above it. CSS overflow-anchor would do this,
// but Safari does not implement it.

/**
 * Run `change`, keeping the first item below `top` where it was on screen while the inserted
 * items animate. Items are elements of `list` with a `data-id`.
 */
export async function keepPlace(list: HTMLElement, top: number, change: () => Promise<void>): Promise<void> {
  const items = [...list.querySelectorAll<HTMLElement>("[data-id]")];
  const anchor = items.find((item) => item.getBoundingClientRect().bottom > top);
  if (!anchor) return change();
  const id = anchor.dataset["id"]!;
  const offset = anchor.getBoundingClientRect().top;
  const correct = () => {
    const now = list.querySelector<HTMLElement>(`[data-id="${CSS.escape(id)}"]`);
    if (now) scrollBy(0, now.getBoundingClientRect().top - offset);
  };
  const observer = new ResizeObserver(correct);
  observer.observe(list);
  try {
    await change();
    correct();
    await Promise.allSettled(list.getAnimations({ subtree: true }).map((animation) => animation.finished));
    correct();
  } finally {
    observer.disconnect();
  }
}
