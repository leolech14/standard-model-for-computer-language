#!/usr/bin/env python3
"""
Task Store
==========
SMoC Role: Store | Domain: Task

YAML-based task state management.

Validated Architecture (Gemini + Perplexity 2026-01-23):
- YAML format for hybrid human-AI safety
- Follows sprint.py pattern for atomic operations
- Uses ruamel.yaml for safe round-trip editing
- Schema validation via pre-defined structure

Usage:
    ./task_store.py list                              # List all tasks
    ./task_store.py show TASK-122                     # Show task details
    ./task_store.py add --id 128 --subject "Name" --score 85
    ./task_store.py update TASK-122 --status complete --commit abc123
    ./task_store.py boost TASK-127 --score 85 --reason "Evidence found"

Part of S5 (Task Registry subsystem).
See: .agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

# Use ruamel.yaml for safe round-trip editing (preserves comments)
try:
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
except ImportError:
    # Fallback to PyYAML
    import yaml as pyyaml
    yaml = None

REPO_ROOT = Path(__file__).parent.parent.parent
TASKS_DIR = REPO_ROOT / ".agent" / "registry" / "active"
ARCHIVE_DIR = REPO_ROOT / ".agent" / "registry" / "archive"
# Legacy LEARNING_SYSTEM tasks (for migration)
LEGACY_DIR = ARCHIVE_DIR / "legacy_learning_system" / "tasks"

# Risk-adjusted thresholds
THRESHOLDS = {"A": 85, "A+": 95, "A++": 99}


def ensure_dirs():
    """Create task directories if they don't exist."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def load_task(task_id: str) -> tuple[Path, dict]:
    """Load a task file by ID."""
    # Normalize ID
    if not task_id.startswith("TASK-"):
        task_id = f"TASK-{task_id}"

    # Check active tasks first
    task_file = TASKS_DIR / f"{task_id}.yaml"
    if task_file.exists():
        with open(task_file) as f:
            if yaml:
                return task_file, yaml.load(f)
            else:
                return task_file, pyyaml.safe_load(f)

    # Check archive
    archive_file = ARCHIVE_DIR / f"{task_id}.yaml"
    if archive_file.exists():
        with open(archive_file) as f:
            if yaml:
                return archive_file, yaml.load(f)
            else:
                return archive_file, pyyaml.safe_load(f)

    # Check legacy LEARNING_SYSTEM tasks
    legacy_file = LEGACY_DIR / f"{task_id}.yaml"
    if legacy_file.exists():
        with open(legacy_file) as f:
            if yaml:
                return legacy_file, yaml.load(f)
            else:
                return legacy_file, pyyaml.safe_load(f)

    # Check legacy archive
    legacy_archive = LEGACY_DIR / "archive" / f"{task_id}.yaml"
    if legacy_archive.exists():
        with open(legacy_archive) as f:
            if yaml:
                return legacy_archive, yaml.load(f)
            else:
                return legacy_archive, pyyaml.safe_load(f)

    raise FileNotFoundError(f"Task {task_id} not found")


def save_task(path: Path, data: dict):
    """Save task data atomically."""
    # Write to temp file first, then rename (atomic on POSIX)
    temp_path = path.with_suffix('.tmp')
    with open(temp_path, 'w') as f:
        if yaml:
            yaml.dump(data, f)
        else:
            pyyaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    temp_path.rename(path)


def get_status_emoji(score: int, risk: str = "A") -> str:
    """Determine status emoji based on score and threshold."""
    threshold = THRESHOLDS.get(risk, 85)
    if score >= threshold:
        return "🟢"
    elif score >= 50:
        return "🟡"
    else:
        return "🔴"


def cmd_list(args):
    """List all tasks."""
    ensure_dirs()

    tasks = []

    # Load from active directory
    for task_file in TASKS_DIR.glob("TASK-*.yaml"):
        with open(task_file) as f:
            if yaml:
                data = yaml.load(f)
            else:
                data = pyyaml.safe_load(f)
            if data:
                data['_source'] = 'active'
                tasks.append(data)

    # Load from legacy LEARNING_SYSTEM directory
    if LEGACY_DIR.exists():
        for task_file in LEGACY_DIR.glob("TASK-*.yaml"):
            with open(task_file) as f:
                if yaml:
                    data = yaml.load(f)
                else:
                    data = pyyaml.safe_load(f)
                if data:
                    data['_source'] = 'legacy'
                    tasks.append(data)

    # Group by status
    ready, needs_boost, complete, deferred = [], [], [], []

    for task in sorted(tasks, key=lambda t: int(str(t.get('id', 0)).replace('TASK-', ''))):
        task_id = str(task.get('id', '0'))
        tid = task_id if task_id.startswith('TASK-') else f"TASK-{task_id}"

        # Handle both legacy and new schemas
        # New schema: confidence.factual/alignment/current/onwards
        # Legacy schema: score
        confidence = task.get('confidence', {})
        if confidence:
            # New schema: compute min of 4D scores
            scores = [confidence.get(k, 0) for k in ['factual', 'alignment', 'current', 'onwards'] if confidence.get(k)]
            score = min(scores) if scores else 0
        else:
            score = task.get('score', 0)

        risk = task.get('risk', 'A')
        status = task.get('status', 'pending').lower()
        # Handle both title (new) and subject (legacy)
        subject = (task.get('title') or task.get('subject') or 'Untitled')[:40]
        emoji = get_status_emoji(score, risk)

        line = f"{emoji} {tid:12} {subject:40} [{score}%]"

        if status == 'complete':
            commit = task.get('commit', '?')
            complete.append(f"☑️  {tid:12} {subject:40} [{commit}]")
        elif status == 'deferred':
            deferred.append(f"💤 {tid:12} {subject:40}")
        elif score >= THRESHOLDS.get(risk, 85):
            ready.append(line)
        else:
            needs_boost.append(line)

    print(f"\n{'='*65}")
    print(f"TASK REGISTRY ({len(tasks)} tasks)")
    print(f"{'='*65}\n")

    if ready:
        print("READY TO EXECUTE:")
        for line in ready:
            print(f"  {line}")
        print()

    if needs_boost:
        print("NEEDS BOOST:")
        for line in needs_boost:
            print(f"  {line}")
        print()

    if complete:
        print(f"COMPLETE ({len(complete)} tasks):")
        for line in complete[-5:]:
            print(f"  {line}")
        if len(complete) > 5:
            print(f"  ... and {len(complete)-5} more")
        print()

    if deferred:
        print("DEFERRED:")
        for line in deferred:
            print(f"  {line}")


