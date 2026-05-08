"""LLM client manager — holds AsyncOpenAI for DeepSeek API."""

from openai import AsyncOpenAI


class LLMClients:
    """Holds AsyncOpenAI client configured for DeepSeek API.

    Initialize during FastAPI lifespan:
        app.state.llm = LLMClients.from_settings(settings)

    DeepSeek API is OpenAI-compatible — uses AsyncOpenAI with custom base_url.
    """

    def __init__(self, client: AsyncOpenAI):
        self.client = client

    @classmethod
    def from_settings(cls, settings) -> "LLMClients":
        """Create DeepSeek client from Settings."""
        return cls(
            client=AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
            ),
        )

    async def close(self):
        if hasattr(self.client, "close"):
            await self.client.close()
