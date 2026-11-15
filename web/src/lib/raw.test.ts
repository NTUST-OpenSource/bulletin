// Requirement: Article view (web-frontend): the school's version.
import { expect, test } from "vitest";
import { raw } from "./raw";

const BASE = "https://student.ntust.edu.tw/p/406-1053-153594,r1436.php?Lang=zh-tw";
const html = (source: string) => {
  const box = document.createElement("div");
  box.innerHTML = raw(source, BASE);
  return box;
};

test.fails("The school's version: no styles, scripts, forms, classes or ids", () => {
  const box = html(
    '<style>p{color:red}</style><link rel=stylesheet href=x.css><script>alert(1)</script>' +
      '<form action=/x><input></form><p class="c" id="i" style="color:red" onclick="x()">text</p>',
  );

  expect(box.innerHTML).toBe("<p>text</p>");
});

test.fails("images take data-src and resolve against the article's URL, loading lazily", () => {
  const image = html('<img data-src="/var/file/53/1053/img/a.jpg" alt="海報">').querySelector("img")!;

  expect(image.getAttribute("src")).toBe("https://student.ntust.edu.tw/var/file/53/1053/img/a.jpg");
  expect(image.getAttribute("loading")).toBe("lazy");
});

test.fails("links resolve, open in a new tab, and keep only http, https and mailto", () => {
  const box = html('<a href="a.pdf">a</a><a href="mailto:x@ntust.edu.tw">m</a><a href="javascript:alert(1)">j</a>');
  const links = [...box.querySelectorAll("a")];

  expect(links.map((a) => a.getAttribute("href"))).toEqual([
    "https://student.ntust.edu.tw/p/a.pdf",
    "mailto:x@ntust.edu.tw",
    null,
  ]);
  expect(links[0]!.getAttribute("target")).toBe("_blank");
  expect(links[0]!.getAttribute("rel")).toBe("noopener noreferrer");
});

test.fails("tables scroll inside the article", () => {
  expect(html("<table><tr><td>1</td></tr></table>").firstElementChild!.className).toBe("table-wrap");
});

test.fails("A plain-text URL becomes a link, but not inside a link", () => {
  const box = html('<p>詳見 https://a.tw/x。 <a href="https://b.tw">https://b.tw</a></p>');

  expect([...box.querySelectorAll("a")].map((a) => a.getAttribute("href"))).toEqual(["https://a.tw/x", "https://b.tw"]);
  expect(box.textContent).toBe("詳見 https://a.tw/x。 https://b.tw");
});
