# Collider Pipeline Stages - Complete Specification

> **Status:** CANONICAL
> **Date:** 2026-01-23
> **Source:** Extracted from `full_analysis.py`

---

## Pipeline Overview

The Collider analysis pipeline processes codebases through **28 stages** organized into **5 phases**:

```
PHASE 1: EXTRACTION (Stages 0-2)
    What's in the code? Parse, classify, enrich.

PHASE 2: ENRICHMENT (Stages 2.5-2.11)
    Add semantic dimensions, scope, control flow, patterns.

PHASE 3: ANALYSIS (Stages 3-6.8)
    Purpose, execution flow, graph metrics, boundaries.

PHASE 4: INTELLIGENCE (Stages 7-8.6)
    Data flow, performance, constraints, Q-scores.

PHASE 5: OUTPUT (Stages 9-12)
    Roadmaps, topology, cortex, visualization.
```

---

## Phase 1: EXTRACTION

### Stage 0: Survey (Pre-Analysis Intelligence)
| Attribute | Value |
|-----------|-------|
| **File** | `survey.py` |
| **Input** | Target directory path |
| **Output** | `SurveyResult` with exclusions, estimates |
| **Function** | `run_survey()` |
| **Optional** | Yes (`--no-survey` to skip) |

**Purpose:** Define WHAT we're analyzing before HOW. Detect vendor directories, minified files, estimate complexity.

---

### Stage 1: Base Analysis
| Attribute | Value |
|-----------|-------|
| **File** | `unified_analysis.py` |
| **Input** | Target path, options |
| **Output** | `nodes[]`, `edges[]` (raw AST) |
| **Function** | `analyze_codebase()` |

**Purpose:** Parse source code into nodes (functions, classes, variables) and edges (calls, imports).

---

### Stage 2: Standard Model Enrichment
| Attribute | Value |
|-----------|-------|
| **File** | `standard_model_enricher.py` |
| **Input** | `nodes[]` |
| **Output** | `nodes[]` with `atom`, `rpbl`, `ring` |
| **Function** | `enrich_with_standard_model()` |

**Purpose:** Classify each node with its Atom ID and RPBL character profile.

---

## Phase 2: ENRICHMENT

### Stage 2.5: Ecosystem Discovery
| Attribute | Value |
|-----------|-------|
| **File** | `discovery_engine.py` |
| **Input** | `nodes[]` |
| **Output** | `nodes[]` with ecosystem-specific atoms |
| **Function** | `discover_ecosystem_unknowns()` |

**Purpose:** Detect T2 ecosystem atoms (React hooks, Django models, etc.).

---

### Stage 2.7: Dimension Classification
| Attribute | Value |
|-----------|-------|
| **File** | `dimension_classifier.py` |
| **Input** | `nodes[]` |
| **Output** | `nodes[]` with D4, D5, D7 dimensions |
| **Function** | `classify_all_dimensions()` |

**Purpose:** Assign octahedral dimension coordinates (D4:BOUNDARY, D5:STATE, D7:TIME).

---

### Stage 2.8: Scope Analysis
| Attribute | Value |
|-----------|-------|
| **File** | `scope_analyzer.py` |
| **Input** | `nodes[]` with `body_source` |
| **Output** | `nodes[]` with `scope_analysis` |
| **Functions** | `analyze_scopes()`, `find_unused_definitions()`, `find_shadowed_definitions()` |

**Purpose:** Build lexical scope graph, detect unused/shadowed definitions.

---

### Stage 2.9: Control Flow Metrics
| Attribute | Value |
|-----------|-------|
| **File** | `control_flow_analyzer.py` |
| **Input** | `nodes[]` with `body_source` |
| **Output** | `nodes[]` with `control_flow` (cyclomatic, nesting) |
| **Function** | `analyze_control_flow()` |

**Purpose:** Calculate cyclomatic complexity and nesting depth per function.

---

### Stage 2.10: Pattern Detection
| Attribute | Value |
|-----------|-------|
| **File** | `pattern_matcher.py` |
| **Input** | `nodes[]` |
| **Output** | `nodes[]` with pattern matches |
| **Class** | `PatternMatcher` |

**Purpose:** Detect T2 patterns (decorators, constructors, framework idioms).

---

