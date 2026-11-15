"""Measure rendering on the labelled corpus sample (design.md, Measurement).

    uv run python scripts/measure_rendering.py SAMPLE LABELS CORPUS OUT

SAMPLE lists the articles (id, site, url, listed_on), LABELS the owner's labels (id, topic,
audience, nature, source, deadline), and CORPUS is the folder whose `pages/` hold the gzipped
article pages. The model settings come from the environment as for `bulletin serve`; set
BULLETIN_THINKING_LEVEL to compare thinking levels. The summary is printed and written to OUT
with every article's details.
"""

import asyncio
import gzip
import json
import logging
import os
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from statistics import fmean
from typing import TYPE_CHECKING, Literal, TypedDict, get_args

import aiohttp

from bulletin.answers import PLACEHOLDER, parse_answer
from bulletin.discord import Checker
from bulletin.keys import KeyRing
from bulletin.model_api import ModelClient, ModelConfig
from bulletin.model_input import model_input
from bulletin.pages import parse_article
from bulletin.rendering import Renderer
from bulletin.renditions import Pending

if TYPE_CHECKING:
    from collections.abc import Iterable

Outcome = Literal["correct", "none", "missed", "false", "wrong"]
SEVERAL = ("topic", "audience")
ONE = ("nature", "source")
API_TRIES = 3  # renders of one article that may end in an API error before it is given up
AVERAGED = ("requests", "input_tokens", "output_tokens", "seconds")


class Entry(TypedDict):
    """An article of the sample."""

    id: int
    site: str
    url: str
    listed_on: str


class Label(TypedDict):
    """The owner's labels of one article."""

    id: int
    topic: list[str]
    audience: list[str]
    nature: str
    source: str
    deadline: str | None


@dataclass(frozen=True)
class Scores:
    """Micro-averaged agreement of predicted tags with the labelled ones."""

    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class Result:
    """What rendering one article gave, beside its labels."""

    id: int
    url: str
    outcome: Literal["passed", "fallback", "api-error"]
    failures: tuple[str, ...]  # the checks that failed attempts, in order
    api_errors: int
    waits: tuple[str, ...]  # the API errors and failed checks that made the article wait
    requests: int
    input_tokens: int
    output_tokens: int
    seconds: float
    images: int
    left_out_images: tuple[str, ...]  # the URLs of input images the answer left out
    tags: dict[str, list[str]]
    labels: dict[str, list[str]]
    model_deadline: date | None  # before the date finder
    deadline: date | None
    labelled_deadline: date | None
    title: str
    summary: str | None
    markdown: str


def tag_scores(pairs: Iterable[tuple[frozenset[str], frozenset[str]]]) -> Scores:
    """Scores over (predicted, labelled) tag sets, counted over every tag of every article."""
    right = wrong = missed = 0
    for got, wanted in pairs:
        right += len(got & wanted)
        wrong += len(got - wanted)
        missed += len(wanted - got)
    precision = right / (right + wrong) if right + wrong else 0.0
    recall = right / (right + missed) if right + missed else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return Scores(precision, recall, f1)


def deadline_outcome(got: date | None, wanted: date | None) -> Outcome:
    """How the rendered deadline compares with the labelled one."""
    if got == wanted:
        return "correct" if got else "none"
    if got is None:
        return "missed"
    return "false" if wanted is None else "wrong"


def summarize(results: list[Result]) -> dict[str, object]:
    """The report: checks, tag agreement, deadlines and the cost per article."""
    passed = [r for r in results if r.outcome == "passed"]
    outcomes = Counter(deadline_outcome(r.deadline, r.labelled_deadline) for r in passed)
    tags: dict[str, object] = {
        dim: asdict(tag_scores((frozenset(r.tags[dim]), frozenset(r.labels[dim])) for r in passed))
        for dim in SEVERAL
    }
    for dim in ONE:
        right = sum(r.tags[dim] == r.labels[dim] for r in passed)
        tags[dim] = {"accuracy": right / len(passed) if passed else 0.0}
    return {
        "articles": len(results),
        "passed": len(passed),
        "passed_first_attempt": sum(not r.failures for r in passed),
        "fallbacks": sum(r.outcome == "fallback" for r in results),
        "given_up_after_api_errors": sum(r.outcome == "api-error" for r in results),
        "api_errors": sum(r.api_errors for r in results),
        "images": sum(r.images for r in results if r.outcome == "passed"),
        "images_left_out": sum(len(r.left_out_images) for r in results),
        "per_article": {
            name: round(fmean(getattr(r, name) for r in results), 1) for name in AVERAGED
        },
        "tags": tags,
        "deadlines": {outcome: outcomes[outcome] for outcome in get_args(Outcome)}
        | {
            "dropped_by_date_finder": sum(
                r.model_deadline is not None and r.deadline is None for r in passed
            )
        },
    }


