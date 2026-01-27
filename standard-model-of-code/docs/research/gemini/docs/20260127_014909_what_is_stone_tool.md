# Research: what is stone tool

> **Date:** 2026-01-27 01:49:09
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:d1b5e47cb4cec3ed102fddf47bea5cfa1b7480fe715af35c996c92ac5a9a7254`
> **Raw JSON:** `raw/20260127_014909_what_is_stone_tool.json`

---

## Query

what is stone tool

---

## Response

Based on the provided codebase documentation, specifically **`context-management/docs/CODESPACE_ALGEBRA.md`** and **`context-management/docs/GLOSSARY.md`**, here is the definition of a **Stone Tool** within the context of **PROJECT_elements**:

### Definition
A **Stone Tool** is a software utility or artifact designed specifically to be "held" and used by an **AI Agent**, not a human.

It derives from **Axiom H4 (The Stone Tool Principle)**, which asserts that in an AI-native architecture, it is valid design to create tools that are ergonomically hostile to humans but optimized for AI consumption.

### The Metaphor (Ergonomics)
The term relies on an anthropological analogy regarding ergonomics:
*   **Prehistoric Stone Tools:** Were knapped and shaped specifically to fit the human **hand** (grip, balance, thumb position).
*   **AI-Native "Stone Tools":** Are shaped to fit the **AI's "hand"** (parseability, token efficiency, structured schema, type safety).

### The "Stone Tool Test"
To determine if a utility is a Stone Tool, the documentation defines a specific test:

> **"Can a human use this tool directly, without AI mediation?"**
> *   **YES:** It is a standard Developer Tool (e.g., a CLI with help text, a linter with colored output).
> *   **NO:** It is a **Stone Tool** (e.g., a script that outputs 50MB of raw JSON, or a complex YAML schema intended for agent consumption).

### Role in the Project
In the **PROJECT_elements** architecture:
1.  **Consumer Classes:** The system recognizes three consumers: End Users, Developers, and **AI Agents**.
2.  **Optimization:** Stone Tools are optimized for the **AI Agent** consumer class.
3.  **Examples:**
    *   **`unified_analysis.json`**: The massive output of the **Collider**. It is too complex for a human to read raw, but perfect for an AI to reason about the codebase structure.
    *   **POM (Project Object Model) YAMLs**: Configuration files designed for the agent to read/write state.

### Why It Matters
This concept justifies the creation of "unusable" (to humans) interfaces. It argues that attempting to make every tool human-readable restricts the AI's capability. By accepting Stone Tools, the project allows for higher-fidelity data transmission between the system and the AI agents.

---

## Citations

_No citations provided_
