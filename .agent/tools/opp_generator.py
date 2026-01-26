#!/usr/bin/env python3
"""
OPP Generator
=============
SMoC Role: Factory | Domain: Opportunity

Generates opportunity (OPP) files from macro findings or manual input.

Validated Architecture (2026-01-25):
- Follows promote_opportunity.py pattern
- Auto-generates OPP-XXX IDs
- Integrates with macro execution results

Usage:
    ./opp_generator.py create --title "Title" --severity HIGH
    ./opp_generator.py from-macro MACRO-001 --execution 0
    ./opp_generator.py list

Part of S13 (Macro Registry) → S5 (Task Registry) integration.
See: .agent/registry/inbox/
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from utils.yaml_utils import load_yaml_preserve as load_yaml, save_yaml_preserve as save_yaml

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
INBOX_DIR = REPO_ROOT / ".agent" / "registry" / "inbox"
MACROS_DIR = REPO_ROOT / ".agent" / "macros"
LIBRARY_DIR = MACROS_DIR / "library"

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'


def ensure_dirs():
    """Create directories if they don't exist."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)


def find_next_opp_id() -> str:
    """Find the next available OPP-XXX ID."""
    existing = list(INBOX_DIR.glob("OPP-*.yaml"))

    if not existing:
        return "OPP-001"

    numbers = []
    for f in existing:
        match = re.search(r'OPP-(\d+)', f.name)
        if match:
            numbers.append(int(match.group(1)))

    next_num = max(numbers) + 1 if numbers else 1
    return f"OPP-{next_num:03d}"


def severity_to_urgency(severity: str) -> str:
    """Map severity to urgency level."""
    mapping = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
        "INFO": "LOW",
    }
    return mapping.get(severity.upper(), "MEDIUM")


def load_macro(macro_id: str) -> tuple[Path, dict]:
    """Load a macro by ID."""
    if not macro_id.startswith("MACRO-"):
        macro_id = f"MACRO-{macro_id}"

    for pattern in [f"{macro_id}.yaml", f"{macro_id}-*.yaml"]:
        matches = list(LIBRARY_DIR.glob(pattern))
        if matches:
            path = matches[0]
            return path, load_yaml(path)

    raise FileNotFoundError(f"Macro {macro_id} not found")


