# Research: where is the Stone Tool Principle documented and how does it integrate with TOOLOME

> **Date:** 2026-01-26 23:29:08
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:394cc413b487432ec6a2fcfd78427ec1f92b93c68c8a38841a574964c3e1ff7b`
> **Raw JSON:** `raw/20260126_232908_where_is_the_stone_tool_principle_documented_and_h.json`

---

## Query

where is the Stone Tool Principle documented and how does it integrate with TOOLOME

---

## Response

Based on the provided codebase context, here is the documentation location and integration logic for the Stone Tool Principle.

### 1. Location of Documentation

The **Stone Tool Principle** (formally **Axiom H4**) is primarily documented in two locations:

*   **Primary Definition:** `context-management/docs/CODESPACE_ALGEBRA.md`
    *   **Section:** 15. CONSUMER CLASSES (AI-Native)
    *   **Key Text:** "AXIOM H4 (Ergonomics Shift): Tools MAY be designed that humans cannot directly use."

*   **Glossary Definition:** `context-management/docs/GLOSSARY.md`
    *   **Section:** CONSUMER CLASSES (Axiom Group H)
    *   **Key Text:** "Stone Tool Test: 'Can a human use this tool directly, without AI mediation?' If NO → AI-native tool (valid design)."

*   **Reference Specs:** The glossary also points to `docs/specs/AI_CONSUMER_CLASS.md` and `docs/deep/THEORY_AMENDMENT_2026-01.md` for full specifications.

### 2. The Principle

The principle asserts that in an AI-native era, **ergonomics shift from human hands to AI "hands."**
*   **Human Hand:** Needs grip, balance, visual UI, natural language (L1).
*   **AI "Hand":** Needs structured data, parseability, high information density (L0, L2).

A "Stone Tool" is a tool intentionally designed to be difficult for humans to use directly but highly optimized for AI agents (e.g., `unified_analysis.json` or complex YAML manifests).

### 3. Integration with TOOLOME

The **TOOLOME** and **STONE_TOOLS** form a partition of the total tool universe (Taxonomy defined in `GLOSSARY.md`).

They integrate by separating concerns based on the **Consumer Class**:

| Taxonomy Segment | Consumer | Purpose | Example |
| :--- | :--- | :--- | :--- |
| **TOOLOME** | **Developer** | **Shape the CODOME** (Action). Tools designed for human clarity and usability. | Formatters, Linters, IDEs. |
| **STONE_TOOLS** | **AI_AGENT** | **Observe the CODOME** (Analysis). Tools designed for machine parseability and structural completeness. | `unified_analysis.json`, `POM YAML`, `Collider` outputs. |

**The Integration Logic:**
AI Agents act as the bridge. They use **Stone Tools** to understand the system (Observation) and then use the **Toolome** or direct file manipulation to modify the system (Action), mediating the results back to the human in Natural Language (L1).

---

## Citations

_No citations provided_
