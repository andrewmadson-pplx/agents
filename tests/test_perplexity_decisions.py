from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from livekit.agents import APIStatusError
from livekit.agents.llm import decisions
from livekit.plugins import perplexity

pytestmark = pytest.mark.unit

QUESTIONS = {
    "human": decisions.Probability("The caller wants a human."),
    "team": decisions.Choice("Which team?", options={"billing": "Invoices", "tech": "Outages"}),
    "frustration": decisions.Score("Frustration?", levels=["Calm", "Annoyed", "Furious"]),
}


def response_body(model="pplx-decider-v1.2"):
    return {
        "model": model,
        "answers": {
            "human": {"type": "noul", "noul": 0.998},
            "team": {
                "type": "choice",
                "choice": "tech",
                "confidence": 0.997,
                "probabilities": {"billing": 0.001, "tech": 0.999},
            },
            "frustration": {
                "type": "score",
                "score": 1.697,
                "confidence": 0.697,
                "legend": {"0": "Calm", "1": "Annoyed", "2": "Furious"},
                "probabilities": {"0": 0.004, "1": 0.294, "2": 0.702},
            },
        },
        "usage": {"input_tokens": 163, "output_tokens": 3},
    }


def session_for(body, status=200):
    response = MagicMock()
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=False)
    response.status = status
    response.headers = {"x-request-id": "request-1"}
    response.json = AsyncMock(return_value=body)
    http_session = MagicMock(spec=aiohttp.ClientSession)
    http_session.post.return_value = response
    return http_session


async def test_decisions_api_uses_env_key_attribution_and_request_id(monkeypatch) -> None:
    monkeypatch.setenv("PERPLEXITY_API_KEY", "env-key")
    http = session_for(response_body())
    model = perplexity.DecisionModel(http_session=http)
    response = await model.evaluate(input="user: Get me a person.", decisions=QUESTIONS)
    assert http.post.call_args.args[0] == "https://api.perplexity.ai/v1/decisions"
    assert http.post.call_args.kwargs["headers"] == {
        "Authorization": "Bearer env-key",
        "X-Pplx-Integration": f"livekit-agents/{perplexity.__version__}",
    }
    assert http.post.call_args.kwargs["json"]["model"] == "pplx-decider-v1.2"
    assert (response.model, response.provider) == ("pplx-decider-v1.2", "Perplexity")
    assert response.request_id == "request-1"
    assert response.errors == {}
    assert response.results["human"].value == 0.998
    assert response.results["team"].value == "tech"
    assert response.results["frustration"].levels == ["Calm", "Annoyed", "Furious"]
    assert response.input_tokens == 163


async def test_openrouter_uses_its_key_endpoint_and_generation_id(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "router-key")
    body = response_body("perplexity/pplx-decider-v1.2-20261016") | {"id": "gen-dec-1"}
    http = session_for(body)
    model = perplexity.DecisionModel.with_openrouter(http_session=http)
    response = await model.evaluate(input="", decisions=QUESTIONS)
    assert http.post.call_args.args[0] == "https://openrouter.ai/api/alpha/decisions"
    assert http.post.call_args.kwargs["headers"] == {"Authorization": "Bearer router-key"}
    assert http.post.call_args.kwargs["json"]["model"] == "perplexity/pplx-decider-v1.2"
    assert (model.model, model.provider) == ("perplexity/pplx-decider-v1.2", "openrouter")
    assert response.model == "perplexity/pplx-decider-v1.2-20261016"
    assert response.request_id == "gen-dec-1"


def test_missing_api_key_fails_at_construction(monkeypatch) -> None:
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ValueError, match="PERPLEXITY_API_KEY"):
        perplexity.DecisionModel()
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        perplexity.DecisionModel.with_openrouter()


async def test_auth_errors_are_not_retried() -> None:
    http = session_for({}, status=401)
    model = perplexity.DecisionModel(api_key="test-key", http_session=http)
    with pytest.raises(APIStatusError) as error:
        await model.evaluate(input="", decisions=QUESTIONS)
    assert (error.value.status_code, error.value.request_id) == (401, "request-1")
    http.post.assert_called_once()
