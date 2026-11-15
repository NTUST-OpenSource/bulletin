"""What the model reads: an article reduced to Markdown, its links and images as placeholders."""

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from bulletin.emoji import strip_emoji
from bulletin.markup import INVISIBLE, RAW_TEXT, WHITESPACE, Element, parse
from bulletin.pages import join

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from bulletin.model import Attachment

HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
LISTS = frozenset({"ul", "ol"})
BOLD = frozenset({"strong", "b"})
# Elements that start a paragraph of their own; any other element is unwrapped to its content.
PARAGRAPHS = frozenset(
    {
        "address",
        "article",
        "aside",
        "blockquote",
        "center",
        "dd",
        "div",
        "dl",
        "dt",
        "fieldset",
        "figcaption",
        "figure",
        "footer",
        "form",
        "header",
        "hr",
        "main",
        "p",
        "pre",
        "section",
    }
)
BLOCKS = PARAGRAPHS | HEADINGS | LISTS | {"table"}
WEB = frozenset({"http", "https"})
# A pasted link that kept the scheme typed before it: "http:// https://host/".
SCHEME_TWICE = re.compile(r"https?://\s*(?=https?://)", re.IGNORECASE)
# A host Discord links: ASCII letters, digits, dots, hyphens and underscores, as punycode and IPs.
HOST = re.compile(r"[A-Za-z0-9._-]+")
SPACES = re.compile(f"[{re.escape(''.join(sorted(WHITESPACE)))}]+")
DROPPED = dict.fromkeys(map(ord, INVISIBLE))
CELL_PIPE = re.compile(r"\|")
# A URL written as text: its ASCII characters, without the brackets and asterisks of Markdown, so
# CJK text and full-width punctuation end it.
TEXT_URL = re.compile(r"(?:https?://|www\.)[A-Za-z0-9\-._~:/?#@!$&'()+,;=%]+")
TRAILING = ".,;:!?'"


@dataclass(frozen=True)
class ModelInput:
    """The input text and the URL each placeholder (`L1`, `I1`, ...) stands for."""

    text: str
    targets: dict[str, str]


def model_input(
    title: str, body_html: str, attachments: Sequence[Attachment], url: str
) -> ModelInput:
    """Reduce an article at `url` to the model's input: its title, body and attachment names.

    Body links and images become `L<n>` and `I<n>`, numbered in order of appearance, one per
    URL; links that are not http(s) keep their text only. The attachment module's files follow
    the body as a list of names with their link placeholders.
    """
    writer = _Writer(url)
    sections = [
        f"Title: {strip_emoji(title)}",
        "Body:\n" + "\n\n".join(writer.blocks(parse(body_html))),
    ]
    module = [a for a in attachments if a.origin == "module"]
    if module:
        names = (f"- [{a.name}]({writer.placeholder('L', a.url)})" for a in module)
        sections.append("Attachments:\n" + "\n".join(names))
    return ModelInput("\n\n".join(section.rstrip() for section in sections), writer.targets)


def _clean(text: str) -> str:
    """Trim every line and collapse runs of spaces and of blank lines.

    Adjacent bold elements, as pasted text often splits a date over them, make one bold run.
    """
    lines = (re.sub(" {2,}", " ", line).strip() for line in text.replace("****", "").split("\n"))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _flat(text: str) -> str:
    """`text` on one line."""
    return " ".join(_clean(text).split("\n"))


def _bold(text: str) -> str:
    core = text.strip()
    if not core:
        return text
    return f"{text[: len(text) - len(text.lstrip())]}**{core}**{text[len(text.rstrip()) :]}"


def _elements(nodes: Iterable[Element | str]) -> list[Element]:
    return [node for node in nodes if isinstance(node, Element)]