class Records(logging.Handler):
    """The rendering log's messages since the last `take`."""

    def __init__(self) -> None:
        """Keep INFO and above."""
        super().__init__(logging.INFO)
        self.messages: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Keep the record."""
        self.messages.append(record)

    def take(self) -> list[logging.LogRecord]:
        """The records since the last call."""
        taken, self.messages = self.messages, []
        return taken


@dataclass
class Recorder:
    """The model client, counting requests and keeping the last answer."""

    client: ModelClient
    requests: int = 0
    last: str = ""

    async def __call__(self, key: str, prompt: str, /) -> str:
        """Ask the client."""
        self.requests += 1
        self.last = await self.client(key, prompt)
        return self.last


def pending(entry: Entry, corpus: Path) -> Pending:
    """The sampled article as the rendering loop would pick it."""
    page = corpus / "pages" / f"{entry['site']}-{entry['id']}.html.gz"
    content = parse_article(gzip.decompress(page.read_bytes()).decode(), entry["url"])
    return Pending(
        entry["id"], 0, entry["url"], content.title, content.body_html, content.attachments,
        date.fromisoformat(entry["listed_on"]),
    )  # fmt: skip


def labelled(label: Label) -> dict[str, list[str]]:
    """The labels by dimension, each as a sorted list."""
    return {dim: sorted(label[dim]) for dim in SEVERAL} | {dim: [label[dim]] for dim in ONE}


async def measure_one(
    renderer: Renderer, recorder: Recorder, records: Records, item: Pending, label: Label
) -> Result:
    """Render `item`, trying again after API errors, and compare it with its labels."""
    client = recorder.client
    before = (recorder.requests, client.input_tokens, client.output_tokens)
    start = time.monotonic()
    api_errors = 0
    rendition = await renderer.render(item)
    while rendition is None and api_errors + 1 < API_TRIES:
        api_errors += 1
        rendition = await renderer.render(item)
    seconds = time.monotonic() - start
    taken = records.take()
    failures = tuple(r.getMessage() for r in taken if r.levelno == logging.INFO)
    waits = tuple(r.getMessage() for r in taken if " waits: " in r.getMessage())
    passed = rendition is not None and not rendition.fallback
    tags: dict[str, list[str]] = {}
    for dim, tag in rendition.tags if rendition else ():
        tags.setdefault(dim, []).append(tag)
    wanted = label["deadline"]
    given = model_input(item.title, item.body_html, item.attachments, item.url)
    images = {name: url for name, url in given.targets.items() if name.startswith("I")}
    markdown = parse_answer(recorder.last).markdown if passed else ""
    kept = {match[0] for match in PLACEHOLDER.finditer(markdown)}
    return Result(
        id=item.announcement_id,
        url=item.url,
        outcome="api-error"
        if rendition is None
        else "fallback"
        if rendition.fallback
        else "passed",
        failures=failures,
        api_errors=api_errors + (rendition is None),
        waits=waits,
        requests=recorder.requests - before[0],
        input_tokens=client.input_tokens - before[1],
        output_tokens=client.output_tokens - before[2],
        seconds=round(seconds, 1),
        images=len(images),
        left_out_images=tuple(url for name, url in images.items() if passed and name not in kept),
        tags={dim: sorted(tags.get(dim, [])) for dim in SEVERAL + ONE},
        labels=labelled(label),
        model_deadline=parse_answer(recorder.last).deadline if passed else None,
        deadline=rendition.deadline if rendition else None,
        labelled_deadline=date.fromisoformat(wanted) if wanted else None,
        title=rendition.title if rendition else item.title,
        summary=rendition.summary if rendition else None,
        markdown=rendition.markdown if rendition else "",
    )


async def measure(entries: list[Entry], labels: dict[int, Label], corpus: Path) -> list[Result]:
    """Render every entry with the configured model, one at a time."""
    config = ModelConfig.from_env(os.environ)
    if not config.keys:
        sys.exit("BULLETIN_MODEL_KEYS is not set")
    check = Path(os.environ.get("BULLETIN_DISCORD_CHECK", "tools/discord-markdown/check.mjs"))
    records = Records()
    log = logging.getLogger("bulletin.rendering")
    log.addHandler(records)
    log.setLevel(logging.INFO)
    results: list[Result] = []
    async with aiohttp.ClientSession() as session:
        recorder = Recorder(ModelClient(session, config))
        ring = KeyRing(config.keys, config.rate)
        renderer = Renderer(
            recorder, ring, Checker(check), config.model, time.monotonic, asyncio.sleep
        )
        try:
            for number, entry in enumerate(entries, 1):
                result = await measure_one(
                    renderer, recorder, records, pending(entry, corpus), labels[entry["id"]]
                )
                results.append(result)
                print(
                    f"{number}/{len(entries)} {entry['id']} {result.outcome}"
                    f" attempts={len(result.failures) + (result.outcome == 'passed')}"
                    f" {result.seconds}s",
                    file=sys.stderr,
                )
        finally:
            await renderer.checker.close()
    return results


def main(argv: list[str]) -> None:
    """Measure, print the summary and write the report."""
    sample, labels, corpus, out = map(Path, argv)
    entries: list[Entry] = json.loads(sample.read_text())
    by_id: dict[int, Label] = {label["id"]: label for label in json.loads(labels.read_text())}
    results = asyncio.run(measure(entries, by_id, corpus))
    config = ModelConfig.from_env(os.environ)
    summary = summarize(results)
    report = {
        "model": config.model,
        "thinking_level": config.thinking_level,
        "summary": summary,
        "articles": [asdict(r) for r in results],
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
