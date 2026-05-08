"""LLM router — single model routing using DeepSeek v4 Flash.

All processing tasks use the same model via OpenAI-compatible API.
"""

from typing import Literal
from app.llm.client import LLMClients
from app.llm.cost_tracker import compute_cost, CostInfo

TaskType = Literal["classification", "tagging", "summarization", "scoring"]

DEFAULT_MODEL = "deepseek-v4-flash"


class ModelRouter:
    """Routes LLM processing tasks to DeepSeek model.

    Args:
        clients: An LLMClients instance with DeepSeek AsyncOpenAI client.
        settings: Optional Settings object for model overrides.
    """

    def __init__(self, clients: LLMClients, settings=None):
        self.clients = clients
        self.settings = settings

    @property
    def model(self) -> str:
        if self.settings and self.settings.DEEPSEEK_MODEL:
            return self.settings.DEEPSEEK_MODEL
        return DEFAULT_MODEL

    async def process(
        self,
        task_type: TaskType,
        system_prompt: str = "",
        user_prompt: str = "",
        max_tokens: int = 4096,
    ) -> tuple[str, CostInfo]:
        """Execute an LLM task through DeepSeek API.

        Args:
            task_type: One of "classification", "tagging", "summarization", "scoring".
            system_prompt: System-level instruction.
            user_prompt: The user/content message.
            max_tokens: Maximum output tokens.

        Returns:
            (response_text, CostInfo) tuple with model, token counts, and cost.
        """
        model = self.model
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        resp = await self.clients.client.chat.completions.create(
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