@dataclass
class _Writer:
    """Writes Markdown and numbers the placeholders it hands out."""

    url: str
    targets: dict[str, str] = field(default_factory=dict[str, str])
    numbers: dict[tuple[str, str], str] = field(default_factory=dict[tuple[str, str], str])

    def placeholder(self, kind: str, target: str) -> str:
        """The placeholder of `target`: its earlier one, or the next of its kind."""
        if (kind, target) not in self.numbers:
            name = f"{kind}{sum(1 for k, _ in self.numbers if k == kind) + 1}"
            self.numbers[kind, target] = name
            self.targets[name] = target
        return self.numbers[kind, target]

    def _web(self, value: str) -> str | None:
        """The http(s) URL that `value` names, if any.

        A scheme typed twice is dropped; a malformed URL, or one whose host Discord would not
        link, names none.
        """
        target = join(self.url, SCHEME_TWICE.sub("", value.strip(), count=1))
        if target is None:
            return None
        parts = urlsplit(target)
        return target if parts.scheme in WEB and HOST.fullmatch(parts.hostname or "") else None

    # shortcut: recursion follows the body's nesting; school bodies nest a few dozen levels at most.
    def blocks(self, container: Element) -> list[str]:
        """The Markdown blocks of `container`'s children."""
        out: list[str] = []
        inline: list[str] = []

        def flush() -> None:
            out.extend(part for part in _clean("".join(inline)).split("\n\n") if part)
            inline.clear()

        for child in container.children:
            if isinstance(child, Element) and child.tag in BLOCKS:
                flush()
                out.extend(block for block in self._block(child) if block)
            else:
                inline.append(self.inline([child]))
        flush()
        return out

    def _block(self, element: Element) -> list[str]:
        if element.tag in LISTS:
            return [self._list(element, 0)]
        if element.tag == "table":
            return [self._table(element)]
        if element.tag in HEADINGS:
            return [_bold(_flat(self.inline(element.children)))]
        return self.blocks(element)

    def inline(self, nodes: Iterable[Element | str], images: list[str] | None = None) -> str:
        """The Markdown of inline content; images go to `images` when it is given (in a link)."""
        parts: list[str] = []
        for node in nodes:
            if isinstance(node, str):
                text = strip_emoji(SPACES.sub(" ", node).translate(DROPPED))
                parts.append(TEXT_URL.sub(self._text_url, text))
            elif node.tag in RAW_TEXT:
                continue
            elif node.tag == "br":
                parts.append("\n")
            elif node.tag == "a":
                parts.append(self._link(node))
            elif node.tag == "img":
                image = self._image(node)
                (parts if images is None else images).append(image)
            elif node.tag in BOLD:
                parts.append(_bold(self.inline(node.children, images)))
            elif node.tag in BLOCKS:
                parts.append("\n\n" + "\n\n".join(self._block(node)) + "\n\n")
            else:
                parts.append(self.inline(node.children, images))
        return "".join(parts)

    def _text_url(self, match: re.Match[str]) -> str:
        url = match[0].rstrip(TRAILING)
        if url.endswith(")") and url.count("(") < url.count(")"):
            url = url[:-1]
        target = url if "://" in url else f"https://{url}"
        return f"<{self.placeholder('L', target)}>{match[0][len(url) :]}"

    def _link(self, element: Element) -> str:
        target = self._web(element.attr("href"))
        if target is None:
            return self.inline(element.children)
        if TEXT_URL.match(element.text()):
            return f"<{self.placeholder('L', target)}>"
        images: list[str] = []
        text = _flat(self.inline(element.children, images))
        name = self.placeholder("L", target)
        return "".join(images) + (f"[{text}]({name})" if text else f"<{name}>")

    def _image(self, element: Element) -> str:
        target = self._web(element.attr("src"))
        if target is None:
            return ""
        alt = _flat(strip_emoji(element.attr("alt")))
        return f"![{alt}]({self.placeholder('I', target)})"

    def _list(self, element: Element, depth: int) -> str:
        lines: list[str] = []
        for number, item in enumerate(_elements(element.children), start=1):
            if item.tag in LISTS:
                lines.append(self._list(item, depth + 1))
                continue
            nested = [child for child in _elements(item.children) if child.tag in LISTS]
            head = _flat(self.inline(c for c in item.children if c not in nested))
            marker = f"{number}." if element.tag == "ol" else "-"
            lines.append(f"{'  ' * depth}{marker} {head}")
            lines.extend(self._list(child, depth + 1) for child in nested)
        return "\n".join(line for line in lines if line.strip())

    def _table(self, table: Element) -> str:
        rows = [
            [
                CELL_PIPE.sub(r"\\|", _flat(self.inline(cell.children)))
                for cell in _elements(row.children)
                if cell.tag in {"td", "th"}
            ]
            for row in table.select("tr")
        ]
        rows = [row for row in rows if any(row)]
        if not rows:
            return ""
        width = max(len(row) for row in rows)
        lines = ["| " + " | ".join(row + [""] * (width - len(row))) + " |" for row in rows]
        lines.insert(1, "| " + " | ".join(["---"] * width) + " |")
        return "\n".join(lines)
