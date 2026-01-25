# Collider Batch Grade

> **STATUS: FAIL-001** - First run captured grades only, not full scans.
> See `docs/OPEN_CONCERNS.md` for details.

Automated batch analysis of 999+ GitHub repositories to validate the Health Model.

## Current State (2026-01-25)

| Directory | Status | Contents |
|-----------|--------|----------|
| `grades_DEGRADED_summary_only/` | DEGRADED | 590 grade summaries (no full analysis) |
| `full_scans/` | EMPTY | Awaiting proper `collider full` run |

**DoD:** 999+ repos with full `unified_analysis.json` output per repo.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     BATCH GRADE SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LOCAL                        CLOUD                          │
│  ┌──────────────┐            ┌──────────────────────────┐   │
│  │ runpod_agent │────API────▶│ RunPod GPU/CPU Pod       │   │
│  │   .py        │            │  ├─ collider clone       │   │
│  │              │◀───SSH─────│  ├─ run_batch_local.py   │   │
│  │              │            │  └─ results/*.json       │   │
│  └──────────────┘            └──────────────────────────┘   │
│        │                                │                    │
│        │ Doppler                        │ GCS/Download       │
│        ▼                                ▼                    │
│  ┌──────────────┐            ┌──────────────────────────┐   │
│  │ RUNPOD_API_  │            │ full_scans/               │   │
│  │   KEY        │            │   unified_analysis.json   │   │
│  └──────────────┘            └──────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `runpod_agent.py` | Full automation: create pod, run job, download results, terminate |
| `run_batch_local.py` | Batch grading script (runs inside pod or locally) |
| `analyze_results.py` | **Results analyzer** - statistics, golden repos, markdown/JSON reports |
| `repos_999.json` | List of 999 GitHub repos to grade |
| `fetch_repos.py` | Script that generated repos_999.json |
| `deploy.sh` | Alternative: GCP Cloud Run deployment (more complex) |

## Analyzing Results

After a batch run, analyze the results:

```bash
# Generate markdown report
python analyze_results.py grades_DEGRADED_summary_only/20260124_224604/final_results_20260125_005603.json

# Save to file
python analyze_results.py <results.json> --output report.md

# JSON output (for programmatic use)
python analyze_results.py <results.json> --format json

# Library usage
from analyze_results import BatchAnalyzer
analyzer = BatchAnalyzer.from_file("final_results.json")
print(analyzer.grade_distribution)       # {'B': 10, 'C': 398, 'D': 178, 'F': 4}
print(analyzer.golden_repos(10, "B"))    # Top 10 Grade B repos by health
print(analyzer.component_variance())     # Which metrics differentiate grades
```

## Quick Start (RunPod - Recommended)

### Prerequisites

```bash
# Doppler credentials (one-time setup)
doppler setup --project ai-tools --config dev

# Python dependencies
source .tools_venv/bin/activate
pip install runpod paramiko
```

### Commands

```bash
# Check status of any running pods
doppler run --project ai-tools --config dev -- \
    .tools_venv/bin/python standard-model-of-code/tools/batch_grade/runpod_agent.py status

# Test run (10 repos only)
doppler run --project ai-tools --config dev -- \
    .tools_venv/bin/python standard-model-of-code/tools/batch_grade/runpod_agent.py run --limit 10

# Full run (999 repos)
doppler run --project ai-tools --config dev -- \
    .tools_venv/bin/python standard-model-of-code/tools/batch_grade/runpod_agent.py run

# Emergency: terminate all pods
doppler run --project ai-tools --config dev -- \
    .tools_venv/bin/python standard-model-of-code/tools/batch_grade/runpod_agent.py terminate-all
```

## Cost Estimate

| Provider | Config | Time | Cost |
|----------|--------|------|------|
| **RunPod RTX 4090** | 16 vCPU, 32 workers | ~30 min | **~$0.17** |
| Cloud Run Jobs | 20 tasks × 4 vCPU | ~30 min | ~$1-2 |
| Local MacBook | 8 workers | ~8 hrs | $0 (but slow) |

## Output Modes

### REQUIRED: Full Analysis (`collider full`)

**Use this for DoD compliance.**

```python
# CORRECT - produces full unified_analysis.json per repo
subprocess.run([
    sys.executable, str(COLLIDER_ROOT / "cli.py"),
    "full", str(repo_dir), "--output", str(output_dir / repo_name)
])
```

Output per repo:
- `unified_analysis.json` (5-50MB) - Full node/edge graph
- `collider_report.html` (1-5MB) - Interactive visualization
- `output.md` (10-100KB) - Brain download

### DEGRADED: Grade Only (`collider grade`)

**WARNING: This was used in the first run. DO NOT use for DoD.**

```python
# WRONG - only produces summary, no unified_analysis.json
subprocess.run([
    sys.executable, str(COLLIDER_ROOT / "cli.py"),
    "grade", str(repo_dir), "--json"
])
```

Output: ~500 bytes JSON summary only.

### Grade Summary Format (DEGRADED)

```json
{
  "meta": {
    "timestamp": "20260124_160000",
    "total_repos": 999,
    "processed": 999,
    "success": 850,
    "failed": 149,
    "duration_sec": 1800,
    "rate_per_hour": 1998
  },
  "grade_distribution": {
    "A": 45,
    "B": 120,
    "C": 280,
    "D": 350,
    "F": 55,
    "FAIL": 149
  },
  "results": [
    {
      "name": "freeCodeCamp/freeCodeCamp",
      "grade": "C",
      "health_index": 5.73,
      "component_scores": {
        "topology": 6.2,
        "elevation": 5.1,
        "gradients": 5.8,
        "alignment": 5.9
      }
    }
  ]
}
```

## Credentials

All secrets stored in Doppler (`ai-tools/dev`):

| Secret | Purpose |
|--------|---------|
| `RUNPOD_API_KEY` | RunPod API access |
| `GITHUB_TOKEN` | (Optional) Higher rate limits for cloning |

## Troubleshooting

### Pod won't start
- Check RunPod balance: https://www.runpod.io/console/user/billing
- Check GPU availability in region

### SSH connection fails
- Ensure SSH key exists: `ls ~/.ssh/id_ed25519*`
- Agent auto-generates if missing

### Clone rate limiting
- Some repos may fail due to GitHub rate limits
- Results include `clone_failed` status for these

## Integration Points

This tool validates the **Health Model** (H = T + E + Gd + A) defined in:
- `docs/specs/HEALTH_MODEL_CONSOLIDATED.md`
- `src/core/topology_reasoning.py` (LandscapeHealthIndex)

Results feed into:
- Golden repo selection for regression tests
- Health formula calibration
- Statistical validation of grading distribution

## Traceability

| Reference | Location |
|-----------|----------|
| Concern tracker | `standard-model-of-code/docs/OPEN_CONCERNS.md` (FAIL-001) |
| Subsystem registry | `.agent/SUBSYSTEM_INTEGRATION.md` (S11) |
| Degraded results | `grades_DEGRADED_summary_only/DEGRADED.md` |
| Full scans target | `full_scans/README.md` |
| Task | #37 in session task list |
