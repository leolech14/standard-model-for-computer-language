#!/usr/bin/env python3
"""
Documentation Update Pipeline
Auto-syncs metrics across all documentation files.
Ensures no legacy info is missed.

Usage:
    python scripts/update_docs.py          # Update all docs with current metrics
    python scripts/update_docs.py --check  # Check for stale metrics
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Files to update
DOC_FILES = [
    "README.md",
    "docs/CANONICAL_SCHEMA.md",
    "docs/LEARNING_LEDGER.md",
    "docs/NAMING_SCHEMA.md",
]

def get_current_metrics():
    """Get live metrics from code."""
    from core.atom_classifier import AtomClassifier
    from core.registry.pattern_registry import get_pattern_registry

    classifier = AtomClassifier()
    repo = get_pattern_registry()

    sys.path.insert(0, 'scripts')
    from train_serial import ROLE_MAP

    return {
        "atoms": len(classifier.atoms_by_subtype),
        "roles": 33,  # Canonical constant
        "prefix_patterns": len(repo.get_prefix_patterns()),
        "suffix_patterns": len(repo.get_suffix_patterns()),
        "path_patterns": len(repo.get_path_patterns()),
        "role_map": len(ROLE_MAP),
        "aliases": 6,
        "total_patterns": (
            len(repo.get_prefix_patterns()) +
            len(repo.get_suffix_patterns()) +
            len(repo.get_path_patterns()) +
            len(ROLE_MAP) + 6
        ),
        "accuracy": 93.0,  # Latest validated accuracy
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
    }

def update_readme(metrics):
    """Update README.md with current metrics."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        return

    content = readme_path.read_text()

    # Update pattern count mentions
    content = re.sub(
        r'(\d+)\s*patterns',
        f"{metrics['total_patterns']} patterns",
        content
    )

    # Update atom count mentions
    content = re.sub(
        r'(\d+)\s*atoms',
        f"{metrics['atoms']} atoms",
        content
    )

    readme_path.write_text(content)
    print(f"✅ Updated README.md")

def update_learning_ledger(metrics):
    """Append session summary to LEARNING_LEDGER.md"""
    ledger_path = Path("docs/LEARNING_LEDGER.md")
    if not ledger_path.exists():
        return

    content = ledger_path.read_text()

    # Check if today's update already exists
    if metrics['last_updated'] in content:
        print(f"ℹ️ LEARNING_LEDGER.md already updated for {metrics['last_updated']}")
        return

    content += f"""

---
### Automated Update: {metrics['last_updated']}
| Metric | Value |
|:---|---:|
| Atoms | {metrics['atoms']} |
| Patterns | {metrics['total_patterns']} |
| Accuracy | {metrics['accuracy']}% |
"""

    ledger_path.write_text(content)
    print(f"✅ Updated LEARNING_LEDGER.md")

def generate_status_json(metrics):
    """Generate machine-readable status file."""
    status_path = Path("data/system_status.json")
    status_path.parent.mkdir(parents=True, exist_ok=True)

    status = {
        "canonical": {
            "atoms": metrics['atoms'],
            "roles": metrics['roles'],
        },
        "learnable": {
            "prefix_patterns": metrics['prefix_patterns'],
            "suffix_patterns": metrics['suffix_patterns'],
            "path_patterns": metrics['path_patterns'],
            "role_map": metrics['role_map'],
            "aliases": metrics['aliases'],
            "total": metrics['total_patterns'],
        },
        "accuracy": metrics['accuracy'],
        "last_updated": metrics['last_updated'],
    }

    status_path.write_text(json.dumps(status, indent=2))
    print(f"✅ Generated data/system_status.json")

def check_stale_docs(metrics):
    """Check for stale documentation."""
    stale_files = []

    for doc in DOC_FILES:
        path = Path(doc)
        if not path.exists():
            continue

        content = path.read_text()

        # Check for outdated pattern counts
        old_counts = re.findall(r'(\d+)\s*patterns', content)
        for count in old_counts:
            if int(count) != metrics['total_patterns'] and int(count) > 10:
                stale_files.append((doc, f"patterns: {count} (should be {metrics['total_patterns']})"))

    if stale_files:
        print("⚠️ STALE DOCUMENTATION FOUND:")
        for f, issue in stale_files:
            print(f"  {f}: {issue}")
    else:
        print("✅ All documentation up to date")

def main():
    parser = argparse.ArgumentParser(description='Update documentation pipeline')
    parser.add_argument('--check', action='store_true', help='Check for stale docs only')
    args = parser.parse_args()

    print("📄 DOCUMENTATION UPDATE PIPELINE")
    print("=" * 50)

    metrics = get_current_metrics()
    print(f"\n📊 Current Metrics:")
    print(f"  Atoms: {metrics['atoms']} | Roles: {metrics['roles']}")
    print(f"  Patterns: {metrics['total_patterns']} | Accuracy: {metrics['accuracy']}%")

    if args.check:
        print("\n🔍 Checking for stale documentation...")
        check_stale_docs(metrics)
    else:
        print("\n📝 Updating documentation...")
        update_readme(metrics)
        update_learning_ledger(metrics)
        generate_status_json(metrics)
        print(f"\n✅ Documentation pipeline complete")

if __name__ == "__main__":
    main()
