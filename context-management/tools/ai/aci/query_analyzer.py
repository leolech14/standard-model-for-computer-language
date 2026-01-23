"""
Query Analyzer for Adaptive Context Intelligence (ACI)

Analyzes incoming queries to determine:
- Intent: What type of question is being asked
- Complexity: How difficult/broad is the query
- Scope: Internal (codebase) vs External (web research)
- Agent Context: Whether .agent/ files are relevant
"""

from enum import Enum
from dataclasses import dataclass
from typing import List
import re


class QueryIntent(Enum):
    """Classification of query intent."""
    ARCHITECTURE = "architecture"   # "how does X work", "explain the design"
    DEBUG = "debug"                 # "fix error", "issue with", "bug in"
    RESEARCH = "research"           # "best practice", "compare", "latest"
    VALIDATE = "validate"           # "check", "verify", "is this correct"
    TASK = "task"                   # "what should I work on", "next task"
    COUNT = "count"                 # "how many", "count of", "total"
    LOCATE = "locate"               # "find", "where is", "which file"
    EXPLAIN = "explain"             # "explain", "what is", "describe"
    IMPLEMENT = "implement"         # "implement", "create", "build"
    UNKNOWN = "unknown"


class QueryComplexity(Enum):
    """Estimated complexity of the query."""
    SIMPLE = "simple"       # Single fact lookup, <1min expected
    MODERATE = "moderate"   # Multi-file reasoning, 1-5min expected
    COMPLEX = "complex"     # Deep analysis, >5min expected


class QueryScope(Enum):
    """Whether query targets internal codebase or external knowledge."""
    INTERNAL = "internal"   # Answer exists in codebase
    EXTERNAL = "external"   # Requires web/external knowledge
    HYBRID = "hybrid"       # Needs both internal and external


@dataclass
class QueryProfile:
    """Complete profile of an analyzed query."""
    query: str
    intent: QueryIntent
    complexity: QueryComplexity
    scope: QueryScope
    needs_agent_context: bool
    suggested_sets: List[str]
    keywords: List[str]
    confidence: float  # 0.0-1.0, how confident is the analysis


# Intent detection keywords
INTENT_KEYWORDS = {
    QueryIntent.ARCHITECTURE: [
        "how does", "architecture", "design", "structure", "work",
        "flow", "pipeline", "system", "overview", "diagram"
    ],
    QueryIntent.DEBUG: [
        "error", "bug", "fix", "issue", "problem", "broken",
        "failing", "crash", "exception", "traceback", "debug"
    ],
    QueryIntent.RESEARCH: [
        "best practice", "compare", "vs", "versus", "latest",
        "trend", "recommendation", "should i", "2026", "2025",
        "industry", "standard", "pattern"
    ],
    QueryIntent.VALIDATE: [
        "check", "verify", "validate", "correct", "right",
        "confirm", "audit", "review", "compliant"
    ],
    QueryIntent.TASK: [
        "task", "todo", "work on", "next step", "priority",
        "sprint", "backlog", "ready", "execute", "claim"
    ],
    QueryIntent.COUNT: [
        "how many", "count", "total", "number of", "statistics",
        "stats", "metrics"
    ],
    QueryIntent.LOCATE: [
        "find", "where is", "which file", "locate", "search",
        "look for", "path to"
    ],
    QueryIntent.EXPLAIN: [
        "explain", "what is", "describe", "tell me about",
        "define", "meaning of", "purpose of"
    ],
    QueryIntent.IMPLEMENT: [
        "implement", "create", "build", "add", "write",
        "develop", "make", "generate"
    ],
}

# External scope indicators
EXTERNAL_INDICATORS = [
    "best practice", "latest", "2026", "2025", "industry",
    "standard", "recommendation", "compare with", "vs",
    "trend", "state of the art", "modern", "current"
]

# Agent context indicators
AGENT_INDICATORS = [
    "task", "sprint", "agent", "kernel", "bare", "truths",
    "registry", "confidence", "4d", "claim", "run", "handoff",
    "boot", "protocol", "manifest"
]

# Complexity indicators
COMPLEX_INDICATORS = [
    "all", "every", "complete", "comprehensive", "full",
    "entire", "across", "refactor", "redesign", "architecture"
]

SIMPLE_INDICATORS = [
    "single", "one", "quick", "just", "only", "specific",
    "this file", "this function", "count", "how many"
]


def _extract_keywords(query: str) -> List[str]:
    """Extract significant keywords from query."""
    # Lowercase and remove punctuation
    clean = re.sub(r'[^\w\s]', ' ', query.lower())
    words = clean.split()

    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'shall',
        'can', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
        'from', 'as', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'under', 'again', 'further',
        'then', 'once', 'here', 'there', 'when', 'where', 'why',
        'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
        'because', 'until', 'while', 'about', 'against', 'this',
        'that', 'these', 'those', 'it', 'its', 'i', 'me', 'my',
        'you', 'your', 'we', 'our', 'they', 'their', 'what', 'which'
    }

    return [w for w in words if w not in stop_words and len(w) > 2]


