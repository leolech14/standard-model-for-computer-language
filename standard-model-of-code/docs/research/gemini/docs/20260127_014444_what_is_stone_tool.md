# Research: what is stone tool

> **Date:** 2026-01-27 01:44:44
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:d20c0a90c08d691f2312e771bdf71d84dea32b4323e6a2bb2281f342a74fbfe5`
> **Raw JSON:** `raw/20260127_014444_what_is_stone_tool.json`

---

## Query

what is stone tool

---

## Response

Based on the **Codespace Algebra** and **Glossary** documents provided in the context, here is the definition of a **Stone Tool** within the PROJECT_elements framework.

### Definition: Stone Tool
A **Stone Tool** is a software artifact or utility designed specifically for **AI Agents**, not humans. It prioritizes structure, parseability, and information density over human readability or ergonomics.

It represents a fundamental shift in tool design philosophy (Axiom Group H), acknowledging that in an AI-mediated workflow, the "user" of a tool is often a machine, not a person.

---

### The Core Concept (Axiom H4)

The concept is formally defined in `context-management/docs/CODESPACE_ALGEBRA.md` under **Axiom H4 (Ergonomics Shift)**:

> **Stone Tool Principle:** Tools MAY be designed that humans cannot directly use.
>
> *   **Physical Stone Tools:** Were shaped to fit the human **HAND** (grip, balance).
> *   **Software Stone Tools:** Are shaped to fit the **AI's "HAND"** (parseability, typing speed, token efficiency).

### The Stone Tool Test

To determine if something is a Stone Tool, the system applies the following logic:

> **STONE_TOOL_TEST(tool) = "Can a human use this without AI mediation?"**
> *   **YES** → Standard Tool (Toolome)
> *   **NO** → Stone Tool (AI-Native / Valid Design)

### Key Characteristics

1.  **AI-Native Ergonomics:** Humans communicate via Natural Language (L1). AI operates best on Structured Data (L0, L2). Stone Tools operate at L0/L2.
2.  **Mediation:** Humans are not expected to read the raw output of a Stone Tool. An AI Agent acts as the bridge, consuming the Stone Tool's output and translating it for the human.
3.  **High Density:** They often produce massive JSON or YAML outputs that would overwhelm a human but provide perfect context for an LLM.

### Concrete Examples

Based on the documentation, these are the primary Stone Tools in the project:

*   **`unified_analysis.json`**: The massive output of the Collider. It is a "Stone Tool" because it contains thousands of lines of AST data, atom classifications, and graph relationships. It is unreadable to humans but gives an AI perfect situational awareness.
*   **`POM` (Project Object Model) YAMLs**: Structural manifests intended for automated reasoning.
*   **`analyze.py --mode forensic`**: While humans trigger it, the output format is strictly structured for verification, making it a tool designed for the "Surgeon" AI persona.

### Summary
In this architecture, **you** (the human) are the architect. The **AI** is the laborer. The **Stone Tool** is the specialized instrument the laborer uses to measure and manipulate the code—an instrument that doesn't need to fit your hand, because you aren't the one holding it.

---

## Citations

_No citations provided_
