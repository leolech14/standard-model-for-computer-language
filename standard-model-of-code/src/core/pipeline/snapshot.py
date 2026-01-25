"""
Pipeline Snapshot - Captures state at each stage for visualization.

Used by Pipeline Navigator to show before/after comparisons and data flow.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json


@dataclass
class FieldDelta:
    """Tracks a field that was added or changed by a stage."""
    field_name: str
    added_count: int = 0  # How many nodes got this field added
    changed_count: int = 0  # How many nodes had this field changed
    sample_values: List[Any] = field(default_factory=list)  # Up to 3 samples


@dataclass
class StageSnapshot:
    """
    Snapshot of pipeline state at a single stage.

    Captures what the stage received, what it produced, and what changed.
    """
    stage_name: str
    stage_number: Optional[int] = None

    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0

    # Validation
    input_valid: bool = True
    output_valid: bool = True
    skipped: bool = False
    error: Optional[str] = None

    # Counts
    nodes_before: int = 0
    nodes_after: int = 0
    edges_before: int = 0
    edges_after: int = 0

    # What changed
    nodes_added: int = 0
    nodes_removed: int = 0
    edges_added: int = 0
    edges_removed: int = 0

    # Field-level changes (what this stage enriches)
    fields_added: List[FieldDelta] = field(default_factory=list)
    metadata_keys_added: List[str] = field(default_factory=list)

    # Sample data (for UI preview)
    sample_node_before: Optional[Dict] = None
    sample_node_after: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        d = asdict(self)
        # Convert FieldDelta objects
        d['fields_added'] = [asdict(f) for f in self.fields_added]
        return d


@dataclass
class PipelineSnapshot:
    """
    Complete snapshot of a pipeline run.

    Contains snapshots for each stage, enabling full pipeline visualization.
    """
    target_path: str
    started_at: str
    completed_at: Optional[str] = None
    total_duration_ms: float = 0.0

    # Stage snapshots in execution order
    stages: List[StageSnapshot] = field(default_factory=list)

    # Final state summary
    final_nodes: int = 0
    final_edges: int = 0
    final_metadata_keys: List[str] = field(default_factory=list)

    # Pipeline health
    stages_succeeded: int = 0
    stages_failed: int = 0
    stages_skipped: int = 0

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return {
            'target_path': self.target_path,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'total_duration_ms': self.total_duration_ms,
            'stages': [s.to_dict() for s in self.stages],
            'final_nodes': self.final_nodes,
            'final_edges': self.final_edges,
            'final_metadata_keys': self.final_metadata_keys,
            'stages_succeeded': self.stages_succeeded,
            'stages_failed': self.stages_failed,
            'stages_skipped': self.stages_skipped,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


def capture_node_fields(nodes: Dict[str, Dict]) -> Set[str]:
    """Get all field names present across nodes."""
    fields = set()
    for node in nodes.values():
        fields.update(node.keys())
    return fields


def compute_field_deltas(
    nodes_before: Dict[str, Dict],
    nodes_after: Dict[str, Dict],
    max_samples: int = 3
) -> List[FieldDelta]:
    """
    Compute what fields were added/changed between two states.

    Returns list of FieldDelta showing what the stage enriched.
    """
    fields_before = capture_node_fields(nodes_before)
    fields_after = capture_node_fields(nodes_after)

    # New fields that didn't exist before
    new_fields = fields_after - fields_before

    deltas = []
    for field_name in new_fields:
        delta = FieldDelta(field_name=field_name)
        samples = []

        for node_id, node in nodes_after.items():
            if field_name in node:
                delta.added_count += 1
                if len(samples) < max_samples:
                    val = node[field_name]
                    # Truncate long values
                    if isinstance(val, str) and len(val) > 100:
                        val = val[:100] + "..."
                    elif isinstance(val, dict) and len(str(val)) > 100:
                        val = f"{{...{len(val)} keys}}"
                    elif isinstance(val, list) and len(val) > 5:
                        val = f"[...{len(val)} items]"
                    samples.append(val)

        delta.sample_values = samples
        deltas.append(delta)

    # Check for fields that existed but changed values
    common_fields = fields_before & fields_after
    for field_name in common_fields:
        changed = 0
        for node_id in nodes_before:
            if node_id in nodes_after:
                old_val = nodes_before[node_id].get(field_name)
                new_val = nodes_after[node_id].get(field_name)
                if old_val != new_val:
                    changed += 1

        if changed > 0:
            # Find existing delta or create new
            existing = next((d for d in deltas if d.field_name == field_name), None)
            if existing:
                existing.changed_count = changed
            else:
                deltas.append(FieldDelta(
                    field_name=field_name,
                    changed_count=changed
                ))

    return [d for d in deltas if d.added_count > 0 or d.changed_count > 0]


def get_sample_node(nodes: Dict[str, Dict], prefer_enriched: bool = True) -> Optional[Dict]:
    """
    Get a representative sample node for preview.

    Prefers nodes with more fields (more enriched) if prefer_enriched=True.
    """
    if not nodes:
        return None

    if prefer_enriched:
        # Sort by number of fields, take the richest
        sorted_nodes = sorted(
            nodes.values(),
            key=lambda n: len(n),
            reverse=True
        )
        node = sorted_nodes[0]
    else:
        # Just take first
        node = next(iter(nodes.values()))

    # Return a cleaned copy (truncate large fields)
    cleaned = {}
    for k, v in node.items():
        if k == 'body_source' and isinstance(v, str) and len(v) > 200:
            cleaned[k] = v[:200] + f"... ({len(v)} chars)"
        elif isinstance(v, str) and len(v) > 500:
            cleaned[k] = v[:500] + "..."
        else:
            cleaned[k] = v

    return cleaned
