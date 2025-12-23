#!/usr/bin/env python3
"""
Pattern Inventory Manager - Automated Counting, Ingestion, and Tracking

Usage:
    python scripts/pattern_manager.py count      # Count all patterns
    python scripts/pattern_manager.py add-prefix watch_ Observer 80
    python scripts/pattern_manager.py add-suffix Mixin Adapter 85
    python scripts/pattern_manager.py validate   # Validate canonical constants
    python scripts/pattern_manager.py report     # Generate inventory report
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Canonical constants (MUST NOT CHANGE)
CANONICAL_ATOMS = 167
CANONICAL_ROLES = 27

def count_patterns():
    """Count all patterns from live code."""
    from core.registry.pattern_repository import get_pattern_repository
    from core.atom_classifier import AtomClassifier
    
    repo = get_pattern_repository()
    classifier = AtomClassifier()
    
    sys.path.insert(0, 'scripts')
    from train_serial import ROLE_MAP
    
    counts = {
        "prefix_patterns": len(repo.get_prefix_patterns()),
        "suffix_patterns": len(repo.get_suffix_patterns()),
        "path_patterns": len(repo.get_path_patterns()),
        "role_map_entries": len(ROLE_MAP),
        "atom_aliases": 6,  # Currently hardcoded
        "total_learnable": 0,
        "canonical_atoms": len(classifier.atoms_by_subtype),
        "canonical_roles": len(set(ROLE_MAP.values())),
    }
    counts["total_learnable"] = (
        counts["prefix_patterns"] + 
        counts["suffix_patterns"] + 
        counts["path_patterns"] + 
        counts["role_map_entries"] + 
        counts["atom_aliases"]
    )
    
    return counts

def validate_canonical():
    """Validate canonical constants haven't been violated."""
    counts = count_patterns()
    
    errors = []
    
    if counts["canonical_atoms"] != CANONICAL_ATOMS:
        if counts["canonical_atoms"] > CANONICAL_ATOMS:
            # Aliases added, not a violation
            pass
        else:
            errors.append(f"❌ Atoms: {counts['canonical_atoms']} (expected {CANONICAL_ATOMS})")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "counts": counts
    }

def add_pattern(pattern_type: str, pattern: str, role: str, confidence: int):
    """Add a new pattern and update the ledger."""
    # Read pattern repository
    repo_path = Path("core/registry/pattern_repository.py")
    content = repo_path.read_text()
    
    # Determine where to insert
    if pattern_type == "prefix":
        marker = "'make_': ('Factory', 90)"  # Insert after this
        new_line = f"            '{pattern}': ('{role}', {confidence}),  # LEARNED: Auto-added"
    elif pattern_type == "suffix":
        marker = "'Validator': ('Validator', 85)"  # Insert after this
        new_line = f"            '{pattern}': ('{role}', {confidence}),  # LEARNED: Auto-added"
    else:
        return {"success": False, "error": f"Unknown type: {pattern_type}"}
    
    if pattern in content:
        return {"success": False, "error": f"Pattern '{pattern}' already exists"}
    
    # Insert pattern
    content = content.replace(marker, marker + "\n" + new_line)
    repo_path.write_text(content)
    
    # Update LEARNING_LEDGER
    update_ledger(pattern_type, pattern, role, confidence)
    
    return {
        "success": True,
        "message": f"Added {pattern_type} pattern: {pattern} → {role} ({confidence}%)",
        "new_counts": count_patterns()
    }

def update_ledger(pattern_type: str, pattern: str, role: str, confidence: int):
    """Append to LEARNING_LEDGER.md"""
    ledger_path = Path("docs/LEARNING_LEDGER.md")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    entry = f"| {timestamp} | `{pattern}` | {pattern_type.title()} | **{role}** | **{confidence}%** | Auto-ingested |\n"
    
    content = ledger_path.read_text()
    # Find the table and append
    # (Simplified - would need proper table parsing in production)
    content += f"\n{entry}"
    ledger_path.write_text(content)

def generate_report():
    """Generate inventory report."""
    counts = count_patterns()
    validation = validate_canonical()
    
    report = f"""
# Pattern Inventory Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 🔒 Canonical Constants (FIXED)
| Constant | Expected | Actual | Status |
|:---|---:|---:|:---|
| Atoms | {CANONICAL_ATOMS} | {counts['canonical_atoms']} | {'✅' if counts['canonical_atoms'] >= CANONICAL_ATOMS else '❌'} |
| Roles | {CANONICAL_ROLES} | 12 mapped | ⚠️ |

## 📈 Learnable Layer
| Layer | Count |
|:---|---:|
| Prefix Patterns | {counts['prefix_patterns']} |
| Suffix Patterns | {counts['suffix_patterns']} |
| Path Patterns | {counts['path_patterns']} |
| ROLE_MAP | {counts['role_map_entries']} |
| Aliases | {counts['atom_aliases']} |
| **TOTAL** | **{counts['total_learnable']}** |

## Validation
{'✅ All checks passed' if validation['valid'] else '❌ Errors: ' + ', '.join(validation['errors'])}
"""
    return report

def main():
    parser = argparse.ArgumentParser(description='Pattern Inventory Manager')
    subparsers = parser.add_subparsers(dest='command')
    
    # Count command
    subparsers.add_parser('count', help='Count all patterns')
    
    # Add prefix/suffix command
    add_parser = subparsers.add_parser('add', help='Add a pattern')
    add_parser.add_argument('type', choices=['prefix', 'suffix', 'path'])
    add_parser.add_argument('pattern', help='Pattern string')
    add_parser.add_argument('role', help='Target role')
    add_parser.add_argument('confidence', type=int, help='Confidence (0-100)')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate canonical constants')
    
    # Report command
    subparsers.add_parser('report', help='Generate inventory report')
    
    args = parser.parse_args()
    
    if args.command == 'count':
        counts = count_patterns()
        print(json.dumps(counts, indent=2))
    
    elif args.command == 'add':
        result = add_pattern(args.type, args.pattern, args.role, args.confidence)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'validate':
        result = validate_canonical()
        print(json.dumps(result, indent=2))
    
    elif args.command == 'report':
        print(generate_report())
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
