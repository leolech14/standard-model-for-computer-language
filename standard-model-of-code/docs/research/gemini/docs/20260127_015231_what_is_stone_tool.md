# Research: what is stone tool

> **Date:** 2026-01-27 01:52:31
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:a403fd1fbf6ab5821da60ccd94d60021073a8c9e3323eea4cfa2ffb5edb0d447`
> **Raw JSON:** `raw/20260127_015231_what_is_stone_tool.json`

---

## Query

what is stone tool

---

## Response

Based on the provided codebase documentation—specifically **`AI_CONSUMER_CLASS.md`** and **`THEORY_AMENDMENT_2026-01.md`**—here is the definition of a **Stone Tool** within the Standard Model of Code.

### Definition
A **Stone Tool** is a software artifact or utility designed specifically for consumption by **AI Agents**, rather than humans. It prioritizes machine parseability over human usability.

### 1. The Stone Tool Test
The documentation defines a litmus test to identify these tools:

> **"Can a human use this tool directly, without AI mediation?"**

*   **If YES:** It is part of the **TOOLOME** (traditional dev tools like Linters, Formatters).
*   **If NO:** It is a **STONE_TOOL** (AI-native analysis tools).

### 2. Characteristics
Unlike traditional tools evolved for the human hand (ergonomics) or eye (GUI), Stone Tools are evolved for the "AI Hand":

| Feature | Human Tool (Traditional) | Stone Tool (AI-Native) |
| :--- | :--- | :--- |
| **Output** | Human-readable text/GUI | Structured Data (JSON, YAML) |
| **Error Handling** | "Something went wrong" | `{"code": "E001", "context": {...}}` |
| **Optimized For** | Experience & Aesthetics | Parseability & Predictability |
| **User Interface** | Click, Type, Read | Schema, API, Type Constraints |

### 3. Examples from the Codebase

| Tool | Category | Reason |
| :--- | :--- | :--- |
| **CLI with `--help`** | Human Tool | Human can read and operate it. |
| **Collider** | **Stone Tool** | Outputs `unified_analysis.json` (25MB+ of graph data) which is impossible for a human to read directly but perfect for an AI. |
| **POM (Projectome Omniscience)** | **Stone Tool** | Generates a YAML manifest of the entire project structure for AI consumption. |

### 4. The "Stone Tool" Analogy
The term is derived from an evolutionary analogy regarding the "Third Consumer Class" (AI Agents):

1.  **Stone Age:** Tools shaped to fit the **human hand** (Stone Axe).
2.  **Digital Age:** Tools shaped to fit **human perception** (GUI).
3.  **AI Age:** Tools shaped to fit **AI processing** (Stone Tools).

The "Stone Tool" represents the raw, fundamental instruments that AI agents use to build higher-order value, just as early humans used stone tools to build civilization.

### 5. Operational Workflow
Stone Tools are **intermediate artifacts**. They operate in a mediated flow:

```
Human Intent (L1) ──► AI Agent ──► Stone Tool ──► Structured Output ──► AI Agent ──► Human Insight
```

The human never touches the Stone Tool directly; the AI mediates the interaction.

---

## Citations

_No citations provided_
