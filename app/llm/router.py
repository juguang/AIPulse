"""Multi-model LLM router — route tasks to optimal provider/model by task type.

Task routing table (matches 02-RESEARCH.md Pattern 5):
    - classification -> GPT-4o-mini (OpenAI), cheap but capable for category labels
    - tagging       -> GPT-4o-mini (OpenAI), same model, same pricing
    - summarization -> Claude Sonnet (Anthropic), stronger Chinese/multilingual
    - scoring       -> Claude Sonnet (Anthropic), higher reasoning quality

Usage:
    router = ModelRouter(clients)
    text, cost_info = await router.process(
        "classification",
        system_prompt=CLASSIFICATION_SYSTEM,
        user_prompt=CLASSIFICATION_USER.format(title=..., content=...),
    )
"""

from typing import Literal
from app.llm.client import LLMClients
from app.llm.cost_tracker import compute_cost, CostInfo

TaskType = Literal["classification", "tagging", "summarization", "scoring"]

# Route table: maps each processing task to its optimal provider and model.
# Dict lookup pattern instead of if-else branching for maintainability.
TASK_ROUTES: dict[TaskType, dict] = {
    "classification": {
        "provider": "openai",
        "model": "gpt-4o-mini",
    },
    "tagging": {
        "provider": "openai",
        "model": "gpt-4o-mini",
    },
    "summarization": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20260514",
    },
    "scoring": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20260514",
    },
}


class ModelRouter:
    """Routes LLM processing tasks to the appropriate provider/model.

    Args:
        clients: An LLMClients instance with openai and anthropic clients.
        settings: Optional Settings object for model overrides.

    The router handles both OpenAI and Anthropic API differences internally
    (message format, system prompt placement, usage fields) so callers
    get a uniform (text, CostInfo) return tuple regardless of provider.
    """

    def __init__(self, clients: LLMClients, settings=None):
        self.clients = clients
        self.settings = settings

    async def process(
        self,
        task_type: TaskType,
        system_prompt: str = "",
        user_prompt: str = "",
        max_tokens: int = 4096,
    ) -> tuple[str, CostInfo]:
        """Execute an LLM task through the appropriate provider.

        Args:
            task_type: One of "classification", "tagging", "summarization", "scoring".
            system_prompt: System-level instruction (provider-dependent format).
            user_prompt: The user/content message.
            max_tokens: Maximum output tokens.

        Returns:
            (response_text, CostInfo) tuple with model, token counts, and cost.

        Raises:
            ValueError: If task_type has no route or unknown provider.
        """
        route = TASK_ROUTES[task_type]
        model = route["model"]

        if route["provider"] == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})
            resp = await self.clients.openai.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )
            usage = resp.usage
            cost = compute_cost(model, usage.prompt_tokens, usage.completion_tokens)
            return resp.choices[0].message.content, CostInfo(
                model=model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                cost_usd=cost,
            )

        elif route["provider"] == "anthropic":
            messages = [{"role": "user", "content": user_prompt}]
            kwargs = {}
            if system_prompt:
                kwargs["system"] = system_prompt
            resp = await self.clients.anthropic.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                **kwargs,
            )
            usage = resp.usage
            cost = compute_cost(model, usage.input_tokens, usage.output_tokens)
            return resp.content[0].text, CostInfo(
                model=model,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cost_usd=cost,
            )

        raise ValueError(f"Unknown provider: {route['provider']}")
