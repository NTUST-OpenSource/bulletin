"""The units' kind and college by site id, in the order of the school's unit lists."""

import json
from dataclasses import dataclass
from functools import cache
from importlib import resources
from typing import Literal, cast

type Kind = Literal["all", "admin", "academic"]


@dataclass(frozen=True)
class Unit:
    """How the school files one site's unit."""

    site: int
    kind: Kind
    college: str | None = None


@cache
def units() -> tuple[Unit, ...]:
    """Return the units of units.json, in its order."""
    rows = cast(
        "list[dict[str, object]]",
        json.loads((resources.files("bulletin") / "units.json").read_text(encoding="utf-8")),
    )
    return tuple(
        Unit(
            cast("int", row["site"]),
            cast("Kind", row["kind"]),
            cast("str | None", row.get("college")),
        )
        for row in rows
    )
