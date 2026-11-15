"""Checks of the model's answer, in order; any that fails fails the attempt."""


class AnswerError(ValueError):
    """The answer fails a check."""


def restore(text: str, targets: dict[str, str]) -> str:
    """Replace each placeholder in `text` by the URL it stands for."""
    raise NotImplementedError
