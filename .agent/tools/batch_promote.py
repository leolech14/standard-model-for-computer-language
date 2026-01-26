#!/usr/bin/env python3
"""
Batch Promote - Accept multiple opportunities at once.

Usage:
    ./batch_promote.py --threshold 90       # Promote all >= 90% confidence
    ./batch_promote.py --ids OPP-023 OPP-024 OPP-025  # Promote specific IDs
    ./batch_promote.py --category PIPELINE  # Promote all in category
    ./batch_promote.py --dry-run            # Preview without promoting
    ./batch_promote.py --boost-first        # Run AI boost before promoting

Examples:
    # Promote all high-confidence pipeline tasks
    ./batch_promote.py --threshold 95 --category PIPELINE

    # Boost and promote
    ./batch_promote.py --boost-first --threshold 90
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from utils.yaml_utils import load_yaml_preserve as load_yaml, save_yaml_preserve as save_yaml

SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent
INBOX_DIR = AGENT_DIR / "registry" / "inbox"
ACTIVE_DIR = AGENT_DIR / "registry" / "active"

# Risk-based thresholds
RISK_THRESHOLDS = {
    "A": 90,      # Standard tasks
    "A+": 95,     # Important tasks
    "A++": 99,    # Critical tasks
}
DEFAULT_RISK = "A"

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def get_confidence(opp: dict) -> int:
    """Extract overall confidence from opportunity."""
    conf = opp.get("confidence", {})
    if isinstance(conf, dict):
        scores = [conf.get(k, 0) for k in ['factual', 'alignment', 'current', 'onwards'] if conf.get(k)]
        return min(scores) if scores else 0
    return 0


def find_next_task_id() -> int:
    """Find next available task ID."""
    existing = list(ACTIVE_DIR.glob("TASK-*.yaml"))
    max_id = 0
    for f in existing:
        try:
            # Handle both TASK-001 and TASK-010-001 formats
            name = f.stem
            if name.count("-") == 1:
                num = int(name.split("-")[1])
                max_id = max(max_id, num)
        except (ValueError, IndexError):
            pass
    return max_id + 1


def load_opportunities(threshold: int = None, category: str = None, ids: list = None,
                       use_risk_threshold: bool = True) -> list:
    """Load and filter opportunities.

    Args:
        threshold: Override threshold (if None, uses risk-based)
        category: Filter by category
        ids: Filter by specific IDs
        use_risk_threshold: If True, uses risk-based thresholds (A=90, A+=95, A++=99)
    """
    opportunities = []

    for opp_file in sorted(INBOX_DIR.glob("OPP-*.yaml")):
        opp = load_yaml(opp_file)
        opp["_path"] = opp_file

        # Skip already promoted
        if opp.get("promoted_to"):
            continue

        # Filter by IDs
        if ids:
            if opp.get("id") not in ids:
                continue

        # Filter by category
        if category:
            opp_category = opp.get("metadata", {}).get("category", "")
            if opp_category.upper() != category.upper():
                continue

        # Get confidence
        confidence = get_confidence(opp)
        opp["_confidence"] = confidence

        # Get risk level and appropriate threshold
        risk = opp.get("risk", opp.get("metadata", {}).get("risk", DEFAULT_RISK))
        opp["_risk"] = risk

        if use_risk_threshold:
            min_threshold = RISK_THRESHOLDS.get(risk, RISK_THRESHOLDS[DEFAULT_RISK])
        else:
            min_threshold = threshold if threshold is not None else 0

        # Filter by threshold
        if confidence < min_threshold:
            continue

        opportunities.append(opp)

    return opportunities


def validate_promotion(opp: dict) -> tuple[bool, list]:
    """Validate opportunity can be promoted according to hierarchy rules.

    Rules:
    - All gaps must be RESOLVED
    - Confidence must meet risk threshold
    - Description should exist

    Returns:
        (is_valid, list of issues)
    """
    issues = []

    # Check gaps
    gaps = opp.get("gaps", [])
    open_gaps = [g for g in gaps if g.get("status") == "OPEN"]
    if open_gaps:
        issues.append(f"{len(open_gaps)} unresolved gaps")

    # Check confidence vs risk threshold
    risk = opp.get("_risk", DEFAULT_RISK)
    threshold = RISK_THRESHOLDS.get(risk, RISK_THRESHOLDS[DEFAULT_RISK])
    confidence = opp.get("_confidence", 0)
    if confidence < threshold:
        issues.append(f"confidence {confidence}% < threshold {threshold}% for risk {risk}")

    # Check description
    if not opp.get("description"):
        issues.append("missing description")

    return len(issues) == 0, issues


def promote_opportunity(opp: dict, task_id: str, dry_run: bool = False,
                       skip_validation: bool = False) -> tuple[bool, str]:
    """Promote a single opportunity to task.

    Returns:
        (success, message)
    """
    # Validate first
    if not skip_validation:
        valid, issues = validate_promotion(opp)
        if not valid:
            return False, f"Validation failed: {'; '.join(issues)}"

    opp_path = opp["_path"]
    task_path = ACTIVE_DIR / f"{task_id}.yaml"

    now = datetime.now(timezone.utc).isoformat()
    confidence = opp.get("confidence", {})

    # Determine risk level
    risk = opp.get("risk", opp.get("metadata", {}).get("risk", DEFAULT_RISK))

    task = {
        "id": task_id,
        "title": opp.get("title"),
        "description": opp.get("description", ""),
        "status": "READY",
        "risk": risk,  # Hierarchy field
        "confidence": confidence if isinstance(confidence, dict) else {
            "factual": opp["_confidence"],
            "alignment": opp["_confidence"],
            "current": opp["_confidence"],
            "onwards": opp["_confidence"],
        },
        "created": now,
        "updated": now,
        "promoted_from": opp.get("id"),
        "category": opp.get("metadata", {}).get("category", ""),
        # Hierarchy fields
        "sprint_id": None,  # To be assigned to a sprint
        "steps": [],        # Individual actions (STEP-XX)
        "blocked_by": [],   # Task IDs this is blocked by
        "blocks": [],       # Task IDs this blocks
        # Execution tracking
        "runs": [],
        "output": {},
    }

    if dry_run:
        print(f"  {CYAN}[DRY RUN]{NC} Would create {task_id}")
        return True, "dry run"

    # Save task
    save_yaml(task_path, task)

    # Update opportunity (clean internal fields)
    opp["promoted_to"] = task_id
    opp["promoted_at"] = now
    opp_clean = {k: v for k, v in opp.items() if not k.startswith("_")}
    save_yaml(opp_path, opp_clean)

    return True, "promoted"


def run_boost(opportunities: list) -> list:
    """Run AI confidence boost on opportunities."""
    import subprocess

    boosted = []
    for opp in opportunities:
        opp_id = opp.get("id")
        print(f"  Boosting {opp_id}...", end=" ", flush=True)

        try:
            # Run confidence_validator.py for the opportunity
            # Note: confidence_validator works on tasks, so we do a quick assessment
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "confidence_validator.py"), opp_id, "--no-save"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                print(f"{GREEN}OK{NC}")
                boosted.append(opp)
            else:
                print(f"{YELLOW}SKIP{NC}")
        except Exception as e:
            print(f"{RED}ERROR: {e}{NC}")

    return boosted


def main():
    parser = argparse.ArgumentParser(
        description="Batch promote opportunities to tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--threshold", type=int,
                        help="Override threshold (default: use risk-based A=90, A+=95, A++=99)")
    parser.add_argument("--ignore-risk", action="store_true",
                        help="Ignore risk levels, use --threshold only")
    parser.add_argument("--ids", nargs="+",
                        help="Specific opportunity IDs to promote")
    parser.add_argument("--category",
                        help="Only promote from this category")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without promoting")
    parser.add_argument("--boost-first", action="store_true",
                        help="Run AI boost before promoting")
    parser.add_argument("--limit", type=int,
                        help="Maximum number to promote")

    args = parser.parse_args()

    print(f"\n{YELLOW}BATCH PROMOTE{NC}")
    print("=" * 50)
    if args.ignore_risk:
        print(f"Threshold: {args.threshold or 75}% (risk ignored)")
    else:
        print(f"Thresholds: A={RISK_THRESHOLDS['A']}% | A+={RISK_THRESHOLDS['A+']}% | A++={RISK_THRESHOLDS['A++']}%")
    if args.category:
        print(f"Category: {args.category}")
    if args.ids:
        print(f"IDs: {', '.join(args.ids)}")
    print()

    # Load opportunities
    opportunities = load_opportunities(
        threshold=args.threshold or 75,
        category=args.category,
        ids=args.ids,
        use_risk_threshold=not args.ignore_risk,
    )

    if not opportunities:
        print(f"{YELLOW}No opportunities match criteria{NC}")
        return

    # Apply limit
    if args.limit:
        opportunities = opportunities[:args.limit]

    print(f"Found {len(opportunities)} opportunities to promote:\n")

    for opp in opportunities:
        conf = opp["_confidence"]
        title = opp.get("title", "Untitled")[:40]
        category = opp.get("metadata", {}).get("category", "?")
        print(f"  [{conf:3}%] {opp['id']:10} {title:40} ({category})")

    print()

    # Boost first if requested
    if args.boost_first:
        print(f"{YELLOW}Running AI boost...{NC}")
        opportunities = run_boost(opportunities)
        print()

    # Promote
    if args.dry_run:
        print(f"{CYAN}[DRY RUN] Would promote {len(opportunities)} opportunities{NC}\n")
    else:
        print(f"{YELLOW}Promoting...{NC}")

    next_id = find_next_task_id()
    promoted = 0

    failed = 0
    for opp in opportunities:
        task_id = f"TASK-{next_id:03d}"
        opp_id = opp.get("id")

        success, message = promote_opportunity(opp, task_id, args.dry_run)
        if success:
            conf = opp["_confidence"]
            print(f"  {GREEN}[{conf}%]{NC} {opp_id} -> {task_id}")
            next_id += 1
            promoted += 1
        else:
            print(f"  {RED}[FAIL]{NC} {opp_id}: {message}")
            failed += 1

    print()
    print("=" * 50)
    print(f"{GREEN}Promoted: {promoted}{NC}")
    if failed > 0:
        print(f"{RED}Failed: {failed}{NC}")
    if not args.dry_run:
        print(f"\nView with: .agent/tools/task_store.py list")


if __name__ == "__main__":
    main()
