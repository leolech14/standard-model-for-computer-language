"""
Role Registry - Single source of truth for the 33 Canonical Roles.

The Standard Model defines exactly 33 canonical roles (WHY dimension).
This registry provides validation, normalization, and legacy remapping.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Set, List, Optional


@dataclass
class Role:
    """A canonical role from the 33 WHY-dimension roles."""
    name: str
    category: str = ""
    description: str = ""
    examples: List[str] = field(default_factory=list)

# Path to the immutable truth
ROLES_JSON_PATH = Path(__file__).parent.parent.parent.parent / "schema" / "fixed" / "roles.json"


class RoleRegistry:
    """
    Registry for the 33 Canonical Roles.

    Provides:
    - validate(role) / is_canonical(role) - check if role is canonical
    - normalize(role) / get_canonical(role) - map any role to canonical
    - list_names() - get all canonical role names
    - count() - get total canonical roles (should be 33)
    """

    # 33 Canonical Roles (hardcoded backup, overwritten by roles.json)
    _CANONICAL_ROLES: Set[str] = {
        "Query", "Finder", "Loader", "Getter",
        "Command", "Creator", "Mutator", "Destroyer",
        "Factory", "Builder",
        "Repository", "Store", "Cache",
        "Service", "Controller", "Manager", "Orchestrator",
        "Validator", "Guard", "Asserter",
        "Transformer", "Mapper", "Serializer", "Parser",
        "Handler", "Listener", "Subscriber", "Emitter",
        "Utility", "Formatter", "Helper",
        "Internal", "Lifecycle"
    }

    # Non-canonical -> Canonical mapping (The Rosetta Stone)
    _LEGACY_MAPPING: Dict[str, str] = {
        # Test/QA patterns
        "Test": "Asserter",
        "Fixture": "Asserter",
        "TestDouble": "Helper",

        # Validation patterns
        "Specification": "Validator",
        "Specifier": "Validator",
        "Spec": "Validator",
        "Rule": "Validator",
        "Policy": "Guard",

        # Configuration/State patterns
        "Configuration": "Store",
        "Config": "Store",
        "Settings": "Store",
        "Option": "Store",

        # Error handling
        "Exception": "Internal",
        "Error": "Internal",

        # Adapter/Integration patterns
        "Adapter": "Transformer",
        "Converter": "Transformer",
        "Client": "Service",
        "Gateway": "Service",
        "Middleware": "Service",

        # Factory patterns
        "Provider": "Factory",

        # Command patterns
        "Job": "Handler",
        "Task": "Command",
        "Worker": "Handler",
        "CommandHandler": "Handler",
        "EventHandler": "Handler",

        # DDD patterns (structural atoms, minimal role)
        "DTO": "Internal",
        "Entity": "Internal",
        "ValueObject": "Internal",
        "AggregateRoot": "Internal",
        "DomainEvent": "Emitter",
        "DomainService": "Service",
        "ApplicationService": "Service",

        # Suffix-based patterns (non-canonical)
        "Schema": "Internal",
        "Request": "Internal",
        "Response": "Internal",
        "Model": "Internal",
        "Aggregate": "Internal",
        "Vo": "Internal",

        # Listener patterns
        "Observer": "Listener",

        # Implementation details
        "Impl": "Internal",
        "RepositoryImpl": "Repository",

        # Module/Utility patterns
        "Module": "Utility",
        "Iterator": "Utility",

        # Graph inference patterns
        "SubjectUnderTest": "Internal",
        "IntegrationService": "Service",
        "UseCase": "Service",
        "EventProcessor": "Handler",
        "InternalHelper": "Utility",

        # Heuristic classifier patterns
        "APIHandler": "Handler",
        "ImpureFunction": "Utility",
        "Processor": "Service",

        # Entry points
        "EntryPoint": "Controller",
        "Constructor": "Lifecycle",

        # Fallback
        "Unknown": "Internal",
    }

    def __init__(self):
        self._roles_data: Dict[str, dict] = {}
        self._load_roles()

    def _load_roles(self):
        """Load roles from roles.json if available."""
        if ROLES_JSON_PATH.exists():
            try:
                with open(ROLES_JSON_PATH, "r") as f:
                    data = json.load(f)
                    self._roles_data = data.get("roles", {})
                    self._CANONICAL_ROLES = set(self._roles_data.keys())
            except Exception as e:
                print(f"Warning: Failed to load roles.json: {e}")

    # === Validation Methods ===

    def is_canonical(self, role: str) -> bool:
        """Check if a role is canonical (exact match)."""
        return role in self._CANONICAL_ROLES

    def validate(self, role: str) -> bool:
        """Alias for is_canonical."""
        return self.is_canonical(role)

    # === Normalization Methods ===

    def get_canonical(self, role: str) -> str:
        """
        Get the canonical role for a given string.
        Returns 'Internal' if no mapping exists (safe fallback).
        """
        if not role:
            return "Internal"

        # Already canonical
        if role in self._CANONICAL_ROLES:
            return role

        # Try legacy mapping (exact match)
        if role in self._LEGACY_MAPPING:
            return self._LEGACY_MAPPING[role]

        # Try case-insensitive match on canonical
        role_lower = role.lower()
        for canonical in self._CANONICAL_ROLES:
            if canonical.lower() == role_lower:
                return canonical

        # Try case-insensitive match on legacy
        for legacy, canonical in self._LEGACY_MAPPING.items():
            if legacy.lower() == role_lower:
                return canonical

        # Fallback to Internal (always canonical, always safe)
        return "Internal"

    def normalize(self, role: str) -> str:
        """Alias for get_canonical - normalize any role to canonical."""
        return self.get_canonical(role)

    def remap_legacy(self, role: str) -> str:
        """Alias for get_canonical."""
        return self.get_canonical(role)

    # === Query Methods ===

    def list_names(self) -> List[str]:
        """Get all canonical role names."""
        return sorted(self._CANONICAL_ROLES)

    def count(self) -> int:
        """Get total number of canonical roles (should be 33)."""
        return len(self._CANONICAL_ROLES)

    def get_role_data(self, role: str) -> Optional[dict]:
        """Get full role data from roles.json."""
        return self._roles_data.get(role)


# Singleton instance
_registry: Optional[RoleRegistry] = None


def get_role_registry() -> RoleRegistry:
    """Get the singleton role registry."""
    global _registry
    if _registry is None:
        _registry = RoleRegistry()
    return _registry


# Export the legacy mapping for tests
ROLE_NORMALIZATION = RoleRegistry._LEGACY_MAPPING


if __name__ == "__main__":
    registry = get_role_registry()
    print(f"Canonical roles: {registry.count()}")
    print(f"Legacy mappings: {len(ROLE_NORMALIZATION)}")

    # Test normalization
    test_cases = ["Service", "DTO", "Test", "Unknown", "FooBar", "service", "dto"]
    for role in test_cases:
        canonical = registry.normalize(role)
        valid = registry.validate(canonical)
        print(f"  {role:20} -> {canonical:15} (canonical: {valid})")
