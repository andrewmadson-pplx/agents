# Perplexity plugin for LiveKit Agents

Support for [Perplexity](https://www.perplexity.ai/) LLMs via the OpenAI-compatible
chat completions endpoint at `https://api.perplexity.ai`.

See [https://docs.livekit.io/agents/models/llm/perplexity/](https://docs.livekit.io/agents/models/llm/perplexity/) for more information.

## Installation

```bash
pip install livekit-plugins-perplexity
```

## Pre-requisites

You'll need an API key from Perplexity. It can be passed directly or set as the
`PERPLEXITY_API_KEY` environment variable.

## Usage

```python
from livekit.plugins import perplexity

llm = perplexity.LLM(
    model="sonar-pro",
    # api_key picked up from PERPLEXITY_API_KEY if omitted
)
```

The plugin reuses the OpenAI plugin's chat completions transport with
`base_url="https://api.perplexity.ai"` and forwards an `X-Pplx-Integration`
attribution header on every outgoing request.

## Agent API usage

Perplexity's Agent API is compatible with OpenAI's Responses API and is
available through the `perplexity.responses` submodule.

```python
from livekit.plugins import perplexity

llm = perplexity.responses.LLM(
    model="perplexity/sonar",
    # api_key picked up from PERPLEXITY_API_KEY if omitted
)
```

The Responses LLM uses `base_url="https://api.perplexity.ai/v1"`, disables
websocket transport, and sends the same `X-Pplx-Integration` attribution header
on its OpenAI-compatible client.

Agent API built-in tools run on Perplexity's servers. Pass them to the agent
with the Responses LLM:

```python
from livekit.agents import Agent
from livekit.plugins import perplexity

agent = Agent(
    instructions="You are a helpful assistant.",
    llm=perplexity.responses.LLM(model="openai/gpt-5.5"),
    tools=[perplexity.WebSearch(max_results=5), perplexity.FetchUrl(max_urls=1)],
)
```
