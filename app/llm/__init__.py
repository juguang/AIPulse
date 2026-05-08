"""LLM infrastructure for AI Pulse.

Provides multi-model routing, cost tracking, and prompt template management
for the AI content processing pipeline.

Exported modules:
    client       — LLMClients wrapper (AsyncOpenAI + AsyncAnthropic)
    router       — ModelRouter for task-type-based model routing
    cost_tracker — compute_cost function and CostInfo dataclass
    prompts      — Prompt templates for classification, summarization, scoring
"""
