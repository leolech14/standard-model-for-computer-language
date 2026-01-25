# Background Services Ontology

> SMoC-native naming using the 33 canonical roles

**Date:** 2026-01-25
**Naming Source:** `standard-model-of-code/schema/fixed/roles.json`

---

## Naming Convention

**Pattern:** `{Domain}{Role}`

Where `Role` is one of the **33 canonical SMoC roles**:

| Role | Purpose |
|------|---------|
| Loader | Load data from storage/source |
| Store | Manage application state |
| Cache | Temporarily store data for performance |
| Validator | Verify data meets constraints |
| Guard | Protect access or enforce conditions |
| Parser | Parse input format to data |
| Finder | Search for data based on criteria |
| Builder | Construct complex objects step by step |
| Orchestrator | Coordinate complex workflows |

---

## Complete Mapping

| Old File | SMoC Name | Role | Domain |
|----------|-----------|------|--------|
| truth_validator.py | **FactLoader** | Loader | Fact |
| task_registry.py | **TaskStore** | Store | Task |
| boost_confidence.py | **ConfidenceValidator** | Validator | Confidence |
| hsl_daemon.py | **DriftGuard** | Guard | Drift |
| query_analyzer.py | **IntentParser** | Parser | Intent |
| semantic_matcher.py | **SemanticFinder** | Finder | Semantic |
| tier_router.py | **TierOrchestrator** | Orchestrator | Tier |
| context_optimizer.py | **ContextBuilder** | Builder | Context |
| cache_registry.py | **ContextCache** | Cache | Context |
| refinery.py (chunking) | **ChunkParser** | Parser | Chunk |
| refinery.py (ranking) | **ChunkValidator** | Validator | Chunk |
| refinery.py (indexing) | **ChunkFinder** | Finder | Chunk |
| schema_orchestrator.py | **ResearchOrchestrator** | Orchestrator | Research |
| feedback_loop.py | **FeedbackStore** | Store | Feedback |
| aep_orchestrator.py | **EnrichmentOrchestrator** | Orchestrator | Enrichment |

---

## Placement in Existing Subsystems

```
PROJECT_elements
│
├── S2: HSL (Holographic-Socratic Layer)
│   └── DriftGuard [Guard]
│
├── S3: analyze.py (AI Query Interface)
│   │
│   └── ACI Components:
│       │
│       ├── Query Understanding
│       │   ├── IntentParser [Parser]
│       │   └── SemanticFinder [Finder]
│       │
│       ├── Routing
│       │   └── TierOrchestrator [Orchestrator]
│       │
│       ├── Context Assembly
│       │   ├── ContextBuilder [Builder]
│       │   └── ContextCache [Cache]
│       │
│       ├── Chunking
│       │   ├── ChunkParser [Parser]
│       │   ├── ChunkValidator [Validator]
│       │   └── ChunkFinder [Finder]
│       │
│       └── Research
│           ├── ResearchOrchestrator [Orchestrator]
│           └── FeedbackStore [Store]
│
├── S6: BARE (Background Auto-Refinement)
│   ├── FactLoader [Loader]
│   ├── ConfidenceValidator [Validator]
│   └── TaskStore [Store]
│
└── Cross-Subsystem
    └── EnrichmentOrchestrator [Orchestrator]
```

---

## File Renaming Plan

### S6: BARE (.agent/tools/)

```
.agent/tools/
├── truth_validator.py    → fact_loader.py
├── boost_confidence.py   → confidence_validator.py
└── task_registry.py      → task_store.py
```

### S2: HSL (context-management/tools/)

```
context-management/tools/
└── hsl_daemon.py         → drift_guard.py
```

### S3: ACI (context-management/tools/ai/aci/)

```
context-management/tools/ai/aci/
├── query_analyzer.py     → intent_parser.py
├── semantic_matcher.py   → semantic_finder.py
├── tier_router.py        → tier_orchestrator.py
├── context_optimizer.py  → context_builder.py
├── cache_registry.py     → context_cache.py
├── refinery.py           → SPLIT INTO:
│   ├── chunk_parser.py
│   ├── chunk_validator.py
│   └── chunk_finder.py
├── schema_orchestrator.py → research_orchestrator.py
└── feedback_loop.py      → feedback_store.py
```

### Cross-Subsystem (.agent/tools/)

```
.agent/tools/
└── aep_orchestrator.py   → enrichment_orchestrator.py
```

---

## Acronym Retirement

| Acronym | Status | Replacement |
|---------|--------|-------------|
| BARE | RETIRED | S6 subsystem name (keep for subsystem, not components) |
| HSL | RETIRED | S2 subsystem name (keep for subsystem, not components) |
| AEP | RETIRED | EnrichmentOrchestrator |
| ACI | RETIRED | "ACI Components" (group label, not acronym) |
| REFINERY | RETIRED | ChunkParser + ChunkValidator + ChunkFinder |

---

## Why This Works

1. **Uses existing taxonomy** - The 33 roles are already defined in SMoC
2. **Self-documenting** - `DriftGuard` tells you it guards against drift
3. **Predictable** - New components follow `{Domain}{Role}` pattern
4. **Consistent** - Same naming convention as Collider codebase
5. **No metaphors** - "Guard" is a defined role, not a metaphor

---

## Migration Priority

| Priority | Files | Effort |
|:--------:|-------|--------|
| P1 | hsl_daemon.py → drift_guard.py | Low |
| P1 | aep_orchestrator.py → enrichment_orchestrator.py | Low |
| P2 | BARE tools (3 files) | Medium |
| P3 | ACI modules (8 files) | Medium |
| P4 | Split refinery.py into 3 files | High |

---

*This ontology uses SMoC's 33 canonical roles from `schema/fixed/roles.json`*
