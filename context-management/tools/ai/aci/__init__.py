"""
Adaptive Context Intelligence (ACI) System

Automatically selects the right context tier (RAG/Long-Context/Perplexity)
for every query based on intent, complexity, and scope analysis.

The "Curriculum Compiler" - prepares optimal context for AI to study before answering.

Usage:
    from aci import analyze_and_route, ACI_CONFIG

    # Get routing decision for a query
    decision = analyze_and_route("how does atom classification work")
    print(f"Tier: {decision.tier.value}")
    print(f"Sets: {decision.primary_sets}")

    # Access configuration
    print(f"Token budget: {ACI_CONFIG.get('token_budgets', {}).get('hard_cap')}")
"""

import yaml
from pathlib import Path
from typing import Dict, Any

# =============================================================================
# CONFIGURATION LOADER
# =============================================================================
# Load aci_config.yaml once at module import time.
# All ACI submodules should import ACI_CONFIG from here.

def _load_aci_config() -> Dict[str, Any]:
    """Load ACI configuration from YAML file."""
    # Navigate from aci/ -> ai/ -> tools/ -> context-management/ -> config/
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "aci_config.yaml"

    if not config_path.exists():
        print(f"[ACI] Warning: Config not found at {config_path}, using defaults")
        return {}

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
            return config
    except Exception as e:
        print(f"[ACI] Warning: Failed to load config: {e}")
        return {}

# Singleton config - loaded once at import
ACI_CONFIG: Dict[str, Any] = _load_aci_config()

# =============================================================================
# MODULE IMPORTS
# =============================================================================

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
    # Configuration
    "ACI_CONFIG",
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
