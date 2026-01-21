# PROJECT_elements - Comprehensive Onboarding Context
# Prepared for Gemini 2.5 Pro Session

## EXECUTIVE SUMMARY

PROJECT_elements is a codebase analysis framework with two hemispheres:
- **Body** (`standard-model-of-code/`): The Collider engine - 18-stage pipeline for semantic code analysis
- **Brain** (`context-management/`): AI tools, documentation, cloud sync

Key metrics:
- 200 documented atoms, 94 implemented
- 33 canonical roles, 29 implemented
- 18 pipeline stages (was incorrectly documented as 10/12)
- 6 RAG stores pre-indexed for File Search

## CRITICAL ONBOARDING PATHS

### Boot Sequence
```bash
bash context-management/tools/maintenance/boot.sh
```

### Key Documents
1. `CLAUDE.md` (root) - Identity, commands, architecture
2. `context-management/docs/operations/AGENT_KERNEL.md` - Non-negotiables
3. `context-management/docs/operations/AGENT_INITIATION.md` - 4-step protocol
4. `context-management/docs/agent_school/INDEX.md` - Boot checklist
5. `standard-model-of-code/docs/MODEL.md` - Theory
6. `standard-model-of-code/docs/COLLIDER.md` - Tool usage

## THE 18 PIPELINE STAGES

| Stage | Name | Produces |
|-------|------|----------|
| 1 | Base Analysis | AST, initial nodes |
| 2 | Standard Model | atom classification |
| 2.5 | Ecosystem Discovery | framework detection |
| 2.7 | Octahedral Dimensions | 8D vectors |
| 3 | Purpose Field | layers |
| 4 | Execution Flow | reachable_set, orphans |
| 5 | Markov Transitions | state matrix |
| 6 | Knot/Cycle Detection | cycles, knots |
| 6.5 | Graph Analytics | centrality, clustering |
| 6.6 | Statistical Metrics | distributions |
| 7 | Data Flow | data movement graph |
| 8 | Performance Prediction | hotspots |
| 8.5 | Constraint Validation | profile checks |
| 9 | Roadmap Evaluation | maturity score |
| 10 | Visual Reasoning | topology shape |
| 11 | Semantic Cortex | high-level patterns |
| 11b | AI Insights (optional) | LLM analysis |
| 12 | Consolidated Output | JSON, HTML, MD |

## ANTIMATTER LAWS (Guardrails)

| ID | Name | Description |
|----|------|-------------|
| AM001 | Context Myopia | Code that duplicates existing functionality |
| AM002 | Architectural Drift | Code that violates Role or Layer constraints |
| AM003 | Supply Chain Hallucination | Reference to non-existent dependencies |
| AM004 | Orphan Code | Code defined but never used |

## AI ROLES (From AI_USER_GUIDE.md)

1. **The Librarian** - RAG-based exploration, "Where is X?"
2. **The Surgeon** - Forensic traceability, line-level citations
3. **The Architect** - Global reasoning, theory-aware analysis
4. **The Holographic-Socratic Layer** - Continuous validation

## RAG STORES AVAILABLE

| Store | Contents |
|-------|----------|
| `collider-pipeline` | Pipeline code |
| `collider-docs` | Documentation |
| `collider-theory` | Theory files |
| `collider-schema` | Schema definitions |
| `collider-brain` | Brain hemisphere |
| `collider-classifiers` | Classification code |

## COMMANDS

```bash
# Analyze codebase
./collider full <path> --output <dir>

# AI query (Tier 1 - Long Context)
.tools_venv/bin/python context-management/tools/ai/analyze.py "<query>" --set <set>

# RAG query (Tier 2 - File Search)
.tools_venv/bin/python context-management/tools/ai/analyze.py --search "<query>" --store-name <store>

# Socratic verification (Tier 3)
.tools_venv/bin/python context-management/tools/ai/analyze.py --verify pipeline
```

## GAPS FIXED IN THIS SESSION

1. Stage count corrected: 10/12 → 18 across all docs
2. Onboarding section added to root CLAUDE.md
3. Boot script path fixed in AGENT_KERNEL.md
4. PROJECT_MAP.md restored to root
5. Cross-hemisphere links added
6. venv setup instructions added
7. RAG stores documented

## REMAINING QUESTIONS FOR GEMINI

1. Are there any remaining documentation contradictions?
2. What semantic concepts are missing from antimatter laws?
3. How can the 18-stage pipeline be optimized?
4. What additional RAG stores should be indexed?
