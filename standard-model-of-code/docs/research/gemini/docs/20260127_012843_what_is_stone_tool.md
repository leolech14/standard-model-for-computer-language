# Research: what is stone tool

> **Date:** 2026-01-27 01:28:43
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:fc3480e2f01773c6bce9d4e7887251522423fc568780c7ec5df7b5a1cb43be05`
> **Raw JSON:** `raw/20260127_012843_what_is_stone_tool.json`

---

## Query

what is stone tool

---

## Response

Based on the **Codespace Algebra** and **Glossary** documents within the codebase, a **Stone Tool** is a specific class of software tool designed exclusively for **AI Agents**, not humans.

It is defined by **Axiom H4 (The Ergonomics Shift)**.

### 1. The Definition
A **Stone Tool** is an artifact or utility optimized for the "ergonomics" of an AI (parseability, structured data, high volume), rather than the ergonomics of a human (readability, GUI, brevity).

*   **Human Tool:** Shaped for the human hand/eye (e.g., a GUI, a CLI with help text, a linter output).
*   **Stone Tool:** Shaped for the AI's "hand" (e.g., massive JSON blobs, rigid schemas, high-dimensional vectors).

### 2. The Stone Tool Principle (Axiom H4)
Found in `context-management/docs/CODESPACE_ALGEBRA.md`:

> "Tools MAY be designed that humans cannot directly use."

In the prehistoric era, stone tools were chipped to fit the human grip. In the AI era, we must chip tools that fit the **Context Window** and **Reasoning Capabilities** of an LLM.

### 3. The "Stone Tool Test"
To determine if something is a Stone Tool, apply this test found in the Glossary:

> **"Can a human use this tool directly, without AI mediation?"**
> *   **YES** → It is a standard Dev Tool (part of the Toolome).
> *   **NO** → It is a **Stone Tool** (valid AI-native design).

### 4. Examples in PROJECT_elements
The documentation identifies specific assets as Stone Tools:

*   **`unified_analysis.json`**: The output of the Collider. It is often 100MB+ of JSON. A human cannot read it, but an AI Agent reads it to understand the codebase's architecture.
*   **The POM (Project Object Model)**: Strict YAML manifests that define project structure for the AI.
*   **`analyze.py` (in certain modes)**: When it outputs raw structured data meant to be piped into another agent's context window.

### Summary
In this project, calling something a "Stone Tool" is **not an insult** implying it is primitive. It is a classification indicating that the tool is **AI-Native**—specifically engineered to extend the capabilities of an artificial agent where human cognitive limits (like reading 10,000 lines of code in a second) are irrelevant.

---

## Citations

_No citations provided_
