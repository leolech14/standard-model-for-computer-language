# Background AI Data Processing Layer Map

> All autonomous AI processing in PROJECT_elements
> **Status:** PARTIAL IMPLEMENTATION | **Mapped:** 2026-01-23

---

## System Overview

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    BACKGROUND AI DATA PROCESSING LAYER                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║   ┌─────────────────────────────────────────────────────────────────────────┐ ║
║   │                         TRIGGERS                                         │ ║
║   │                                                                          │ ║
║   │   GIT COMMIT         SCHEDULED          FILE CHANGE        MANUAL       │ ║
║   │   (post-commit)      (cron/agent)       (watchpath)        (CLI)        │ ║
║   │        │                  │                  │               │          │ ║
║   └────────┼──────────────────┼──────────────────┼───────────────┼──────────┘ ║
║            │                  │                  │               │            ║
║            ▼                  ▼                  ▼               ▼            ║
║   ┌─────────────────────────────────────────────────────────────────────────┐ ║
║   │                     PROCESSING ENGINES                                   │ ║
║   │                                                                          │ ║
║   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ ║
║   │  │     BARE     │  │     AEP      │  │     HSL      │  │   COLLIDER   │ │ ║
║   │  │  Background  │  │  Autonomous  │  │  Holographic │  │    Static    │ │ ║
║   │  │    Auto-     │  │  Enrichment  │  │   Socratic   │  │   Analysis   │ │ ║
║   │  │  Refinement  │  │   Pipeline   │  │    Layer     │  │              │ │ ║
║   │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │ ║
║   └─────────┼─────────────────┼─────────────────┼─────────────────┼─────────┘ ║
║             │                 │                 │                 │           ║
║             ▼                 ▼                 ▼                 ▼           ║
║   ┌─────────────────────────────────────────────────────────────────────────┐ ║
║   │                     AI BACKENDS                                          │ ║
║   │                                                                          │ ║
║   │   GEMINI (Internal)          PERPLEXITY (External)       COLLIDER       │ ║
║   │   ├── Flash (fast)           └── Research grounding      └── AST        │ ║
║   │   ├── Pro (deep)                                             parsing    │ ║
║   │   └── Context Cache                                                      │ ║
║   └─────────────────────────────────────────────────────────────────────────┘ ║
║             │                 │                 │                 │           ║
║             ▼                 ▼                 ▼                 ▼           ║
║   ┌─────────────────────────────────────────────────────────────────────────┐ ║
║   │                     INTELLIGENCE OUTPUTS                                 │ ║
║   │                                                                          │ ║
║   │   .agent/intelligence/          context-management/reports/              │ ║
║   │   ├── truths/                   └── socratic_audit_*.md                  │ ║
║   │   ├── confidence_reports/                                                │ ║
║   │   ├── centripetal_scans/        standard-model-of-code/docs/research/   │ ║
║   │   └── *.md (metrics)            ├── perplexity/                         │ ║
║   │                                 └── gemini/                              │ ║
║   └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## The Five Engines

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE FIVE PROCESSING ENGINES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ENGINE              PURPOSE                    STATUS      TRIGGER        │
│   ──────              ───────                    ──────      ───────        │
│   BARE                Self-refinement            PARTIAL     Post-commit    │
│   AEP                 Task enrichment            TOOLS OK    Cron/Cloud     │
│   HSL                 Semantic validation        WORKING     Daily/Watch    │
│   REFINERY            Context atomization        IMPLEMENTED On-demand      │
│   CENTRIPETAL         Deep 12-round analysis     TOOL OK     Manual         │
│                                                                             │
│   Integration:                                                              │
│   REFINERY ──▶ feeds ──▶ AEP ──▶ uses ──▶ HSL ──▶ validates ──▶ BARE       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Processing Engines

### 1. BARE (Background Auto-Refinement Engine)

**Status:** PARTIAL | **Spec:** `.agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md`

```
TRIGGER: Git post-commit hook
         .agent/hooks/post-commit
         │
         ▼
┌─────────────────────────────────────────────────────┐
│                    BARE                              │
│                                                      │
│   IMPLEMENTED                     NOT YET           │
│   ───────────                     ───────           │
│   ✓ TruthValidator                ○ CrossValidator  │
│   ✓ ConfidenceBooster             ○ ConceptMapper   │
│   ✓ Discovery Inbox               ○ SelfOptimizer   │
│                                                      │
│   Output:                                            │
│   .agent/intelligence/truths/current_truths.yaml   │
│   .agent/intelligence/confidence_reports/*.json    │
│   .agent/registry/inbox/OPP-*.yaml                 │
└─────────────────────────────────────────────────────┘
```

