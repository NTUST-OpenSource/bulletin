"""What the model reads: an article reduced to Markdown, its links and images as placeholders."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from bulletin.model import Attachment


@dataclass(frozen=True)
class ModelInput:
    """The input text and the URL each placeholder (`L1`, `I1`, ...) stands for."""

    text: str
    targets: dict[str, str]


def model_input(
    title: str, body_html: str, attachments: Sequence[Attachment], url: str
) -> ModelInput:
    """Reduce an article at `url` to the model's input."""
    raise NotImplementedError
