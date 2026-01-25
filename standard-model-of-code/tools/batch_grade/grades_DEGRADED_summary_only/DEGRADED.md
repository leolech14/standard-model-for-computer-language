# DEGRADED OUTPUT - Summary Only

**Status:** FAIL-001
**Date:** 2026-01-24
**Concern Tracker:** `standard-model-of-code/docs/OPEN_CONCERNS.md`

## What This Directory Contains

590 successful `collider grade` summaries from 999 attempted repos.

**Data captured:**
- grade (A-F)
- health_index (0-10)
- component_scores (cycles, elevation, gradients, coupling, isolation)
- node/edge counts

## What This Directory Does NOT Contain

- `unified_analysis.json` per repo
- topology_shape
- dead_code_pct
- layer_distribution
- role_distribution
- Full graph data

## Why This Is Degraded

The batch script used `collider grade --json` instead of `collider full --output`.

**Root cause:** `run_batch_local.py:89`
```python
# WRONG (what was used):
[sys.executable, str(COLLIDER_ROOT / "cli.py"), "grade", str(repo_dir), "--json"]

# CORRECT (what should have been used):
[sys.executable, str(COLLIDER_ROOT / "cli.py"), "full", str(repo_dir), "--output", str(output_dir)]
```

## Still Useful For

- Identifying top-performing repos (Grade B candidates)
- Grade distribution statistics
- Health index validation (limited)

## Top 10 Healthiest (Grade B)

| Health | Repo |
|--------|------|
| 8.29 | mingrammer/diagrams |
| 8.17 | resume/resume.github.com |
| 8.17 | jashkenas/backbone |
| 8.12 | VincentGarreau/particles.js |
| 8.08 | vinta/awesome-python |
| 8.08 | maboloshi/github-chinese |
| 8.05 | helm/charts |
| 8.04 | jamiebuilds/the-super-tiny-compiler |
| 8.04 | samber/lo |
| 8.02 | JakeChampion/fetch |

## Path Forward

Full scans should go to: `../full_scans/`

See Task #37 in session task list.
