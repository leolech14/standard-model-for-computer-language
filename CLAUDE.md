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

## Architecture (Particle/Wave Duality)

| Realm | Path | Physics | Purpose |
|--------|------|---------|---------|
| **Particle** | `standard-model-of-code/` | Measurement, collapse | Collider engine, concrete analysis |
| **Wave** | `context-management/` | Potential, field | AI tools, planning, research |
| **Observer** | `.agent/` | Decides what to measure | Task registry, BARE, intelligence |

> The Collider collapses the "wave function" of source code into a **particle** of knowledge (`unified_analysis.json`).
> The Wave domain holds the **field of potential** — AI reasoning, strategy, context.

**Full integration map:** `.agent/SUBSYSTEM_INTEGRATION.md`

## Roadmap (Single Source of Truth)

**`.agent/ROADMAP.yaml`** - The unified, machine-readable roadmap for the entire project.

| What | Where |
|------|-------|
| **Roadmap** | `.agent/ROADMAP.yaml` |
| **Task Batches** | `.agent/registry/batches/` |
| **Active Tasks** | `.agent/registry/active/` |
| **Opportunities** | `.agent/registry/inbox/` |
| **Registry Index** | `.agent/registry/INDEX.md` |

**Current Focus:** Phase 3 (Reachability) + Phase 10 (Survey/Intelligence Layer)

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
# For Particle work (Collider engine):
cd standard-model-of-code && pip install -e .

# For Wave work (AI tools, planning):
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

## Research Rules (Non-Negotiable)

**Perplexity Research:** ALWAYS save outputs to `standard-model-of-code/docs/research/perplexity/`

```bash
# Filename format
YYYYMMDD_HHMMSS_topic_slug.md

# Example
20260122_143000_context_window_utilization.md
```

After ANY Perplexity query (MCP or otherwise), immediately save the response using the Write tool. Include:
- Query text
- Full response
- Citations
- Date/model used

**Gemini Research:** Save significant findings to `standard-model-of-code/docs/research/`

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

## AI Config

| Setting | Value |
|---------|-------|
| Model | `gemini-3-pro-preview` |
| Backend | AI Studio (default) or Vertex AI |
| Project | `elements-archive-2026` |
| Bucket | `gs://elements-archive-2026/` |
| Account | `leonardolech3@gmail.com` |

## Archive

| Tier | Location | Purpose |
|------|----------|---------|
| Local | `archive/` | Staging, legacy code |
| Offshore | `gs://elements-archive-2026/` | GCS backup |

## Rules

1. Always regenerate HTML: `./collider full . --output .collider`
2. Run tests before commit
3. Know which realm you're in (Particle/Wave/Observer)
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

## Domain Handoff

For **Particle** work (Collider, analysis):
```
@standard-model-of-code/CLAUDE.md
```

For **Wave** work (AI, planning, research):
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
