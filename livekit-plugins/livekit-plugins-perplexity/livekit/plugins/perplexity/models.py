from typing import Literal

PerplexityChatModels = Literal["sonar-pro"]

PerplexityResponsesModels = Literal["perplexity/sonar"]

# The -latest aliases move to newer releases.
DecisionModels = Literal[
    "pplx-decider-v1.2",
    "pplx-decider-flash-v1.2",
    "pplx-decider-latest",
    "pplx-decider-flash-latest",
]
OpenRouterDecisionModels = Literal[
    "perplexity/pplx-decider-v1.2",
    "perplexity/pplx-decider-flash-v1.2",
    "~perplexity/pplx-decider-latest",
    "~perplexity/pplx-decider-flash-latest",
]
