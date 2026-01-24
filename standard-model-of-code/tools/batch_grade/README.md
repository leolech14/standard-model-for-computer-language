# Collider Batch Grade

Automated batch grading of 999 GitHub repositories to validate the Health Model.

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
│  │ RUNPOD_API_  │            │ grades/                   │   │
│  │   KEY        │            │   final_results_*.json   │   │
│  └──────────────┘            └──────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `runpod_agent.py` | Full automation: create pod, run job, download results, terminate |
| `run_batch_local.py` | Batch grading script (runs inside pod or locally) |
| `repos_999.json` | List of 999 GitHub repos to grade |
| `fetch_repos.py` | Script that generated repos_999.json |
| `deploy.sh` | Alternative: GCP Cloud Run deployment (more complex) |

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

## Output Format

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