**Tools:**
| Tool | Purpose | Command |
|------|---------|---------|
| `fact_loader.py` | Extract repo facts | `python .agent/tools/fact_loader.py` |
| `confidence_validator.py` | 4D AI scoring | `python .agent/tools/confidence_validator.py TASK-XXX` |

---

### 2. AEP (Autonomous Enrichment Pipeline)

**Status:** SPEC + TOOLS | **Spec:** `.agent/specs/AUTONOMOUS_ENRICHMENT_PIPELINE.md`

```
TRIGGER: Cron (hourly) or Cloud Function
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│                          AEP                                  │
│                                                               │
│   INBOX           ENRICHMENT         PROMOTION      ACTIVE    │
│  (OPP-*)    ───▶    ENGINE     ───▶    GATE    ───▶ (TASK-*) │
│                        │                                      │
│                        ▼                                      │
│              ┌─────────────────┐                             │
│              │  RESEARCH LOOPS │                             │
│              │  • Gemini       │                             │
│              │  • Perplexity   │                             │
│              │  • Collider     │                             │
│              └─────────────────┘                             │
│                                                               │
│   Promotion Gate:                                             │
│   A++ (95%+) → Auto-promote                                  │
│   A+  (90%+) → Auto-promote                                  │
│   A   (85%+) → Promote with review                           │
│   B   (75%+) → Hold for enrichment                           │
│   C/F (<75%) → Defer/Reject                                  │
└──────────────────────────────────────────────────────────────┘
```

**Tools:**
| Tool | Purpose | Command |
|------|---------|---------|
| `enrichment_orchestrator.py` | Full pipeline orchestration | `python .agent/tools/enrichment_orchestrator.py` |
| `triage_inbox.py` | Score opportunities | `python .agent/tools/triage_inbox.py --score` |
| `confidence_validator.py` | 4D AI assessment | `python .agent/tools/confidence_validator.py --all` |
| `batch_promote.py` | Bulk promotion | `python .agent/tools/batch_promote.py --threshold 85` |
| `promote_opportunity.py` | Single promotion | `python .agent/tools/promote_opportunity.py OPP-XXX` |
| `add_task_steps.py` | Map task steps | `python .agent/tools/add_task_steps.py TASK-XXX` |

---

### 3. HSL (Holographic-Socratic Layer)

**Status:** IMPLEMENTED | **Spec:** `context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md`

```
TRIGGER: Daily 6AM + File watchpath + Manual
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│                          HSL                                │
│                                                             │
│   semantic_models.yaml (Antimatter Laws)                    │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              SocraticValidator                       │  │
│   │                                                      │  │
│   │   For each domain:                                   │  │
│   │   1. Load antimatter laws                           │  │
│   │   2. Query Gemini with codebase context             │  │
│   │   3. Detect violations                              │  │
│   │   4. Update reports                                 │  │
│   └─────────────────────────────────────────────────────┘  │
│            │                                                │
│            ▼                                                │
│   Violations Detected:                                      │
│   • AM001: Context Myopia                                  │
│   • AM002: Architectural Drift                             │
│   • AM003: Supply Chain Hallucination                      │
│                                                             │
│   Output: context-management/reports/socratic_audit_*.md   │
└────────────────────────────────────────────────────────────┘
```

**Antimatter Laws (Violations Detected):**
| ID | Name | Description | Severity |
|----|------|-------------|----------|
| AM001 | Context Myopia | Missing imports/definitions | HIGH |
| AM002 | Architectural Drift | Layer boundary violations | CRITICAL |
| AM003 | Supply Chain Hallucination | Phantom package imports | HIGH |

**Automation:**
| Component | Status | Details |
|-----------|--------|---------|
| LaunchAgent | CONFIGURED | `com.elements.socratic-audit` |
| Daily Schedule | ACTIVE | 6:00 AM |
| File Watchpath | PARTIAL | `semantic_models.yaml`, `src/core/` |
| Throttle | 5 min | Debounce during active editing |