def _detect_intent(query: str, keywords: List[str]) -> tuple[QueryIntent, float]:
    """Detect query intent with confidence score."""
    query_lower = query.lower()

    best_intent = QueryIntent.UNKNOWN
    best_score = 0.0

    for intent, indicators in INTENT_KEYWORDS.items():
        score = 0.0
        for indicator in indicators:
            if indicator in query_lower:
                # Weight by indicator length (longer = more specific)
                score += len(indicator) / 10.0

        if score > best_score:
            best_score = score
            best_intent = intent

    # Normalize confidence to 0-1
    confidence = min(best_score / 3.0, 1.0)

    return best_intent, confidence


def _detect_complexity(query: str, keywords: List[str]) -> QueryComplexity:
    """Estimate query complexity."""
    query_lower = query.lower()

    # Check for simple indicators
    for indicator in SIMPLE_INDICATORS:
        if indicator in query_lower:
            return QueryComplexity.SIMPLE

    # Check for complex indicators
    complex_count = sum(1 for ind in COMPLEX_INDICATORS if ind in query_lower)
    if complex_count >= 2:
        return QueryComplexity.COMPLEX

    # Use keyword count as heuristic
    if len(keywords) <= 3:
        return QueryComplexity.SIMPLE
    elif len(keywords) <= 6:
        return QueryComplexity.MODERATE
    else:
        return QueryComplexity.COMPLEX


def _detect_scope(query: str, keywords: List[str]) -> QueryScope:
    """Detect if query needs external knowledge."""
    query_lower = query.lower()

    external_count = sum(1 for ind in EXTERNAL_INDICATORS if ind in query_lower)

    if external_count >= 2:
        return QueryScope.EXTERNAL
    elif external_count == 1:
        return QueryScope.HYBRID
    else:
        return QueryScope.INTERNAL


def _needs_agent_context(query: str, intent: QueryIntent) -> bool:
    """Determine if .agent/ context is relevant."""
    query_lower = query.lower()

    # Task-related intents always need agent context
    if intent == QueryIntent.TASK:
        return True

    # Check for agent-specific keywords
    for indicator in AGENT_INDICATORS:
        if indicator in query_lower:
            return True

    return False


def _suggest_sets(intent: QueryIntent, needs_agent: bool, keywords: List[str]) -> List[str]:
    """Suggest analysis sets based on query profile."""
    sets = []

    # Intent-based suggestions
    intent_sets = {
        QueryIntent.ARCHITECTURE: ["pipeline", "theory", "architecture_review"],
        QueryIntent.DEBUG: ["pipeline", "classifiers", "tests"],
        QueryIntent.VALIDATE: ["research_validation", "tests"],
        QueryIntent.TASK: ["agent_tasks", "agent_kernel"],
        QueryIntent.COUNT: [],  # Use INSTANT tier (truths)
        QueryIntent.LOCATE: [],  # Use RAG tier
        QueryIntent.EXPLAIN: ["theory", "docs_core"],
        QueryIntent.IMPLEMENT: ["pipeline", "classifiers"],
        QueryIntent.RESEARCH: [],  # External research
        QueryIntent.UNKNOWN: ["theory"],
    }

    sets.extend(intent_sets.get(intent, []))

    # Add agent sets if needed
    if needs_agent:
        if "agent_tasks" not in sets:
            sets.insert(0, "agent_tasks")
        if "agent_kernel" not in sets:
            sets.insert(0, "agent_kernel")

    # Keyword-based additions
    keyword_sets = {
        "viz": "viz_core",
        "visualization": "viz_core",
        "constraint": "constraints",
        "role": "role_registry",
        "atom": "research_atoms",
        "classifier": "classifiers",
        "schema": "schema",
    }

    for kw in keywords:
        if kw in keyword_sets and keyword_sets[kw] not in sets:
            sets.append(keyword_sets[kw])

    return sets[:5]  # Limit to 5 suggestions


def analyze_query(query: str) -> QueryProfile:
    """
    Analyze a query and return a complete profile.

    Args:
        query: The user's question or instruction

    Returns:
        QueryProfile with intent, complexity, scope, and suggestions
    """
    keywords = _extract_keywords(query)
    intent, confidence = _detect_intent(query, keywords)
    complexity = _detect_complexity(query, keywords)
    scope = _detect_scope(query, keywords)
    needs_agent = _needs_agent_context(query, intent)
    suggested_sets = _suggest_sets(intent, needs_agent, keywords)

    return QueryProfile(
        query=query,
        intent=intent,
        complexity=complexity,
        scope=scope,
        needs_agent_context=needs_agent,
        suggested_sets=suggested_sets,
        keywords=keywords,
        confidence=confidence
    )


# Convenience function for quick checks
def is_agent_query(query: str) -> bool:
    """Quick check if query relates to agent/task management."""
    profile = analyze_query(query)
    return profile.needs_agent_context


def is_external_query(query: str) -> bool:
    """Quick check if query needs external knowledge."""
    profile = analyze_query(query)
    return profile.scope in (QueryScope.EXTERNAL, QueryScope.HYBRID)
