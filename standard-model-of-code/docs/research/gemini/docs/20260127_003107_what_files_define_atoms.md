# Research: what files define atoms

> **Date:** 2026-01-27 00:31:07
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:f501456985c5c27be7b99a4e45934756dc5021ffff92be3c05a995271b626b45`
> **Raw JSON:** `raw/20260127_003107_what_files_define_atoms.json`

---

## Query

what files define atoms

---

## Response

Based on the codebase context, the definition of **Atoms** (the fundamental structural units of code) is split across three layers: Theoretical, Schema, and Implementation.

Here are the specific files that define them:

### 1. The Canonical Registry (Schema)
**File:** `standard-model-of-code/schema/atoms.json`
*   **Purpose:** The "Periodic Table" of code. This is the immutable source of truth listing all **167 canonical atoms** (e.g., `LOG.FNC.M` for Method, `DAT.VAR.L` for Local Variable).
*   **Status:** "Locked" as of Jan 16, 2026 (per `TIMELINE_ANALYSIS.md`).

### 2. The Implementation (Python Code)
**File:** `standard-model-of-code/src/core/atom_registry.py`
*   **Purpose:** The active Python class that the **Collider** tool uses during analysis.
*   **Note:** It currently implements **94 of the 167 atoms** (the "working set" needed for current language support).

### 3. The Detection Patterns
**File:** `standard-model-of-code/src/patterns/particle_defs.json`
*   **Purpose:** Contains the regex patterns and heuristics used to detect these atoms in source code (e.g., identifying that a string starting with `get` is likely a `Query` role).

### 4. The Theory
**File:** `standard-model-of-code/docs/MODEL.md`
*   **Purpose:** Explains *why* these atoms exist, how they are organized into the 4 Phases (Data, Logic, Organization, Execution), and how they map to the physical universe metaphor.

---

### Summary Table

| Layer | File Path | Content |
| :--- | :--- | :--- |
| **Schema** | `standard-model-of-code/schema/atoms.json` | Full list of 167 Atoms (JSON) |
| **Code** | `standard-model-of-code/src/core/atom_registry.py` | 94 Implemented Atoms (Python) |
| **Rules** | `standard-model-of-code/src/patterns/particle_defs.json` | Detection Logic (JSON) |
| **Theory** | `standard-model-of-code/docs/MODEL.md` | Concepts & Definitions (Markdown) |

---

## Citations

_No citations provided_
