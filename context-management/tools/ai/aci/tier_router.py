"""
Tier Router for Adaptive Context Intelligence (ACI)

Routes queries to the appropriate execution tier based on query profile:
- TIER 0 (INSTANT): Use cached truths for simple counts/stats
- TIER 1 (RAG): Use File Search for targeted lookups
- TIER 2 (LONG_CONTEXT): Gemini 3 Pro with 1M context for reasoning
- TIER 3 (PERPLEXITY): Use external research for web knowledge
- TIER 4 (FLASH_DEEP): Gemini 2.0 Flash with 2M context for massive analysis

Integrates with SemanticMatcher for graph-based context selection using:
- PURPOSE field (π₁-π₄) hierarchy
- 8-dimensional semantic space
- 19 edge types for upstream/downstream traversal
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional

from .query_analyzer import (
    QueryProfile,
    QueryIntent,
    QueryComplexity,
    QueryScope,
    analyze_query
)
from .semantic_matcher import (
    SemanticMatch,
    SemanticTarget,
    semantic_match,
    EdgeDirection,
    format_semantic_match,
)

# Model token limit fallbacks (used when API unavailable)
_TOKEN_LIMIT_DEFAULTS = {
    "gemini-3-pro": 1_000_000,
    "gemini-2.0-flash": 1_000_000,
    "gemini-2.0-flash-thinking-exp": 2_000_000,
}


def get_model_token_limit(model_name: str, default: int = 1_000_000) -> int:
    """
    Get input token limit for a Gemini model.

    Queries the Gemini API for the model's input_token_limit.
    Falls back to sensible defaults if API call fails.

    Args:
        model_name: Model identifier (e.g., "gemini-2.0-flash")
        default: Fallback limit if API unavailable

    Returns:
        Token limit as int, or default value on errors
    """
    try:
        from google import genai
        client = genai.Client()
        model_info = client.models.get(model=model_name)
        return model_info.input_token_limit
    except Exception:
        # Fall back to known defaults
        return _TOKEN_LIMIT_DEFAULTS.get(model_name, default)


def get_tier_token_limit(tier: "Tier") -> int:
    """
    Get recommended token limit for a tier.

    Dynamically queries the Gemini API to get the appropriate token limit
    for a tier's primary model. Falls back to sensible defaults on errors.

    Args:
        tier: The execution tier

    Returns:
        Recommended token limit for that tier
    """
    tier_models = {
        "instant": "gemini-3-pro",
        "rag": "gemini-3-pro",
        "long_context": "gemini-3-pro",
        "perplexity": None,  # External service, not applicable
        "flash_deep": "gemini-2.0-flash-thinking-exp",
        "hybrid": "gemini-2.0-flash-thinking-exp",
    }

    model = tier_models.get(tier.value)
    if model is None:
        return 1_000_000  # Default for external services

    return get_model_token_limit(model)


class Tier(Enum):
    """Execution tiers for query handling."""
    INSTANT = "instant"           # Tier 0: Cached truths, no AI call
    RAG = "rag"                   # Tier 1: File Search with citations
    LONG_CONTEXT = "long_context" # Tier 2: Gemini 3 Pro (1M context)
    PERPLEXITY = "perplexity"     # Tier 3: External web research
    FLASH_DEEP = "flash_deep"     # Tier 4: Gemini 2.0 Flash (2M context) - massive analysis
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
    # Semantic matching (graph-based context selection)
    semantic: Optional[SemanticMatch] = None
    context_flow: str = "turbulent"  # "laminar" (coherent) or "turbulent" (mixed)
    traversal_direction: EdgeDirection = EdgeDirection.BOTH


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

# Keywords that trigger FLASH_DEEP tier (2M context)
FLASH_DEEP_TRIGGERS = {
    # Comprehensive analysis keywords
    "comprehensive", "holistic", "exhaustive", "complete analysis",
    "everything", "all files", "entire codebase", "full codebase",
    "whole project", "entire project", "all modules", "all code",
    # Deep analysis keywords
    "deep analysis", "deep dive", "thorough analysis", "full analysis",
    # Multi-scope keywords
    "across all", "everywhere", "project-wide", "codebase-wide",
    # Synthesis keywords
    "synthesize all", "combine all", "integrate all", "summarize all",
    # Comparison keywords (needing multiple codebases)
    "compare repos", "compare projects", "cross-repo", "multi-repo",
}


def _is_flash_deep_query(query: str) -> tuple[bool, str]:
    """
    Detect if query needs FLASH_DEEP tier (2M context).

    Returns:
        (should_use_flash_deep, reason)
    """
    query_lower = query.lower()

    # Check for trigger keywords
    for trigger in FLASH_DEEP_TRIGGERS:
        if trigger in query_lower:
            return True, f"Keyword '{trigger}' detected - needs massive context"

    # Check for multiple explicit set requests (would exceed 1M)
    set_mentions = sum(1 for word in ["pipeline", "theory", "architecture", "agent", "visualization"]
                       if word in query_lower)
    if set_mentions >= 3:
        return True, f"Multiple domains ({set_mentions}) requested - needs massive context"

    return False, ""


def _get_fallback_tier(tier: Tier) -> Optional[Tier]:
    """Get fallback tier if primary fails."""
    fallbacks = {
        Tier.INSTANT: Tier.RAG,
        Tier.RAG: Tier.LONG_CONTEXT,
        Tier.LONG_CONTEXT: Tier.FLASH_DEEP,  # Escalate to larger context
        Tier.FLASH_DEEP: None,  # No fallback - maximum capacity
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
    elif tier == Tier.FLASH_DEEP:
        # FLASH_DEEP: Load EVERYTHING - 2M context capacity
        # Include all major sets for comprehensive analysis
        comprehensive_sets = [
            "pipeline", "theory", "architecture_review",
            "agent_full", "visualization", "classifiers"
        ]
        # Start with comprehensive sets, add any suggested that aren't included
        sets = comprehensive_sets + [s for s in sets if s not in comprehensive_sets]

    # Ensure we have at least one set
    if not sets:
        sets = ["theory"]

    # Limit based on tier capacity
    max_sets = 10 if tier == Tier.FLASH_DEEP else 5
    return sets[:max_sets]


def route_query(query: str, force_tier: Optional[Tier] = None, use_semantic: bool = True) -> RoutingDecision:
    """
    Route a query to the appropriate execution tier.

    This is the AUTO CONTEXT LOADER - it activates automatically on query input
    and uses the SMoC relationship graph for intelligent context selection.

    Args:
        query: The user's question or instruction
        force_tier: Optional tier override
        use_semantic: Whether to use semantic matching (default True)

    Returns:
        RoutingDecision with tier, sets, semantic match, and reasoning
    """
    # Analyze the query
    profile = analyze_query(query)

    # Perform semantic matching for graph-based context selection
    sem_match = semantic_match(query) if use_semantic else None

    # Handle forced tier
    if force_tier is not None:
        sets = _determine_sets(profile, force_tier)
        # Merge semantic suggestions if available
        if sem_match and sem_match.suggested_sets:
            sets = _merge_sets_ordered(sem_match.suggested_sets, sets)
        return RoutingDecision(
            tier=force_tier,
            primary_sets=sets,
            fallback_tier=_get_fallback_tier(force_tier),
            use_truths=force_tier == Tier.INSTANT,
            inject_agent=profile.needs_agent_context,
            reasoning=f"Forced to {force_tier.value} tier",
            semantic=sem_match,
            context_flow=sem_match.context_flow if sem_match else "turbulent",
            traversal_direction=sem_match.targets[0].direction if sem_match and sem_match.targets else EdgeDirection.BOTH,
        )

    # Check for FLASH_DEEP triggers FIRST (before routing matrix)
    # This allows comprehensive queries to bypass the matrix
    is_flash_deep, flash_reason = _is_flash_deep_query(query)
    if is_flash_deep and profile.scope == QueryScope.INTERNAL:
        tier = Tier.FLASH_DEEP
        reasoning = f"FLASH_DEEP: {flash_reason}"
    else:
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

    # Determine sets - use semantic matching first, then profile
    primary_sets = _determine_sets(profile, tier)

    # Merge semantic suggestions (semantic-first for laminar flow)
    if sem_match and sem_match.suggested_sets:
        if sem_match.context_flow == "laminar":
            # Laminar flow: semantic sets take priority (coherent context)
            primary_sets = _merge_sets_ordered(sem_match.suggested_sets, primary_sets)
        else:
            # Turbulent flow: profile sets take priority (broader context)
            primary_sets = _merge_sets_ordered(primary_sets, sem_match.suggested_sets)

    use_truths = _should_use_truths(profile.intent, profile.complexity)
    inject_agent = profile.needs_agent_context

    # If agent context needed, ensure agent sets are included
    if inject_agent and tier in (Tier.LONG_CONTEXT, Tier.HYBRID, Tier.FLASH_DEEP):
        agent_sets = ["agent_kernel", "agent_tasks"]
        for s in agent_sets:
            if s not in primary_sets:
                primary_sets.insert(0, s)

    # Enrich reasoning with semantic context
    if sem_match and sem_match.reasoning:
        reasoning = f"{reasoning} | Semantic: {sem_match.reasoning}"

    return RoutingDecision(
        tier=tier,
        primary_sets=primary_sets,
        fallback_tier=_get_fallback_tier(tier),
        use_truths=use_truths,
        inject_agent=inject_agent,
        reasoning=reasoning,
        semantic=sem_match,
        context_flow=sem_match.context_flow if sem_match else "turbulent",
        traversal_direction=sem_match.targets[0].direction if sem_match and sem_match.targets else EdgeDirection.BOTH,
    )


def _merge_sets_ordered(priority_sets: List[str], secondary_sets: List[str]) -> List[str]:
    """Merge two set lists, preserving order with priority_sets first."""
    seen = set()
    result = []
    for s in priority_sets:
        if s not in seen:
            seen.add(s)
            result.append(s)
    for s in secondary_sets:
        if s not in seen:
            seen.add(s)
            result.append(s)
    return result[:5]  # Limit to 5 sets


def tier_from_string(tier_str: str) -> Optional[Tier]:
    """Convert string to Tier enum."""
    tier_map = {
        "instant": Tier.INSTANT,
        "rag": Tier.RAG,
        "long_context": Tier.LONG_CONTEXT,
        "long-context": Tier.LONG_CONTEXT,
        "longcontext": Tier.LONG_CONTEXT,
        "perplexity": Tier.PERPLEXITY,
        "flash_deep": Tier.FLASH_DEEP,
        "flash-deep": Tier.FLASH_DEEP,
        "flashdeep": Tier.FLASH_DEEP,
        "deep": Tier.FLASH_DEEP,  # Shorthand
        "hybrid": Tier.HYBRID,
    }
    return tier_map.get(tier_str.lower())


def format_routing_decision(decision: RoutingDecision) -> str:
    """Format routing decision for display."""
    lines = [
        f"Tier: {decision.tier.value.upper()}",
        f"Sets: {', '.join(decision.primary_sets)}",
        f"Context Flow: {decision.context_flow}",
        f"Reason: {decision.reasoning}",
    ]

    if decision.fallback_tier:
        lines.append(f"Fallback: {decision.fallback_tier.value}")
    if decision.use_truths:
        lines.append("Will check repo_truths.yaml first")
    if decision.inject_agent:
        lines.append("Agent context will be auto-injected")

    # Semantic matching details
    if decision.semantic:
        lines.append("")
        lines.append("Semantic Match:")
        if decision.semantic.targets:
            for t in decision.semantic.targets:
                parts = []
                if t.purpose:
                    parts.append(f"π₂={t.purpose}")
                if t.layer:
                    parts.append(f"layer={t.layer}")
                if t.roles:
                    parts.append(f"roles=[{','.join(t.roles[:2])}]")
                lines.append(f"  Target: {' '.join(parts)}")
        lines.append(f"  Traversal: {decision.traversal_direction.value}")

    return "\n".join(lines)
