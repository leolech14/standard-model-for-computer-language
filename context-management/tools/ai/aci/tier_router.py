"""
Tier Router for Adaptive Context Intelligence (ACI)

Routes queries to the appropriate execution tier based on query profile:
- TIER 0 (INSTANT): Use cached truths for simple counts/stats
- TIER 1 (RAG): Use File Search for targeted lookups
- TIER 2 (LONG_CONTEXT): Use full context sets for reasoning
- TIER 3 (PERPLEXITY): Use external research for web knowledge
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

from .query_analyzer import (
    QueryProfile,
    QueryIntent,
    QueryComplexity,
    QueryScope,
    analyze_query
)


class Tier(Enum):
    """Execution tiers for query handling."""
    INSTANT = "instant"           # Tier 0: Cached truths, no AI call
    RAG = "rag"                   # Tier 1: File Search with citations
    LONG_CONTEXT = "long_context" # Tier 2: Full context Gemini
    PERPLEXITY = "perplexity"     # Tier 3: External web research
    HYBRID = "hybrid"             # Multi-tier execution


@dataclass
class RoutingDecision:
    """Complete routing decision for a query."""
    tier: Tier
    primary_sets: List[str]      # Analysis sets to use
    fallback_tier: Optional[Tier] # If primary fails
    use_truths: bool             # Check repo_truths.yaml first
    inject_agent: bool           # Auto-inject agent_* sets
    reasoning: str               # Why this tier was chosen


# Decision matrix: (Intent, Complexity, Scope) -> Tier
# Format: {(intent, complexity, scope): (tier, reasoning)}
ROUTING_MATRIX = {
    # COUNT queries - use INSTANT tier (truths)
    (QueryIntent.COUNT, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
        (Tier.INSTANT, "Simple count query - use cached truths"),

    # LOCATE queries - use RAG for fast search
    (QueryIntent.LOCATE, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
        (Tier.RAG, "File location query - RAG with citations"),
    (QueryIntent.LOCATE, QueryComplexity.MODERATE, QueryScope.INTERNAL):
        (Tier.RAG, "Multi-file search - RAG with citations"),

    # DEBUG queries - prefer RAG then escalate to LONG_CONTEXT
    (QueryIntent.DEBUG, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
        (Tier.RAG, "Simple debug - search for error patterns"),
    (QueryIntent.DEBUG, QueryComplexity.MODERATE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Moderate debug - need multi-file reasoning"),
    (QueryIntent.DEBUG, QueryComplexity.COMPLEX, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Complex debug - need full context"),

    # ARCHITECTURE queries - always LONG_CONTEXT
    (QueryIntent.ARCHITECTURE, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Architecture query - need structural reasoning"),
    (QueryIntent.ARCHITECTURE, QueryComplexity.MODERATE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Architecture query - need multi-file reasoning"),
    (QueryIntent.ARCHITECTURE, QueryComplexity.COMPLEX, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Complex architecture - full context needed"),

    # TASK queries - LONG_CONTEXT with agent sets
    (QueryIntent.TASK, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Task query - need agent context"),
    (QueryIntent.TASK, QueryComplexity.MODERATE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Task planning - need agent context"),
    (QueryIntent.TASK, QueryComplexity.COMPLEX, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Complex task planning - full agent context"),

    # VALIDATE queries - LONG_CONTEXT
    (QueryIntent.VALIDATE, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Validation query - need reasoning"),
    (QueryIntent.VALIDATE, QueryComplexity.MODERATE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Validation query - need reasoning"),

    # EXPLAIN queries - depends on complexity
    (QueryIntent.EXPLAIN, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
        (Tier.RAG, "Simple explanation - search for definitions"),
    (QueryIntent.EXPLAIN, QueryComplexity.MODERATE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Explanation needs context"),

    # IMPLEMENT queries - LONG_CONTEXT
    (QueryIntent.IMPLEMENT, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Implementation needs code context"),
    (QueryIntent.IMPLEMENT, QueryComplexity.MODERATE, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Implementation needs full context"),
    (QueryIntent.IMPLEMENT, QueryComplexity.COMPLEX, QueryScope.INTERNAL):
        (Tier.LONG_CONTEXT, "Complex implementation - full context"),

    # RESEARCH queries (external scope) - PERPLEXITY
    (QueryIntent.RESEARCH, QueryComplexity.SIMPLE, QueryScope.EXTERNAL):
        (Tier.PERPLEXITY, "External research - use web search"),
    (QueryIntent.RESEARCH, QueryComplexity.MODERATE, QueryScope.EXTERNAL):
        (Tier.PERPLEXITY, "External research - use web search"),
    (QueryIntent.RESEARCH, QueryComplexity.COMPLEX, QueryScope.EXTERNAL):
        (Tier.PERPLEXITY, "Deep research - use Perplexity"),

    # HYBRID scope - need both internal and external
    (QueryIntent.RESEARCH, QueryComplexity.SIMPLE, QueryScope.HYBRID):
        (Tier.HYBRID, "Hybrid query - internal + external"),
    (QueryIntent.RESEARCH, QueryComplexity.MODERATE, QueryScope.HYBRID):
        (Tier.HYBRID, "Hybrid query - internal + external"),
    (QueryIntent.ARCHITECTURE, QueryComplexity.SIMPLE, QueryScope.HYBRID):
        (Tier.HYBRID, "Architecture comparison - internal + external"),
}


def _get_fallback_tier(tier: Tier) -> Optional[Tier]:
    """Get fallback tier if primary fails."""
    fallbacks = {
        Tier.INSTANT: Tier.RAG,
        Tier.RAG: Tier.LONG_CONTEXT,
        Tier.LONG_CONTEXT: None,  # No fallback
        Tier.PERPLEXITY: Tier.LONG_CONTEXT,  # Fall back to internal
        Tier.HYBRID: Tier.LONG_CONTEXT,
    }
    return fallbacks.get(tier)


def _should_use_truths(intent: QueryIntent, complexity: QueryComplexity) -> bool:
    """Determine if repo_truths.yaml should be checked first."""
    # COUNT queries always check truths
    if intent == QueryIntent.COUNT:
        return True

    # Simple queries might benefit from truths
    if complexity == QueryComplexity.SIMPLE:
        return intent in (QueryIntent.LOCATE, QueryIntent.EXPLAIN)

    return False


def _determine_sets(profile: QueryProfile, tier: Tier) -> List[str]:
    """Determine which analysis sets to use."""
    sets = []

    # Start with suggested sets from analyzer
    sets.extend(profile.suggested_sets)

    # Tier-specific adjustments
    if tier == Tier.RAG:
        # RAG works best with focused sets
        if not sets:
            sets = ["pipeline", "classifiers"]
    elif tier == Tier.LONG_CONTEXT:
        # Long context can handle larger sets
        if profile.intent == QueryIntent.TASK:
            # Task queries need full agent context
            sets = ["agent_full"] + [s for s in sets if not s.startswith("agent_")]
        elif profile.intent == QueryIntent.ARCHITECTURE:
            if "architecture_review" not in sets:
                sets.append("architecture_review")

    # Ensure we have at least one set
    if not sets:
        sets = ["theory"]

    return sets[:5]  # Limit to 5 sets


def route_query(query: str, force_tier: Optional[Tier] = None) -> RoutingDecision:
    """
    Route a query to the appropriate execution tier.

    Args:
        query: The user's question or instruction
        force_tier: Optional tier override

    Returns:
        RoutingDecision with tier, sets, and reasoning
    """
    # Analyze the query
    profile = analyze_query(query)

    # Handle forced tier
    if force_tier is not None:
        return RoutingDecision(
            tier=force_tier,
            primary_sets=_determine_sets(profile, force_tier),
            fallback_tier=_get_fallback_tier(force_tier),
            use_truths=force_tier == Tier.INSTANT,
            inject_agent=profile.needs_agent_context,
            reasoning=f"Forced to {force_tier.value} tier"
        )

    # Look up in routing matrix
    key = (profile.intent, profile.complexity, profile.scope)
    if key in ROUTING_MATRIX:
        tier, reasoning = ROUTING_MATRIX[key]
    else:
        # Default routing based on scope
        if profile.scope == QueryScope.EXTERNAL:
            tier = Tier.PERPLEXITY
            reasoning = "External scope - defaulting to Perplexity"
        elif profile.scope == QueryScope.HYBRID:
            tier = Tier.HYBRID
            reasoning = "Hybrid scope - need internal and external"
        else:
            # Default to LONG_CONTEXT for internal queries
            tier = Tier.LONG_CONTEXT
            reasoning = "Default routing to long context"

    # Determine sets and other options
    primary_sets = _determine_sets(profile, tier)
    use_truths = _should_use_truths(profile.intent, profile.complexity)
    inject_agent = profile.needs_agent_context

    # If agent context needed, ensure agent sets are included
    if inject_agent and tier in (Tier.LONG_CONTEXT, Tier.HYBRID):
        agent_sets = ["agent_kernel", "agent_tasks"]
        for s in agent_sets:
            if s not in primary_sets:
                primary_sets.insert(0, s)

    return RoutingDecision(
        tier=tier,
        primary_sets=primary_sets,
        fallback_tier=_get_fallback_tier(tier),
        use_truths=use_truths,
        inject_agent=inject_agent,
        reasoning=reasoning
    )


def tier_from_string(tier_str: str) -> Optional[Tier]:
    """Convert string to Tier enum."""
    tier_map = {
        "instant": Tier.INSTANT,
        "rag": Tier.RAG,
        "long_context": Tier.LONG_CONTEXT,
        "long-context": Tier.LONG_CONTEXT,
        "longcontext": Tier.LONG_CONTEXT,
        "perplexity": Tier.PERPLEXITY,
        "hybrid": Tier.HYBRID,
    }
    return tier_map.get(tier_str.lower())


def format_routing_decision(decision: RoutingDecision) -> str:
    """Format routing decision for display."""
    lines = [
        f"Tier: {decision.tier.value.upper()}",
        f"Sets: {', '.join(decision.primary_sets)}",
        f"Reason: {decision.reasoning}",
    ]

    if decision.fallback_tier:
        lines.append(f"Fallback: {decision.fallback_tier.value}")
    if decision.use_truths:
        lines.append("Will check repo_truths.yaml first")
    if decision.inject_agent:
        lines.append("Agent context will be auto-injected")

    return "\n".join(lines)
