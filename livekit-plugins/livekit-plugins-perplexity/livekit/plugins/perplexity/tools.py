from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from livekit.agents import ProviderTool


class PerplexityTool(ProviderTool):
    """Base class for Perplexity Agent API server-side provider tools."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]: ...


@dataclass
class WebSearch(PerplexityTool):
    """Enable the Agent API web search tool.

    See https://docs.perplexity.ai/docs/agent-api/tools/web-search for the ``filters``
    and ``user_location`` fields.
    """

    search_type: Literal["web", "fast"] | None = None
    filters: dict[str, Any] | None = None
    user_location: dict[str, Any] | None = None
    max_results: int | None = None
    max_tokens: int | None = None
    max_tokens_per_page: int | None = None

    def __post_init__(self) -> None:
        super().__init__(id="perplexity_web_search")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"type": "web_search"}
        for key in (
            "search_type",
            "filters",
            "user_location",
            "max_results",
            "max_tokens",
            "max_tokens_per_page",
        ):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        return result


@dataclass
class FetchUrl(PerplexityTool):
    """Enable the Agent API tool that fetches and extracts content from URLs."""

    max_urls: int | None = None

    def __post_init__(self) -> None:
        super().__init__(id="perplexity_fetch_url")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"type": "fetch_url"}
        if self.max_urls is not None:
            result["max_urls"] = self.max_urls
        return result
