# PROJECT_elements

> The effort to find the basic constituents of computer programs.

## Identity

| Fact | Value |
|------|-------|
| Theory | Standard Model of Code |
| Tool | Collider |
| Atoms | 3,616 total (80 core + 3,536 ecosystem), 250+ ecosystems |
| Roles | 33 canonical, 29 implemented |
| Pipeline | 18 stages (see `full_analysis.py`) |

## Architecture

| Hemisphere | Path | Purpose |
|------------|------|---------|
| **Body** | `standard-model-of-code/` | Collider engine |
| **Brain** | `context-management/` | AI tools, cloud mirror |

## Agent Onboarding (START HERE)

New AI agents MUST complete initiation before working:

```bash
# Run the boot script (generates INITIATION_REPORT)
bash context-management/tools/maintenance/boot.sh
```

| Doc | Purpose |
|-----|---------|
| `context-management/docs/operations/AGENT_KERNEL.md` | Non-negotiables, session rules |
| `context-management/docs/operations/AGENT_INITIATION.md` | 4-step initiation protocol |
| `context-management/docs/agent_school/INDEX.md` | Boot checklist, report format |
| `context-management/docs/AI_USER_GUIDE.md` | Three AI roles (Librarian, Surgeon, Architect) |

## Environment Setup

```bash
# For Body work (Collider):
cd standard-model-of-code && pip install -e .

# For Brain work (AI tools):
python -m venv .tools_venv
source .tools_venv/bin/activate
pip install google-genai pyyaml
```

## Secrets (Doppler)

All secrets managed via Doppler (project: `ai-tools`, config: `dev`):

```bash
# Setup (one-time per machine)
doppler setup --project ai-tools --config dev

# Verify
doppler secrets

# Add new secret
doppler secrets set SECRET_NAME="value" --project ai-tools --config dev
```

| Secret | Purpose |
|--------|---------|
| `GEMINI_API_KEY` | File Search RAG queries |
| `ANTHROPIC_API_KEY` | Claude API (if needed) |

## Commands

| Task | Command |
|------|---------|
| Analyze codebase | `./collider full <path> --output <dir>` |
| With AI insights | `./collider full <path> --ai-insights` |
| Run tests | `cd standard-model-of-code && pytest tests/ -q` |
| AI query | `.tools_venv/bin/python context-management/tools/ai/analyze.py "<query>" --set brain` |
| **Socratic Audit** | `python context-management/tools/ai/analyze.py --verify pipeline` |
| Mirror to GCS | `python context-management/tools/archive/archive.py mirror` |
| Offload large files | `python context-management/tools/archive/archive.py offload` |

## Holographic-Socratic Layer

The **Holographic-Socratic Layer** is a 24/7 AI guardian that detects drift between documentation and implementation. It runs automatically via `PROJECT_sentinel` and stores structured intelligence to GCS.

- **Config**: `context-management/config/semantic_models.yaml`
- **Docs**: `context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md`
- **Output**: `gs://elements-archive-2026/intelligence/`


## Universal Property Binder (UPB)

The visualization intelligence layer - many-to-many binding between data and visual channels.

| Doc | Purpose |
|-----|---------|
| `standard-model-of-code/docs/specs/UNIVERSAL_PROPERTY_BINDER.md` | Architecture + ASCII diagrams |
| `standard-model-of-code/docs/specs/UPB_TASK_REGISTRY.md` | Implementation task list |
| `standard-model-of-code/docs/specs/UPB_LEGACY_SPRAWL.md` | Affected modules with confidence scores |

**Design Constraints**: Max 300 lines/module, 7 files total, ~1,140 lines (vs app.js 12K)

## File Lookup

| Need to... | Go to |
|------------|-------|
| Understand theory | `standard-model-of-code/docs/MODEL.md` |
| Understand tool | `standard-model-of-code/docs/COLLIDER.md` |
| Understand UPB | `standard-model-of-code/docs/specs/UNIVERSAL_PROPERTY_BINDER.md` |
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
| Model | `gemini-2.5-pro` |
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

## Commit Convention: AI-Native

For significant commits, structure messages as **knowledge transfer artifacts** for future AI agents:

```
<type>: <summary>

## CHANGES
| File | Description |
|------|-------------|

## API (if changed)
// Usage: MODULE.function()

## FINDING CODE
grep -r "PATTERN" path/

## TESTING
./collider full . --output .collider_report

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `docs`, `chore`

This is a **pattern**, not automation. Apply it when commits are significant.

## Hemisphere Handoff

For Body (Collider) work:
```
@standard-model-of-code/CLAUDE.md
```

For Brain (AI/Context) work:
```
@context-management/docs/AI_USER_GUIDE.md
```

## RAG Stores (File Search)

Pre-indexed stores for fast querying:

| Store | Contents |
|-------|----------|
| `collider-pipeline` | Pipeline code |
| `collider-docs` | Documentation |
| `collider-theory` | Theory files |
| `collider-schema` | Schema definitions |

Query: `.tools_venv/bin/python context-management/tools/ai/analyze.py --search "query" --store-name <store>`
