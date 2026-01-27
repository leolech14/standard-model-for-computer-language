# Research: What tools do we have for mapping/analyzing our own repository? List: 1) Collider capabilities for s...

> **Date:** 2026-01-27 01:43:06
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:3177e54af39a14739d9ac9dd83e1ce4d89ffa21a173cbe6f9f09f805c1c0ca52`
> **Raw JSON:** `raw/20260127_014306_what_tools_do_we_have_for_mapping_analyzing_our_ow.json`

---

## Query

What tools do we have for mapping/analyzing our own repository? List: 1) Collider capabilities for self-analysis 2) Cloud Refinery 3) Any other analysis/mapping tools. Show me the COMMANDS to run them.

---

## Response

Based on the `BACKGROUND_AI_LAYER_MAP.md`, `TOOL.md`, and `CLI_GRAMMAR.md`, here are the tools available for self-analysis and mapping of the `PROJECT_elements` repository.

### 1. Collider (The Physics Engine)
**Purpose:** Performs static analysis to collapse the "wave function" of source code into a concrete graph of "particles" (Nodes) and forces (Edges). It analyzes the **CODOME** (executable code).

*   **Capabilities:** AST parsing, Atom classification, 8D dimensional analysis, 3D Graph generation.
*   **Output:** `unified_analysis.json` (The Ground Truth).

**COMMANDS:**
```bash
# 1. Run full analysis on the current directory
./collider full . --output .collider

# 2. Run analysis with 3D visualization server
./collider viz . --3d

# 3. Generate human-readable HTML report
./collider report --input .collider/unified_analysis.json
```

---

### 2. Context Refinery (The Atomizer)
**Purpose:** Breaks large code contexts into semantic units ("chunks") optimized for AI ingestion. It uses relevance scoring to prioritize code for limited context windows.

*   **Capabilities:** Python/Markdown/YAML chunking, Relevance scoring (Type/Length/Docstring), JSON export.
*   **Location:** `context-management/tools/ai/aci/refinery.py`

**COMMANDS:**
```bash
# 1. Atomize a specific directory into chunks
python context-management/tools/ai/aci/refinery.py src/core/ --export chunks.json

# 2. Analyze a specific file's atomization
python context-management/tools/ai/aci/refinery.py src/core/full_analysis.py --verbose
```

---

### 3. Other Analysis & Mapping Tools

#### A. Holographic-Socratic Layer (HSL)
**Purpose:** Maps the **symmetry** between Code and Documentation. It detects "Antimatter" (architectural violations like Context Myopia or Drift).
**Location:** `context-management/tools/ai/analyze.py`

**COMMANDS:**
```bash
# 1. Verify semantic integrity of a specific domain (e.g., pipeline)
python context-management/tools/ai/analyze.py --verify pipeline

# 2. Audit a specific candidate file against the "Antimatter Laws"
python context-management/tools/ai/analyze.py --verify pipeline --candidate src/core/violation_stage.py
```

#### B. Continuous Cartographer / Drift Guard
**Purpose:** A daemon that watches the file system and auto-updates the map (`unified_analysis.json`) when code changes.
**Location:** `context-management/tools/drift_guard.py`

**COMMANDS:**
```bash
# 1. Run a single cartography pass to update the internal map
python context-management/tools/continuous_cartographer.py

# 2. Start the background daemon (watches for file changes)
python context-management/tools/drift_guard.py --local --debug
```

#### C. Centripetal Scan
**Purpose:** Performs a deep, 12-round progressive resolution scan, moving from macro structure to nano invariants. Uses both internal analysis and external research.
**Location:** `.agent/tools/centripetal_scan.py`

**COMMANDS:**
```bash
# 1. Initiate a deep scan (Requires API quota)
python .agent/tools/centripetal_scan.py
```

#### D. The Unified Interface (`./pe`)
**Purpose:** A wrapper that routes natural language intent to the specific tools listed above.

**COMMANDS:**
```bash
# Analyze structure (Routes to Collider)
./pe "analyze the code structure"

# Audit docs (Routes to HSL)
./pe "check for doc drift"

# Health check (Routes to BARE/Truths)
./pe status
```

---

## Citations

_No citations provided_
