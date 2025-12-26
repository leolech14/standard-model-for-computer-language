# Standard Code Validation Megaprompts

> **Epistemic Stance**: These prompts validate a MAP of software engineering, not the territory. All findings should assume the map will evolve.

---

## The Paradigm (Share With Every Prompt)

> **"We know that we don't know."**

When executing any validation prompt:

1. **Canonical ≠ Complete**: Numbers like 167 atoms, 33 roles, 8 dimensions are *working sets*, not claims of totality. Finding gaps is expected and valuable.

2. **Unknown is First-Class**: Entities that don't fit cleanly are *evidence to evolve the map*, not failures.

3. **Postulates, Not Theorems**: Every claim has "How It Could Be Wrong" and "Validation Method" columns. We test hypotheses, not prove truths.

4. **Open World Assumption**: The model is designed to extend. Your findings may add atoms, roles, lenses—this is success.

---

## Prompts Index

| # | File | Purpose |
|---|------|---------|
| 01 | [01_claims_ledger.md](01_claims_ledger.md) | Extract & categorize all theory claims |
| 02 | [02_lens_validation.md](02_lens_validation.md) | Test 8 lenses against real questions |
| 03 | [03_dimension_orthogonality.md](03_dimension_orthogonality.md) | Verify 8D mutual exclusivity |
| 04 | [04_atom_coverage.md](04_atom_coverage.md) | Test 167 atoms vs AST types |
| 05 | [05_role_taxonomy.md](05_role_taxonomy.md) | Human annotation study design |
| 06 | [06_detection_signals.md](06_detection_signals.md) | Evidence model for classification |
| 07 | [07_confidence_calibration.md](07_confidence_calibration.md) | Design calibrated confidence |
| 08 | [08_edge_semantics.md](08_edge_semantics.md) | Full graph schema |
| 09 | [09_analysis_pipeline.md](09_analysis_pipeline.md) | Ordered analysis stages |
| 10 | [10_correctness_definitions.md](10_correctness_definitions.md) | What "correct" means |
| 11 | [11_benchmark_design.md](11_benchmark_design.md) | Validation Pack specs |
| 12 | [12_semantic_similarity.md](12_semantic_similarity.md) | 8D distance metrics |
| 13 | [13_entropy_complexity.md](13_entropy_complexity.md) | Complexity at each level |
| 14 | [14_governance_evolution.md](14_governance_evolution.md) | Evolution protocol |

## Recommended Order

| Phase | Prompts | Goal |
|-------|---------|------|
| **Foundation** | 1, 3, 4 | Validate core definitions |
| **Taxonomy** | 2, 5 | Validate lenses and roles |
| **Implementation** | 6, 7, 9 | Build detection and pipeline |
| **Validation** | 10, 11 | Build test infrastructure |
| **Advanced** | 8, 12, 13 | Edge semantics and metrics |
| **Governance** | 14 | Long-term sustainability |

## Usage

1. **Read the Paradigm first** (above)
2. Copy the megaprompt text
3. Append the relevant context (e.g., `STANDARD_CODE.md` content)
4. Send to an LLM (Claude, GPT-4, etc.)
5. Treat all findings as **evolution opportunities**, not failures

---

> *"The territory exists. This document is a living legend. Canon is a tool, not a claim of totality."*
