"""Requirement "Model configuration": the settings, and requests in both API formats."""

import json
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from bulletin.model_api import ApiError, ApiFormat, ModelClient, ModelConfig
from bulletin.prompt import answer_schema

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

FIXTURES = Path(__file__).parent / "fixtures" / "model"
GEMINI = json.loads((FIXTURES / "gemini-answer.json").read_text(encoding="utf-8"))["response"]
OPENAI = json.loads((FIXTURES / "openai-answer.json").read_text(encoding="utf-8"))["response"]
KEY = "test-key-0123456789"


class Api:
    """A fake API that records each request and answers as the recordings did."""

    def __init__(self) -> None:
        self.requests: list[tuple[str, dict[str, str], object]] = []
        self.status = 200

    async def answer(self, request: web.Request) -> web.Response:
        self.requests.append((request.path_qs, dict(request.headers), await request.json()))
        if self.status != 200:
            error = {"error": {"code": self.status, "message": f"quota exceeded for {KEY}"}}
            return web.json_response(error, status=self.status)
        return web.json_response(OPENAI if request.path.endswith("completions") else GEMINI)


@pytest.fixture
async def api() -> AsyncGenerator[tuple[Api, TestServer]]:
    fake = Api()
    app = web.Application()
    app.router.add_post("/v1beta/models/gemini-4-hydrogen:generateContent", fake.answer)
    app.router.add_post("/v1/chat/completions", fake.answer)
    running = TestServer(app, host="127.0.0.1")
    async with running:
        yield fake, running


async def ask(config: ModelConfig) -> str:
    async with aiohttp.ClientSession() as session:
        return await ModelClient(session, config)(KEY, "the prompt")


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Model configuration")
async def test_gemini(api: tuple[Api, TestServer]) -> None:
    """Model configuration: Gemini's generateContent with the schema and the thinking level."""
    fake, server = api
    endpoint = str(server.make_url("/v1beta"))

    text = await ask(ModelConfig(keys=(KEY,), endpoint=endpoint))

    assert json.loads(text)["deadline"] == "2026-12-10"
    ((path, headers, body),) = fake.requests
    assert path == "/v1beta/models/gemini-4-hydrogen:generateContent"
    assert headers["x-goog-api-key"] == KEY
    assert "Authorization" not in headers
    assert body == {
        "contents": [{"parts": [{"text": "the prompt"}]}],
        "generationConfig": {
            "responseFormat": {"text": {"mimeType": "APPLICATION_JSON", "schema": answer_schema()}},
            "thinkingConfig": {"thinkingLevel": "low"},
        },
    }


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Model configuration")
async def test_an_openai_compatible_endpoint(api: tuple[Api, TestServer]) -> None:
    """Model configuration: chat completions at the endpoint, the key as a bearer token."""
    fake, server = api
    config = ModelConfig(
        keys=(KEY,), api_format=ApiFormat.OPENAI, endpoint=str(server.make_url("/v1")), model="m"
    )

    text = await ask(config)

    assert json.loads(text)["title"]
    ((path, headers, body),) = fake.requests
    assert path == "/v1/chat/completions"
    assert headers["Authorization"] == f"Bearer {KEY}"
    assert body == {
        "model": "m",
        "messages": [{"role": "user", "content": "the prompt"}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "rendition", "schema": answer_schema(), "strict": True},
        },
        "reasoning_effort": "low",
    }


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Model configuration")
async def test_an_api_error(api: tuple[Api, TestServer]) -> None:
    """Model configuration: an answer other than HTTP 200 is an API error with its status."""
    fake, server = api
    fake.status = 429

    with pytest.raises(ApiError) as raised:
        await ask(ModelConfig(keys=(KEY,), endpoint=str(server.make_url("/v1beta"))))

    assert raised.value.status == 429


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Model configuration")
async def test_an_unreachable_api() -> None:
    """Model configuration: a request that reaches no API is an API error without a status."""
    with pytest.raises(ApiError) as raised:
        await ask(ModelConfig(keys=(KEY,), endpoint="http://127.0.0.1:9/v1beta"))

    assert raised.value.status is None


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Model configuration")
def test_the_settings() -> None:
    """Model configuration: endpoint, format, model, keys and thinking level, with defaults."""
    assert ModelConfig.from_env({}) == ModelConfig()
    assert ModelConfig.from_env(
        {
            "BULLETIN_MODEL_KEYS": " a, b ,,",
            "BULLETIN_MODEL_FORMAT": "openai",
            "BULLETIN_MODEL_ENDPOINT": "http://llama:8080/v1/",
            "BULLETIN_MODEL": "gemma",
            "BULLETIN_MODEL_RATE": "30",
            "BULLETIN_THINKING_LEVEL": "",
        }
    ) == ModelConfig(("a", "b"), ApiFormat.OPENAI, "http://llama:8080/v1", "gemma", 30, "")


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Model configuration")
@pytest.mark.parametrize(
    ("name", "value"),
    [("BULLETIN_MODEL_FORMAT", "claude"), ("BULLETIN_MODEL_RATE", "0")],
)
def test_wrong_settings(name: str, value: str) -> None:
    """Model configuration: a wrong setting names its variable."""
    with pytest.raises(ValueError, match=name):
        ModelConfig.from_env({name: value})
