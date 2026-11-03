from __future__ import annotations

import pytest

from livekit.plugins.perplexity import __version__, responses
from livekit.plugins.perplexity.responses.llm import PERPLEXITY_RESPONSES_BASE_URL

pytestmark = pytest.mark.plugin("perplexity")


def test_default_model_base_url_and_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test-key")
    llm = responses.LLM()
    assert llm.model == "sonar-pro"
    assert llm._opts.use_websocket is False
    assert PERPLEXITY_RESPONSES_BASE_URL == "https://api.perplexity.ai/v1"
    assert str(llm._client.base_url).startswith("https://api.perplexity.ai/v1")


def test_attribution_header_attached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test-key")
    llm = responses.LLM()
    assert llm._client.default_headers["X-Pplx-Integration"] == f"livekit-agents/{__version__}"


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
    with pytest.raises(ValueError, match="PERPLEXITY_API_KEY"):
        responses.LLM()


def test_responses_submodule_exported() -> None:
    assert responses.LLM is not None


def test_provider_tools_serialize_for_responses_llm() -> None:
    from livekit.agents import llm
    from livekit.agents.llm._provider_format.openai import to_responses_fnc_ctx
    from livekit.plugins import perplexity

    tool_ctx = llm.ToolContext(
        [
            perplexity.WebSearch(search_type="fast", filters={"search_recency_filter": "week"}),
            perplexity.FetchUrl(),
        ]
    )
    assert to_responses_fnc_ctx(tool_ctx, provider_tool_type=responses.LLM._provider_tool_type) == [
        {"type": "web_search", "search_type": "fast", "filters": {"search_recency_filter": "week"}},
        {"type": "fetch_url"},
    ]
