# STANDARD MODEL VALIDATION STRATEGY
> Prompts and protocols to validate the correctness of the theory.

## 1. SCOPE & CLAIMS
**Prompt:**
"Help me turn our theory into a claims ledger. Given the following document/section: [PASTE], extract every claim and label it as Definition / Empirical claim / Analogy / Normative goal / Implementation assumption. For each claim, propose: (a) what evidence would support it, (b) what would falsify it, (c) what 'confidence' means for this claim, (d) what scope limitations should be stated."

## 2. LENS SYSTEM VALIDATION
**Prompt:**
"We use 8 lenses (Identity…Epistemology). Take these real developer questions: [LIST]. Map each question to one primary lens + optional secondary lens. Identify questions that don't fit cleanly and propose either (a) a missing lens, (b) a redefinition, or (c) a rule for composing lenses."

## 3. DIMENSION DEFINITIONS & MUTUAL EXCLUSIVITY
**Prompt:**
"Review our 8 dimensions (WHAT/LAYER/ROLE/BOUNDARY/STATE/EFFECT/ACTIVATION/LIFETIME). For each dimension: define values precisely, list boundary cases, and write constraints for mutual exclusivity. Then propose a minimal 'Unknown/Other' policy that doesn't collapse the taxonomy."

## 4. ATOM COVERAGE & AST MAPPING
**Prompt:**
"We claim 167 atoms cover AST node types. For languages [X, Y, Z], propose a methodology to test coverage and mapping stability. Include: (a) how to build the crosswalk from official AST node kinds to our atoms, (b) how to handle language-specific nodes, (c) how to measure 'coverage %', (d) how to evolve atoms without breaking old analyses."

## 5. ROLE TAXONOMY VALIDATION
**Prompt:**
"We have 33/35 roles. Design a validation study to test: (1) role clarity, (2) inter-annotator agreement, (3) confusion pairs, (4) robustness across architectures. Provide a labeling guide outline + annotation workflow + metrics + how to revise roles without invalidating history."

## 6. DETECTION SIGNALS & EVIDENCE GRAPH
**Prompt:**
"For each dimension (and role/atom), list detection features: name patterns, paths, imports, call graph, field analysis, decorators, scope, etc. Provide a structured evidence model that records: feature → support strength → counter-evidence → confidence update rule."

## 7. CONFIDENCE, CALIBRATION, & EPISTEMOLOGY
**Prompt:**
"Design a confidence system for classification (atoms/roles/dimensions/edges). Define: (a) what confidence represents, (b) how it's computed (rules + ML + cross-checks), (c) calibration tests, (d) when to escalate to human review, (e) how confidence weights evolve over time."

## 8. EDGE SEMANTICS & INVERSES
**Prompt:**
"We have multiple edge families (structural/dependency/inheritance/semantic/temporal). Define a rigorous edge schema: properties, directionality, inverses, composability, and how edges should be extracted (static vs dynamic). Include validation checks (e.g., inverse consistency, transitivity where applicable)."

## 9. PROGRAM ANALYSIS STACK
**Prompt:**
"Produce a dependency-ordered analysis pipeline that can populate D1–D8 + edges. For each step: required inputs, outputs, tools/algorithms (AST parsing, call graph, dataflow/side effects, type inference, lifecycle inference), failure modes, and fallbacks."

## 10. "CORRECTNESS" DEFINITION
**Prompt:**
"Define what 'correct' means for our code knowledge graph. Separate: structural correctness (calls/imports/etc.), semantic correctness (roles/layers), and epistemic correctness (confidence/provenance). For each: propose measurable metrics, tests, and minimum acceptable thresholds."

## 11. BENCHMARK & DATASET DESIGN
**Prompt:**
"Design a 'Validation Pack' for our model: repo selection criteria, sampling strategy (nodes across levels), annotation guidelines, gold sets, evaluation metrics, and a regression suite to prevent backsliding when taxonomy evolves."

## 12. SIMILARITY METRICS (8D MANIFOLD)
**Prompt:**
"We treat each node as a point in an 8D coordinate system. Propose distance metrics (symbolic + learned), embedding strategies, and ways to validate that 'nearby' nodes are truly semantically similar for developer tasks (search, refactor impact, onboarding)."

## 13. ENTROPY/COMPLEXITY ACROSS LEVELS
**Prompt:**
"We want complexity/entropy measures at multiple levels (e.g., function/file/system). Propose a mathematically sound definition of 'entropy by level', how to compute it from atom distributions/edges, and how to validate correlation with maintainability outcomes."

## 14. GOVERNANCE & EVOLUTION
**Prompt:**
"Define a governance process for evolving atoms/roles/dimensions: versioning, migration rules, deprecation, backward compatibility, and a 'scientific log' of hypothesis → test → revision. Include how to communicate uncertainty ('we don't truly know yet') without weakening usefulness."