### Stage 2.11: Data Flow Analysis (D6:EFFECT)
| Attribute | Value |
|-----------|-------|
| **File** | `data_flow_analyzer.py` |
| **Input** | `nodes[]` with `body_source` |
| **Output** | `nodes[]` with `d6_effect`, `purity_score` |
| **Function** | `analyze_data_flow()` |

**Purpose:** Classify D6:EFFECT dimension (PURE/READ/WRITE/MUTATE).

---

## Phase 3: ANALYSIS

### Stage 3: Purpose Field
| Attribute | Value |
|-----------|-------|
| **File** | `purpose_field.py` |
| **Input** | `nodes[]`, `edges[]` |
| **Output** | `PurposeField` with π₂ (particle purpose) |
| **Function** | `detect_purpose_field()` |

**Purpose:** Assign π₂ (particle-level purpose) from naming, signatures, context.

---

### Stage 3.5: Organelle Purpose (π₃)
| Attribute | Value |
|-----------|-------|
| **File** | `purpose_emergence.py` |
| **Input** | `nodes[]` with π₂ |
| **Output** | `nodes[]` with `organelle_purpose` |
| **Function** | `classify_containers()` |

**Purpose:** Infer π₃ from contained particles (class purpose from methods).

---

### Stage 3.6: System Purpose (π₄)
| Attribute | Value |
|-----------|-------|
| **File** | `purpose_emergence.py` |
| **Input** | `nodes[]` with π₃ |
| **Output** | `nodes[]` with `file_purpose` |
| **Function** | `classify_files()` |

**Purpose:** Infer π₄ from contained organelles (file purpose from classes).

---

### Stage 4: Execution Flow
| Attribute | Value |
|-----------|-------|
| **File** | `execution_flow.py` |
| **Input** | `nodes[]`, `edges[]`, `PurposeField` |
| **Output** | `ExecutionFlow` with entry points, orphans |
| **Function** | `detect_execution_flow()` |

**Purpose:** Trace execution paths from entry points, detect orphan code.

---

### Stage 5: Markov Transition Matrix
| Attribute | Value |
|-----------|-------|
| **File** | `full_analysis.py` (inline) |
| **Input** | `nodes[]`, `edges[]` |
| **Output** | `markov` dict with transition weights |
| **Function** | `compute_markov_matrix()` |

**Purpose:** Compute probability of transitioning between nodes.

---

### Stage 6: Knot/Cycle Detection
| Attribute | Value |
|-----------|-------|
| **File** | `full_analysis.py` (inline) |
| **Input** | `nodes[]`, `edges[]` |
| **Output** | `knots` dict with cycles, bidirectional edges |
| **Function** | `detect_knots()` |

**Purpose:** Find circular dependencies and tangled code.

---

### Stage 6.5: Graph Analytics
| Attribute | Value |
|-----------|-------|
| **File** | `graph_analyzer.py` |
| **Input** | `nodes[]`, `edges[]` |
| **Output** | `nodes[]` with degree, centrality metrics |
| **Functions** | `compute_degree_distribution()`, `compute_betweenness_centrality()`, etc. |

**Purpose:** Calculate graph theory metrics for each node.

---

### Stage 6.6: Statistical Metrics
| Attribute | Value |
|-----------|-------|
| **File** | `analytics_engine.py` |
| **Input** | `nodes[]` |
| **Output** | `stats` dict with entropy, Halstead metrics |
| **Function** | `compute_all_metrics()` |

**Purpose:** Calculate information-theoretic and Halstead complexity metrics.

---

### Stage 6.7: Semantic Purpose Analysis
| Attribute | Value |
|-----------|-------|
| **File** | `graph_framework.py`, `graph_metrics.py`, `intent_extractor.py` |
| **Input** | `nodes[]`, `edges[]` |
| **Output** | `nodes[]` with `semantic_role`, `intent_profile`, centrality metrics |
| **Functions** | `build_nx_graph()`, `classify_node_role()`, `build_node_intent_profile()` |

**Purpose:** Implement PURPOSE = f(edges) - determine code purpose through relationships, not content. Classifies nodes as utility/orchestrator/hub/leaf based on degree patterns. Extracts intent from docstrings and git commit history.

---

