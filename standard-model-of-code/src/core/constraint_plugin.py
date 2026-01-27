"""
Constraint Plugin - Hub-Connected Real-Time Validation
=======================================================
SMoC Role: Service | Domain: Validation

Event-driven constraint validation plugin.
Listens for graph updates and emits violation events in real-time.

Usage:
    from src.core.registry.registry_of_registries import get_meta_registry
    from src.core.constraint_plugin import ConstraintPlugin

    hub = get_meta_registry()
    plugin = ConstraintPlugin()
    plugin.initialize(hub)
    plugin.register()
    plugin.start()

    # Emit node additions during analysis
    hub.event_bus.emit('graph:node-added', {'node': {...}})

    # Listen for violations
    hub.event_bus.on('violation:detected', lambda v: handle_violation(v))

Part of: MODULE_CONVERSION_INVENTORY.md (Priority 1 - Demonstrator)
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from .plugin import EventDrivenPlugin
except ImportError:
    from plugin import EventDrivenPlugin

try:
    from .constraint_engine import ConstraintEngine
except ImportError:
    from constraint_engine import ConstraintEngine


class ConstraintPlugin(EventDrivenPlugin):
    """
    Real-time constraint validation service.

    Instead of batch validation at end of analysis, this plugin
    validates nodes as they're discovered, emitting violations immediately.

    Events:
        Listens:
        - 'graph:node-added' - Validate individual node
        - 'graph:edge-added' - Validate individual edge
        - 'pipeline:stage:complete' - Run batch validation

        Emits:
        - 'violation:detected' - When rule violated
        - 'constraint:validated' - When validation complete
        - 'constraint:ready' - Plugin initialized
    """

    def __init__(
        self,
        arch_profile=None,
        dim_profile=None,
        rules_path: Optional[Path] = None
    ):
        super().__init__(
            name='constraint-validator',
            version='1.0.0',
            dependencies=['schemas']  # Rules might come from schema registry
        )
        self._engine: Optional[ConstraintEngine] = None
        self._arch_profile = arch_profile
        self._dim_profile = dim_profile
        self._rules_path = rules_path
        self._violations: List[Dict[str, Any]] = []

    def initialize(self, hub) -> None:
        """Create constraint engine."""
        super().initialize(hub)

        # Create engine with injected profiles
        self._engine = ConstraintEngine(
            arch_profile=self._arch_profile,
            dim_profile=self._dim_profile,
            rules_path=self._rules_path
        )

    def register(self) -> None:
        """Subscribe to graph update events."""
        self.register_events({
            'graph:node-added': self._validate_node,
            'graph:edge-added': self._validate_edge,
            'pipeline:stage:complete': self._run_batch_validation
        })

    def start(self) -> None:
        """Signal ready."""
        self.hub.event_bus.emit('constraint:ready', {
            'name': self.name,
            'rule_count': len(self._engine.rules) if self._engine else 0
        })

    def stop(self) -> None:
        """Cleanup."""
        self.hub.event_bus.emit('constraint:stopped', {
            'name': self.name,
            'violations_detected': len(self._violations)
        })
        self._violations.clear()
        self._engine = None

    # Event Handlers (Real-time validation)

    def _validate_node(self, data: Dict[str, Any]) -> None:
        """
        Validate a single node as it's added.

        Args:
            data: {node: {...}} - Node data
        """
        if not self._engine:
            return

        node = data.get('node')
        if not node:
            return

        # Check node against constraint rules
        try:
            violations = self._engine.validate_node(node)

            for violation in violations:
                violation_dict = {
                    'node_id': violation.node_id,
                    'rule': violation.rule_id,
                    'reason': violation.reason,
                    'tier': violation.tier.value,
                    'confidence': violation.confidence
                }
                self._violations.append(violation_dict)
                self.hub.event_bus.emit('violation:detected', violation_dict)

        except Exception as e:
            self.hub.event_bus.emit('constraint:error', {
                'node_id': node.get('id'),
                'error': str(e)
            })

    def _validate_edge(self, data: Dict[str, Any]) -> None:
        """
        Validate a single edge as it's added.

        Args:
            data: {edge: {...}} - Edge data
        """
        if not self._engine:
            return

        edge = data.get('edge')
        if not edge:
            return

        # Edge-specific validation logic
        # (ConstraintEngine doesn't have edge-specific validation yet)
        # This is a placeholder for future edge constraint rules

    def _run_batch_validation(self, data: Dict[str, Any]) -> None:
        """
        Run full batch validation at stage completion.

        Args:
            data: {stage: str, ...} - Stage completion event
        """
        # Only run on specific stages (e.g., after graph is built)
        stage = data.get('stage')
        if stage not in ('edge_extraction', 'graph_analytics'):
            return

        # Emit validation complete
        self.hub.event_bus.emit('constraint:validated', {
            'stage': stage,
            'violations': len(self._violations)
        })

    # Public API (for batch validation via service)

    def validate_batch(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """
        Validate nodes and edges in batch.

        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries

        Returns:
            Validation report with violations
        """
        if not self._engine:
            raise RuntimeError("ConstraintEngine not initialized")

        return self._engine.validate_graph(nodes, edges)

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all violations detected so far."""
        return list(self._violations)

    def clear_violations(self) -> None:
        """Clear violation history."""
        self._violations.clear()


# Helper for backward compatibility
def get_constraint_engine_from_hub(hub) -> ConstraintEngine:
    """
    Get constraint engine from hub (backward compatibility).

    Args:
        hub: RegistryOfRegistries instance

    Returns:
        ConstraintEngine instance (unwrapped)
    """
    plugin = hub.get('service:constraint-validator')
    if plugin and hasattr(plugin, '_engine') and plugin._engine:
        return plugin._engine

    # Fallback: Create and register
    plugin = ConstraintPlugin()
    plugin.initialize(hub)
    plugin.register()
    plugin.start()

    assert plugin._engine is not None, "Failed to initialize constraint engine"
    return plugin._engine