**Tools:**
| Tool | Purpose | Command |
|------|---------|---------|
| `analyze.py --verify` | Run domain audit | `python context-management/tools/ai/analyze.py --verify pipeline` |
| `analyze.py --verify --candidate` | Audit specific file | `...--verify pipeline --candidate path/to/file.py` |

**Key Files:**
| File | Purpose |
|------|---------|
| `semantic_models.yaml` | Antimatter Laws + Domain definitions |
| `socratic_audit_latest.md` | Living output report |
| `com.elements.socratic-audit.plist` | LaunchAgent config |

---

### 4. REFINERY (Context Refinery)

**Status:** IMPLEMENTED | **Tool:** `context-management/tools/ai/aci/refinery.py`

```
TRIGGER: On-demand / CLI
         │
         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         CONTEXT REFINERY                                    │
│                                                                             │
│   "Break large context into semantic units, score relevance,               │
│    cache for efficient retrieval."                                          │
│                                                                             │
│   CHUNKERS:                                                                 │
│   ├── PythonChunker:   class/function/imports extraction                   │
│   ├── MarkdownChunker: header-based section splitting                      │
│   ├── YamlChunker:     top-level key blocks                                │
│   └── GenericChunker:  paragraph-based fallback                            │
│                                                                             │
│   SCORING:                                                                  │
│   ├── Type weights (class > function > imports)                            │
│   ├── Length bonus (logarithmic, caps at ~1000 chars)                      │
│   ├── Docstring bonus (+0.1)                                               │
│   └── Type hint bonus (+0.05)                                              │
│                                                                             │
│   OUTPUT:                                                                   │
│   └── RefineryNode: (content, source_file, chunk_id, chunk_type,          │
│                      relevance_score, start_line, end_line, metadata)      │
│                                                                             │
│   Output: .agent/intelligence/chunks/*.json                                │
└────────────────────────────────────────────────────────────────────────────┘
```

**Components:**
| Component | Purpose | Status |
|-----------|---------|--------|
| RefineryNode | Atomic chunk dataclass | DONE |
| PythonChunker | Class/function extraction | DONE |
| MarkdownChunker | Header-based sections | DONE |
| YamlChunker | Top-level key blocks | DONE |
| Relevance scoring | Type/length/docstring heuristics | DONE |
| JSON export | Chunk registry output | DONE |
| ACI integration | Exported via aci/__init__.py | DONE |

**Future Enhancements (Gemini Validated):**
| Gap | Severity | Recommendation |
|-----|----------|----------------|
| Vector embeddings | HIGH | Add Sentence Transformers for semantic scoring |
| Cross-chunk awareness | HIGH | Graph traversals for dependencies |
| Context positioning | MEDIUM | U-shaped attention optimization |
| Chunk size limits | MEDIUM | Token budget enforcement |

**Tools:**
| Tool | Purpose | Command |
|------|---------|---------|
| `refinery.py` | CLI for atomization | `python context-management/tools/ai/aci/refinery.py <file_or_dir>` |
| `refinery.py --export` | Export chunks | `python ...refinery.py src/ --export chunks.json` |

**Why It Matters:**
- Enables AEP to have pre-atomized context
- Reduces token cost (only send relevant atoms)
- Enables Gemini context caching (same atoms = cache hit)

---

### 5. Centripetal Scan (Deep Analysis)

**Status:** IMPLEMENTED | **Tool:** `.agent/tools/centripetal_scan.py`

```
TRIGGER: Manual (API quota required)
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│                   CENTRIPETAL SCAN                          │
│            12-Round Progressive Resolution                  │
│                                                             │
│   EXTERNAL (MACRO) ───────────────▶ INTERNAL (NANO)        │
│                                                             │
│   Round 1-3:  MACRO  │ Directories, realms, entry points   │
│   Round 4-6:  MESO   │ Modules, data flow, integration     │
│   Round 7-9:  MICRO  │ Core files, configs, patterns       │
│   Round 10-12: NANO  │ Invariants, edge cases, synthesis   │
│                                                             │
│   Each round:                                               │
│   1. EXTERNAL query (Perplexity) → World knowledge         │
│   2. INTERNAL query (Gemini) → Codebase knowledge          │
│   3. SYNTHESIS → Reconcile external vs internal            │
│                                                             │
│   Output: .agent/intelligence/centripetal_scans/           │
└────────────────────────────────────────────────────────────┘
```

