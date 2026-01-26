#!/usr/bin/env python3
"""
triage_inbox.py - Score, prioritize, and clean the opportunity inbox.

Usage:
    ./triage_inbox.py                    # Full triage report
    ./triage_inbox.py --score            # Score all unscored opportunities
    ./triage_inbox.py --duplicates       # Find duplicates of active tasks
    ./triage_inbox.py --archive OPP-XXX  # Archive specific opportunity
    ./triage_inbox.py --archive-range 23 57  # Archive OPP-023 to OPP-057
    ./triage_inbox.py --clean            # Archive all duplicates and noise

Outputs:
    - Console report with priority ranking
    - .agent/intelligence/triage_reports/YYYYMMDD_HHMMSS_triage.json
"""

import sys
import json
import re
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

from utils.yaml_utils import load_yaml, save_yaml

# Paths
SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent
INBOX_DIR = AGENT_DIR / "registry" / "inbox"
ACTIVE_DIR = AGENT_DIR / "registry" / "active"
ARCHIVE_DIR = AGENT_DIR / "registry" / "archive"
REPORTS_DIR = AGENT_DIR / "intelligence" / "triage_reports"

# Ensure directories exist
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'
BOLD = '\033[1m'


def similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio (0-1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def load_all_opportunities() -> List[Tuple[Path, dict]]:
    """Load all opportunities from inbox."""
    opps = []
    for f in sorted(INBOX_DIR.glob("OPP-*.yaml")):
        data = load_yaml(f)
        if data:
            opps.append((f, data))
    return opps


def load_all_tasks() -> List[Tuple[Path, dict]]:
    """Load all active tasks."""
    tasks = []
    for f in sorted(ACTIVE_DIR.glob("TASK-*.yaml")):
        data = load_yaml(f)
        if data:
            tasks.append((f, data))
    return tasks


def score_opportunity(opp: dict, tasks: List[dict]) -> dict:
    """
    Score an opportunity with 4D confidence.

    Heuristics:
    - factual: Based on evidence quality and description clarity
    - alignment: Based on source and relation to known tasks
    - current: Based on related_to fields and file references
    - onwards: Based on urgency and strategic value
    """
    scores = {
        "factual": 50,
        "alignment": 50,
        "current": 50,
        "onwards": 50,
    }

    title = opp.get("title", "")
    desc = opp.get("description", "")
    source = opp.get("source", "UNKNOWN")
    urgency = opp.get("urgency", "MEDIUM")
    related_to = opp.get("related_to", [])
    evidence = opp.get("evidence", [])

    # FACTUAL: Does it have clear description and evidence?
    if len(desc) > 100:
        scores["factual"] += 15
    if len(desc) > 300:
        scores["factual"] += 10
    if evidence:
        scores["factual"] += 20
    if len(title) > 20 and len(title) < 80:
        scores["factual"] += 5

    # ALIGNMENT: Is it from a trusted source?
    source_boost = {
        "BARE": 25,
        "RESEARCH": 20,
        "HUMAN": 15,
        "WATCHER": 10,
        "EXTERNAL": 5,
        "MIGRATION": -10,  # Bulk imports often noisy
    }
    scores["alignment"] += source_boost.get(source, 0)

    # Check if it relates to known tasks
    task_titles = [t.get("title", "").lower() for t in tasks]
    for t_title in task_titles:
        if similarity(title.lower(), t_title) > 0.5:
            scores["alignment"] += 10
            break

    # CURRENT: Does it reference real files/tasks?
    if related_to:
        scores["current"] += 15
        # Check if related files exist
        for ref in related_to[:3]:  # Check first 3
            if Path(ref).exists():
                scores["current"] += 5

    # ONWARDS: Strategic value
    urgency_boost = {
        "CRITICAL": 30,
        "HIGH": 20,
        "MEDIUM": 10,
        "LOW": 0,
    }
    scores["onwards"] += urgency_boost.get(urgency, 0)

    # Keywords that indicate strategic value
    strategic_keywords = ["pipeline", "automation", "discovery", "refinery", "confidence", "core"]
    for kw in strategic_keywords:
        if kw in title.lower() or kw in desc.lower():
            scores["onwards"] += 5
            break

    # Cap scores at 100
    for k in scores:
        scores[k] = min(100, max(0, scores[k]))

    # Verdict is min
    scores["verdict"] = min(scores["factual"], scores["alignment"],
                           scores["current"], scores["onwards"])

    return scores


def find_duplicates(opps: List[Tuple[Path, dict]], tasks: List[Tuple[Path, dict]]) -> List[dict]:
    """Find opportunities that duplicate existing tasks."""
    duplicates = []

    task_titles = [(p, t.get("title", ""), t.get("id", "")) for p, t in tasks]

    for opp_path, opp in opps:
        opp_title = opp.get("title", "")
        opp_id = opp.get("id", opp_path.stem)

        for task_path, task_title, task_id in task_titles:
            sim = similarity(opp_title, task_title)
            if sim > 0.7:  # 70% similarity threshold
                duplicates.append({
                    "opp_id": opp_id,
                    "opp_title": opp_title,
                    "task_id": task_id,
                    "task_title": task_title,
                    "similarity": sim,
                    "opp_path": str(opp_path),
                })

    return duplicates


def categorize_opportunities(opps: List[Tuple[Path, dict]]) -> dict:
    """Categorize opportunities by source and type."""
    categories = {
        "by_source": {},
        "by_urgency": {},
        "noise": [],  # Likely noise (very short titles, checklist items, etc.)
    }

    for path, opp in opps:
        source = opp.get("source", "UNKNOWN")
        urgency = opp.get("urgency", "MEDIUM")
        title = opp.get("title", "")
        opp_id = opp.get("id", path.stem)

        # By source
        if source not in categories["by_source"]:
            categories["by_source"][source] = []
        categories["by_source"][source].append(opp_id)

        # By urgency
        if urgency not in categories["by_urgency"]:
            categories["by_urgency"][urgency] = []
        categories["by_urgency"][urgency].append(opp_id)

        # Detect noise
        is_noise = False
        # Very short title (likely a checklist item)
        if len(title) < 25:
            is_noise = True
        # Starts with backtick (code snippet, not task)
        if title.startswith("`"):
            is_noise = True
        # Color/token fragment
        if title.startswith("color.") or title.startswith("shadow."):
            is_noise = True

        if is_noise:
            categories["noise"].append(opp_id)

    return categories


def archive_opportunity(opp_id: str, reason: str = "triage") -> bool:
    """Move an opportunity to archive."""
    # Find the file
    opp_file = INBOX_DIR / f"{opp_id}.yaml"
    if not opp_file.exists():
        print(f"{RED}Not found: {opp_id}{NC}")
        return False

    # Load and update
    opp = load_yaml(opp_file)
    if not opp:
        return False

    opp["archived_at"] = datetime.now(timezone.utc).isoformat()
    opp["archive_reason"] = reason

    # Move to archive
    archive_file = ARCHIVE_DIR / f"{opp_id}.yaml"
    save_yaml(archive_file, opp)
    opp_file.unlink()

    print(f"{GREEN}Archived: {opp_id} ({reason}){NC}")
    return True


def generate_triage_report(opps: List[Tuple[Path, dict]], tasks: List[Tuple[Path, dict]]) -> dict:
    """Generate full triage report."""
    task_dicts = [t for _, t in tasks]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_opportunities": len(opps),
            "total_active_tasks": len(tasks),
        },
        "scored": [],
        "duplicates": [],
        "categories": {},
        "recommendations": [],
    }

    # Score all opportunities
    for path, opp in opps:
        opp_id = opp.get("id", path.stem)
        scores = score_opportunity(opp, task_dicts)
        report["scored"].append({
            "id": opp_id,
            "title": opp.get("title", "")[:60],
            "source": opp.get("source", "UNKNOWN"),
            "scores": scores,
        })

    # Sort by verdict (highest first)
    report["scored"].sort(key=lambda x: x["scores"]["verdict"], reverse=True)

    # Find duplicates
    report["duplicates"] = find_duplicates(opps, tasks)

    # Categorize
    report["categories"] = categorize_opportunities(opps)

    # Generate recommendations
    high_value = [s for s in report["scored"] if s["scores"]["verdict"] >= 70]
    low_value = [s for s in report["scored"] if s["scores"]["verdict"] < 50]

    report["recommendations"] = [
        f"PROMOTE: {len(high_value)} opportunities score >= 70% (ready for promotion)",
        f"REVIEW: {len(report['scored']) - len(high_value) - len(low_value)} opportunities score 50-69%",
        f"ARCHIVE: {len(low_value)} opportunities score < 50% (low value)",
        f"DUPLICATES: {len(report['duplicates'])} match existing tasks (archive)",
        f"NOISE: {len(report['categories'].get('noise', []))} appear to be checklist items",
    ]

    # Summary counts
    report["summary"]["high_value"] = len(high_value)
    report["summary"]["low_value"] = len(low_value)
    report["summary"]["duplicates"] = len(report["duplicates"])
    report["summary"]["noise"] = len(report["categories"].get("noise", []))

    return report


