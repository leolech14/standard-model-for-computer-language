#!/usr/bin/env python3
"""
ATOM LOADER - Integrates all atom sources into unified taxonomy.

Loads from:
- src/patterns/atoms.json (14 base atoms + AST mappings)
- src/patterns/ATOMS_TIER0_CORE.yaml (42 T0 atoms)
- src/patterns/ATOMS_TIER1_STDLIB.yaml (21 T1 atoms)
- src/patterns/ATOMS_TIER2_ECOSYSTEM.yaml (17 T2 atoms)

Total: 80+ atoms unified into single taxonomy.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any


def load_yaml_atoms(yaml_path: Path) -> List[Dict]:
    """Load atoms from a YAML file."""
    if not yaml_path.exists():
        return []

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return data.get('atoms', [])


def load_json_atoms(json_path: Path) -> Dict:
    """Load atoms from atoms.json."""
    if not json_path.exists():
        return {}

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def infer_phase_family(atom_id: str) -> tuple:
    """Infer phase and family from atom ID pattern."""
    # For YAML atoms like C1_IntLiteral
    if atom_id.startswith('C1_'):
        return ('DATA', 'Literals') if 'Literal' in atom_id else ('LOGIC', 'Expressions')
    if atom_id.startswith('C2_'):
        return ('LOGIC', 'Statements')
    if atom_id.startswith('C3_'):
        return ('ORGANIZATION', 'Structures')

    # For JSON atoms like DAT.BYT.A
    if atom_id.startswith('DAT'):
        return ('DATA', 'Primitives')
    if atom_id.startswith('LOG'):
        return ('LOGIC', 'Functions')
    if atom_id.startswith('ORG'):
        return ('ORGANIZATION', 'Aggregates')
    if atom_id.startswith('EXE'):
        return ('EXECUTION', 'Handlers')
    if atom_id.startswith('SYS'):
        return ('EXECUTION', 'System')

    return ('LOGIC', 'Unknown')


def build_unified_taxonomy(patterns_dir: Path = None) -> Dict:
    """
    Build unified taxonomy from all atom sources.

    Returns structure compatible with atom_classifier.py:
    {
        "phases": {
            "DATA": {
                "families": {
                    "Literals": {
                        "atoms": [{"id": "...", "name": "..."}]
                    }
                }
            }
        },
        "atoms": {...},  # flat lookup
        "mappings": {...},  # AST mappings
        "tier_info": {...}  # tier metadata
    }
    """
    if patterns_dir is None:
        patterns_dir = Path(__file__).parent.parent / "patterns"

    # Initialize structure
    taxonomy = {
        "version": "2.0.0",
        "phases": {},
        "atoms": {},
        "mappings": {},
        "tier_info": {
            "T0": {"count": 0, "source": "ATOMS_TIER0_CORE.yaml"},
            "T1": {"count": 0, "source": "ATOMS_TIER1_STDLIB.yaml"},
            "T2": {"count": 0, "source": "ATOMS_TIER2_ECOSYSTEM.yaml"},
            "base": {"count": 0, "source": "atoms.json"}
        }
    }

    # Load base atoms.json
    base_json = load_json_atoms(patterns_dir / "atoms.json")
    if "atoms" in base_json:
        for atom_id, atom_data in base_json["atoms"].items():
            phase, family = infer_phase_family(atom_id)
            _add_atom(taxonomy, phase, family, {
                "id": atom_id,
                "name": atom_data.get("name", atom_id),
                "description": atom_data.get("description", ""),
                "tier": "base"
            })
            taxonomy["atoms"][atom_id] = atom_data
            taxonomy["tier_info"]["base"]["count"] += 1

    # Copy AST mappings
    if "mappings" in base_json:
        taxonomy["mappings"] = base_json["mappings"]

    # Load T0 atoms
    t0_atoms = load_yaml_atoms(patterns_dir / "ATOMS_TIER0_CORE.yaml")
    for atom in t0_atoms:
        atom_id = atom.get("id", "")
        phase, family = infer_phase_family(atom_id)
        _add_atom(taxonomy, phase, family, {
            "id": atom_id,
            "name": atom.get("name", atom_id),
            "symbol": atom.get("symbol", ""),
            "dimensions": atom.get("default_dimensions", []),
            "tier": "T0"
        })
        taxonomy["atoms"][atom_id] = atom
        taxonomy["tier_info"]["T0"]["count"] += 1

    # Load T1 atoms
    t1_atoms = load_yaml_atoms(patterns_dir / "ATOMS_TIER1_STDLIB.yaml")
    for atom in t1_atoms:
        atom_id = atom.get("id", "")
        phase, family = infer_phase_family(atom_id)
        _add_atom(taxonomy, phase, family, {
            "id": atom_id,
            "name": atom.get("name", atom_id),
            "symbol": atom.get("symbol", ""),
            "tier": "T1"
        })
        taxonomy["atoms"][atom_id] = atom
        taxonomy["tier_info"]["T1"]["count"] += 1

    # Load T2 atoms
    t2_atoms = load_yaml_atoms(patterns_dir / "ATOMS_TIER2_ECOSYSTEM.yaml")
    for atom in t2_atoms:
        atom_id = atom.get("id", "")
        phase, family = infer_phase_family(atom_id)
        _add_atom(taxonomy, phase, family, {
            "id": atom_id,
            "name": atom.get("name", atom_id),
            "symbol": atom.get("symbol", ""),
            "tier": "T2"
        })
        taxonomy["atoms"][atom_id] = atom
        taxonomy["tier_info"]["T2"]["count"] += 1

    return taxonomy


def _add_atom(taxonomy: Dict, phase: str, family: str, atom: Dict):
    """Add atom to taxonomy structure."""
    if phase not in taxonomy["phases"]:
        taxonomy["phases"][phase] = {"families": {}}

    if family not in taxonomy["phases"][phase]["families"]:
        taxonomy["phases"][phase]["families"][family] = {"atoms": []}

    taxonomy["phases"][phase]["families"][family]["atoms"].append(atom)


def get_unified_taxonomy() -> Dict:
    """Get or build unified taxonomy (cached)."""
    if not hasattr(get_unified_taxonomy, '_cache'):
        get_unified_taxonomy._cache = build_unified_taxonomy()
    return get_unified_taxonomy._cache


def print_summary():
    """Print summary of loaded atoms."""
    taxonomy = build_unified_taxonomy()

    print("=" * 60)
    print("UNIFIED ATOM TAXONOMY")
    print("=" * 60)

    total = 0
    for tier, info in taxonomy["tier_info"].items():
        count = info["count"]
        total += count
        print(f"  {tier}: {count} atoms from {info['source']}")

    print("-" * 60)
    print(f"  TOTAL: {total} atoms")
    print()

    print("BY PHASE:")
    for phase, phase_data in taxonomy["phases"].items():
        phase_count = sum(len(f["atoms"]) for f in phase_data["families"].values())
        print(f"  {phase}: {phase_count} atoms")
        for family, family_data in phase_data["families"].items():
            print(f"    - {family}: {len(family_data['atoms'])}")

    print()
    print("AST MAPPINGS:")
    for lang, mappings in taxonomy["mappings"].items():
        print(f"  {lang}: {len(mappings)} mappings")


if __name__ == "__main__":
    print_summary()
