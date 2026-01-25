# PROJECT_elements Architecture Map

> Navigation guide for humans and AI agents.
> **Updated:** 2026-01-23 | **Registry:** v3.9.0

---

## Directory Structure

```
PROJECT_elements/
├── .agent/                    # AI Agent Infrastructure (BARE)
│   ├── hooks/                 # Git hooks (post-commit → TruthValidator)
│   ├── intelligence/          # Generated facts and insights
│   ├── registry/              # Task management (YAML + Markdown)
│   ├── specs/                 # System specifications
│   ├── tools/                 # CLI tools (task_store.py, sprint.py)
│   └── workflows/             # Workflow definitions
│
├── context-management/        # BRAIN Hemisphere - AI Tools
│   ├── config/                # YAML configs (analysis_sets, prompts)
│   ├── docs/                  # Operations documentation
│   ├── registry/              # Auto-generated REGISTRY.json
│   ├── reports/               # Generated reports
│   └── tools/                 # AI tools (analyze.py, archive.py)
│       ├── ai/                # Gemini analysis tools
│       ├── archive/           # GCS mirroring
│       ├── mcp/               # MCP servers (Perplexity)
│       └── utils/             # Shared utilities (DualFormatSaver)
│
├── standard-model-of-code/    # BODY Hemisphere - Collider Engine
│   ├── docs/                  # Theory documentation (MODEL.md)
│   │   ├── research/          # Research outputs (Perplexity, Gemini)
│   │   └── specs/             # Technical specifications
│   ├── src/                   # Source code
│   │   ├── core/              # Pipeline stages
│   │   ├── patterns/          # Atom definitions (YAML)
│   │   └── tools/             # CLI entry point (collider)
│   ├── tests/                 # pytest tests
│   └── tools/                 # Research tools
│
├── archive/                   # Historical/deprecated code
└── assets/                    # User-uploaded files (PDFs, images)
```

---

## Canonical Locations

| Purpose | Canonical Path | Notes |
|---------|----------------|-------|
| **Task Registry** | `.agent/registry/LEARNING_SYSTEM_TASK_REGISTRY.md` | Human-readable view |
| **Task YAML** | `.agent/registry/tasks/TASK-*.yaml` | Machine-readable |
| **Theory Docs** | `standard-model-of-code/docs/MODEL.md` | Core theory |
| **Collider Docs** | `standard-model-of-code/docs/COLLIDER.md` | Tool documentation |
| **AI Config** | `context-management/config/` | analysis_sets.yaml, prompts.yaml |
| **Research Outputs** | `standard-model-of-code/docs/research/` | Perplexity/, Gemini/ |
| **Atom Definitions** | `standard-model-of-code/src/patterns/ATOMS_*.yaml` | Tier 0, 1, 2 |

---

## Generated vs Source

| Type | Indicator | Examples |
|------|-----------|----------|
| **Source** | Tracked in git | `*.py`, `*.md`, `*.yaml` in src/ |
| **Generated** | In .gitignore | `.collider/`, `__pycache__/`, `*.egg-info/` |
| **Auto-updated** | Tracked but auto-modified | `REGISTRY.json`, `repo_truths.yaml` |

---

## Quick Task Lookup

| Need to... | Go to |
|------------|-------|
| Analyze codebase | `./collider full <path> --output .collider` |
| Query with AI | `python context-management/tools/ai/analyze.py --set <set> "query"` |
| Manage tasks | `python .agent/tools/task_store.py list` |
| Add new task | `python .agent/tools/task_store.py add --id N --subject "X" --score 85` |
| Run tests | `cd standard-model-of-code && pytest tests/ -q` |
| Mirror to GCS | `python context-management/tools/archive/archive.py mirror` |

---

## Particle/Wave Duality

The repository follows a **physics-inspired architecture**:

### PARTICLE (standard-model-of-code/)
**Measurement, collapse** - The Collider engine collapses the "wave function" of source code into concrete knowledge.

```bash
# Run analysis (collapse wave → particle)
./collider full /path/to/repo --output .collider

# Output: unified_analysis.json (the "particle" of knowledge)
```

### WAVE (context-management/)
**Potential, field** - AI reasoning, strategy, context engineering. Holds the field of potential.

```bash
# Query with set (explore the wave)
python context-management/tools/ai/analyze.py --set pipeline "How does X work?"

# Index for RAG
python context-management/tools/ai/analyze.py --index --set theory --store-name my-store
```

### OBSERVER (.agent/)
**Decides what to measure** - Task registry, BARE intelligence, workflow orchestration.

The Observer chooses which aspects of the Wave to collapse into Particles.

---

## BARE (Background Auto-Refinement Engine)

Autonomous processors that run on git hooks:

| Processor | Trigger | Output |
|-----------|---------|--------|
| TruthValidator | post-commit | `.agent/intelligence/truths/repo_truths.yaml` |
| ConfidenceBooster | (planned) | Boosted task scores |
| OpportunityExplorer | (planned) | Discovery inbox |

---

## Key Files for AI Agents

When starting a new session, AI agents should read:

1. `CLAUDE.md` - Project-specific instructions
2. `.agent/registry/LEARNING_SYSTEM_TASK_REGISTRY.md` - Current task state
3. `.agent/intelligence/truths/repo_truths.yaml` - Repository facts
4. `context-management/docs/operations/AGENT_KERNEL.md` - Non-negotiables

---

## Adding New Features

| Feature Type | Where to Add |
|--------------|--------------|
| New atom type | `standard-model-of-code/src/patterns/ATOMS_TIER*.yaml` |
| New analysis set | `context-management/config/analysis_sets.yaml` |
| New AI prompt | `context-management/config/prompts.yaml` |
| New research tool | `standard-model-of-code/tools/research/` |
| New agent tool | `.agent/tools/` |

---

## Related Projects

| Project | Relationship |
|---------|--------------|
| PROJECT_vector-ui | UI components extending Collider |
| PROJECT_atman | Data viz + agent orchestration |
| PROJECT_sentinel | Local automation manager |

---

*Auto-generated structure validated against codebase 2026-01-23*
