# Research: COMPREHENSIVE PROJECT HEALTH CHECK.

Give me:
1. Total file count by category (code, docs, config, t...

> **Date:** 2026-01-24 19:05:28
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:bb4aa78c578320c8bb1491efceb6512377ae94b167173a0e70fc51955de2eaa2`
> **Raw JSON:** `raw/20260124_190528_comprehensive_project_health_check___give_me__1__t.json`

---

## Query

COMPREHENSIVE PROJECT HEALTH CHECK.

Give me:
1. Total file count by category (code, docs, config, tests)
2. Dead code or orphaned modules
3. Documentation coverage (what is documented vs undocumented)
4. Test coverage status
5. Technical debt indicators
6. Overall health score (0-100)

Be quantitative where possible.

---

## Response

Based on a static analysis of the provided codebase (`standard-model-of-code`), here is the Comprehensive Project Health Check.

### 1. File Count by Category
Based on the provided context, the codebase is heavily weighted towards Python core logic and YAML configuration schemas.

*   **Source Code (.py):** 12 files
    *   *Core Logic:* 10 files (Extractors, Classifiers, Engines)
    *   *Orchestration:* 2 files (`full_analysis.py`, `unified_analysis.py`)
*   **Configuration/Schemas (.yaml):** 6 files
    *   *Constraints:* 2 files
    *   *Profiles:* 4 files
*   **Documentation (.md):** 0 files (visible in context, though referenced in comments).
*   **Tests (`test_*.py`):** 0 files.
    *   *Note:* There are no dedicated test files visible. Testing appears to rely on `if __name__ == "__main__":` blocks inside source files.

### 2. Dead Code & Orphaned Modules
There are specific indicators of dead or "zombie" code that have been explicitly marked but not removed.

*   **`src/core/universal_detector.py`:** This file appears to be a legacy entry point. It contains commented-out imports marked as `# QUARANTINED` (e.g., `ParticleClassifier`, `DependencyAnalyzer`). It overlaps significantly with `full_analysis.py` but uses deprecated or disabled components.
*   **Quarantined Logic in `unified_analysis.py`:**
    *   Stage 2 (RPBL Classification) is explicitly marked `[SKIPPED - QUARANTINED]` in the code comments, with the `ParticleClassifier` logic commented out.
*   **Redundant Logic:** `heuristic_classifier.py` and `universal_classifier.py` share overlapping responsibilities regarding role detection (e.g., identifying "Factory" or "Service" patterns).

### 3. Documentation Coverage
**Status: High (A-)**

The codebase exhibits excellent inline documentation standards.
*   **Module Level:** Every Python file includes a high-level docstring describing its purpose, usage, and outputs.
*   **Class/Function Level:** Key methods (e.g., `classify_disconnection`, `validate_graph`) have detailed docstrings explaining parameters and return values.
*   **Self-Describing Data:** The YAML files (`rules.yaml`, `taxonomy.yaml`) act as documentation for the architectural rules engine, effectively serving as "executable documentation."

### 4. Test Coverage Status
**Status: Critical (D)**

*   **Formal Tests:** 0% visible. No `tests/` directory or `test_*.py` files were provided in the context.
*   **Smoke Tests:** 60%. Most core files (e.g., `constraint_engine.py`, `dimension_classifier.py`) contain `if __name__ == "__main__":` blocks that run basic scenarios. While this ensures the file runs, it does not constitute a regression test suite.
*   **Risk:** The heavy reliance on regex and tree-sitter queries without a formal test suite makes refactoring high-risk, particularly for `edge_extractor.py` which handles complex AST parsing.

### 5. Technical Debt Indicators

*   **Monolithic Orchestrator:** `src/core/full_analysis.py` is approximately 1,000 lines long. It handles CLI parsing, file orchestration, timing, graph analytics, and HTML generation. This violates the Single Responsibility Principle and should be refactored (e.g., moving `Codome` logic to a dedicated module).
*   **Error Swallowing:** There is a prevalence of broad `try...except Exception` blocks inside loops (e.g., in `full_analysis.py` loops for `detect_js_imports` and `analyze_scopes`). While this prevents the tool from crashing on a single bad file, it masks underlying parsing failures.
*   **Dynamic Imports:** `unified_analysis.py` uses try/except blocks to import optional dependencies (like `llm_classifier`). This makes static analysis of the tool itself difficult and dependency management fragile.
*   **Legacy/Zombie Code:** As noted in section 2, the presence of "QUARANTINED" code paths suggests incomplete refactoring.

### 6. Overall Health Score: 72/100

| Category | Score | Notes |
| :--- | :--- | :--- |
| **Architecture** | 85/100 | Strong domain modeling (Standard Model atoms, RPBL). Clear separation of schema vs. logic. |
| **Code Quality** | 75/100 | Well-typed python, good naming conventions, but `full_analysis.py` is too large. |
| **Documentation** | 95/100 | Excellent inline docs and schema descriptions. |
| **Testing** | 15/100 | Use of `__main__` blocks is insufficient for a project of this complexity. |
| **Maintainability** | 90/100 | The use of YAML profiles to drive logic makes the system highly configurable without code changes. |

**Recommendation:**
1.  Delete `src/core/universal_detector.py`.
2.  Extract the `Codome` logic and `Report Generation` logic out of `full_analysis.py` into their own modules.
3.  Formalize the `if __name__ == "__main__":` blocks into a proper `pytest` suite.

---

## Citations

_No citations provided_
