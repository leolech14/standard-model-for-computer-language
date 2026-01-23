"""
Adaptive Context Intelligence (ACI) System

Automatically selects the right context tier (RAG/Long-Context/Perplexity)
for every query based on intent, complexity, and scope analysis.

Usage:
    from aci import analyze_and_route

    # Get routing decision for a query
    decision = analyze_and_route("how does atom classification work")
    print(f"Tier: {decision.tier.value}")
    print(f"Sets: {decision.primary_sets}")
"""

from .query_analyzer import (
    QueryIntent,
    QueryComplexity,
    QueryScope,
    QueryProfile,
    analyze_query,
    is_agent_query,
    is_external_query,
)

from .tier_router import (
    Tier,
    RoutingDecision,
    route_query,
    tier_from_string,
    format_routing_decision,
)

from .context_optimizer import (
    OptimizedContext,
    load_repo_truths,
    answer_from_truths,
    optimize_context,
    format_context_summary,
)

__all__ = [
    # Query Analyzer
    "QueryIntent",
    "QueryComplexity",
    "QueryScope",
    "QueryProfile",
    "analyze_query",
    "is_agent_query",
    "is_external_query",
    # Tier Router
    "Tier",
    "RoutingDecision",
    "route_query",
    "tier_from_string",
    "format_routing_decision",
    # Context Optimizer
    "OptimizedContext",
    "load_repo_truths",
    "answer_from_truths",
    "optimize_context",
    "format_context_summary",
]


def analyze_and_route(query: str, force_tier: str = ""):
    """
    Convenience function: analyze query and route to appropriate tier.

    Args:
        query: The user's question
        force_tier: Optional tier override ("instant", "rag", "long_context", "perplexity")

    Returns:
        RoutingDecision with tier, sets, and reasoning
    """
    forced = tier_from_string(force_tier) if force_tier else None
    return route_query(query, force_tier=forced)
