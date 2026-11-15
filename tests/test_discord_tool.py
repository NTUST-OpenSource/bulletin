"""Scaffolding: the Node check behind "Discord Markdown" answers one line per input."""

import json
import shutil
import subprocess
from pathlib import Path

CHECK = Path(__file__).parents[1] / "tools" / "discord-markdown" / "check.mjs"


def test_the_check_answers_each_line() -> None:
    node = shutil.which("node")
    assert node is not None
    lines = [{"text": "[a](https://example.com) **b**"}, {"text": "@everyone"}]

    done = subprocess.run(  # noqa: S603 - a fixed script under the repository
        [node, str(CHECK)],
        input="".join(json.dumps(line) + "\n" for line in lines),
        capture_output=True,
        text=True,
        check=True,
    )

    assert [json.loads(line) for line in done.stdout.splitlines()] == [
        {"problems": []},
        {"problems": ["mention"]},
    ]
