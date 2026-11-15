"""The model's API: Gemini's generateContent or an OpenAI-compatible chat completions API."""

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    import aiohttp

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-4-hydrogen"


class ApiFormat(StrEnum):
    """How a request asks the model and how its answer reads."""

    GEMINI = "gemini"  # generateContent, the key in x-goog-api-key
    OPENAI = "openai"  # chat/completions, the key as a bearer token


class ApiError(Exception):
    """The API answered with a status other than 200, or the request did not reach it."""

    def __init__(self, status: int | None, message: str) -> None:
        """Keep the status, None when no answer came."""
        super().__init__(f"HTTP {status}: {message}" if status else message)
        self.status = status


@dataclass(frozen=True)
class ModelConfig:
    """The model's settings; without keys the service renders nothing."""

    keys: tuple[str, ...] = ()
    api_format: ApiFormat = ApiFormat.GEMINI
    endpoint: str = GEMINI_ENDPOINT
    model: str = DEFAULT_MODEL
    rate: int = 10  # requests per key per minute
    thinking_level: str = "low"  # empty sends none

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> ModelConfig:
        """Read the `BULLETIN_MODEL*` and `BULLETIN_THINKING_LEVEL` variables."""
        raise NotImplementedError


class ModelClient:
    """One request at a time to the configured API."""

    def __init__(self, session: aiohttp.ClientSession, config: ModelConfig) -> None:
        """Post over `session` with `config`'s settings."""
        self.session = session
        self.config = config

    async def __call__(self, key: str, prompt: str) -> str:
        """The answer's text for `prompt`, asked with `key`."""
        raise NotImplementedError
