// Requirement: Article view (web-frontend): the rewrite's Markdown.
import { describe, expect, test } from "vitest";
import { markdown } from "./markdown";

describe("blocks", () => {
  test.fails("paragraphs keep their line breaks", () => {
    expect(markdown("one\ntwo\n\nthree")).toBe("<p>one<br>two</p><p>three</p>");
  });

  test.fails("headings, subtext and quotes", () => {
    expect(markdown("# A\n## B\n### C\n-# small\n> quoted\n> more")).toBe(
      '<h3>A</h3><h4>B</h4><h5>C</h5><p class="sub">small</p><blockquote>quoted<br>more</blockquote>',
    );
  });

  test.fails("lists nest by two spaces and switch kinds", () => {
    expect(markdown("- a\n  - b\n- c\n1. d")).toBe("<ul><li>a<ul><li>b</li></ul></li><li>c</li></ul><ol><li>d</li></ol>");
  });
});

describe("inline", () => {
  test.fails("bold, italic, strike and code", () => {
    expect(markdown("**b** *i* ~~s~~ `c*d*`")).toBe("<p><strong>b</strong> <em>i</em> <s>s</s> <code>c*d*</code></p>");
  });

  test.fails("links, autolinks and images open safely", () => {
    expect(markdown("[報名](https://forms.gle/x) <https://a.tw/b>")).toBe(
      '<p><a href="https://forms.gle/x" target="_blank" rel="noopener noreferrer">報名</a> ' +
        '<a href="https://a.tw/b" target="_blank" rel="noopener noreferrer">https://a.tw/b</a></p>',
    );
    expect(markdown("![海報](https://a.tw/p.png)")).toBe('<p><img src="https://a.tw/p.png" alt="海報" loading="lazy"></p>');
  });

  test.fails("A plain-text URL becomes a link, without trailing punctuation", () => {
    expect(markdown("見 https://a.tw/x?y=1。下一句")).toBe(
      '<p>見 <a href="https://a.tw/x?y=1" target="_blank" rel="noopener noreferrer">https://a.tw/x?y=1</a>。下一句</p>',
    );
  });

  test.fails("An unsafe link in the rewrite is shown as text", () => {
    for (const unsafe of ["[x](javascript:alert(1))", "[x](data:text/html,hi)", "<javascript:alert(1)>", "![x](javascript:1)"]) {
      expect(markdown(unsafe), unsafe).not.toMatch(/<a |<img /);
    }
  });

  test.fails("text is escaped, also inside links and nested brackets", () => {
    expect(markdown('<script>alert("x")</script> & [a [b]](https://a.tw)')).not.toContain("<script>");
    expect(markdown("[**粗**](https://a.tw)")).toContain("<strong>粗</strong>");
    expect(markdown('[x](https://a.tw/"onmouseover="1)')).not.toContain('"onmouseover');
  });
});
