"""
Unit tests for RoleRegistry - Single source of truth for the 33 Canonical Roles.

Tests verify:
- All 33 canonical roles are loaded
- Validation correctly identifies canonical vs non-canonical
- Normalization maps non-canonical to canonical
- Case-insensitive matching works
- Singleton pattern is enforced
- No canonical roles appear in normalization keys
- All normalization targets are canonical
"""

import pytest
from src.core.registry import get_role_registry, RoleRegistry, ROLE_NORMALIZATION


class TestRoleRegistry:
    """Tests for RoleRegistry functionality."""

    def test_loads_33_canonical_roles(self):
        """Registry must load exactly 33 canonical roles."""
        registry = get_role_registry()
        assert registry.count() == 33, f"Expected 33 canonical roles, got {registry.count()}"

    def test_validate_canonical_roles(self):
        """All canonical roles must validate as True."""
        registry = get_role_registry()
        canonical = [
            'Service', 'Controller', 'Repository', 'Factory', 'Handler',
            'Helper', 'Formatter', 'Query', 'Finder', 'Loader', 'Getter',
            'Command', 'Creator', 'Mutator', 'Destroyer', 'Builder',
            'Store', 'Cache', 'Manager', 'Orchestrator', 'Validator',
            'Guard', 'Asserter', 'Transformer', 'Mapper', 'Serializer',
            'Parser', 'Listener', 'Subscriber', 'Emitter', 'Utility',
            'Internal', 'Lifecycle'
        ]
        for role in canonical:
            assert registry.validate(role) is True, f"'{role}' should be canonical"

    def test_validate_non_canonical_returns_false(self):
        """Non-canonical roles must validate as False."""
        registry = get_role_registry()
        non_canonical = [
            'DTO', 'Test', 'Module', 'Unknown', 'Entity',
            'Configuration', 'EventHandler', 'Specification'
        ]
        for role in non_canonical:
            assert registry.validate(role) is False, f"'{role}' should NOT be canonical"

    def test_normalize_canonical_unchanged(self):
        """All 33 canonical roles must remain unchanged after normalization."""
        registry = get_role_registry()
        for role in registry.list_names():
            assert registry.normalize(role) == role, f"Canonical '{role}' was changed"

    def test_normalize_non_canonical_maps_correctly(self):
        """Non-canonical roles must map to their correct canonical equivalents."""
        registry = get_role_registry()
        mappings = {
            'DTO': 'Internal',
            'Test': 'Asserter',
            'Module': 'Utility',
            'EventHandler': 'Handler',
            'Configuration': 'Store',
            'Specification': 'Validator',
            'EntryPoint': 'Controller',
            'Constructor': 'Lifecycle',
            'DomainService': 'Service',
            'CommandHandler': 'Handler',
        }
        for non_canonical, expected_canonical in mappings.items():
            result = registry.normalize(non_canonical)
            assert result == expected_canonical, \
                f"'{non_canonical}' should map to '{expected_canonical}', got '{result}'"

    def test_normalize_unknown_fallback_to_internal(self):
        """Unknown roles must fallback to 'Internal'."""
        registry = get_role_registry()
        unknown_roles = [
            'CompletelyUnknownRole',
            'SomethingRandom',
            'NotARealRole',
            'FooBarBaz',
        ]
        for role in unknown_roles:
            assert registry.normalize(role) == 'Internal', \
                f"Unknown role '{role}' should fallback to 'Internal'"

    def test_normalize_empty_and_none(self):
        """Empty string and None-like inputs should fallback to 'Internal'."""
        registry = get_role_registry()
        assert registry.normalize('') == 'Internal'
        assert registry.normalize(None) == 'Internal'

    def test_normalize_case_insensitive_canonical(self):
        """Canonical role names should be matched case-insensitively."""
        registry = get_role_registry()
        # Canonical - case insensitive
        assert registry.normalize('service') == 'Service'
        assert registry.normalize('SERVICE') == 'Service'
        assert registry.normalize('Service') == 'Service'
        assert registry.normalize('controller') == 'Controller'
        assert registry.normalize('CONTROLLER') == 'Controller'

    def test_normalize_case_insensitive_non_canonical(self):
        """Non-canonical role names should be matched case-insensitively."""
        registry = get_role_registry()
        # Non-canonical - case insensitive
        assert registry.normalize('dto') == 'Internal'
        assert registry.normalize('DTO') == 'Internal'
        assert registry.normalize('Dto') == 'Internal'
        assert registry.normalize('test') == 'Asserter'
        assert registry.normalize('TEST') == 'Asserter'

    def test_singleton_pattern(self):
        """get_role_registry() must return the same instance."""
        r1 = get_role_registry()
        r2 = get_role_registry()
        assert r1 is r2, "get_role_registry() should return singleton"

    def test_all_normalization_targets_are_canonical(self):
        """Every mapping target must be a valid canonical role."""
        registry = get_role_registry()
        for source, target in ROLE_NORMALIZATION.items():
            assert registry.validate(target), \
                f"Normalization '{source}' -> '{target}' targets non-canonical role"

    def test_no_canonical_role_in_normalization_keys(self):
        """Canonical roles must NOT appear as normalization sources."""
        registry = get_role_registry()
        for source in ROLE_NORMALIZATION.keys():
            assert not registry.validate(source), \
                f"Canonical role '{source}' should not be in normalization keys"

    def test_list_names_returns_sorted(self):
        """list_names() should return sorted canonical role names."""
        registry = get_role_registry()
        names = registry.list_names()
        assert names == sorted(names), "list_names() should return sorted list"
        assert len(names) == 33

    def test_is_canonical_alias(self):
        """is_canonical() should be an alias for validate()."""
        registry = get_role_registry()
        assert registry.is_canonical('Service') == registry.validate('Service')
        assert registry.is_canonical('DTO') == registry.validate('DTO')

    def test_get_canonical_alias(self):
        """get_canonical() should be an alias for normalize()."""
        registry = get_role_registry()
        assert registry.get_canonical('DTO') == registry.normalize('DTO')
        assert registry.get_canonical('Service') == registry.normalize('Service')


class TestRoleNormalizationMapping:
    """Tests for the ROLE_NORMALIZATION mapping itself."""

    def test_mapping_has_expected_entries(self):
        """ROLE_NORMALIZATION should have at least 40 mappings."""
        assert len(ROLE_NORMALIZATION) >= 40, \
            f"Expected at least 40 mappings, got {len(ROLE_NORMALIZATION)}"

    def test_no_self_mappings(self):
        """No role should map to itself."""
        for source, target in ROLE_NORMALIZATION.items():
            assert source != target, f"Self-mapping found: '{source}' -> '{target}'"

    def test_critical_mappings_exist(self):
        """Critical non-canonical patterns must have mappings."""
        critical = ['DTO', 'Test', 'Module', 'Unknown', 'Entity', 'Configuration']
        for role in critical:
            assert role in ROLE_NORMALIZATION, \
                f"Critical mapping missing for '{role}'"
