#!/usr/bin/env python3
"""
Canonical Type Registry

Single source of truth loader for the canonical type system.
All components should import canonical types from here.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalType:
    """A canonical architectural component type."""
    id: str
    layer: str
    description: str
    aliases: tuple[str, ...]
    rpbl: Dict[str, int]


class TypeRegistry:
    """
    Registry for canonical architectural types.
    
    Load once, use everywhere - ensures consistency across all detector components.
    """
    
    _instance: Optional['TypeRegistry'] = None
    
    def __init__(self, types_path: Optional[Path] = None):
        if types_path is None:
            types_path = Path(__file__).parent.parent / "patterns" / "canonical_types.json"
        
        with open(types_path, 'r', encoding='utf-8') as f:
            self._data = json.load(f)
        
        self._types: Dict[str, CanonicalType] = {}
        self._alias_map: Dict[str, str] = {}  # alias -> canonical id
        self._by_layer: Dict[str, List[str]] = {}
        self._layer_weights: Dict[str, float] = {}
        
        self._build_registry()
    
    def _build_registry(self) -> None:
        """Build lookup structures from JSON data."""
        layers = self._data.get("layers", {})
        
        for layer_name, layer_data in layers.items():
            self._by_layer[layer_name] = []
            
            for type_def in layer_data.get("types", []):
                type_id = type_def["id"]
                aliases = tuple(type_def.get("aliases", []))
                
                ct = CanonicalType(
                    id=type_id,
                    layer=layer_name,
                    description=type_def.get("description", ""),
                    aliases=aliases,
                    rpbl=type_def.get("rpbl", {}),
                )
                
                self._types[type_id] = ct
                self._by_layer[layer_name].append(type_id)
                
                # Register aliases
                for alias in aliases:
                    self._alias_map[alias] = type_id
        
        # Load scoring weights
        scoring = self._data.get("scoring", {})
        self._layer_weights = scoring.get("layer_weights", {})
    
    @classmethod
    def get_instance(cls) -> 'TypeRegistry':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def normalize(self, type_name: str) -> str:
        """
        Normalize a type name to its canonical form.
        
        Examples:
            "Event" -> "DomainEvent"
            "Schema" -> "DTO"
            "Service" -> "ApplicationService"
        """
        if type_name in self._types:
            return type_name
        if type_name in self._alias_map:
            return self._alias_map[type_name]
        return type_name  # Return as-is if unknown
    
    def is_valid(self, type_name: str) -> bool:
        """Check if a type name (or alias) is in the canonical set."""
        return type_name in self._types or type_name in self._alias_map
    
    def get_type(self, type_name: str) -> Optional[CanonicalType]:
        """Get the canonical type definition, resolving aliases."""
        normalized = self.normalize(type_name)
        return self._types.get(normalized)
    
    def get_layer(self, type_name: str) -> Optional[str]:
        """Get the layer a type belongs to."""
        ct = self.get_type(type_name)
        return ct.layer if ct else None
    
    def get_layer_weight(self, layer: str) -> float:
        """Get the scoring weight for a layer."""
        return self._layer_weights.get(layer, 1.0)
    
    def all_types(self) -> Set[str]:
        """Get all canonical type IDs."""
        return set(self._types.keys())
    
    def types_in_layer(self, layer: str) -> List[str]:
        """Get all type IDs in a specific layer."""
        return self._by_layer.get(layer, [])
    
    def all_layers(self) -> List[str]:
        """Get all layer names."""
        return list(self._by_layer.keys())
    
    def get_rpbl(self, type_name: str) -> Dict[str, int]:
        """Get RPBL scores for a type."""
        ct = self.get_type(type_name)
        return ct.rpbl if ct else {}


# Convenience functions for module-level access
def get_registry() -> TypeRegistry:
    """Get the type registry singleton."""
    return TypeRegistry.get_instance()


def normalize_type(type_name: str) -> str:
    """Normalize a type name to canonical form."""
    return get_registry().normalize(type_name)


def is_valid_type(type_name: str) -> bool:
    """Check if a type is in the canonical set."""
    return get_registry().is_valid(type_name)


def get_all_types() -> Set[str]:
    """Get all canonical type IDs."""
    return get_registry().all_types()


def get_layer(type_name: str) -> Optional[str]:
    """Get the layer a type belongs to."""
    return get_registry().get_layer(type_name)


if __name__ == "__main__":
    # Demo
    registry = TypeRegistry()
    
    print("=== Canonical Type Registry ===\n")
    
    for layer in registry.all_layers():
        types = registry.types_in_layer(layer)
        weight = registry.get_layer_weight(layer)
        print(f"📁 {layer.upper()} (weight: {weight})")
        for t in types:
            ct = registry.get_type(t)
            aliases = f" ({', '.join(ct.aliases)})" if ct.aliases else ""
            print(f"   • {t}{aliases}")
        print()
    
    print("=== Normalization Examples ===")
    test_names = ["Event", "Schema", "Service", "Helper", "Repository", "Unknown"]
    for name in test_names:
        normalized = registry.normalize(name)
        valid = "✓" if registry.is_valid(name) else "✗"
        print(f"  {name:15} → {normalized:20} {valid}")