---

## Trigger Matrix

| Trigger | Frequency | Engines Activated | Output |
|---------|-----------|-------------------|--------|
| **Git commit** | Every commit | BARE (TruthValidator) | `truths/`, GCS mirror |
| **Cron hourly** | Every hour | AEP (orchestrator) | Promoted tasks |
| **Daily 6AM** | Once/day | HSL (Socratic audit) | `socratic_audit_*.md` |
| **File change** | On save | HSL (watchpath) | Debounced audit |
| **Manual** | On demand | Any | Varies |

---

## Data Flow

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW                                        │
│                                                                            │
│   RAW INPUTS                    PROCESSING                   OUTPUTS       │
│   ──────────                    ──────────                   ───────       │
│                                                                            │
│   Source Code  ──────┐                                                     │
│                      │    ┌─────────────┐    ┌─────────────────────────┐  │
│   Git History  ──────┼───▶│  COLLIDER   │───▶│ unified_analysis.json   │  │
│                      │    └─────────────┘    └─────────────────────────┘  │
│   Config Files ──────┘                                 │                   │
│                                                        ▼                   │
│                           ┌─────────────┐    ┌─────────────────────────┐  │
│   OPP-*.yaml  ───────────▶│    AEP      │───▶│ TASK-*.yaml (validated) │  │
│   (raw ideas)             └─────────────┘    └─────────────────────────┘  │
│                                    │                                       │
│                                    ▼                                       │
│                           ┌─────────────┐    ┌─────────────────────────┐  │
│   Codebase    ───────────▶│    HSL      │───▶│ socratic_audit_*.md     │  │
│   semantic_models.yaml    └─────────────┘    │ (violations detected)   │  │
│                                              └─────────────────────────┘  │
│                                                                            │
│                           ┌─────────────┐    ┌─────────────────────────┐  │
│   Git commit  ───────────▶│   BARE      │───▶│ truths/                 │  │
│                           └─────────────┘    │ confidence_reports/     │  │
│                                              └─────────────────────────┘  │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## AI Backend Matrix

| Backend | Type | Use Case | Cost | Speed |
|---------|------|----------|------|-------|
| **Gemini Flash** | Internal | Fast queries, triage | Low | Fast |
| **Gemini Pro** | Internal | Deep reasoning, synthesis | Medium | Medium |
| **Gemini Context Cache** | Internal | Repeated queries same context | Low | Fast |
| **Perplexity** | External | Research grounding, citations | Medium | Medium |
| **Collider** | Static | AST parsing, structure extraction | Free | Fast |
| **Research Schemas** | Orchestration | Multi-query validation, consensus | Varies | Medium |

**Research Schemas** orchestrate multiple queries across backends to produce validated answers:
- `validation_trio`: Cross-model verification (detect hallucinations)
- `depth_ladder`: Find optimal context size
- `adversarial_pair`: Stress-test claims (thesis vs antithesis)

Docs: `context-management/docs/RESEARCH_SCHEMAS.md`
Engine: `context-management/tools/ai/aci/research_orchestrator.py`

---

## Tool Inventory (23 total)

### Core Pipeline Tools
| Tool | Purpose | Trigger |
|------|---------|---------|
| `enrichment_orchestrator.py` | Chain all enrichment tools | Cron/manual |
| `triage_inbox.py` | Score and dedupe OPPs | Enrichment step 1 |
| `confidence_validator.py` | 4D AI assessment | Enrichment step 2 |
| `batch_promote.py` | Bulk promotion | AEP step 3 |
| `promote_opportunity.py` | Single OPP → TASK | Manual |
| `add_task_steps.py` | Map task substeps | Post-promotion |

### Analysis Tools
| Tool | Purpose | Trigger |
|------|---------|---------|
| `centripetal_scan.py` | 12-round deep analysis | Manual |
| `fact_loader.py` | Extract repo facts | Post-commit |
| `wave_particle_balance.py` | Realm metrics | Manual |
| `industrial_triage.py` | Batch assessment | Manual |

