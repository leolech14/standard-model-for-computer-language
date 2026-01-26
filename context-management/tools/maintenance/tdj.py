#!/usr/bin/env python3
"""
TDJ - Timestamp Daily Journal
=============================
SMoC Role: Index | Domain: Temporal

Persistent temporal index of all repository files.
Enables point-in-time queries, activity detection, staleness analysis,
pattern filtering, and AI context injection.

Usage:
    python tdj.py --scan                    # Full rescan to JSONL
    python tdj.py --scan --quiet            # Silent scan (for automation)
    python tdj.py recent 7                  # Files created in last 7 days
    python tdj.py modified 1                # Files modified in last 1 day
    python tdj.py stale 30                  # Not modified in 30+ days
    python tdj.py pattern "src/core"        # Files matching path pattern
    python tdj.py summary                   # Project timeline summary
    python tdj.py context                   # AI-ready XML context block

Flags:
    --quiet, -q                             # Suppress all output (for automation)

Replaces: timestamps.py + project_elements_file_timestamps.csv
Output: .agent/intelligence/tdj.jsonl

Macro: MACRO-002-tdj
Trigger: Daily 6AM schedule + drift_guard events
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
TDJ_FILE = PROJECT_ROOT / ".agent" / "intelligence" / "tdj.jsonl"
LEGACY_CSV = PROJECT_ROOT / "project_elements_file_timestamps.csv"

# Patterns to ignore during scan
IGNORE_PATTERNS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    ".tools_venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "*.pyc",
    ".DS_Store",
    "tdj.jsonl",  # Prevent self-reference loop
}

# File extensions to track (None = all)
TRACK_EXTENSIONS = None  # Track everything

# Global quiet flag (set by --quiet argument)
QUIET = False

# =============================================================================
# SCANNER
# =============================================================================

def should_ignore(path: Path) -> bool:
    """Check if path should be ignored."""
    path_str = str(path)
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True
        if pattern.startswith("*") and path_str.endswith(pattern[1:]):
            return True
    return False


def scan_filesystem() -> List[Dict]:
    """Scan all files and return entries."""
    entries = []
    scan_ts = time.time()

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Filter directories in-place to skip ignored
        dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]

        for filename in files:
            filepath = Path(root) / filename

            if should_ignore(filepath):
                continue

            try:
                stat = filepath.stat()
                rel_path = str(filepath.relative_to(PROJECT_ROOT))

                entry = {
                    "path": rel_path,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "ctime": stat.st_birthtime if hasattr(stat, 'st_birthtime') else stat.st_ctime,
                    "scan_ts": scan_ts,
                }
                entries.append(entry)
            except (OSError, ValueError) as e:
                # Skip files we can't stat
                continue

    return entries


def write_jsonl(entries: List[Dict]):
    """Write entries to JSONL file with metadata header."""
    TDJ_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Metadata as first line
    metadata = {
        "_meta": True,
        "version": "1.0.0",
        "type": "temporal_index",
        "project": "PROJECT_elements",
        "generated": datetime.now().isoformat(),
        "entry_count": len(entries),
        "scan_duration_ms": 0,  # Will be updated
    }

    start = time.time()

    with open(TDJ_FILE, 'w') as f:
        # Write metadata
        f.write(json.dumps(metadata) + '\n')

        # Write entries
        for entry in entries:
            f.write(json.dumps(entry) + '\n')

    duration_ms = int((time.time() - start) * 1000)
    if not QUIET:
        print(f"Scan complete: {len(entries)} files in {duration_ms}ms")
        print(f"Output: {TDJ_FILE}")


def cmd_scan():
    """Full filesystem scan to JSONL."""
    if not QUIET:
        print(f"Scanning {PROJECT_ROOT}...")
    entries = scan_filesystem()
    write_jsonl(entries)


# =============================================================================
# QUERY ENGINE
# =============================================================================

def load_entries() -> List[Dict]:
    """Load entries from JSONL file."""
    if not TDJ_FILE.exists():
        # Fall back to legacy CSV if JSONL doesn't exist
        if LEGACY_CSV.exists():
            return load_legacy_csv()
        print(f"Error: {TDJ_FILE} not found. Run 'tdj.py --scan' first.")
        sys.exit(1)

    entries = []
    with open(TDJ_FILE, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data.get("_meta"):
                continue  # Skip metadata line
            # Convert timestamps to datetime for queries
            data['mtime_dt'] = datetime.fromtimestamp(data['mtime'])
            data['ctime_dt'] = datetime.fromtimestamp(data['ctime'])
            entries.append(data)
    return entries


def load_legacy_csv() -> List[Dict]:
    """Load from legacy CSV format for backwards compatibility."""
    import csv
    entries = []
    with open(LEGACY_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {
                'path': row['path'].replace(str(PROJECT_ROOT) + '/', ''),
                'size': int(row.get('size_bytes', 0)),
                'mtime': float(row.get('modified_epoch', 0)),
                'ctime': float(row.get('birth_epoch', 0)),
                'mtime_dt': datetime.fromisoformat(row['modified_iso']),
                'ctime_dt': datetime.fromisoformat(row['birth_iso']),
            }
            entries.append(entry)
    return entries


def cmd_recent(days: int):
    """Files created in the last N days."""
    entries = load_entries()
    cutoff = datetime.now() - timedelta(days=days)
    recent = [e for e in entries if e['ctime_dt'] > cutoff]
    recent.sort(key=lambda x: x['ctime_dt'], reverse=True)

    print(f"# Files created in last {days} day(s): {len(recent)}\n")
    for e in recent[:50]:
        print(f"{e['ctime_dt'].strftime('%Y-%m-%d')}  {e['path']}")
    if len(recent) > 50:
        print(f"\n... and {len(recent) - 50} more")


def cmd_modified(days: int):
    """Files modified in the last N days."""
    entries = load_entries()
    cutoff = datetime.now() - timedelta(days=days)
    modified = [e for e in entries if e['mtime_dt'] > cutoff]
    modified.sort(key=lambda x: x['mtime_dt'], reverse=True)

    print(f"# Files modified in last {days} day(s): {len(modified)}\n")
    for e in modified[:50]:
        print(f"{e['mtime_dt'].strftime('%Y-%m-%d')}  {e['path']}")
    if len(modified) > 50:
        print(f"\n... and {len(modified) - 50} more")


def cmd_stale(days: int):
    """Files not modified in N+ days (excluding archives)."""
    entries = load_entries()
    cutoff = datetime.now() - timedelta(days=days)

    stale = [e for e in entries
             if e['mtime_dt'] < cutoff
             and '/archive/' not in e['path']
             and '/.archive/' not in e['path']
             and '/node_modules/' not in e['path']
             and e['path'].endswith(('.py', '.md', '.json', '.ts', '.js', '.yaml', '.yml'))]
    stale.sort(key=lambda x: x['mtime_dt'])

    print(f"# Files not modified in {days}+ days (excluding archives): {len(stale)}\n")
    for e in stale[:50]:
        print(f"{e['mtime_dt'].strftime('%Y-%m-%d')}  {e['path']}")
    if len(stale) > 50:
        print(f"\n... and {len(stale) - 50} more")


def cmd_pattern(pattern: str):
    """Files matching a path pattern."""
    entries = load_entries()
    matches = [e for e in entries if pattern in e['path']]
    matches.sort(key=lambda x: x['ctime_dt'], reverse=True)

    print(f"# Files matching '{pattern}': {len(matches)}\n")
    for e in matches[:50]:
        print(f"{e['ctime_dt'].strftime('%Y-%m-%d')}  {e['path']}")
    if len(matches) > 50:
        print(f"\n... and {len(matches) - 50} more")


def cmd_summary():
    """Project timeline summary."""
    entries = load_entries()

    # Group by date
    by_date = defaultdict(int)
    for e in entries:
        by_date[e['ctime_dt'].strftime('%Y-%m-%d')] += 1

    # Find key dates
    sorted_dates = sorted(by_date.items())
    first_date = sorted_dates[0][0] if sorted_dates else "unknown"
    last_date = sorted_dates[-1][0] if sorted_dates else "unknown"
    peak_date = max(by_date.items(), key=lambda x: x[1]) if by_date else ("unknown", 0)

    # Recent activity
    week_ago = datetime.now() - timedelta(days=7)
    recent_count = len([e for e in entries if e['ctime_dt'] > week_ago])

    print("# PROJECT TIMELINE SUMMARY (TDJ)\n")
    print(f"Total files tracked: {len(entries)}")
    print(f"First file created: {first_date}")
    print(f"Most recent file: {last_date}")
    print(f"Peak activity day: {peak_date[0]} ({peak_date[1]} files)")
    print(f"Files created in last 7 days: {recent_count}")
    print(f"\n## Activity by Month:\n")

    by_month = defaultdict(int)
    for date, count in sorted_dates:
        by_month[date[:7]] += count
    for month, count in sorted(by_month.items()):
        bar = '█' * min(count // 100, 80)  # Cap bar length
        print(f"{month}: {bar} {count}")


def cmd_context():
    """Generate AI-ready XML context block."""
    entries = load_entries()

    week_ago = datetime.now() - timedelta(days=7)
    day_ago = datetime.now() - timedelta(days=1)

    recent_created = [e for e in entries if e['ctime_dt'] > week_ago]
    recent_modified = [e for e in entries if e['mtime_dt'] > day_ago]

    # Focus areas (most active directories in last 7 days)
    dir_activity = defaultdict(int)
    for e in recent_created:
        parts = e['path'].split('/')
        if len(parts) > 1:
            dir_activity['/'.join(parts[:2])] += 1

    top_dirs = sorted(dir_activity.items(), key=lambda x: x[1], reverse=True)[:5]

    # Calculate project age
    project_birth = datetime(2025, 12, 3)
    project_age = (datetime.now() - project_birth).days

    print("<!-- TDJ: TIMESTAMP DAILY JOURNAL CONTEXT -->")
    print("<temporal_index>")
    print(f"  <total_files>{len(entries)}</total_files>")
    print(f"  <project_birth>2025-12-03</project_birth>")
    print(f"  <project_age_days>{project_age}</project_age_days>")
    print(f"  <files_created_last_7_days>{len(recent_created)}</files_created_last_7_days>")
    print(f"  <files_modified_last_24h>{len(recent_modified)}</files_modified_last_24h>")
    print("  <active_areas>")
    for dir_path, count in top_dirs:
        print(f'    <area path="{dir_path}" recent_files="{count}"/>')
    print("  </active_areas>")
    print("  <recent_files>")
    for e in sorted(recent_created, key=lambda x: x['ctime_dt'], reverse=True)[:10]:
        print(f'    <file created="{e["ctime_dt"].strftime("%Y-%m-%d")}">{e["path"]}</file>')
    print("  </recent_files>")
    print("</temporal_index>")
    print("<!-- END TDJ CONTEXT -->")


# =============================================================================
# CLI
# =============================================================================

def main():
    global QUIET

    # Parse global flags
    args = sys.argv[1:]
    if "--quiet" in args:
        QUIET = True
        args.remove("--quiet")
    if "-q" in args:
        QUIET = True
        args.remove("-q")

    if len(args) < 1:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "--scan" or cmd == "scan":
        cmd_scan()
    elif cmd == "recent":
        days = int(args[1]) if len(args) > 1 else 7
        cmd_recent(days)
    elif cmd == "modified":
        days = int(args[1]) if len(args) > 1 else 1
        cmd_modified(days)
    elif cmd == "stale":
        days = int(args[1]) if len(args) > 1 else 30
        cmd_stale(days)
    elif cmd == "pattern":
        if len(args) < 2:
            print("Usage: tdj.py pattern PATTERN")
            sys.exit(1)
        cmd_pattern(args[1])
    elif cmd == "summary":
        cmd_summary()
    elif cmd == "context":
        cmd_context()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