def print_report(report: dict):
    """Print triage report to console."""
    print(f"\n{BOLD}{'=' * 70}{NC}")
    print(f"{BOLD}OPPORTUNITY INBOX TRIAGE REPORT{NC}")
    print(f"{'=' * 70}")
    print(f"Generated: {report['generated_at']}")

    s = report["summary"]
    print(f"\n{BOLD}SUMMARY{NC}")
    print(f"  Total opportunities: {s['total_opportunities']}")
    print(f"  Active tasks: {s['total_active_tasks']}")
    print(f"  {GREEN}High value (>=70%): {s['high_value']}{NC}")
    print(f"  {YELLOW}Duplicates: {s['duplicates']}{NC}")
    print(f"  {RED}Noise items: {s['noise']}{NC}")
    print(f"  {RED}Low value (<50%): {s['low_value']}{NC}")

    print(f"\n{BOLD}TOP 10 (Highest Priority){NC}")
    print(f"{'ID':<10} {'SCORE':<6} {'SOURCE':<12} TITLE")
    print("-" * 70)
    for item in report["scored"][:10]:
        score = item["scores"]["verdict"]
        color = GREEN if score >= 70 else (YELLOW if score >= 50 else RED)
        print(f"{item['id']:<10} {color}{score:>3}%{NC}   {item['source']:<12} {item['title'][:40]}")

    if report["duplicates"]:
        print(f"\n{BOLD}DUPLICATES (Match Existing Tasks){NC}")
        for dup in report["duplicates"][:10]:
            print(f"  {YELLOW}{dup['opp_id']}{NC} ~= {dup['task_id']} ({dup['similarity']*100:.0f}% match)")

    print(f"\n{BOLD}RECOMMENDATIONS{NC}")
    for rec in report["recommendations"]:
        print(f"  - {rec}")

    print(f"\n{'=' * 70}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Triage the opportunity inbox")
    parser.add_argument("--score", action="store_true", help="Score all opportunities")
    parser.add_argument("--duplicates", action="store_true", help="Find duplicates only")
    parser.add_argument("--archive", metavar="OPP_ID", help="Archive specific opportunity")
    parser.add_argument("--archive-range", nargs=2, type=int, metavar=("START", "END"),
                        help="Archive range OPP-START to OPP-END")
    parser.add_argument("--clean", action="store_true", help="Archive all duplicates and noise")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of console")

    args = parser.parse_args()

    # Load data
    opps = load_all_opportunities()
    tasks = load_all_tasks()

    if not opps:
        print(f"{YELLOW}No opportunities in inbox.{NC}")
        return 0

    # Handle specific commands
    if args.archive:
        return 0 if archive_opportunity(args.archive, "manual") else 1

    if args.archive_range:
        start, end = args.archive_range
        archived = 0
        for i in range(start, end + 1):
            opp_id = f"OPP-{i:03d}"
            if archive_opportunity(opp_id, "batch_triage"):
                archived += 1
        print(f"\n{GREEN}Archived {archived} opportunities.{NC}")
        return 0

    # Generate report
    report = generate_triage_report(opps, tasks)

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORTS_DIR / f"{timestamp}_triage.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
        print(f"Report saved: {report_file}")

    if args.clean:
        print(f"\n{BOLD}CLEANING...{NC}")
        # Archive duplicates
        for dup in report["duplicates"]:
            archive_opportunity(dup["opp_id"], f"duplicate_of_{dup['task_id']}")
        # Archive noise
        for noise_id in report["categories"].get("noise", []):
            archive_opportunity(noise_id, "noise_checklist_item")
        print(f"{GREEN}Cleanup complete.{NC}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
