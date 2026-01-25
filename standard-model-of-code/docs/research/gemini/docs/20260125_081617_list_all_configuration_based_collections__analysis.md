# Research: List ALL configuration-based collections: analysis_sets (how many sets?), prompts (how many?), seman...

> **Date:** 2026-01-25 08:16:17
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:911ddd659aba985526ae75a6ebe662429d3295102305bd317694a6465723889f`
> **Raw JSON:** `raw/20260125_081617_list_all_configuration_based_collections__analysis.json`

---

## Query

List ALL configuration-based collections: analysis_sets (how many sets?), prompts (how many?), semantic_models, research_schemas, ACI tiers. For each: name, path, item count.

---

## Response

Based on the provided codebase context, here are the configuration-based collections.

### 1. Analysis Sets
**Path:** `context-management/config/analysis_sets.yaml`
**Item Count:** 35 sets
**Description:** Defines coherent slices of the codebase for AI analysis, categorized by purpose (Core, Task, Research, Agent, etc.).

| Category | Set Names |
| :--- | :--- |
| **Data Boxes** | `archive`, `repo_docs`, `roadmap`, `docs_core`, `repo_theory`, `repo_tool`, `archeology` |
| **Micro-Sets** | `constraints`, `viz_core`, `theory`, `schema` |
| **Composed** | `pipeline`, `classifiers`, `architecture_review`, `implementation_review` |
| **Legacy** | `brain`, `body`, `viz`, `complete` |
| **Task** | `role_registry`, `tests` |
| **Research** | `research_core`, `research_tools`, `research_atoms`, `research_full`, `research_validation` |
| **Agent** | `agent_session`, `agent_kernel`, `agent_tasks`, `agent_intelligence`, `agent_specs`, `agent_full` |
| **ACI** | `aci_core`, `aci_siblings`, `aci_audit` |

### 2. Prompts
**Path:** `context-management/config/prompts.yaml`
**Item Count:** 9 items (5 templates + 4 modes)
**Description:** System prompts and templates for specialized analysis tasks.

**Analysis Templates (5):**
*   `insights`: General architecture/pattern analysis.
*   `insights_source`: Source code quality and refactoring analysis.
*   `plan_validation`: Validates implementation plans against code reality.
*   `role_validation`: Audits code against the Standard Model canonical roles.
*   `task_assessment`: Scores tasks on Factual, Alignment, Current, and Onwards dimensions.

**Execution Modes (4):**
*   `standard`: Default text output.
*   `forensic`: Requires file path/line number citations.
*   `architect`: Enforces Standard Model terminology (Atoms, Rings, Tiers).
*   `interactive`: Optimized for chat sessions.

### 3. ACI Tiers (Configuration)
**Path:** `context-management/config/aci_config.yaml`
**Item Count:** 4 defined in config
**Description:** Routing thresholds and budgets for Adaptive Context Intelligence.

1.  **instant**: Cached truths (<100ms).
2.  **rag**: File Search targeted lookups (<5s).
3.  **long_context**: Full context reasoning (<60s).
4.  **perplexity**: External web research (<30s).

*Note: The code in `tier_orchestrator.py` implements two additional logic-based tiers not present in the YAML config:*
*   *`FLASH_DEEP`: For massive context (2M tokens).*
*   *`HYBRID`: Combines Internal + External synthesis.*

### 4. Semantic Models
**Path:** `context-management/config/semantic_models.yaml`
**Item Count:** Unknown (File content not provided)
**Description:** Referenced in `analyze.py` and `HOLOGRAPHIC_SOCRATIC_LAYER.md`. Used for defining "Antimatter Laws" and semantic domain definitions for the Socratic Validator.

### 5. Research Schemas
**Path:** `context-management/config/research_schemas.yaml` (Inferred from `research_orchestrator.py`)
**Item Count:** Unknown (File content not provided)
**Description:** Referenced in `research_orchestrator.py`. Defines multi-step research plans (schemas) containing runs, strategies, and synthesis configurations for the Research Engine.

---

## Citations

_No citations provided_
