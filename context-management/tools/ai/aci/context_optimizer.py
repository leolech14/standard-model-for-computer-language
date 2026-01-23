"""
Context Optimizer for Adaptive Context Intelligence (ACI)

Handles:
- Automatic injection of .agent/ context when needed
- Strategic positioning of critical files (sandwich/front-load)
- Context budget management (from aci_config.yaml)
- Truths integration for instant queries
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
import yaml

# =============================================================================
# CONFIGURATION
# =============================================================================
# Load from aci_config.yaml via the module's config loader.
# Defaults are provided as fallback if config is unavailable.

_DEFAULT_TOKEN_BUDGETS = {
    "guru": 50_000,        # Focused analysis
    "architect": 150_000,  # Multi-file reasoning
    "archeologist": 200_000,  # Deep exploration
    "perilous": 200_001,   # Avoid - lost-in-middle effects
}

_DEFAULT_HARD_CAP = 200_000  # Maximum recommended tokens

def _get_config():
    """Get ACI config, with lazy import to avoid circular dependency."""
    try:
        # Import here to avoid circular import at module load time
        from . import ACI_CONFIG
        return ACI_CONFIG
    except ImportError:
        return {}

def get_token_budgets() -> Dict[str, int]:
    """Get token budgets from config or defaults."""
    config = _get_config()
    config_budgets = config.get("token_budgets", {})
    # Merge config over defaults
    budgets = _DEFAULT_TOKEN_BUDGETS.copy()
    budgets.update(config_budgets)
    return budgets

def get_hard_cap() -> int:
    """Get hard cap from config or default."""
    config = _get_config()
    return config.get("token_budgets", {}).get("hard_cap", _DEFAULT_HARD_CAP)

# Note: Use get_token_budgets() and get_hard_cap() functions directly.
# Module-level constants removed to ensure config is always read.


@dataclass
class OptimizedContext:
    """Result of context optimization."""
    sets: List[str]              # Final list of sets to use
    truths: Optional[Dict]       # Repo truths if loaded
    positioning: str             # "sandwich" or "front-load"
    critical_files: List[str]    # Files to position strategically
    estimated_tokens: int        # Estimated total token count
    budget_warning: bool         # True if exceeding recommended budget


def load_repo_truths(project_root: Path) -> Optional[Dict]:
    """Load cached truths from BARE TruthValidator."""
    truths_path = project_root / ".agent/intelligence/truths/repo_truths.yaml"
    if not truths_path.exists():
        return None

    try:
        with open(truths_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def answer_from_truths(query: str, truths: Dict) -> Optional[str]:
    """Try to answer a query using cached truths."""
    query_lower = query.lower()

    # Pattern: "how many X files"
    if "how many" in query_lower:
        counts = truths.get("counts", {})
        files = counts.get("files", {})

        # Check for specific file type
        for ext, count in files.items():
            if ext in query_lower:
                return f"There are {count} {ext} files in the repository."

        # General file count
        if "files" in query_lower and files:
            total = sum(files.values())
            breakdown = ", ".join(f"{c} {e}" for e, c in files.items())
            return f"Total files: {total} ({breakdown})"

        # Lines of code
        if "lines" in query_lower or "loc" in query_lower:
            loc = counts.get("lines_of_code")
            if loc:
                return f"The repository contains approximately {loc:,} lines of code."

        # Functions
        if "function" in query_lower:
            funcs = counts.get("functions")
            if funcs:
                return f"There are approximately {funcs} functions in the repository."

        # Classes
        if "class" in query_lower:
            classes = counts.get("classes")
            if classes:
                return f"There are approximately {classes} classes in the repository."

    # Pattern: "what is the pipeline" - check for known facts
    if "pipeline" in query_lower and "stages" in query_lower:
        pipeline = truths.get("pipeline", {})
        stages = pipeline.get("stages")
        if stages:
            return f"The analysis pipeline has {stages} stages."

    return None


def get_critical_files_for_sets(
    sets: List[str],
    sets_config: Dict
) -> List[str]:
    """Extract critical files from set configurations."""
    critical = []
    seen = set()

    for set_name in sets:
        set_def = sets_config.get(set_name, {})
        files = set_def.get("critical_files", [])
        for f in files:
            if f not in seen:
                critical.append(f)
                seen.add(f)

    return critical


def get_positional_strategy(
    sets: List[str],
    sets_config: Dict
) -> str:
    """Determine positioning strategy from sets."""
    # Priority: sandwich > front-load > none
    strategies = []

    for set_name in sets:
        set_def = sets_config.get(set_name, {})
        strategy = set_def.get("positional_strategy")
        if strategy:
            strategies.append(strategy)

    if "sandwich" in strategies:
        return "sandwich"
    elif "front-load" in strategies:
        return "front-load"
    else:
        return "none"


def estimate_tokens_for_sets(
    sets: List[str],
    sets_config: Dict
) -> int:
    """Estimate total token count for given sets."""
    total = 0
    seen_sets = set()

    def _estimate_recursive(set_name: str) -> int:
        if set_name in seen_sets:
            return 0
        seen_sets.add(set_name)

        set_def = sets_config.get(set_name, {})
        tokens = set_def.get("max_tokens", 50_000)

        # Handle includes
        for included in set_def.get("includes", []):
            tokens = max(tokens, _estimate_recursive(included))

        return tokens

    for s in sets:
        total += _estimate_recursive(s)

    return total


def inject_agent_context(
    sets: List[str],
    inject_level: str = "minimal"
) -> List[str]:
    """Inject appropriate agent context sets.

    Args:
        sets: Current list of sets
        inject_level: "minimal" (kernel only), "standard" (kernel+tasks),
                      "full" (all agent sets)
    """
    injection_map = {
        "minimal": ["agent_kernel"],
        "standard": ["agent_kernel", "agent_tasks"],
        "full": ["agent_full"],
    }

    to_inject = injection_map.get(inject_level, ["agent_kernel"])

    # Inject at beginning (high attention position)
    result = []
    for s in to_inject:
        if s not in sets:
            result.append(s)

    result.extend(s for s in sets if s not in to_inject)
    return result


def optimize_context(
    sets: List[str],
    sets_config: Dict,
    project_root: Path,
    use_truths: bool = True,
    inject_agent: bool = False,
    inject_level: str = "standard"
) -> OptimizedContext:
    """
    Optimize context for a query.

    Args:
        sets: Initial list of analysis sets
        sets_config: Full sets configuration
        project_root: Path to project root
        use_truths: Whether to load repo_truths.yaml
        inject_agent: Whether to inject agent context
        inject_level: Level of agent context injection

    Returns:
        OptimizedContext with optimized sets and metadata
    """
    # Inject agent context if requested
    if inject_agent:
        sets = inject_agent_context(sets, inject_level)

    # Load truths if requested
    truths = load_repo_truths(project_root) if use_truths else None

    # Get critical files and positioning
    critical_files = get_critical_files_for_sets(sets, sets_config)
    positioning = get_positional_strategy(sets, sets_config)

    # Estimate tokens and check against config-driven hard cap
    estimated_tokens = estimate_tokens_for_sets(sets, sets_config)
    hard_cap = get_hard_cap()
    budget_warning = estimated_tokens > hard_cap

    return OptimizedContext(
        sets=sets,
        truths=truths,
        positioning=positioning,
        critical_files=critical_files,
        estimated_tokens=estimated_tokens,
        budget_warning=budget_warning
    )


def format_context_summary(ctx: OptimizedContext) -> str:
    """Format context optimization summary for display."""
    lines = [
        f"Sets: {', '.join(ctx.sets)}",
        f"Estimated tokens: {ctx.estimated_tokens:,}",
        f"Positioning: {ctx.positioning}",
    ]

    if ctx.critical_files:
        lines.append(f"Critical files: {len(ctx.critical_files)}")

    if ctx.truths:
        lines.append("Truths: loaded")

    if ctx.budget_warning:
        lines.append(f"WARNING: Exceeds {get_hard_cap():,} token budget!")

    return "\n".join(lines)
