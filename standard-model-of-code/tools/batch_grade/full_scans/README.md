# Full Scans Output Directory

**Status:** EMPTY - Awaiting proper batch run
**DoD:** 999+ repos with full `collider full` output

## Expected Structure

```
full_scans/
├── YYYYMMDD_HHMMSS/              # Run timestamp
│   ├── meta.json                 # Run metadata (repos, duration, success/fail)
│   ├── repos/
│   │   ├── owner_reponame/
│   │   │   ├── unified_analysis.json    # Full analysis (5-50MB)
│   │   │   ├── collider_report.html     # Visualization
│   │   │   └── output.md                # Brain download
│   │   └── ...
│   └── summary.json              # Aggregated statistics
└── README.md
```

## Required Command

The batch script must use `collider full`, not `collider grade`:

```python
# CORRECT:
subprocess.run([
    sys.executable,
    str(COLLIDER_ROOT / "cli.py"),
    "full",
    str(repo_dir),
    "--output", str(output_dir / repo_name)
])
```

## Expected Output Per Repo

| File | Size | Contents |
|------|------|----------|
| `unified_analysis.json` | 5-50 MB | Full node/edge graph, metrics |
| `collider_report.html` | 1-5 MB | Interactive visualization |
| `output.md` | 10-100 KB | Brain download report |

## Storage Estimate

| Repos | Estimated Size |
|-------|----------------|
| 10 (proof of concept) | ~500 MB |
| 100 | ~5 GB |
| 590 (successful from grade run) | ~30 GB |
| 999 (full target) | ~50 GB |

## Traceability

- Concern: `standard-model-of-code/docs/OPEN_CONCERNS.md` (FAIL-001)
- Task: #37 in session task list
- Degraded results: `../grades_DEGRADED_summary_only/`