### Stage 6.8: Codome Boundaries
| Attribute | Value |
|-----------|-------|
| **File** | `full_analysis.py` (inline) |
| **Input** | `nodes[]`, `edges[]` |
| **Output** | `codome_result` with boundary nodes, inferred edges |
| **Function** | `create_codome_boundaries()` |

**Purpose:** Generate synthetic nodes for external callers (test frameworks, CLI, etc.).

---

## Phase 4: INTELLIGENCE

### Stage 7: Data Flow (Macro)
| Attribute | Value |
|-----------|-------|
| **File** | `full_analysis.py` (inline) |
| **Input** | `nodes[]`, `edges[]` |
| **Output** | `data_flow` dict with sources, sinks |
| **Function** | `compute_data_flow()` |

**Purpose:** Identify data sources (inputs) and sinks (outputs) at system level.

---

### Stage 8: Performance Prediction
| Attribute | Value |
|-----------|-------|
| **File** | `performance_predictor.py` |
| **Input** | `nodes[]`, `ExecutionFlow` |
| **Output** | `perf` dict with hotspots, predictions |
| **Function** | `predict_performance()` |

**Purpose:** Predict performance characteristics from static analysis.

---

### Stage 8.5: Constraint Validation
| Attribute | Value |
|-----------|-------|
| **File** | `constraint_engine.py` |
| **Input** | `nodes[]`, `edges[]` |
| **Output** | `constraint_report` with violations |
| **Class** | `ConstraintEngine` |

**Purpose:** Validate architectural constraints and detect violations.

---

### Stage 8.6: Purpose Intelligence (Q-Scores)
| Attribute | Value |
|-----------|-------|
| **File** | `purpose_intelligence.py` |
| **Input** | `nodes[]` |
| **Output** | `nodes[]` with Q-scores, intelligence metrics |
| **Function** | `enrich_nodes_with_intelligence()` |

**Purpose:** Calculate quality scores and purpose clarity metrics.

---

## Phase 5: OUTPUT

### Stage 9: Roadmap Evaluation
| Attribute | Value |
|-----------|-------|
| **File** | `roadmap_evaluator.py` |
| **Input** | Full analysis output, roadmap name |
| **Output** | `roadmap` dict with evaluation |
| **Function** | `evaluate_roadmap()` |
| **Optional** | Yes (requires `--roadmap` flag) |

**Purpose:** Evaluate codebase against a defined roadmap.

---

### Stage 10: Visual Reasoning
| Attribute | Value |
|-----------|-------|
| **File** | `topology_reasoning.py` |
| **Input** | `nodes[]`, `edges[]` |
| **Output** | `topology` classification (Star, Mesh, Islands) |
| **Class** | `TopologyClassifier` |

**Purpose:** Classify the overall graph topology shape.

---

### Stage 11: Semantic Cortex
| Attribute | Value |
|-----------|-------|
| **File** | `semantic_cortex.py` |
| **Input** | `nodes[]` |
| **Output** | `semantic` dict with concepts, themes |
| **Class** | `ConceptExtractor` |

**Purpose:** Extract semantic concepts and business domain themes.

---

### Stage 11b: AI Insights (Optional)
| Attribute | Value |
|-----------|-------|
| **File** | `full_analysis.py` (inline) |
| **Input** | Full analysis output |
| **Output** | `ai_insights` from LLM |
| **Function** | `_generate_ai_insights()` |
| **Optional** | Yes (requires `--ai-insights` flag) |

**Purpose:** Generate LLM-powered insights about the codebase.

---

### Stage 12: Output Generation
| Attribute | Value |
|-----------|-------|
| **File** | `brain_download.py`, `visualize_graph_webgl.py` |
| **Input** | All previous outputs |
| **Output** | `unified_analysis.json`, `collider_report.html`, `output.md` |
| **Functions** | `generate_output()`, `generate_visualization()` |

**Purpose:** Generate final artifacts (JSON, HTML, Markdown).

---

## Stage Dependencies

