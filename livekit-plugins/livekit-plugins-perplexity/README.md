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

## Decisions API usage

`perplexity.DecisionModel` evaluates probability questions, named choices, and ordered
scores over a conversation in one request through Perplexity's Decisions API. Use
`DecisionModel.with_openrouter()` to call the same models through OpenRouter's Decisions
API with `OPENROUTER_API_KEY`.

```python
from livekit.agents import llm, utils
from livekit.plugins import perplexity

async with utils.http_context.open():
    model = perplexity.DecisionModel(model="pplx-decider-v1.2")
    # or: perplexity.DecisionModel.with_openrouter()
    context = llm.ChatContext.empty()
    context.add_message(role="user", content="Please let me speak to a person.")
    response = await model.evaluate(
        input=context,
        decisions={
            "handoff": llm.Probability("The caller requests a human."),
            "intent": llm.Choice(
                "What does the caller want?",
                options={"booking": "Make a reservation", "other": "Anything else"},
            ),
            "frustration": llm.Score(
                "How frustrated is the caller?", levels=["Calm", "Annoyed", "Angry"]
            ),
        },
    )
    for name, result in response.results.items():
        print(name, result.value)
```

`pplx-decider-v1.2` (27B) is the default and `pplx-decider-flash-v1.2` is a 4B model.
`pplx-decider-latest` and `pplx-decider-flash-latest` move to newer
releases. Through OpenRouter, use the `perplexity/` prefix, for example
`perplexity/pplx-decider-flash-v1.2`, or the `~perplexity/pplx-decider-latest` alias.
A request takes up to 128 decisions, each choice up to 255 options, and each score up to
10 levels.
