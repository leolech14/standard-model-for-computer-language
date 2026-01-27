"""
Registry of Registries - Collider Runtime Access (THE HUB)

AUTHORITATIVE SOURCE OF TRUTH: .agent/intelligence/LOL.yaml
============================================================
This Python module provides RUNTIME access to Collider registries only.
For the COMPLETE List of Lists (LOL) covering ALL project inventories:
- Collider registries (6)
- Agent registries (6)
- Context registries (3)
- Subsystems (13)
- Files, tools, hooks, etc.

See: .agent/intelligence/LOL.yaml

Collider registries exposed here (runtime objects):
- AtomRegistry: 3,525 atoms (80 core + 3,445 T2)
- RoleRegistry: 33 canonical roles
- TypeRegistry: 36 node types
- PatternRegistry: 36 role detection patterns
- SchemaRegistry: 13 optimization schemas
- WorkflowRegistry: 4 analysis workflows

Hub Services (cross-module coordination):
- EventBus: Pub/sub for decoupled module communication

Usage:
    from src.core.registry.registry_of_registries import get_meta_registry

    hub = get_meta_registry()

    # Access registries
    roles = hub.get('roles')

    # Use event bus
    hub.event_bus.on('analysis:complete', lambda data: print(data))
    hub.event_bus.emit('analysis:complete', {'nodes': 100})
"""

from typing import Dict, Any, List, Optional

# Core Registries
from .role_registry import get_role_registry, RoleRegistry
from .pattern_registry import get_pattern_registry, PatternRegistry
from .schema_registry import get_schema_registry, SchemaRegistry
from .workflow_registry import get_workflow_registry, WorkflowRegistry

# EventBus (cross-module communication)
from ..event_bus import get_event_bus, EventBus

# TypeRegistry is in parent core/ directory
try:
    from ..type_registry import get_registry as get_type_registry, TypeRegistry
except ImportError:
    get_type_registry = None
    TypeRegistry = None

# AtomRegistry is in parent core/ directory
try:
    from ..atom_registry import AtomRegistry
    def get_atom_registry():
        return AtomRegistry()
except ImportError:
    get_atom_registry = None
    AtomRegistry = None


class RegistryOfRegistries:
    """
    The Meta-Registry.

    Acts as the single entry point for all system inventories.
    """

    _instance: Optional['RegistryOfRegistries'] = None

    def __init__(self):
        self._registries: Dict[str, Any] = {}
        self.event_bus: EventBus = get_event_bus()  # Global event bus for cross-module communication
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Register the standard core registries."""
        # 1. Atoms (the fundamental building blocks)
        if get_atom_registry:
            self.register("atoms", get_atom_registry())

        # 2. Roles
        self.register("roles", get_role_registry())

        # 3. Patterns
        self.register("patterns", get_pattern_registry())

        # 4. Schemas
        self.register("schemas", get_schema_registry())

        # 5. Workflows
        self.register("workflows", get_workflow_registry())

        # 6. Types (if available)
        if get_type_registry:
            self.register("types", get_type_registry())

    @classmethod
    def get_instance(cls) -> 'RegistryOfRegistries':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: str, registry: Any) -> None:
        """Register a new registry."""
        self._registries[name] = registry

    def get(self, name: str) -> Optional[Any]:
        """Get a registry by name."""
        return self._registries.get(name.lower())

    def list_registries(self) -> List[str]:
        """List names of all registered registries."""
        return sorted(list(self._registries.keys()))

    def status_report(self) -> Dict[str, str]:
        """Get a status summary of all registries and services."""
        report = {}

        # EventBus status
        if self.event_bus:
            event_count = len(self.event_bus.get_events())
            report["event_bus"] = f"Active ({event_count} events registered)"

        # Registry statuses
        for name, reg in self._registries.items():
            # Handle specific registry types
            if name == "atoms" and hasattr(reg, 'atoms'):
                t0t1 = len(reg.atoms)
                t2 = len(reg.t2_atoms)
                report[name] = f"Active ({t0t1} canonical + {t2} T2 = {t0t1 + t2} total)"
            elif name == "types" and hasattr(reg, 'all_types'):
                report[name] = f"Active ({len(reg.all_types())} types)"
            elif name == "roles" and hasattr(reg, 'count'):
                report[name] = f"Active ({reg.count()} roles)"
            elif hasattr(reg, 'count'):
                count = reg.count() if callable(reg.count) else reg.count
                report[name] = f"Active ({count} items)"
            elif hasattr(reg, 'list_all'):
                report[name] = f"Active ({len(reg.list_all())} items)"
            else:
                report[name] = "Active"
        return report


def get_meta_registry() -> RegistryOfRegistries:
    """Get the meta-registry singleton."""
    return RegistryOfRegistries.get_instance()
