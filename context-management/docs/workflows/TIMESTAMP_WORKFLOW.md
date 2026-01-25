# Timestamp Workflow

**Purpose:** Track chronological file creation and modification across PROJECT_elements
**Keywords:** timestamps history, timestamps record, repos chronological order, file creation and modification, temporal analysis

---

## Quick Reference

```bash
# Generate fresh timestamp CSV
python3 standard-model-of-code/scripts/generate_repo_timestamps.py

# Output: project_elements_file_timestamps.csv (root)
```

---

## Current Statistics (2026-01-23)

| Metric | Value |
|--------|-------|
| Total Files | 56,361 |
| Total Size | 4.31 GB |
| Date Range | 2025-10-07 to 2026-01-23 |
| CSV Location | `/project_elements_file_timestamps.csv` |

### Files by Top Directory

| Directory | Files |
|-----------|------:|
| standard-model-of-code | 45,105 |
| .tools_venv | 9,717 |
| archive | 935 |
| context-management | 325 |
| .agent | 157 |

### Recent Activity (Last 7 Days)

| Date | Files Created |
|------|--------------|
| 2026-01-23 | 43,187 |
| 2026-01-22 | 1,663 |
| 2026-01-21 | 2,140 |
| 2026-01-20 | 3,309 |
| 2026-01-19 | 728 |
| 2026-01-18 | 4,134 |
| 2026-01-17 | 41 |

---

## CSV Schema

```csv
path,size_bytes,birth_epoch,birth_iso,modified_epoch,modified_iso
```

| Column | Description |
|--------|-------------|
| path | Absolute file path |
| size_bytes | File size in bytes |
| birth_epoch | Unix timestamp of creation (macOS st_birthtime) |
| birth_iso | ISO 8601 creation datetime |
| modified_epoch | Unix timestamp of last modification |
| modified_iso | ISO 8601 modification datetime |

---

## Available Tools

### 1. Generate Timestamps (Primary)

```bash
python3 standard-model-of-code/scripts/generate_repo_timestamps.py [--output PATH]
```

**Location:** `standard-model-of-code/scripts/generate_repo_timestamps.py`

**Features:**
- Uses macOS `st_birthtime` for true file creation time
- Skips: `.git`, `node_modules`, `__pycache__`, `.venv`, binary files
- Output: CSV at project root (default)

### 2. Update Timestamps (Shell Wrapper)

```bash
bash context-management/tools/maintenance/update_timestamps.sh
```

### 3. Timestamps Analysis (Python)

```bash
python3 context-management/tools/maintenance/timestamps.py
```

---

## Historical Archives

| Archive | Date | Files |
|---------|------|-------|
| `archive/data/project_elements_file_timestamps_2026-01-18.csv` | 2026-01-18 | ~11,000 |

---

## Usage Patterns

### Get Files Created Today

```bash
grep "$(date +%Y-%m-%d)" project_elements_file_timestamps.csv | wc -l
```

### Get Oldest Files

```bash
sort -t',' -k3 -n project_elements_file_timestamps.csv | head -10
```

### Get Newest Files

```bash
sort -t',' -k3 -n project_elements_file_timestamps.csv | tail -10
```

### Get Files Modified After Creation

```bash
python3 << 'EOF'
import csv
count = 0
with open('project_elements_file_timestamps.csv') as f:
    for row in csv.DictReader(f):
        if row['birth_epoch'] != row['modified_epoch']:
            count += 1
print(f"Files modified after creation: {count}")
EOF
```

---

## Agent Onboarding Integration

This workflow is registered in:
- `.agent/registry/INDEX.md` (under Tools)
- `context-management/docs/operations/AGENT_KERNEL.md` (non-negotiables)
- `CLAUDE.md` (canonical sources)

### Keywords for Agent Recognition

When user requests any of these, invoke this workflow:
- "timestamps history"
- "timestamps record"
- "repos chronological order"
- "file creation and modification"
- "temporal analysis"
- "when was this file created"
- "file history"
- "project timeline"

---

## Regeneration Schedule

**Recommended:** Run `generate_repo_timestamps.py` at:
1. Start of each development session
2. Before major commits
3. Weekly for archival (save to `archive/data/`)

---

## Notes

- **43K files on 2026-01-23** - Mostly from `.repos_cache/` (calibration repos)
- **st_birthtime** - Only available on macOS; Linux falls back to st_ctime
- **Large files excluded** - Binary files and compiled outputs are skipped
