# Research: CONTEXT: We have a Survey module (Stage 0) that runs before code analysis. Currently it's positioned...

> **Date:** 2026-01-23 12:30:51
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:dac58f5e725faee7412374225029df781302e5a4bbdef034d43d73584f3032cc`
> **Raw JSON:** `raw/20260123_123051_context__we_have_a_survey_module__stage_0__that_ru.json`

---

## Query

CONTEXT: We have a Survey module (Stage 0) that runs before code analysis. Currently it's positioned as 'exclude vendor code' but we've realized it's actually ONTOLOGICAL - it DEFINES what the codome IS before we measure it.

The distinction:
- OLD VIEW: Survey = optimization (skip vendor to save time)
- NEW VIEW: Survey = ontological definition (define boundaries before measuring)

Key insight: 'Before you measure a thing, you must define what the thing IS.'

Survey answers 5 questions:
1. IDENTITY: What is this project? (language, framework, ecosystem)
2. BOUNDARIES: Where does it start/end? (ours vs vendor vs generated)
3. NATURE: What file types are code vs config vs data?
4. POLLUTION: What shouldn't be here? (misplaced files)
5. ADAPTATION: How should pipeline behave? (parsers, thresholds)

QUESTIONS:
1. Should we make this ontological distinction MORE CLEAR in docs and code?
2. If yes, HOW? Concrete suggestions for:
   - Naming (should 'Survey' be renamed to something more ontological?)
   - Documentation structure
   - Code organization
   - User-facing messaging (CLI output, reports)
3. Is the 5-question framework the right structure, or should it be different?
4. Any risks or downsides to this framing?

Be specific and actionable.

---

## Response

Based on the codebase context provided, particularly `src/core/survey.py` and `src/core/full_analysis.py`, here is the analysis and specific recommendations for reframing the Survey module.

### 1. Should we make this ontological distinction MORE CLEAR?

**YES.**

Your insight is architecturally sound. Currently, `src/core/survey.py` is written defensively ("What do I exclude?"). This is a "Negative Definition." Shifting to a "Positive Definition" ("What is this system?") creates a stronger foundation for the subsequent analysis.

If Stage 0 misidentifies the system (e.g., treating a Monorepo as a single monolith, or analyzing build artifacts as source code), Stages 1-12 will hallucinate structure where none exists. **The definition of the object must precede the measurement of the object.**

### 2. HOW? Concrete Suggestions

#### A. Naming & Terminology (The "Codome" Shift)

Keep the filename `survey.py` (it describes the action), but change the conceptual entities within it.

*   **Phase Name:** Rename "Stage 0: Survey" to **"Stage 0: Codome Definition"**.
*   **Result Object:** Rename `SurveyResult` to **`CodomeManifest`**.
*   **Exclusions:** Rename `recommended_excludes` to **`BoundaryConstraint`**.

#### B. Code Organization (`src/core/survey.py`)

Refactor `SurveyResult` to explicitly answer the 5 questions. Currently, it mixes counts with exclusions.

**Current (`src/core/survey.py`):**
```python
@dataclass
class SurveyResult:
    root_path: str
    scan_time_ms: float
    total_files: int = 0
    # ... lists of exclusions ...
    estimated_nodes: int = 0
```

**Proposed Refactor:**
```python
@dataclass
class SystemIdentity:
    primary_language: str      # e.g., "Python"
    dominant_framework: str    # e.g., "Django" (detect via lockfiles in survey)
    architecture_style: str    # e.g., "Monorepo" vs "Standard"

@dataclass
class CodomeManifest:
    """Defines the ontological boundaries of the system to be analyzed."""
    identity: SystemIdentity   # Q1: Identity
    
    # Q2: Boundaries (The "Inclusion/Exclusion" logic)
    boundary_constraints: List[str]  # Formerly recommended_excludes
    
    # Q3: Nature (Code vs Config vs Data ratios)
    composition: Dict[str, float] # e.g., {'source': 0.8, 'config': 0.1, 'data': 0.1}
    
    # Q4: Pollution (Binaries, huge logs, minified files inside source dirs)
    pollution_alerts: List[str]
    
    # Q5: Adaptation (Config for the next stages)
    pipeline_config: Dict[str, Any] # Recommended parser settings
