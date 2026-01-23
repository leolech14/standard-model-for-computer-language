#!/usr/bin/env python3
"""
Legacy Task Registry Importer - Consolidate all scattered tasks into unified registry.

Parses task registries in Markdown format and imports them into .agent/registry/
with normalized 4D confidence scoring.

Scoring Normalization:
- 3D (Confidence, Alignment, Usefulness) → 4D (Factual=Conf, Alignment=Align, Current=Useful, Onwards=avg)
- 2D (Factual, Alignment) → 4D (Factual, Alignment, Current=avg, Onwards=avg)
- 1D (Score) → 4D (all same value)

Usage:
    ./import_legacy_tasks.py scan                    # Preview what would be imported
    ./import_legacy_tasks.py import --source upb     # Import UPB tasks
    ./import_legacy_tasks.py import --all            # Import all registries
    ./import_legacy_tasks.py status                  # Show consolidation status

Part of Task Centralization Initiative.
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
except ImportError:
    import yaml as pyyaml
    yaml = None

REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_DIR = REPO_ROOT / ".agent" / "registry"
INBOX_DIR = REGISTRY_DIR / "inbox"
ACTIVE_DIR = REGISTRY_DIR / "active"

# Legacy registry locations and their scoring systems
LEGACY_REGISTRIES = {
    "upb": {
        "path": REPO_ROOT / "standard-model-of-code/docs/specs/UPB_TASK_REGISTRY.md",
        "scoring": "3D",  # Confidence, Alignment, Usefulness
        "category": "VISUALIZATION",
    },
    "pipeline": {
        "path": REPO_ROOT / "standard-model-of-code/docs/specs/PIPELINE_REFACTOR_TASK_REGISTRY.md",
        "scoring": "2D",  # Factual, Alignment
        "category": "PIPELINE",
    },
    "tree_sitter": {
        "path": REPO_ROOT / "standard-model-of-code/docs/specs/TREE_SITTER_TASK_REGISTRY.md",
        "scoring": "2D",  # Factual, Alignment
        "category": "TREE_SITTER",
    },
    "token_system": {
        "path": REPO_ROOT / "standard-model-of-code/docs/reports/TOKEN_SYSTEM_TASK_REGISTRY.md",
        "scoring": "1D",  # Single score
        "category": "TOKEN_SYSTEM",
    },
    "sidebar": {
        "path": REPO_ROOT / "standard-model-of-code/docs/reports/SIDEBAR_REFACTOR_TASK_REGISTRY.md",
        "scoring": "1D",
        "category": "VISUALIZATION",
    },
    "docs_improvement": {
        "path": REPO_ROOT / "standard-model-of-code/docs/reports/DOCS_IMPROVEMENT_TASK_REGISTRY.md",
        "scoring": "1D",
        "category": "DOCUMENTATION",
    },
    "modularization": {
        "path": REPO_ROOT / "standard-model-of-code/docs/reports/MODULARIZATION_TASKS.md",
        "scoring": "1D",
        "category": "REFACTORING",
    },
    "docs_reorg": {
        "path": REPO_ROOT / "context-management/docs/DOCS_REORG_TASK_REGISTRY.md",
        "scoring": "1D",
        "category": "DOCUMENTATION",
    },
    "mcp_factory": {
        "path": REPO_ROOT / "context-management/tools/mcp/mcp_factory/TASK_STEP_LOG.md",
        "scoring": "1D",
        "category": "MCP",
    },
    "smoc_roadmap": {
        "path": REPO_ROOT / "standard-model-of-code/ROADMAP.md",
        "scoring": "PHASES",  # Phase-based, not task-based
        "category": "ROADMAP",
    },
}


def normalize_to_4d(scores: dict, scoring_type: str) -> dict:
    """
    Normalize any scoring system to 4D (Factual, Alignment, Current, Onwards).

    Args:
        scores: Original scores dict
        scoring_type: "3D", "2D", "1D", or "PHASES"

    Returns:
        Dict with factual, alignment, current, onwards keys (0-100)
    """
    if scoring_type == "3D":
        # Confidence, Alignment, Usefulness → 4D
        conf = scores.get("confidence", 80)
        align = scores.get("alignment", 80)
        useful = scores.get("usefulness", 80)
        avg = (conf + align + useful) // 3
        return {
            "factual": conf,
            "alignment": align,
            "current": useful,
            "onwards": avg,
        }
    elif scoring_type == "2D":
        # Factual, Alignment → 4D
        factual = scores.get("factual", scores.get("confidence", 80))
        align = scores.get("alignment", 80)
        avg = (factual + align) // 2
        return {
            "factual": factual,
            "alignment": align,
            "current": avg,
            "onwards": avg,
        }
    elif scoring_type == "1D":
        # Single score → all dimensions
        score = scores.get("score", 80)
        return {
            "factual": score,
            "alignment": score,
            "current": score,
            "onwards": score,
        }
    else:
        # Default
        return {
            "factual": 70,
            "alignment": 70,
            "current": 70,
            "onwards": 70,
        }


def parse_upb_registry(content: str) -> list[dict]:
    """Parse UPB_TASK_REGISTRY.md format."""
    tasks = []

    # Pattern for task headers like "### Task 1.1: Create scales.js"
    task_pattern = re.compile(r'### Task (\d+\.\d+): (.+)')

    # Pattern for score tables
    score_pattern = re.compile(r'\|\s*\*\*(\w+)\*\*\s*\|\s*(\d+)%')

    # Find all task sections
    sections = re.split(r'(?=### Task \d+\.\d+:)', content)

    for section in sections:
        task_match = task_pattern.search(section)
        if not task_match:
            continue

        task_id = task_match.group(1)
        title = task_match.group(2).strip()

        # Extract scores
        scores = {}
        for score_match in score_pattern.finditer(section):
            dim = score_match.group(1).lower()
            value = int(score_match.group(2))
            scores[dim] = value

        # Determine status from section
        status = "PENDING"
        if "[x] GEMINI" in section or "[x] DONE" in section:
            status = "COMPLETE"
        elif "[~]" in section:
            status = "IN_PROGRESS"
        elif "OPTIONAL" in section:
            status = "DEFERRED"

        tasks.append({
            "source_id": f"UPB-{task_id}",
            "title": title,
            "scores": scores,
            "status": status,
            "description": section[:500],  # First 500 chars as description
        })

    return tasks


def parse_pipeline_registry(content: str) -> list[dict]:
    """Parse PIPELINE_REFACTOR_TASK_REGISTRY.md format."""
    tasks = []

    # Pattern for task headers like "### P1-01: Define BaseStage"
    task_pattern = re.compile(r'### (P\d+-\d+): (.+)')

    # Pattern for confidence line
    conf_pattern = re.compile(r'\*\*Confidence:\*\*\s*(\d+)%')

    sections = re.split(r'(?=### P\d+-\d+:)', content)

    for section in sections:
        task_match = task_pattern.search(section)
        if not task_match:
            continue

        task_id = task_match.group(1)
        title = task_match.group(2).strip()

        # Extract confidence
        conf_match = conf_pattern.search(section)
        confidence = int(conf_match.group(1)) if conf_match else 80

        # Look for alignment hints
        alignment = confidence  # Default same as confidence

        tasks.append({
            "source_id": f"PIPE-{task_id}",
            "title": title,
            "scores": {"factual": confidence, "alignment": alignment},
            "status": "PENDING",
            "description": section[:500],
        })

    return tasks


def parse_generic_registry(content: str, source_prefix: str) -> list[dict]:
    """Parse generic task registry with checkbox format."""
    tasks = []

    # Pattern for checkbox items: - [ ] Task description or - [x] Done task
    checkbox_pattern = re.compile(r'- \[([x~\s])\]\s*(.+)')

    task_num = 1
    for match in checkbox_pattern.finditer(content):
        status_char = match.group(1)
        description = match.group(2).strip()

        status = "PENDING"
        if status_char == 'x':
            status = "COMPLETE"
        elif status_char == '~':
            status = "IN_PROGRESS"

        tasks.append({
            "source_id": f"{source_prefix}-{task_num:03d}",
            "title": description[:80],
            "scores": {"score": 70},  # Default score
            "status": status,
            "description": description,
        })
        task_num += 1

    return tasks


def parse_registry(registry_key: str) -> list[dict]:
    """Parse a legacy registry and return normalized tasks."""
    config = LEGACY_REGISTRIES.get(registry_key)
    if not config:
        print(f"Unknown registry: {registry_key}")
        return []

    path = config["path"]
    if not path.exists():
        print(f"Registry not found: {path}")
        return []

    content = path.read_text()
    scoring = config["scoring"]
    category = config["category"]

    # Use appropriate parser
    if registry_key == "upb":
        tasks = parse_upb_registry(content)
    elif registry_key == "pipeline":
        tasks = parse_pipeline_registry(content)
    else:
        prefix = registry_key.upper()[:4]
        tasks = parse_generic_registry(content, prefix)

    # Normalize scores and add metadata
    for task in tasks:
        task["confidence"] = normalize_to_4d(task["scores"], scoring)
        task["category"] = category
        task["source_registry"] = registry_key
        task["source_file"] = str(path.relative_to(REPO_ROOT))

    return tasks


def get_next_opp_id() -> int:
    """Get next available OPP ID."""
    existing = list(INBOX_DIR.glob("OPP-*.yaml"))
    if not existing:
        return 8  # Start after existing OPP-001 through OPP-007

    max_id = 0
    for f in existing:
        try:
            num = int(f.stem.split("-")[1])
            max_id = max(max_id, num)
        except (ValueError, IndexError):
            continue
    return max_id + 1


def create_opportunity(task: dict, opp_id: int) -> dict:
    """Create an opportunity YAML from a parsed task."""
    confidence = task["confidence"]
    overall = min(confidence.values())

    return {
        "id": f"OPP-{opp_id:03d}",
        "title": task["title"],
        "source": "MIGRATION",
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "description": task.get("description", "Migrated from legacy registry"),
        "urgency": "HIGH" if overall >= 90 else "MEDIUM" if overall >= 75 else "LOW",
        "confidence": confidence,
        "related_to": [task["source_file"]],
        "metadata": {
            "source_id": task["source_id"],
            "source_registry": task["source_registry"],
            "category": task["category"],
            "original_status": task["status"],
        },
    }


def save_opportunity(opp: dict):
    """Save opportunity to YAML file."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    path = INBOX_DIR / f"{opp['id']}.yaml"

    with open(path, 'w') as f:
        if yaml:
            yaml.dump(opp, f)
        else:
            pyyaml.dump(opp, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return path


def cmd_scan(args):
    """Scan and preview what would be imported."""
    print("\n" + "=" * 70)
    print("LEGACY REGISTRY SCAN")
    print("=" * 70)

    total_tasks = 0

    for key, config in LEGACY_REGISTRIES.items():
        path = config["path"]
        exists = "✓" if path.exists() else "✗"

        if path.exists():
            tasks = parse_registry(key)
            count = len(tasks)
            total_tasks += count

            complete = sum(1 for t in tasks if t["status"] == "COMPLETE")
            pending = sum(1 for t in tasks if t["status"] == "PENDING")

            print(f"\n{exists} {key.upper()}")
            print(f"  Path: {path.relative_to(REPO_ROOT)}")
            print(f"  Scoring: {config['scoring']}")
            print(f"  Tasks: {count} (✓{complete} pending:{pending})")

            if args.verbose and tasks:
                print("  Sample tasks:")
                for task in tasks[:3]:
                    conf = task["confidence"]
                    overall = min(conf.values())
                    print(f"    - [{overall}%] {task['title'][:50]}")
        else:
            print(f"\n{exists} {key.upper()} - NOT FOUND")

    print("\n" + "-" * 70)
    print(f"TOTAL: {total_tasks} tasks across {len(LEGACY_REGISTRIES)} registries")
    print("=" * 70)


def cmd_import(args):
    """Import tasks from legacy registries."""
    if args.source and args.source != "all":
        registries = [args.source]
    else:
        registries = list(LEGACY_REGISTRIES.keys())

    if args.dry_run:
        print("[DRY RUN] Would import from:", registries)
        return

    next_id = get_next_opp_id()
    imported = 0

    for key in registries:
        if key not in LEGACY_REGISTRIES:
            print(f"Unknown registry: {key}")
            continue

        tasks = parse_registry(key)

        # Filter by status if requested
        if not args.include_complete:
            tasks = [t for t in tasks if t["status"] != "COMPLETE"]

        print(f"\nImporting {len(tasks)} tasks from {key}...")

        for task in tasks:
            opp = create_opportunity(task, next_id)
            path = save_opportunity(opp)
            print(f"  Created: {opp['id']} - {task['title'][:40]}")
            next_id += 1
            imported += 1

    print(f"\n✓ Imported {imported} tasks as opportunities")
    print(f"  Next: Review in .agent/registry/inbox/")
    print(f"  Then: ./promote_opportunity.py OPP-XXX to promote to tasks")


def cmd_status(args):
    """Show consolidation status."""
    print("\n" + "=" * 70)
    print("TASK CONSOLIDATION STATUS")
    print("=" * 70)

    # Count centralized
    inbox = list(INBOX_DIR.glob("OPP-*.yaml"))
    active = list(ACTIVE_DIR.glob("TASK-*.yaml"))

    print(f"\nCentralized Registry (.agent/registry/):")
    print(f"  Inbox (OPP-*):  {len(inbox)}")
    print(f"  Active (TASK-*): {len(active)}")

    # Count legacy
    print(f"\nLegacy Registries (scattered):")
    legacy_total = 0
    for key, config in LEGACY_REGISTRIES.items():
        if config["path"].exists():
            tasks = parse_registry(key)
            pending = sum(1 for t in tasks if t["status"] != "COMPLETE")
            legacy_total += pending
            print(f"  {key:20} {pending:4} pending")

    print(f"\n" + "-" * 70)
    print(f"Centralized: {len(inbox) + len(active)}")
    print(f"Legacy:      {legacy_total}")
    print(f"TOTAL:       {len(inbox) + len(active) + legacy_total}")

    if legacy_total > 0:
        print(f"\n⚠️  {legacy_total} tasks still in legacy registries")
        print(f"   Run: ./import_legacy_tasks.py import --all")
    else:
        print(f"\n✓ All tasks centralized!")


def main():
    parser = argparse.ArgumentParser(
        description="Import legacy task registries into unified .agent/registry/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Scan
    scan_p = subparsers.add_parser("scan", help="Preview what would be imported")
    scan_p.add_argument("-v", "--verbose", action="store_true", help="Show sample tasks")

    # Import
    import_p = subparsers.add_parser("import", help="Import tasks from legacy registries")
    import_p.add_argument("--source", help="Registry to import (or 'all')")
    import_p.add_argument("--all", action="store_true", help="Import from all registries")
    import_p.add_argument("--include-complete", action="store_true", help="Include completed tasks")
    import_p.add_argument("--dry-run", action="store_true", help="Preview without creating files")

    # Status
    subparsers.add_parser("status", help="Show consolidation status")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "import":
        if args.all:
            args.source = "all"
        cmd_import(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