### Registry Tools
| Tool | Purpose | Trigger |
|------|---------|---------|
| `task_store.py` | CRUD for tasks | Manual |
| `sprint.py` | Sprint management | Manual |
| `deal_cards.py` | Task card generation | Manual |
| `update_task_hierarchy.py` | Parent/child links | Manual |

### Cloud Tools
| Tool | Purpose | Trigger |
|------|---------|---------|
| `cloud/sync_registry.py` | GCS sync | Cron |
| `cloud/auto_boost_function.py` | Cloud Function entry | Cloud trigger |

---

## Implementation Status

```
╔════════════════════════════════════════════════════════════════╗
║                    IMPLEMENTATION STATUS                        ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║   ENGINE          COMPONENTS          STATUS                    ║
║   ──────          ──────────          ──────                    ║
║                                                                 ║
║   BARE            TruthValidator      ██████████░░  80%        ║
║                   ConfidenceBooster   ██████████░░  80%        ║
║                   CrossValidator      ░░░░░░░░░░░░   0%        ║
║                   ConceptMapper       ░░░░░░░░░░░░   0%        ║
║                                                                 ║
║   AEP             Orchestrator        ████████████ 100%        ║
║                   Triage              ████████████ 100%        ║
║                   Promotion           ████████████ 100%        ║
║                   Cloud Deploy        ░░░░░░░░░░░░   0%        ║
║                                                                 ║
║   HSL             SocraticValidator   ████████████ 100%        ║
║                   Antimatter Laws     ██████████░░  80%        ║
║                   Auto-triggers       ██████░░░░░░  50%        ║
║                                                                 ║
║   CENTRIPETAL     Scan Tool           ████████████ 100%        ║
║                   Full Run            ░░░░░░░░░░░░   0%        ║
║                   (blocked by quota)                            ║
║                                                                 ║
║   REFINERY        Chunkers            ████████████ 100%        ║
║                   Relevance Scoring   ████████████ 100%        ║
║                   Vector Embeddings   ░░░░░░░░░░░░   0%        ║
║                                                                 ║
║   OVERALL         ████████████░░░░░░  ~70%                     ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
```

---

## Next Steps

| Priority | Action | Engine | Blocked By |
|:--------:|--------|--------|------------|
| P1 | Run full centripetal scan | Centripetal | API quota |
| P2 | Deploy AEP to Cloud Function | AEP | GCP setup |
| P3 | Enable HSL auto-triggers | HSL | Sentinel config |
| P4 | Implement CrossValidator | BARE | Design decision |
| P5 | Implement ConceptMapper | BARE | Research needed |

---

## Quick Start Examples

### Run the Full Enrichment Pipeline

```bash
# Dry run first (see what would happen)
python .agent/tools/enrichment_orchestrator.py --dry-run

# Run full pipeline (triage → boost → promote)
python .agent/tools/enrichment_orchestrator.py
```

### Run HSL Audit

```bash
# Audit the pipeline domain
python context-management/tools/ai/analyze.py --verify pipeline

# Audit a specific file
python context-management/tools/ai/analyze.py --verify pipeline \
    --candidate standard-model-of-code/src/core/full_analysis.py
```

### Check Wave-Particle Balance

```bash
# Quick balance check (uses existing analysis)
python .agent/tools/wave_particle_balance.py

# Full analysis with Collider
python .agent/tools/wave_particle_balance.py --run-collider

# JSON output for tooling
python .agent/tools/wave_particle_balance.py --json
```

### Run Centripetal Scan

```bash
# Requires API quota - 12 rounds of deep analysis
doppler run -- python .agent/tools/centripetal_scan.py
```

### Manual BARE Operations

```bash
# Update repository truths
python .agent/tools/fact_loader.py

# Boost a specific task's confidence
python .agent/tools/confidence_validator.py TASK-007

# Boost all tasks needing attention
python .agent/tools/confidence_validator.py --all
```

---

## Related Documents

| Doc | Purpose |
|-----|---------|
| `.agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md` | BARE spec |
| `.agent/specs/AUTONOMOUS_ENRICHMENT_PIPELINE.md` | AEP spec |
| `context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md` | HSL spec |
| `context-management/docs/RESEARCH_SCHEMAS.md` | Research Schema orchestration |
| `.agent/SUBSYSTEM_INTEGRATION.md` | Integration map |
| `ARCHITECTURE_MAP.md` | Full architecture |

---

*Generated from codebase analysis 2026-01-23*
