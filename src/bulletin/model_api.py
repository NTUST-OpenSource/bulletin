"""The model's API: Gemini's generateContent or an OpenAI-compatible chat completions API."""

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, cast

import aiohttp

from bulletin.prompt import answer_schema

if TYPE_CHECKING:
    from collections.abc import Mapping

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-4-hydrogen"
TIMEOUT = aiohttp.ClientTimeout(total=300, connect=30)
OK = 200


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
        """Read the `BULLETIN_MODEL*` and `BULLETIN_THINKING_LEVEL` variables.

        `BULLETIN_MODEL_KEYS` holds comma-separated keys; raise ValueError naming a variable
        that is wrong.
        """
        defaults = cls()
        name = "BULLETIN_MODEL_FORMAT"
        try:
            api_format = ApiFormat(env.get(name, defaults.api_format))
        except ValueError as error:
            msg = f"{name} is gemini or openai"
            raise ValueError(msg) from error
        name = "BULLETIN_MODEL_RATE"
        rate = env.get(name, str(defaults.rate))
        if not rate.isdigit() or int(rate) < 1:
            msg = f"{name} is a number of requests per minute, at least 1"
            raise ValueError(msg)
        keys = (key.strip() for key in env.get("BULLETIN_MODEL_KEYS", "").split(","))
        return cls(
            tuple(filter(None, keys)),
            api_format,
            env.get("BULLETIN_MODEL_ENDPOINT", defaults.endpoint).rstrip("/"),
            env.get("BULLETIN_MODEL", defaults.model),
            int(rate),
            env.get("BULLETIN_THINKING_LEVEL", defaults.thinking_level),
        )

    @property
    def url(self) -> str:
        """Where each request is posted."""
        if self.api_format is ApiFormat.OPENAI:
            return f"{self.endpoint}/chat/completions"
        return f"{self.endpoint}/models/{self.model}:generateContent"

    def headers(self, key: str) -> dict[str, str]:
        """The header that carries `key`: never the URL."""
        if self.api_format is ApiFormat.OPENAI:
            return {"Authorization": f"Bearer {key}"}
        return {"x-goog-api-key": key}

    def body(self, prompt: str) -> dict[str, object]:
        """The request's JSON body: the prompt, the answer schema and the thinking level."""
        schema = answer_schema()
        if self.api_format is ApiFormat.OPENAI:
            chat: dict[str, object] = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {"name": "rendition", "schema": schema, "strict": True},
                },
            }
            return chat | ({"reasoning_effort": self.thinking_level} if self.thinking_level else {})
        config: dict[str, object] = {
            "responseFormat": {"text": {"mimeType": "APPLICATION_JSON", "schema": schema}}
        }
        if self.thinking_level:
            config["thinkingConfig"] = {"thinkingLevel": self.thinking_level}
        return {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": config}


def _field(value: object, name: str) -> object:
    return cast("dict[str, object]", value).get(name) if isinstance(value, dict) else None


def _items(value: object) -> list[object]:
    return cast("list[object]", value) if isinstance(value, list) else []


def answer_text(api_format: ApiFormat, answer: object) -> str:
    """The text of an answer, empty for one without text (a blocked prompt, a refusal).

    Gemini: the first candidate's text parts that are not thoughts. OpenAI: the first choice's
    content.
    """
    if api_format is ApiFormat.OPENAI:
        choices = _items(_field(answer, "choices"))
        content = _field(_field(choices[0], "message"), "content") if choices else None
        return content if isinstance(content, str) else ""
    candidates = _items(_field(answer, "candidates"))
    parts = _items(_field(_field(candidates[0], "content"), "parts")) if candidates else []
    return "".join(
        text
        for part in parts
        if isinstance(text := _field(part, "text"), str) and _field(part, "thought") is not True
    )


def error_message(answer: object) -> str:
    """The message of an error answer; Gemini's compatible endpoint wraps it in a list of one."""
    items = _items(answer)
    error = _field(items[0] if items else answer, "error")
    message = error if isinstance(error, str) else _field(error, "message")
    return message if isinstance(message, str) else ""


class ModelClient:
    """One request at a time to the configured API."""

    def __init__(self, session: aiohttp.ClientSession, config: ModelConfig) -> None:
        """Post over `session` with `config`'s settings."""
        self.session = session
        self.config = config

    async def __call__(self, key: str, prompt: str) -> str:
        """The answer's text for `prompt`, asked with `key`; redirects are not followed.

        Raises:
            ApiError: the API answered with a status other than 200, or did not answer.
        """
        config = self.config
        try:
            async with self.session.post(
                config.url,
                json=config.body(prompt),
                headers=config.headers(key),
                timeout=TIMEOUT,
                allow_redirects=False,
            ) as response:
                text = await response.text(errors="replace")
                status = response.status
        except (aiohttp.ClientError, TimeoutError) as error:
            raise ApiError(None, str(error) or type(error).__name__) from error
        try:
            answer: object = json.loads(text)
        except json.JSONDecodeError:
            answer = None
        if status != OK:
            raise ApiError(status, error_message(answer) or text[:200])
        return answer_text(config.api_format, answer)
