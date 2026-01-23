"""
Feedback Loop for Adaptive Context Intelligence (ACI)

Logs every ACI query and enables learning from results:
- Query profile
- Tier selected
- Sets used
- Tokens consumed
- Success/retry signal

Feedback is stored in .agent/intelligence/aci_feedback.yaml
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict
import yaml
import os

from .query_analyzer import QueryProfile
from .tier_router import RoutingDecision


@dataclass
class FeedbackEntry:
    """A single feedback entry for an ACI query."""
    timestamp: str
    query: str
    intent: str
    complexity: str
    scope: str
    tier: str
    sets_used: List[str]
    tokens_input: int
    tokens_output: int
    success: bool
    retry_count: int
    fallback_used: bool
    duration_ms: int
    error: Optional[str] = None


class FeedbackLoop:
    """
    Manages feedback collection and storage for ACI.

    Feedback is used to:
    1. Track query patterns over time
    2. Identify common failure modes
    3. Tune routing decisions
    4. Measure token efficiency
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.feedback_dir = project_root / ".agent/intelligence"
        self.feedback_file = self.feedback_dir / "aci_feedback.yaml"
        self._ensure_dir()

    def _ensure_dir(self):
        """Ensure feedback directory exists."""
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

    def _load_feedback(self) -> Dict:
        """Load existing feedback data."""
        if not self.feedback_file.exists():
            return {
                "version": "1.0.0",
                "created": datetime.now(timezone.utc).isoformat(),
                "entries": [],
                "stats": {
                    "total_queries": 0,
                    "by_tier": {},
                    "by_intent": {},
                    "success_rate": 0.0,
                    "avg_tokens": 0,
                }
            }

        try:
            with open(self.feedback_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {"version": "1.0.0", "entries": [], "stats": {}}

    def _save_feedback(self, data: Dict):
        """Save feedback data."""
        with open(self.feedback_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def _update_stats(self, data: Dict, entry: FeedbackEntry):
        """Update aggregate statistics."""
        stats = data.get("stats", {})

        # Total queries
        stats["total_queries"] = stats.get("total_queries", 0) + 1

        # By tier
        by_tier = stats.get("by_tier", {})
        by_tier[entry.tier] = by_tier.get(entry.tier, 0) + 1
        stats["by_tier"] = by_tier

        # By intent
        by_intent = stats.get("by_intent", {})
        by_intent[entry.intent] = by_intent.get(entry.intent, 0) + 1
        stats["by_intent"] = by_intent

        # Success rate (rolling)
        total = stats["total_queries"]
        old_rate = stats.get("success_rate", 0.0)
        new_rate = ((old_rate * (total - 1)) + (1.0 if entry.success else 0.0)) / total
        stats["success_rate"] = round(new_rate, 4)

        # Average tokens (rolling)
        old_avg = stats.get("avg_tokens", 0)
        new_avg = ((old_avg * (total - 1)) + entry.tokens_input) / total
        stats["avg_tokens"] = int(new_avg)

        data["stats"] = stats

    def log_query(
        self,
        profile: QueryProfile,
        decision: RoutingDecision,
        tokens_input: int,
        tokens_output: int,
        success: bool,
        duration_ms: int,
        retry_count: int = 0,
        fallback_used: bool = False,
        error: Optional[str] = None
    ):
        """
        Log a query execution to the feedback file.

        Args:
            profile: Query profile from analyzer
            decision: Routing decision from router
            tokens_input: Input tokens consumed
            tokens_output: Output tokens generated
            success: Whether query succeeded
            duration_ms: Execution time in milliseconds
            retry_count: Number of retries needed
            fallback_used: Whether fallback tier was used
            error: Error message if failed
        """
        entry = FeedbackEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            query=profile.query[:200],  # Truncate long queries
            intent=profile.intent.value,
            complexity=profile.complexity.value,
            scope=profile.scope.value,
            tier=decision.tier.value,
            sets_used=decision.primary_sets,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            success=success,
            retry_count=retry_count,
            fallback_used=fallback_used,
            duration_ms=duration_ms,
            error=error
        )

        data = self._load_feedback()

        # Keep only last 1000 entries
        entries = data.get("entries", [])
        if len(entries) >= 1000:
            entries = entries[-999:]

        entries.append(asdict(entry))
        data["entries"] = entries

        self._update_stats(data, entry)
        self._save_feedback(data)

    def get_stats(self) -> Dict:
        """Get current feedback statistics."""
        data = self._load_feedback()
        return data.get("stats", {})

    def get_recent_entries(self, count: int = 10) -> List[Dict]:
        """Get most recent feedback entries."""
        data = self._load_feedback()
        entries = data.get("entries", [])
        return entries[-count:]

    def get_tier_recommendations(self) -> Dict[str, str]:
        """
        Analyze feedback to suggest routing improvements.

        Returns dict of suggestions based on patterns.
        """
        data = self._load_feedback()
        entries = data.get("entries", [])

        if len(entries) < 10:
            return {"status": "Need more data (10+ queries)"}

        suggestions = {}

        # Check for high retry rates per tier
        tier_retries = {}
        tier_counts = {}
        for e in entries:
            tier = e.get("tier", "unknown")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            tier_retries[tier] = tier_retries.get(tier, 0) + e.get("retry_count", 0)

        for tier, count in tier_counts.items():
            if count > 5:
                retry_rate = tier_retries[tier] / count
                if retry_rate > 0.3:
                    suggestions[tier] = f"High retry rate ({retry_rate:.1%}), consider fallback"

        # Check for token efficiency
        stats = data.get("stats", {})
        avg_tokens = stats.get("avg_tokens", 0)
        if avg_tokens > 150_000:
            suggestions["tokens"] = f"High avg tokens ({avg_tokens:,}), consider smaller sets"

        return suggestions if suggestions else {"status": "No issues detected"}


# Module-level convenience functions
_feedback_instance: Optional[FeedbackLoop] = None


def get_feedback_loop(project_root: Optional[Path] = None) -> FeedbackLoop:
    """Get or create feedback loop instance."""
    global _feedback_instance

    if _feedback_instance is None:
        root = project_root
        if root is None:
            # Try to detect project root
            env_root = os.environ.get("PROJECT_ROOT")
            if env_root:
                root = Path(env_root)
            else:
                root = Path(__file__).parent.parent.parent.parent.parent
        _feedback_instance = FeedbackLoop(root)

    return _feedback_instance


def log_aci_query(
    profile: QueryProfile,
    decision: RoutingDecision,
    tokens_input: int,
    tokens_output: int,
    success: bool,
    duration_ms: int,
    **kwargs
):
    """Convenience function to log an ACI query."""
    fb = get_feedback_loop()
    fb.log_query(
        profile=profile,
        decision=decision,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        success=success,
        duration_ms=duration_ms,
        **kwargs
    )
