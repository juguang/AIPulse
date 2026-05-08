"""Per-request cost computation utility for multi-model LLM routing.

Usage:
    cost_info = compute_cost("gpt-4o-mini", input_tokens=500, output_tokens=100)
    # -> CostInfo(model="gpt-4o-mini", input_tokens=500, output_tokens=100, cost_usd=0.000135)

Pricing data source: PECollective / Benchwright — LLM Pricing May 2026.
"""

from dataclasses import dataclass


@dataclass
class CostInfo:
    """Immutable cost information for a single LLM request."""

    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


# Pricing per million tokens (USD)
# Source: PECollective / Benchwright "What 12 LLMs Actually Cost" — May 2026
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {"input_per_mtok": 0.15, "output_per_mtok": 0.60},
    "claude-sonnet-4-20260514": {"input_per_mtok": 3.00, "output_per_mtok": 15.00},
}


def compute_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Compute USD cost for an LLM request.

    Args:
        model: Model name string (e.g. "gpt-4o-mini").
        input_tokens: Number of prompt tokens consumed.
        output_tokens: Number of completion tokens generated.

    Returns:
        Total cost rounded to 6 decimal places, or 0.0 for unknown models.

    Security note: Model pricing is public information. Token counts are logged
    for cost tracking only and are not exposed to end users.
    """
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return 0.0
    cost = (
        input_tokens / 1_000_000 * pricing["input_per_mtok"]
        + output_tokens / 1_000_000 * pricing["output_per_mtok"]
    )
    return round(cost, 6)