```
Stage 0  ─────────────────────────────────────────────────────────┐
Stage 1  ─┬─ Stage 2 ─┬─ Stage 2.5                               │
          │           ├─ Stage 2.7                               │
          │           ├─ Stage 2.8                               │
          │           ├─ Stage 2.9                               │
          │           ├─ Stage 2.10                              │
          │           └─ Stage 2.11                              │
          │                                                      │
          └─────────────┬─ Stage 3 ─┬─ Stage 3.5 ─── Stage 3.6  │
                        │           │                            │
                        ├─ Stage 4 ─┴────────────────────────────┤
                        │                                        │
                        ├─ Stage 5                               │
                        ├─ Stage 6                               │
                        ├─ Stage 6.5                             │
                        ├─ Stage 6.6                             │
                        └─ Stage 6.8                             │
                                                                 │
Stage 7 ────────────────────────────────────────────────────────┤
Stage 8 ────────────────────────────────────────────────────────┤
Stage 8.5 ──────────────────────────────────────────────────────┤
Stage 8.6 ──────────────────────────────────────────────────────┤
                                                                 │
Stage 9 (optional) ─────────────────────────────────────────────┤
Stage 10 ───────────────────────────────────────────────────────┤
Stage 11 ───────────────────────────────────────────────────────┤
Stage 11b (optional) ───────────────────────────────────────────┤
                                                                 │
Stage 12 ◄───────────────────────────────────────────────────────┘
```

---

## Implementation Status

| Stage | BaseStage Class | Status |
|-------|-----------------|--------|
| 0 | `SurveyStage` | IMPLEMENTED |
| 1 | `BaseAnalysisStage` | IMPLEMENTED |
| 2 | `StandardModelStage` | IMPLEMENTED |
| 2.5 | `EcosystemDiscoveryStage` | IMPLEMENTED |
| 2.7 | `DimensionClassificationStage` | IMPLEMENTED |
| 2.8 | `ScopeAnalysisStage` | IMPLEMENTED |
| 2.9 | `ControlFlowStage` | IMPLEMENTED |
| 2.10 | `PatternDetectionStage` | IMPLEMENTED |
| 2.11 | `DataFlowAnalysisStage` | IMPLEMENTED |
| 3 | `PurposeFieldStage` | IMPLEMENTED |
| 3.5 | `OrganellePurposeStage` | IMPLEMENTED |
| 3.6 | `SystemPurposeStage` | IMPLEMENTED |
| 4 | `EdgeExtractionStage` | IMPLEMENTED |
| 5 | `MarkovMatrixStage` | IMPLEMENTED |
| 6 | `KnotDetectionStage` | IMPLEMENTED |
| 6.5 | `GraphAnalyticsStage` | IMPLEMENTED |
| 6.6 | `StatisticalMetricsStage` | IMPLEMENTED |
| 6.7 | `SemanticPurposeStage` | IMPLEMENTED |
| 6.8 | `CodomeBoundaryStage` | IMPLEMENTED |
| 7 | `DataFlowMacroStage` | IMPLEMENTED |
| 8 | `PerformancePredictionStage` | IMPLEMENTED |
| 8.5 | `ConstraintValidationStage` | IMPLEMENTED |
| 8.6 | `PurposeIntelligenceStage` | IMPLEMENTED |
| 9 | `RoadmapEvaluationStage` | IMPLEMENTED |
| 10 | `TopologyReasoningStage` | IMPLEMENTED |
| 11 | `SemanticCortexStage` | IMPLEMENTED |
| 11b | `AIInsightsStage` | IMPLEMENTED |
| 12 | `OutputGenerationStage` | IMPLEMENTED |

---

## Usage

```python
from src.core.pipeline import (
    PipelineManager,
    create_default_pipeline,  # 5 core stages
    create_full_pipeline,     # All 27 stages
    STAGE_ORDER,
)
from src.core.data_management import CodebaseState

# Option 1: Create pipeline with 5 core stages (fast)
pipeline = create_default_pipeline()

# Option 2: Create full 27-stage pipeline
pipeline = create_full_pipeline(
    output_dir="/path/to/output",
    skip_ai=True,  # Skip AI insights by default
)

# Initialize state
state = CodebaseState(target_path="/path/to/repo")

# Run pipeline
final_state = pipeline.run(state)

# Access results
print(f"Nodes: {len(final_state.nodes)}")
print(f"Edges: {len(final_state.edges)}")

# Stage order is available as constant
print(f"Pipeline has {len(STAGE_ORDER)} stages")
```
