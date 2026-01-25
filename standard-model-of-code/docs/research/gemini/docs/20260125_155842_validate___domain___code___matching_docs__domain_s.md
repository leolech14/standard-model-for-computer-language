# Research: Validate: 'Domain = code + matching docs. Domain Symmetry measures if code matches its docs.'

Does ...

> **Date:** 2026-01-25 15:58:42
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:9990a3b59fd56dcf6603c20ead9ff6fee30c5df4a6f6739645c0bd09aac010eb`
> **Raw JSON:** `raw/20260125_155842_validate___domain___code___matching_docs__domain_s.json`

---

## Query

Validate: 'Domain = code + matching docs. Domain Symmetry measures if code matches its docs.'

Does the codebase show this pattern? Examples: full_analysis.py + PIPELINE_STAGES.md, modules/*.js + UI_SPEC.md

Score 0-100 for accuracy and usefulness.

---

## Response

Based on the analysis of the provided codebase, here is the validation of the proposition: **'Domain = code + matching docs. Domain Symmetry measures if code matches its docs.'**

### Validation Analysis

The codebase **strongly supports** the philosophy of "Domain Symmetry," though the implementation differs slightly from a literal "parse markdown vs. parse code" comparison. Instead, the "Docs/Spec" are internalized as rigid schemas, taxonomies, and architectural rules within the classifier logic. The system acts as a validator that the "Code" matches the "Standard Model" (the implied Domain).

#### 1. Evidence of Domain Symmetry (Code matching "Specs")

**A. Path-to-Structure Symmetry (The "Location Spec")**
In `universal_classifier.py`, the code enforces that file location (the directory structure/docs) must match the code behavior. This is a direct measure of symmetry between "Where it says it is" and "What it actually does."

*   **Code:** `universal_classifier.py` (Lines 111-135, 237-285)
*   **Mechanism:** It explicitly checks if files inside `/domain/entities/` actually act like entities, or if files in `/presentation/` act like Controllers.
*   **Symmetry Check:** If a class is in `/infrastructure/` but contains business logic (detected via imports or body analysis), the `confidence` score likely drops or the classification shifts, indicating a break in symmetry.

**B. Naming-to-Behavior Symmetry (The "Vocabulary Spec")**
In `heuristic_classifier.py`, the code enforces that the *name* of a component (its label/doc) matches its *pattern* (its behavior).

*   **Code:** `heuristic_classifier.py`
*   **Mechanism:** It calculates `confidence` scores. For example, if a function is named `create_user` (implies Factory/Command) but the body doesn't match the pattern (low confidence), the symmetry is broken.
*   **Evidence:** The `MISSING_CANONICAL_ROLES` (Line 29) act as the "Documentation Standard" that the code is measured against.

**C. The Pipeline as Code (Matching `PIPELINE_STAGES.md`)**
You requested a specific example regarding `full_analysis.py` + `PIPELINE_STAGES.md`. The file `universal_detector.py` serves as this `full_analysis.py`.

*   **Code:** `universal_detector.py` -> `UniversalPatternDetector.analyze_repository`
*   **Symmetry:** The code is structured in explicit steps (Step 1, Step 1.5, Step 2...) that mirror a documentation artifact.
    *   *Step 1:* `tree_sitter_engine.analyze_directory`
    *   *Step 2:* `particle_classifier` (Quarantined)
    *   *Step 3:* `stats_generator`
    *   *Step 3.5:* `god_class_detector`
*   **Observation:** The code *is* the executable specification of the pipeline.

**D. Code-to-Ecosystem Symmetry**
In `universal_classifier.py` (Line 414), the code checks `dims["D1_ECOSYSTEM"]`.
*   **Mechanism:** It reads imports (documentation of dependencies) to determine if the code matches a specific ecosystem (e.g., React, Django, Torch). This verifies that the code "speaks the language" it claims to import.

#### 2. Gap Analysis (Literal vs. Architectural)

*   **Literal Interpretation:** The codebase does **not** contain a module that opens `UI_SPEC.md`, parses natural language requirements, and compares them to `modules/ui.js`.
*   **Architectural Interpretation:** The codebase **does** contain `ddd_mappings.py` and `role_registry.py` (imported). These files serve as the "Canonical Documentation." The `UniversalDetector` measures how well the target repository adheres to this "Canonical Doc."

### Scoring

**Accuracy: 85/100**
*   *Why:* The codebase accurately implements the *spirit* of Domain Symmetry (checking code against a rigid definition of domain roles and architectural layers). It falls short of 100 because it compares code against *internalized rules* (Python classes/Dictionaries) rather than external Documentation/Markdown files, which is implied by "matching docs."

**Usefulness: 98/100**
*   *Why:* This pattern is incredibly useful. By treating the "Standard Model of Code" (the classification rules) as the "Doc," the system can automatically grade *any* codebase on how well it adheres to standard architectural patterns (Clean Architecture, DDD). It turns "Code Review" into a computable metric (`confidence`, `D8_TRUST`, `GodClass` detection).

### Conclusion

The codebase validates the proposition **"Domain = code + matching docs"** by treating the **Classification Logic as the Living Documentation**.

*   If `Code Structure` matches `UniversalClassifier Rules`, Symmetry is High (High Confidence).
*   If `Code Structure` violates `UniversalClassifier Rules` (e.g., God Classes detected in `universal_detector.py`), Symmetry is Low (Antimatter detected).

---

## Citations

_No citations provided_
