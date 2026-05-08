"""Per-request cost computation for DeepSeek API.

Usage:
    cost_info = compute_cost("deepseek-v4-flash", input_tokens=500, output_tokens=100)
"""

from dataclasses import dataclass


@dataclass
class CostInfo:
    """Immutable cost information for a single LLM request."""

    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


# DeepSeek v4 Flash pricing (per million tokens, USD)
# Source: DeepSeek official pricing — May 2026
MODEL_PRICING: dict[str, dict[str, float]] = {
    "deepseek-v4-flash": {"input_per_mtok": 0.30, "output_per_mtok": 0.60},
}


def compute_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Compute USD cost for an LLM request."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return 0.0
    cost = (
        input_tokens / 1_000_000 * pricing["input_per_mtok"]
        + output_tokens / 1_000_000 * pricing["output_per_mtok"]
    )
    return round(cost, 6)
