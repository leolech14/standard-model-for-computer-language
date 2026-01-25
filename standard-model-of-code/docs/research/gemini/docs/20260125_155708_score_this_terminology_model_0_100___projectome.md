# Research: Score this terminology model 0-100:

PROJECTOME = all project contents
CODOME = executable code (.py...

> **Date:** 2026-01-25 15:57:08
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:47bd2d8baf759f878ac4191245be4bbe35e2ed600087cd0d0b2145433c1bf8ae`
> **Raw JSON:** `raw/20260125_155708_score_this_terminology_model_0_100___projectome.json`

---

## Query

Score this terminology model 0-100:

PROJECTOME = all project contents
CODOME = executable code (.py, .js)
CONTEXTOME = non-executable (.md, .yaml)
DOMAINS = cross-cuts (Pipeline, Viz, Governance)

Score on: FACTUAL (matches codebase?), ALIGNMENT (serves mission?), USEFULNESS (helps AI reasoning?)

Table format please.

---

## Response

Here is the scoring analysis of the proposed terminology model based on the active codebase context.

| Dimension | Score | Analysis |
| :--- | :--- | :--- |
| **FACTUAL** | **95/100** | **Accurate Mapping.** The model precisely maps to the repository's physical state. The codebase is strictly divided into executable logic (`src`, `tools`) and semantic definitions (`docs`, `registry`, `schemas`). The "Domains" list (Pipeline, Viz, Governance) accurately reflects the active scopes defined in `KERNEL.md` (e.g., `.agent` for governance, `collider` for pipeline). |
| **ALIGNMENT** | **65/100** | **Metaphor Clash.** The project uses a **Quantum Physics** metaphor (Standard Model, Particle/Wave, Collider, Objects/Concepts). The `-OME` suffix introduces a **Biological Systems** metaphor (Genome, Proteome). While it serves the mission of identifying "constituents," it cuts across the established `Concepts` (Specs) vs `Objects` (Instances) duality defined in the Kernel. |
| **USEFULNESS** | **92/100** | **High Utility for Context Engineering.** This is superior to the current model for **Token Budgeting**. It allows the agent to instantly classify files: `CODOME` files are typically high-attention targets (Guru tier), while `CONTEXTOME` files are reference materials best suited for RAG or "Sandwiching" (Architect/Archeologist tiers). It turns abstract architecture into concrete file-handling rules. |

### Summary Recommendation
**Adopt as Operational Taxonomy.** While it clashes with the *philosophical* Physics metaphor, it is highly effective as an *operational* model for the AI agent to manage context windows and file priorities.

**Mapping to Current Architecture:**
*   **Codome** ≈ Particle (Implementation/Objects)
*   **Contextome** ≈ Wave (Specs/Concepts) + Registry Data
*   **Projectome** ≈ The Repository Root

---

## Citations

_No citations provided_