def cmd_show(args):
    """Show task details."""
    try:
        path, task = load_task(args.task_id)
        print(f"\n{path.name}")
        print("-" * 40)
        if yaml:
            yaml.dump(task, __import__('sys').stdout)
        else:
            print(pyyaml.dump(task, default_flow_style=False))
    except FileNotFoundError as e:
        print(f"Error: {e}")


def cmd_add(args):
    """Add a new task."""
    ensure_dirs()

    task_id = f"TASK-{args.id}"
    task_file = TASKS_DIR / f"{task_id}.yaml"

    if task_file.exists():
        print(f"Error: {task_id} already exists")
        return

    task = {
        'id': args.id,
        'subject': args.subject,
        'score': args.score,
        'risk': args.risk,
        'category': args.category or '',
        'description': args.description or '',
        'status': 'pending',
        'created': datetime.now(timezone.utc).isoformat(),
        'commit': None,
        '4d_scores': {
            'factual': args.score,
            'alignment': args.score,
            'current': args.score,
            'onwards': args.score
        },
        'history': []
    }

    save_task(task_file, task)
    emoji = get_status_emoji(args.score, args.risk)
    print(f"Added: {emoji} {task_id} {args.subject} [{args.score}%]")


def cmd_update(args):
    """Update a task."""
    try:
        path, task = load_task(args.task_id)

        if args.status:
            task['status'] = args.status
            if args.status == 'complete' and args.commit:
                task['commit'] = args.commit
                # Move to archive
                new_path = ARCHIVE_DIR / path.name
                save_task(new_path, task)
                path.unlink()
                print(f"Completed and archived: {args.task_id}")
                return

        if args.score is not None:
            old_score = task.get('score', 0)
            task['score'] = args.score
            task['history'].append({
                'date': datetime.now(timezone.utc).isoformat(),
                'change': f"{old_score}% → {args.score}%",
                'reason': args.reason or 'Manual update'
            })

        save_task(path, task)
        emoji = get_status_emoji(task['score'], task.get('risk', 'A'))
        print(f"Updated: {emoji} {args.task_id} [{task['score']}%]")

    except FileNotFoundError as e:
        print(f"Error: {e}")


def cmd_boost(args):
    """Boost task confidence with reason."""
    args.status = None
    args.commit = None
    cmd_update(args)


def main():
    parser = argparse.ArgumentParser(
        description="Task Registry CLI - YAML-based task management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List
    subparsers.add_parser("list", help="List all tasks")

    # Show
    show_p = subparsers.add_parser("show", help="Show task details")
    show_p.add_argument("task_id", help="Task ID (e.g., TASK-122 or 122)")

    # Add
    add_p = subparsers.add_parser("add", help="Add new task")
    add_p.add_argument("--id", type=int, required=True, help="Task number")
    add_p.add_argument("--subject", required=True, help="Task subject")
    add_p.add_argument("--score", type=int, required=True, help="Confidence score")
    add_p.add_argument("--risk", default="A", choices=["A", "A+", "A++"])
    add_p.add_argument("--category", help="Task category")
    add_p.add_argument("--description", help="Task description")

    # Update
    update_p = subparsers.add_parser("update", help="Update task")
    update_p.add_argument("task_id", help="Task ID")
    update_p.add_argument("--status", choices=["pending", "complete", "deferred"])
    update_p.add_argument("--score", type=int)
    update_p.add_argument("--commit", help="Commit hash (for complete)")
    update_p.add_argument("--reason", help="Reason for change")

    # Boost (shorthand)
    boost_p = subparsers.add_parser("boost", help="Boost task confidence")
    boost_p.add_argument("task_id", help="Task ID")
    boost_p.add_argument("--score", type=int, required=True)
    boost_p.add_argument("--reason", required=True)

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "boost":
        cmd_boost(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