def create_opp(
    title: str,
    description: str,
    severity: str = "MEDIUM",
    source: str = "manual",
    suggested_action: str = None,
    related_to: list = None,
    tags: list = None,
) -> Path:
    """Create a new opportunity file."""
    ensure_dirs()

    opp_id = find_next_opp_id()
    opp_file = INBOX_DIR / f"{opp_id}.yaml"
    now = datetime.now(timezone.utc).isoformat()

    opp = {
        "id": opp_id,
        "title": title,
        "description": description,
        "urgency": severity_to_urgency(severity),
        "source": source,
        "created_at": now,
    }

    if suggested_action:
        opp["suggested_action"] = suggested_action

    if related_to:
        opp["related_to"] = related_to

    if tags:
        opp["tags"] = tags

    # Write with header
    with open(opp_file, 'w') as f:
        f.write(f"# Opportunity: {title}\n")
        f.write(f"# Created: {now}\n")
        f.write(f"# Source: {source}\n\n")
        if USE_RUAMEL:
            yaml.dump(opp, f)
        else:
            pyyaml.dump(opp, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return opp_file


# =============================================================================
# CLI COMMANDS
# =============================================================================

def cmd_create(args):
    """Create a new opportunity manually."""
    opp_file = create_opp(
        title=args.title,
        description=args.description or "",
        severity=args.severity,
        source="manual",
        suggested_action=args.action,
        tags=args.tags.split(",") if args.tags else None,
    )

    print(f"{GREEN}Created: {opp_file}{NC}")
    print(f"\nNext steps:")
    print(f"  1. Review: cat {opp_file}")
    print(f"  2. Promote: ./promote_opportunity.py {opp_file.name}")


def cmd_from_macro(args):
    """Create opportunities from macro execution findings."""
    try:
        path, macro = load_macro(args.macro_id)
    except FileNotFoundError as e:
        print(f"{RED}Error: {e}{NC}")
        sys.exit(1)

    executions = macro.get("executions", [])
    if not executions:
        print(f"{YELLOW}No executions found for {args.macro_id}{NC}")
        sys.exit(1)

    # Get the requested execution (default: most recent)
    exec_idx = args.execution if args.execution is not None else -1
    try:
        execution = executions[exec_idx]
    except IndexError:
        print(f"{RED}Execution {exec_idx} not found. Total: {len(executions)}{NC}")
        sys.exit(1)

    findings = execution.get("findings", {})
    if not findings:
        print(f"{YELLOW}No findings in execution {exec_idx}{NC}")
        sys.exit(0)

    print(f"\n{YELLOW}Generating OPPs from {args.macro_id} execution...{NC}")
    created = []

    # Generate OPP for each finding type
    for finding_type, finding_value in findings.items():
        if finding_value and finding_value not in [0, "0", "0%", None]:
            title = f"[{args.macro_id}] {finding_type.replace('_', ' ').title()}"

            # Build description
            if isinstance(finding_value, int):
                desc = f"Found {finding_value} issues.\n\nDiscovered by {args.macro_id} audit."
            else:
                desc = f"Finding: {finding_value}\n\nDiscovered by {args.macro_id} audit."

            # Determine severity
            severity = "HIGH" if finding_type in ["dead_code", "integration_failures"] else "MEDIUM"

            opp_file = create_opp(
                title=title,
                description=desc,
                severity=severity,
                source=f"macro:{args.macro_id}",
                tags=[finding_type, "audit", args.macro_id],
            )
            created.append(opp_file)
            print(f"  {GREEN}Created: {opp_file.name}{NC} - {title}")

    # Also create OPPs from follow_up_created if present
    follow_ups = execution.get("follow_up_created", [])
    for follow_up in follow_ups:
        opp_file = create_opp(
            title=f"[{args.macro_id}] {follow_up}",
            description=f"Follow-up action from {args.macro_id} audit.",
            severity="MEDIUM",
            source=f"macro:{args.macro_id}",
            suggested_action=follow_up,
            tags=["follow_up", args.macro_id],
        )
        created.append(opp_file)
        print(f"  {GREEN}Created: {opp_file.name}{NC} - {follow_up[:50]}...")

    print(f"\n{GREEN}Created {len(created)} opportunities.{NC}")
    print(f"\nNext: Review in .agent/registry/inbox/")


def cmd_list(args):
    """List all opportunities in inbox."""
    ensure_dirs()

    opps = list(INBOX_DIR.glob("OPP-*.yaml"))
    if not opps:
        print("No opportunities in inbox.")
        return

    print(f"\n{'='*65}")
    print(f"OPPORTUNITIES ({len(opps)} in inbox)")
    print(f"{'='*65}\n")

    for opp_file in sorted(opps):
        data = load_yaml(opp_file)
        opp_id = data.get("id", "?")
        title = data.get("title", "Untitled")[:45]
        urgency = data.get("urgency", "?")
        source = data.get("source", "?")[:15]

        urgency_color = {
            "CRITICAL": RED,
            "HIGH": YELLOW,
            "MEDIUM": NC,
            "LOW": NC,
        }.get(urgency, NC)

        print(f"  {opp_id:10} {urgency_color}{urgency:8}{NC} {title:45} [{source}]")


def main():
    parser = argparse.ArgumentParser(
        description="OPP Generator - Create opportunities from findings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    ./opp_generator.py create --title "Fix dead code" --severity HIGH
    ./opp_generator.py from-macro MACRO-001
    ./opp_generator.py from-macro MACRO-001 --execution -1
    ./opp_generator.py list
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create
    create_p = subparsers.add_parser("create", help="Create new opportunity manually")
    create_p.add_argument("--title", required=True, help="Opportunity title")
    create_p.add_argument("--description", help="Detailed description")
    create_p.add_argument("--severity", default="MEDIUM",
                         choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                         help="Severity level")
    create_p.add_argument("--action", help="Suggested action")
    create_p.add_argument("--tags", help="Comma-separated tags")

    # From Macro
    macro_p = subparsers.add_parser("from-macro", help="Create OPPs from macro findings")
    macro_p.add_argument("macro_id", help="Macro ID (e.g., MACRO-001)")
    macro_p.add_argument("--execution", type=int, help="Execution index (default: -1 = most recent)")

    # List
    subparsers.add_parser("list", help="List opportunities in inbox")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create(args)
    elif args.command == "from-macro":
        cmd_from_macro(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
