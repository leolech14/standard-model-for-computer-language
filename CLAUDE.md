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

## Wave-Particle Symmetry (Documentation Standard)

**Current:** 🥈 Silver (81/100) | **Target:** 🥇 Gold (90+)

The standard for "perfect documentation" - when every code construct has a corresponding doc, and every doc claim has code proof.

| Doc | Purpose |
|-----|---------|
| `.agent/specs/WAVE_PARTICLE_SYMMETRY.md` | Full spec, scoring rubric, tiers |
| `.agent/intelligence/WAVE_PARTICLE_BALANCE.md` | Current metrics from Collider |
| `.agent/intelligence/PRIORITY_MATRIX.md` | Action plan to reach Gold |

```
Symmetry Score = Structural(25) + Behavioral(25) + Examples(20) + References(15) + Freshness(15)
```

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
| `GEMINI_API_KEY` | Gemini AI queries (required) |
| `PERPLEXITY_API_KEY` | External research grounding |
| `ANTHROPIC_API_KEY` | Claude API (if needed) |

### Environment Variables (Full Reference)

| Variable | Purpose | Default |
|----------|---------|---------|
| `GEMINI_API_KEY` | AI Studio authentication | Required |
| `PERPLEXITY_API_KEY` | Research validation | Optional |
| `GCS_BUCKET` | Cloud storage bucket | `elements-archive-2026` |
| `PROJECT_ROOT` | Override project root path | Auto-detected |
| `CI` | Disable interactive prompts | `false` |
| `NONINTERACTIVE` | Force non-interactive mode | `false` |
| `SESSION_LOG` | Path to session log file | None |

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
| **Setup commit hooks** | `pre-commit install --hook-type commit-msg --hook-type pre-commit` |
| Analyze codebase | `./collider full <path> --output <dir>` |
| With AI insights | `./collider full <path> --ai-insights` |
| Run tests | `cd standard-model-of-code && pytest tests/ -q` |
| AI query | `.tools_venv/bin/python context-management/tools/ai/analyze.py "<query>" --set brain` |
| **Socratic Audit** | `python context-management/tools/ai/analyze.py --verify pipeline` |
| **Research Schemas** | `python analyze.py --research validation_trio "query"` |
| List schemas | `python analyze.py --list-research-schemas` |
| Mirror to GCS | `python context-management/tools/archive/archive.py mirror` |
| Offload large files | `python context-management/tools/archive/archive.py offload` |

## Background AI Processing Layer

Five autonomous engines that continuously refine, validate, and enrich the repository:

| Engine | Purpose | Trigger | Status |
|--------|---------|---------|--------|
| **BARE** | Self-refinement (truths, confidence) | Post-commit | PARTIAL |
| **AEP** | Task enrichment pipeline | Cron/Cloud | TOOLS OK |
| **HSL** | Semantic validation (Antimatter Laws) | Daily 6AM | WORKING |
| **REFINERY** | Context atomization | On-demand | PLANNED |
| **CENTRIPETAL** | Deep 12-round analysis | Manual | TOOL OK |

**Full map:** `context-management/docs/BACKGROUND_AI_LAYER_MAP.md`

### Holographic-Socratic Layer (HSL)

The 24/7 AI guardian that detects drift between documentation and implementation.

- **Config**: `context-management/config/semantic_models.yaml`
- **Docs**: `context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md`
- **Output**: `context-management/reports/socratic_audit_*.md`

### Research Schemas

Reusable patterns that orchestrate multiple ACI queries with different configurations to produce validated, multi-perspective answers.

| Schema | Purpose |
|--------|---------|
| `validation_trio` | Cross-model verification (detect hallucinations) |
| `depth_ladder` | Find optimal context size |
| `adversarial_pair` | Stress-test claims (thesis vs antithesis) |
| `forensic_investigation` | Root cause analysis |
| `quick_validate` | Fast sanity check |

- **Config**: `context-management/config/research_schemas.yaml`
- **Docs**: `context-management/docs/RESEARCH_SCHEMAS.md`
- **Engine**: `context-management/tools/ai/aci/research_orchestrator.py`

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
| Understand Research Schemas | `context-management/docs/RESEARCH_SCHEMAS.md` |
| Modify atoms | `standard-model-of-code/src/patterns/ATOMS_TIER*.yaml` |
| Modify classifier | `standard-model-of-code/src/core/atom_classifier.py` |
| Modify pipeline | `standard-model-of-code/src/core/full_analysis.py` |
| Edit visualization | `standard-model-of-code/src/core/viz/assets/*` |
| Configure AI tool | `context-management/config/analysis_sets.yaml` |
| Configure research schemas | `context-management/config/research_schemas.yaml` |
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
5. **NEVER stop without path forward** → priority matrix with confidence scores

## Handoff Protocol (MANDATORY)

Every session end MUST include:

```markdown
## Path Forward

| Priority | Next Action | Confidence | Blocker |
|----------|-------------|------------|---------|
| P0 | [Immediate action] | 95% | None |
| P1 | [High priority] | 85% | Needs X |
| P2 | [Should do] | 70% | Blocked by Y |

**Recommendation**: [What to do first based on goal]
**Risk**: [Unknowns or concerns]
```

See `context-management/docs/agent_school/DOD.md` for full template.

## Commit Convention: AI-Native (Enforced)

**All commits must follow Conventional Commits format.** This is enforced by pre-commit hooks.

```
<type>(<scope>): <subject>

[optional body with details]

Co-Authored-By: Claude <noreply@anthropic.com>
```

| Element | Required | Values |
|---------|----------|--------|
| **type** | Yes | `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert` |
| **scope** | No | `collider`, `viz`, `agent`, `aci`, `hsl`, `refinery`, `archive` |
| **subject** | Yes | Imperative, lowercase, no period |

**Config:** `.pre-commit-config.yaml`, `commitlint.config.js`

For significant commits, add structured body as **knowledge transfer artifact**:

```
feat(collider): Add topology health grading

## CHANGES
| File | Description |
|------|-------------|

## TESTING
pytest tests/ -q

Co-Authored-By: Claude <noreply@anthropic.com>
```

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
