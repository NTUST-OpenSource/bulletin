"""Scaffolding for "Sites and boards" (public-api): the unit data the sites list is ordered by."""

import json
from collections import Counter
from pathlib import Path
from typing import get_args

from bulletin.units import Kind, units

SEED = Path(__file__).parents[1] / "seeds" / "boards.json"


def test_every_polled_site_appears_once() -> None:
    boards = json.loads(SEED.read_text(encoding="utf-8"))["boards"]
    polled = {b["site_id"] for b in boards if b["tier"] != "off" and b["category"] != "excluded"}
    counts = Counter(unit.site for unit in units())
    assert polled <= set(counts)
    assert all(n == 1 for n in counts.values())


def test_colleges_belong_to_academic_units() -> None:
    assert {unit.kind for unit in units()} == set(get_args(Kind.__value__))
    assert all((unit.college is not None) == (unit.kind == "academic") for unit in units())


def test_the_school_wide_board_comes_first() -> None:
    first = units()[0]
    assert (first.site, first.kind) == (1045, "all")
