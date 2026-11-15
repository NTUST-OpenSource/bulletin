// The school's HTML through DOMPurify, without the school's styles or scripts, with links and
// images fixed against the article's URL (design.md, "Rendering article text").
import DOMPurify from "dompurify";
import { BARE_URL, trimmed } from "./markdown";

const LINKS = /^(https?|mailto):$/;
const ABSOLUTE = /^[a-z][a-z0-9+.-]*:/i;

/** `url` against `base`; null when it cannot be read. */
function resolved(url: string, base: string): URL | null {
  try {
    return new URL(url, base);
  } catch {
    return null;
  }
}

/** Fix one sanitized element: images load from the school lazily, links open safely. */
function fix(node: Element, base: string): void {
  if (node.tagName === "IMG") {
    const src = node.getAttribute("data-src") || node.getAttribute("src");
    node.removeAttribute("data-src");
    const url = src ? resolved(src, base) : null;
    if (url && ["http:", "https:"].includes(url.protocol)) node.setAttribute("src", ABSOLUTE.test(src!) ? src! : url.href);
    else node.removeAttribute("src");
    node.setAttribute("loading", "lazy");
  } else if (node.tagName === "A") {
    const href = node.getAttribute("href");
    const url = href ? resolved(href, base) : null;
    if (url && LINKS.test(url.protocol)) {
      node.setAttribute("href", ABSOLUTE.test(href!) ? href! : url.href);
      node.setAttribute("target", "_blank");
      node.setAttribute("rel", "noopener noreferrer");
    } else node.removeAttribute("href");
  }
}

/** Turn URLs in text nodes outside links into links. */
function linkify(root: DocumentFragment): void {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const texts: Text[] = [];
  while (walker.nextNode()) {
    const text = walker.currentNode as Text;
    if (!text.parentElement?.closest("a") && BARE_URL.test(text.data)) texts.push(text);
    BARE_URL.lastIndex = 0;
  }
  for (const text of texts) {
    const parts = document.createDocumentFragment();
    let last = 0;
    for (const m of text.data.matchAll(BARE_URL)) {
      const [url, trail] = trimmed(m[0]);
      parts.append(text.data.slice(last, m.index));
      const link = document.createElement("a");
      link.textContent = url;
      link.setAttribute("href", url);
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");
      parts.append(link, trail);
      last = m.index + m[0].length;
    }
    parts.append(text.data.slice(last));
    text.replaceWith(parts);
  }
}

export function raw(html: string, base: string): string {
  const purify = DOMPurify(window);
  purify.addHook("afterSanitizeAttributes", (node) => fix(node, base));
  const fragment = purify.sanitize(html, {
    FORBID_TAGS: ["style", "link", "form", "input", "button", "select", "textarea"],
    FORBID_ATTR: ["style", "class", "id"],
    RETURN_DOM_FRAGMENT: true,
  });
  for (const table of fragment.querySelectorAll("table")) {
    const wrap = document.createElement("div");
    wrap.className = "table-wrap";
    table.replaceWith(wrap);
    wrap.append(table);
  }
  linkify(fragment);
  const box = document.createElement("div");
  box.append(fragment);
  return box.innerHTML;
}
