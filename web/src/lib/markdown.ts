// The rewrite's Discord Markdown as escaped HTML (design.md, "Rendering article text"): all text is
// escaped first, and only the subset the prompt produces becomes markup.

const ENTITIES: Record<string, string> = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export const escape = (text: string): string => text.replace(/[&<>"']/g, (c) => ENTITIES[c]!);

/** A URL in plain text: the characters a URL is made of, which stop at CJK text. */
export const BARE_URL = /https?:\/\/[A-Za-z0-9\-._~:/?#@!$&*+,;=%]+/g;
const TRAILING = /[.,;:!?]+$/;

/** A bare URL without the punctuation that ends its sentence, and that punctuation. */
export function trimmed(url: string): [string, string] {
  const trail = TRAILING.exec(url)?.[0] ?? "";
  return [url.slice(0, url.length - trail.length), trail];
}

/** `url` when it is an absolute http or https URL. */
export function safe(url: string): string | null {
  try {
    return ["http:", "https:"].includes(new URL(url).protocol) ? url : null;
  } catch {
    return null;
  }
}

const anchor = (href: string, inner: string) =>
  `<a href="${escape(href)}" target="_blank" rel="noopener noreferrer">${inner}</a>`;

const BRACKETED = String.raw`((?:[^\[\]]|\[[^\]]*\])*)`; // one level of nested brackets
const TOKEN = new RegExp(
  [
    "`([^`]+)`", // 1 code
    String.raw`!\[${BRACKETED}\]\(([^)\s]+)\)`, // 2 alt, 3 URL
    String.raw`\[${BRACKETED}\]\(([^)\s]+)\)`, // 4 text, 5 URL
    String.raw`<(https?:\/\/[^\s<>]+)>`, // 6 autolink
    `(${BARE_URL.source})`, // 7 bare URL
    String.raw`\*\*(.+?)\*\*`, // 8 bold
    "~~(.+?)~~", // 9 strike
    String.raw`\*([^*\s](?:[^*]*[^*\s])?)\*`, // 10 italic
  ].join("|"),
  "g",
);

function token(m: RegExpMatchArray, links: boolean): string {
  const [whole, code, alt, src, text, href, auto, bare, bold, strike, italic] = m;
  if (code !== undefined) return `<code>${escape(code)}</code>`;
  if (src !== undefined) {
    const url = safe(src);
    return url ? `<img src="${escape(url)}" alt="${escape(alt ?? "")}" loading="lazy">` : escape(whole);
  }
  if (href !== undefined) {
    const url = safe(href);
    return url && links ? anchor(url, inline(text ?? "", false)) : escape(whole);
  }
  if (auto !== undefined) return links ? anchor(auto, escape(auto)) : escape(whole);
  if (bare !== undefined) {
    const [url, trail] = trimmed(bare);
    return links ? anchor(url, escape(url)) + escape(trail) : escape(whole);
  }
  if (bold !== undefined) return `<strong>${inline(bold, links)}</strong>`;
  if (strike !== undefined) return `<s>${inline(strike, links)}</s>`;
  return `<em>${inline(italic ?? "", links)}</em>`;
}

/** One line's inline markup; link text gets no links of its own. */
function inline(text: string, links = true): string {
  let html = "";
  let last = 0;
  for (const m of text.matchAll(TOKEN)) {
    html += escape(text.slice(last, m.index)) + token(m, links);
    last = m.index + m[0].length;
  }
  return html + escape(text.slice(last));
}

export function markdown(source: string): string {
  let html = "";
  let para: string[] = [];
  let quote: string[] = [];
  const stack: ("ul" | "ol")[] = [];
  const flush = () => {
    if (para.length) html += `<p>${para.map((line) => inline(line)).join("<br>")}</p>`;
    if (quote.length) html += `<blockquote>${quote.map((line) => inline(line)).join("<br>")}</blockquote>`;
    para = [];
    quote = [];
  };
  const closeTo = (depth: number) => {
    while (stack.length > depth) html += `</li></${stack.pop()}>`;
  };
  for (const line of source.replace(/\r/g, "").split("\n")) {
    const item = /^(\s*)([-*]|\d+\.)\s+(.*)$/.exec(line);
    if (item) {
      flush();
      const depth = Math.floor(item[1]!.length / 2);
      const kind = /\d/.test(item[2]!) ? "ol" : "ul";
      if (stack.length < depth + 1) {
        while (stack.length < depth + 1) {
          html += `<${kind}><li>`;
          stack.push(kind);
        }
      } else {
        closeTo(depth + 1);
        if (stack[depth] === kind) html += "</li><li>";
        else {
          html += `</li></${stack.pop()}><${kind}><li>`;
          stack.push(kind);
        }
      }
      html += inline(item[3]!);
      continue;
    }
    closeTo(0);
    let m: RegExpExecArray | null;
    if (!line.trim()) flush();
    else if ((m = /^(#{1,3})\s+(.*)$/.exec(line))) {
      flush();
      html += `<h${m[1]!.length + 2}>${inline(m[2]!)}</h${m[1]!.length + 2}>`;
    } else if ((m = /^-#\s+(.*)$/.exec(line))) {
      flush();
      html += `<p class="sub">${inline(m[1]!)}</p>`;
    } else if ((m = /^>\s?(.*)$/.exec(line))) {
      if (para.length) flush();
      quote.push(m[1]!);
    } else {
      if (quote.length) flush();
      para.push(line);
    }
  }
  closeTo(0);
  flush();
  return html;
}
