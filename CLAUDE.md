# PROJECT_elements

> The effort to find the basic constituents of computer programs.

## Identity

| Fact | Value |
|------|-------|
| Theory | Standard Model of Code |
| Tool | Collider |
| Atoms | 200 documented, 94 implemented, 600+ ecosystem potential |
| Roles | 33 canonical, 29 implemented |
| Pipeline | 12 stages |

## Architecture

| Hemisphere | Path | Purpose |
|------------|------|---------|
| **Body** | `standard-model-of-code/` | Collider engine |
| **Brain** | `context-management/` | AI tools, cloud mirror |

## Commands

| Task | Command |
|------|---------|
| Analyze codebase | `./collider full <path> --output <dir>` |
| With AI insights | `./collider full <path> --ai-insights` |
| Run tests | `cd standard-model-of-code && pytest tests/ -q` |
| AI query | `.tools_venv/bin/python context-management/tools/ai/analyze.py "<query>" --set brain_core` |
| Mirror to GCS | `python context-management/tools/archive/archive.py mirror` |
| Offload large files | `python context-management/tools/archive/archive.py offload` |

## File Lookup

| Need to... | Go to |
|------------|-------|
| Understand theory | `standard-model-of-code/docs/MODEL.md` |
| Understand tool | `standard-model-of-code/docs/COLLIDER.md` |
| Modify atoms | `standard-model-of-code/src/patterns/ATOMS_TIER*.yaml` |
| Modify classifier | `standard-model-of-code/src/core/atom_classifier.py` |
| Modify pipeline | `standard-model-of-code/src/core/full_analysis.py` |
| Edit visualization | `standard-model-of-code/src/core/viz/assets/*` |
| Configure AI tool | `context-management/config/analysis_sets.yaml` |
| Configure archive | `context-management/tools/archive/config.yaml` |

## GCP Config

| Setting | Value |
|---------|-------|
| Project | `elements-archive-2026` |
| Bucket | `gs://elements-archive-2026/` |
| Model | `gemini-2.0-flash-001` |
| Account | `leonardolech3@gmail.com` |

## Archive

| Tier | Location | Purpose |
|------|----------|---------|
| Local | `archive/` | Staging, legacy code |
| Offshore | `gs://elements-archive-2026/` | GCS backup |

## Rules

1. Always regenerate HTML: `./collider full . --output .collider`
2. Run tests before commit
3. Know which hemisphere you're in
4. Large outputs → offload to GCS

## Hemisphere Handoff

For Body (Collider) work:
```
@standard-model-of-code/CLAUDE.md
```
