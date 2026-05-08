"""LLM client manager — holds AsyncOpenAI and AsyncAnthropic instances."""

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic


class LLMClients:
    """Holds AsyncOpenAI and AsyncAnthropic clients.

    Initialize during FastAPI lifespan:
        app.state.llm = LLMClients.from_settings(settings)

    Usage in routers:
        clients = getattr(request.app.state, "llm", None)
        resp, cost = await clients.openai.chat.completions.create(...)
    """

    def __init__(self, openai_client: AsyncOpenAI, anthropic_client: AsyncAnthropic):
        self.openai = openai_client
        self.anthropic = anthropic_client

    @classmethod
    def from_settings(cls, settings) -> "LLMClients":
        """Create clients from a Settings object (app.config.Settings)."""
        return cls(
            openai_client=AsyncOpenAI(api_key=settings.OPENAI_API_KEY),
            anthropic_client=AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY),
        )

    async def close(self):
        """Close both clients gracefully.

        Both clients share a single httpx.AsyncClient session internally;
        calling close() ensures proper cleanup.
        """
        if hasattr(self.openai, "close"):
            await self.openai.close()
        if hasattr(self.anthropic, "close"):
            await self.anthropic.close()