```

#### C. User-Facing Messaging (`src/core/full_analysis.py`)

Update the CLI output in `run_full_analysis` to reflect this ontological stance. Instead of listing what you *ignored*, list what you *found*.

**Current:**
```text
🔍 Stage 0: Survey...
   → Found 12 vendor directories
   → Excluding 45 paths
   → Estimated 5000 nodes
```

**Proposed:**
```text
🌐 Stage 0: Codome Definition
   → Identity:   Python / FastAPI Application
   → Boundaries: Rigid (Vendor & Build artifacts excluded)
   → Nature:     85% Source Code, 15% Configuration
   → Pollution:  Clean (No binary artifacts detected)
   → Adaptation: Tuning AST parsers for Python
```

#### D. Documentation Structure

Update the module docstring in `src/core/survey.py` to serve as the manifesto for this layer.

```python
"""
CODOME DEFINITION LAYER (Stage 0)
=================================

This module defines the ontology of the target system before analysis begins.
It is not merely an optimization (exclusion); it is a definition.

It answers:
1. IDENTITY: What is this? (Language, Framework)
2. BOUNDARIES: What is 'Self' vs 'Other'? (Vendor, Gen-code)
3. NATURE: What is the texture? (Code/Config/Data ratio)
4. POLLUTION: What violates the physics of this repo?
5. ADAPTATION: How must the instruments be calibrated?
"""
```

### 3. Is the 5-question framework right?

Yes, it is excellent because it maps directly to the subsequent pipeline stages:

1.  **IDENTITY** $\to$ Maps to **Stage 1 (AST Parsing)**. Knowing it's Python tells us which `TreeSitter` grammar to load.
2.  **BOUNDARIES** $\to$ Maps to **Stage 2.7 (Dimensions)**. Helps define `D4_BOUNDARY` (Internal vs External).
3.  **NATURE** $\to$ Maps to **Stage 5.6 (Enrichment)**. Helps distinguish `DAT` (Data) from `LOG` (Logic) atoms early.
4.  **POLLUTION** $\to$ Maps to **Stage 8.5 (Constraints)**. Early detection of "Antimatter" (e.g., a 50MB SQL dump in `src/`).
5.  **ADAPTATION** $\to$ Maps to **Observability**. Sets timeouts and memory limits based on size/complexity.

**Refinement:**
Add **TOPOLOGY** as a sub-point of Identity. Is this a Monolith, a Monorepo, or a Microservice? `survey.py` can detect this by looking for multiple `package.json` or `requirements.txt` files at the root vs subdirs.

### 4. Risks and Downsides

1.  **"The Map is not the Territory" Risk:**
    *   *Risk:* If the Survey defines the Codome incorrectly (e.g., decides a folder is "Vendor" when it's actually "Legacy Core"), that code effectively ceases to exist for the rest of the pipeline.
    *   *Mitigation:* The Survey must be **Conservative by default, Aggressive by configuration**. Always report *what* was excluded and *why* in the final report.

2.  **Performance Creep:**
    *   *Risk:* "Ontological Definition" sounds expensive. If we start parsing `package.json` or reading file headers to determine "Identity," Stage 0 might slow down.
    *   *Mitigation:* Keep Stage 0 strictly **Filesystem-based** (file names, extensions, directory structure). Do not open files for deep AST parsing here. `detect_minified_files` already reads files; ensure it reads *only* headers/first lines.

3.  **The "Polyglot" Edge Case:**
    *   *Risk:* Defining "Identity" is hard for mixed repos (e.g., Python backend + React frontend).
    *   *Mitigation:* The `Identity` struct must support lists/sets (e.g., `primary_languages: ["Python", "TypeScript"]`). Do not force a single identity.

### Action Plan

1.  **Modify `src/core/survey.py`**:
    *   Rename internal variables to match the 5 questions (e.g., `exclusions` -> `boundaries`).
    *   Add simple heuristics to detect `Identity` (look for `pom.xml`, `requirements.txt`, `package.json`).
2.  **Modify `src/core/full_analysis.py`**:
    *   Update the print statements for Stage 0.
3.  **Documentation**:
    *   Update the docstring in `survey.py`.

---

## Citations

_No citations provided_
