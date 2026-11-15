"""Requirement "No emoji" of the rendering capability."""

import json
import shutil
import subprocess

from bulletin.emoji import strip_emoji

# Every code point Unicode presents as an emoji by default, by Node's own Unicode data.
PRESENTED = (
    "const r = /\\p{Emoji_Presentation}/u; const o = [];"
    " for (let c = 0; c <= 0x10ffff; c++)"
    " if ((c < 0xd800 || c > 0xdfff) && r.test(String.fromCodePoint(c))) o.push(c);"
    " console.log(JSON.stringify(o));"
)
VS16 = chr(0xFE0F)  # asks for emoji presentation
KEYCAP = chr(0x20E3)
SYMBOLS = "".join(map(chr, (0x203B, 0x2605, 0x25CF, 0x2460, 0x2103, 0xA9, 0x4E2D, 0x3002)))


def test_every_emoji_is_removed() -> None:
    """No emoji: every character Unicode presents as an emoji is removed."""
    node = shutil.which("node")
    assert node is not None
    done = subprocess.run(  # noqa: S603 - a fixed script
        [node, "-e", PRESENTED], capture_output=True, text=True, check=True
    )
    presented: list[int] = json.loads(done.stdout)

    assert len(presented) > 1000
    assert [hex(c) for c in presented if strip_emoji(chr(c))] == []


def test_text_symbols_stay() -> None:
    """No emoji: reference marks, stars, bullets, circled numbers and units are text, not emoji;
    a symbol that asks for emoji presentation goes, a keycap keeps its digit."""
    assert strip_emoji(SYMBOLS) == SYMBOLS
    assert strip_emoji(f"{chr(0x270D)}{VS16} Apply {chr(0x2705)} now") == "Apply now"
    assert strip_emoji(f"1{VS16}{KEYCAP} Register") == "1 Register"
    assert strip_emoji(f"Due{chr(0x1F4E2)}") == "Due"
