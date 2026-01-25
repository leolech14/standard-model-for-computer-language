"""
Registry of Registries (The "List of Lists")

A central meta-registry that aggregates all system registries:
- RoleRegistry (Roles)
- TypeRegistry (Types)
- PatternRegistry (Patterns)
- SchemaRegistry (Schemas)
- WorkflowRegistry (Workflows)
"""

from typing import Dict, Any, List, Optional

# Core Registries
from .role_registry import get_role_registry, RoleRegistry
from .pattern_registry import get_pattern_registry, PatternRegistry
from .schema_registry import get_schema_registry, SchemaRegistry
from .workflow_registry import get_workflow_registry, WorkflowRegistry

# TypeRegistry is in parent core/ directory
try:
    from ..type_registry import get_registry as get_type_registry, TypeRegistry
except ImportError:
    # Handle case where type_registry might not be importable yet
    get_type_registry = None
    TypeRegistry = None


class RegistryOfRegistries:
    """
    The Meta-Registry.
    
    Acts as the single entry point for all system inventories.
    """
    
    _instance: Optional['RegistryOfRegistries'] = None
    
    def __init__(self):
        self._registries: Dict[str, Any] = {}
        self._initialize_defaults()
        
    def _initialize_defaults(self):
        """Register the standard core registries."""
        # 1. Roles
        self.register("roles", get_role_registry())
        
        # 2. Patterns
        self.register("patterns", get_pattern_registry())
        
        # 3. Schemas
        self.register("schemas", get_schema_registry())
        
        # 4. Workflows
        self.register("workflows", get_workflow_registry())
        
        # 5. Types (if available)
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
        """Get a status summary of all registries."""
        report = {}
        for name, reg in self._registries.items():
            # Try specific counts if known
            if hasattr(reg, 'count'):
                count = reg.count() if callable(reg.count) else reg.count
                report[name] = f"Active ({count} items)"
            elif hasattr(reg, 'list_all'):
                report[name] = f"Active ({len(reg.list_all())} items)"
            elif isinstance(reg, TypeRegistry):
                report[name] = f"Active ({len(reg.all_types())} types)"
            elif isinstance(reg, RoleRegistry):
                report[name] = "Active (33 roles)"
            else:
                report[name] = "Active"
        return report


def get_meta_registry() -> RegistryOfRegistries:
    """Get the meta-registry singleton."""
    return RegistryOfRegistries.get_instance()
