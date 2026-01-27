# Research: what is stone tool

> **Date:** 2026-01-27 01:45:40
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:0bebde2331b37850342f172333c1974c7d247c8eee548c0036af28a42f155b49`
> **Raw JSON:** `raw/20260127_014540_what_is_stone_tool.json`

---

## Query

what is stone tool

---

## Response

Based on the `CODESPACE_ALGEBRA.md` and `GLOSSARY.md` files in the codebase, a **Stone Tool** is a specific class of software utility designed **exclusively for AI Agents**, not humans.

### 1. The Definition (Axiom H4)
According to **Axiom H4 (Ergonomics Shift)** found in `CODESPACE_ALGEBRA.md`, the definition is:

> **Stone Tool Principle:** "Tools MAY be designed that humans cannot directly use."

In this architecture, software tools are usually designed for human ergonomics (GUIs, readable text, CLI help menus). **Stone Tools** are designed for **AI ergonomics** (parseability, structured data, high information density).

### 2. The Metaphor
The documentation uses this analogy:
*   **Paleolithic Stone Tools:** Were shaped specifically to fit the **human hand** (grip, leverage).
*   **AI Stone Tools:** Are shaped specifically to fit the **AI "hand"** (Context windows, JSON parsing, token budgets).

### 3. The "Stone Tool Test"
To determine if a utility is a Stone Tool, the documentation applies this logic:

```
STONE_TOOL_TEST(tool) = "Can a human use this without AI mediation?"
```
*   **If YES:** It is a standard Dev Tool (Toolome).
*   **If NO:** It is a **Stone Tool** (valid AI-native design).

### 4. Examples in PROJECT_elements
Based on `GLOSSARY.md`, the repository distinguishes between:

1.  **TOOLOME (Dev Tools):** Things humans use (formatters, linters, `git`).
2.  **STONE_TOOLS (Analysis Tools):** Things the AI uses to understand the code.
    *   **`unified_analysis.json`**: A massive JSON output from the Collider engine. It is too large and complex for a human to read, but perfect for an AI to query.
    *   **`POM YAML`**: Physical Object Model manifests.

### Summary
A **Stone Tool** is a piece of infrastructure that generates data formats (like complex JSON graphs) optimized for LLM consumption, accepting that these outputs may be illegible or unusable to a human developer without an AI intermediary.

---

## Citations

_No citations provided_
