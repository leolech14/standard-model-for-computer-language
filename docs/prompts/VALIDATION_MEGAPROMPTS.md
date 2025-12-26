# STANDARD CODE VALIDATION MEGAPROMPTS
> Comprehensive prompts for rigorous theory validation.

---

## MEGAPROMPT 1: CLAIMS LEDGER & FALSIFIABILITY

### Context
You are a scientific auditor analyzing the "Standard Code" theory—a proposed universal ontology for software.
The theory makes many claims: some are definitions (unfalsifiable by design), some are empirical (testable), some are analogies (illustrative), and some are normative goals (aspirations).

### Your Task
Given the attached `STANDARD_CODE.md` document, systematically extract and categorize every claim.

### Instructions

1. **Extract Claims**: Read each section and extract every statement that asserts something about code, structure, or classification.

2. **Categorize Each Claim** as one of:
   - **Definition**: A term being defined (e.g., "A Node is L3") — unfalsifiable, evaluated for clarity and consistency
   - **Empirical Claim**: A testable assertion (e.g., "167 atoms cover all AST types") — requires evidence
   - **Analogy**: A comparison to another domain (e.g., "Functions are like atoms in physics") — evaluated for pedagogical value
   - **Normative Goal**: A desired outcome (e.g., "Every question should be answerable by one lens") — evaluated for feasibility
   - **Implementation Assumption**: A code/tooling dependency (e.g., "Tree-sitter is used for parsing") — evaluated for portability

3. **For Each Empirical Claim, Provide**:
   - (a) **Supporting Evidence**: What data/experiment would confirm this?
   - (b) **Falsification Criteria**: What observation would disprove this?
   - (c) **Confidence Interpretation**: What does "90% confidence" mean here?
   - (d) **Scope Limitations**: Under what conditions does this NOT apply?

4. **Output Format**: A structured table or JSON with columns:
   ```
   | Claim ID | Text | Section | Type | Evidence Required | Falsification | Scope |
   ```

### Expected Output
A "Claims Ledger" document that could be used as a scientific checklist for validation.

---

## MEGAPROMPT 2: LENS SYSTEM VALIDATION

### Context
Standard Code defines 8 "Lenses" (perspectives) for understanding code:
1. Identity (What is it called?)
2. Ontology (What exists?)
3. Classification (What kind is it?)
4. Composition (How is it structured?)
5. Relationships (How is it connected?)
6. Transformation (What does it do?)
7. Semantics (What does it mean?)
8. Epistemology (How certain are we?)

The claim is that these 8 lenses are **complete** (answer every question) and **orthogonal** (non-overlapping).

### Your Task
Test this claim against real developer questions.

### Instructions

1. **Input**: A list of 50 real developer questions (examples below):
   - "Why is this function so slow?"
   - "What calls this method?"
   - "Is this safe to delete?"
   - "What is this variable for?"
   - "Who wrote this?"
   - "When was this last changed?"
   - "What would break if I renamed this?"

2. **For Each Question**:
   - Map it to a **primary lens** (the main perspective needed)
   - Map it to **secondary lenses** (if applicable)
   - Rate the fit: **Clean** (perfect match), **Stretched** (fits with interpretation), **Gap** (doesn't fit)

3. **Identify Gaps**:
   - Questions that don't fit any lens
   - Questions that require merging lenses in non-obvious ways

4. **Propose Fixes** (if gaps exist):
   - (a) Add a new lens (define it precisely)
   - (b) Redefine an existing lens to absorb the gap
   - (c) Create a "lens composition rule" for multi-perspective questions

### Expected Output
- Mapping table: Question → Lens(es) → Fit Rating
- Gap analysis with proposed fixes
- Verdict: Are 8 lenses sufficient? If not, what's the minimal extension?

---

## MEGAPROMPT 3: DIMENSION ORTHOGONALITY & BOUNDARY CASES

### Context
Standard Code classifies every code entity along 8 dimensions:
1. **WHAT** (167 atom types)
2. **LAYER** (Interface, Application, Core, Infrastructure, Test)
3. **ROLE** (33 canonical roles)
4. **BOUNDARY** (Internal, Input, I/O, Output)
5. **STATE** (Stateful, Stateless)
6. **EFFECT** (Pure, Read, Write, ReadModify)
7. **ACTIVATION** (Direct, Event, Time)
8. **LIFETIME** (Transient, Session, Global)

The claim is that these dimensions are **orthogonal** (independent) and **mutually exclusive** (each entity has exactly one value per dimension).

### Your Task
Rigorously test orthogonality and identify boundary cases.

### Instructions

1. **For Each Dimension**:
   - Define each value **precisely** (necessary and sufficient conditions)
   - List 3-5 **boundary cases** (entities that are hard to classify)
   - Specify **constraints** (e.g., "If EFFECT=Pure, then STATE must be Stateless")

2. **Orthogonality Test**:
   - For every pair of dimensions (28 pairs), ask:
     - Can every combination of values exist? (e.g., Pure + Stateful?)
     - If not, document the constraint.

3. **"Unknown" Policy**:
   - Define when "Unknown" is a valid value
   - Distinguish "Unknown" (not yet classified) from "N/A" (dimension doesn't apply)
   - Propose rules to prevent "Unknown" from becoming a catch-all

4. **Mutual Exclusivity Violations**:
   - Find cases where an entity could legitimately have 2 values (e.g., both "Direct" and "Event" activation)
   - Propose either: (a) new values, (b) primary/secondary scheme, or (c) redefine dimensions

### Expected Output
- Dimension definition table with precise boundaries
- Orthogonality matrix (28 pairs)
- Boundary case examples
- "Unknown" policy document

---

## MEGAPROMPT 4: ATOM COVERAGE & AST MAPPING

### Context
Standard Code defines 167 "Atoms" organized into 4 Phases × 4 Families = 16 Families.
The claim is that these 167 atoms **completely cover** all AST node types across all programming languages.

### Your Task
Design and execute a coverage test.

### Instructions

1. **Select Target Languages**: Python, TypeScript, Java, Go, Rust

2. **For Each Language**:
   - Extract the official AST node type list (e.g., Tree-sitter grammar)
   - Create a **crosswalk table**: `AST Node Kind → Atom ID`
   - Mark each mapping as: **Direct** (1:1), **Merged** (N:1), **Split** (1:N), **Missing**

3. **Coverage Metrics**:
   - **Coverage %**: AST nodes mapped / Total AST nodes
   - **Atom Utilization %**: Atoms used / 167
   - **Unmapped Nodes**: List with proposed fix (new atom or merge)

4. **Stability Test**:
   - If language X adds a new AST node in version Y, how do we handle it?
   - Propose a versionless atom schema OR versioned atom registry

5. **Evolution Protocol**:
   - If we must add atom #168, what's the process?
   - How do we migrate existing analysis data?

### Expected Output
- Crosswalk tables for 5 languages
- Coverage summary (should be >95%)
- Unmapped node list with proposals
- Evolution protocol document

---

## MEGAPROMPT 5: ROLE TAXONOMY VALIDATION

### Context
Standard Code defines 33 canonical roles (Query, Command, Repository, etc.).
Roles are assigned based on name patterns, decorators, call graph position, and LLM inference.

### Your Task
Design a human annotation study to validate role taxonomy.

### Instructions

1. **Study Design**:
   - **Sample**: 200 functions from 10 diverse repos (20 each)
   - **Annotators**: 3 independent human experts
   - **Task**: Assign one role to each function (or "Unknown")

2. **Annotation Guidelines** (create outline):
   - Role definitions with examples
   - Decision tree for ambiguous cases
   - "Unknown" criteria

3. **Metrics**:
   - **Inter-Annotator Agreement**: Fleiss' kappa
   - **Confusion Matrix**: Which role pairs are confused most?
   - **Classifier Agreement**: Human vs. Standard Code classifier

4. **Post-Study Actions**:
   - Merge confused role pairs OR add distinguishing features
   - Revise role definitions based on annotator feedback
   - Update classifier training data

5. **Backward Compatibility**:
   - If we merge roles A and B into AB, how do old analyses migrate?
   - Version scheme for role taxonomy

### Expected Output
- Annotation guideline outline
- Study protocol document
- Analysis plan with metrics
- Migration protocol

---

## MEGAPROMPT 6: DETECTION SIGNALS & EVIDENCE MODEL

### Context
Classification in Standard Code is based on multiple signals:
- Name patterns (prefix/suffix)
- File path patterns
- Decorators/annotations
- Call graph position
- Import dependencies
- Field analysis (stateful/stateless)
- Scope analysis (lifetime)
- LLM inference (fallback)

### Your Task
Create a formal evidence model for classification.

### Instructions

1. **For Each Dimension and Role**, list all detection features:
   ```
   Dimension/Role → [Feature1: weight, Feature2: weight, ...]
   ```

2. **Define an Evidence Record Schema**:
   ```json
   {
     "entity_id": "...",
     "dimension": "ROLE",
     "candidate_value": "Repository",
     "evidence": [
       {"feature": "suffix_match", "value": "Repository", "strength": 0.95},
       {"feature": "imports_db_module", "strength": 0.7},
       {"feature": "call_graph_position", "value": "leaf", "strength": 0.3}
     ],
     "counter_evidence": [
       {"feature": "no_persistence_calls", "strength": -0.5}
     ],
     "final_confidence": 0.78,
     "confidence_update_rule": "weighted_sum_with_counter"
   }
   ```

3. **Confidence Update Rules**:
   - Simple weighted sum
   - Bayesian update
   - Rule-based overrides (e.g., decorator always wins)

4. **Provenance Tracking**:
   - Every classification must trace back to evidence
   - Support for "explain this classification" queries

### Expected Output
- Feature catalog (all signals with weights)
- Evidence record schema
- Confidence computation algorithm
- Provenance query examples

---

## MEGAPROMPT 7: CONFIDENCE & CALIBRATION SYSTEM

### Context
Standard Code assigns confidence scores to classifications (0-100%).
The claim is that these confidence scores are **calibrated** (when we say 90%, we are right 90% of the time).

### Your Task
Design a calibration and epistemics system.

### Instructions

1. **Define What Confidence Means**:
   - Probability of correctness? Agreement with gold standard? Model uncertainty?
   - Choose one interpretation and document it

2. **Confidence Computation Pipeline**:
   - Step 1: Rule-based confidence (pattern match strength)
   - Step 2: Model-based confidence (ML classifier probability)
   - Step 3: Cross-check adjustment (if call graph agrees, boost; if conflicts, reduce)
   - Step 4: Final aggregation

3. **Calibration Test**:
   - Take all classifications with confidence 85-90%
   - Measure actual accuracy against gold set
   - Plot: Expected vs. Actual (should be diagonal)
   - Compute ECE (Expected Calibration Error)

4. **Recalibration**:
   - If miscalibrated, apply Platt scaling or isotonic regression
   - Document recalibration procedure

5. **Human Review Escalation**:
   - Threshold for automatic human review (e.g., <60% confidence)
   - Priority queue by impact (high-connectivity nodes first)

6. **Confidence Evolution**:
   - As more code is analyzed, do confidence weights need re-tuning?
   - Online learning? Periodic batch retraining?

### Expected Output
- Confidence definition document
- Computation pipeline specification
- Calibration protocol
- Escalation policy
- Evolution/retraining schedule

---

## MEGAPROMPT 8: EDGE SEMANTICS & GRAPH SCHEMA

### Context
Standard Code defines 6 edge families:
1. Structural (contains, is_part_of)
2. Dependency (calls, imports, uses)
3. Inheritance (inherits, implements, mixes_in)
4. Semantic (is_a, has_role, serves, delegates_to)
5. Temporal (initializes, triggers, disposes, precedes)
6. (possibly more)

### Your Task
Define a rigorous graph schema with full semantics.

### Instructions

1. **For Each Edge Type**:
   - **Definition**: Precise meaning
   - **Source/Target Constraints**: What entity types can be connected?
   - **Properties**: weight, confidence, static/dynamic, etc.
   - **Inverse**: What's the reverse edge? (e.g., calls ↔ called_by)
   - **Transitivity**: Is it transitive? (e.g., contains is transitive)
   - **Composability**: Can edges combine? (e.g., inherits + implements = mixed_inheritance)

2. **Extraction Method**:
   - Static analysis: AST-based
   - Dynamic analysis: Runtime tracing
   - Inference: Graph-based propagation

3. **Validation Checks**:
   - Inverse consistency: If A→B exists, B→A exists (for symmetric edges)
   - Transitivity closure: If enabled, verify closure
   - Level constraints: Contains only goes higher→lower

4. **Schema Language**:
   - Propose a formal schema (JSON Schema, Cypher constraints, etc.)
   - Tool to validate graph against schema

### Expected Output
- Edge schema document (all edge types with full metadata)
- Extraction method per edge
- Validation query set
- Schema definition file

---

## MEGAPROMPT 9: ANALYSIS PIPELINE ARCHITECTURE

### Context
To populate the 8D classification + edge graph, a multi-stage analysis pipeline is needed.

### Your Task
Design the dependency-ordered analysis pipeline.

### Instructions

1. **Pipeline Stages** (ordered by dependency):
   ```
   1. AST Parsing (source → tree)
   2. Symbol Resolution (tree → named entities)
   3. Call Graph Construction (entities → calls edges)
   4. Import Graph Construction (files → imports edges)
   5. Type Inference (entities → types)
   6. Containment Graph (all → structural edges)
   7. D1 Classification (entities → atoms)
   8. D2-D8 Classification (entities → dimensions)
   9. Role Assignment (entities → roles)
   10. Edge Enrichment (add semantic/temporal edges)
   11. Confidence Aggregation
   12. Graph Validation
   ```

2. **For Each Stage**:
   - **Inputs**: What data is required?
   - **Outputs**: What is produced?
   - **Tools/Algorithms**: Tree-sitter? Call graph algorithm? etc.
   - **Failure Modes**: What can go wrong? (e.g., unparseable file)
   - **Fallbacks**: What to do on failure? (skip? estimate? LLM fallback?)

3. **Parallelization**:
   - Which stages can run in parallel?
   - Dependency DAG visualization

4. **Incremental Updates**:
   - If a single file changes, what re-runs?
   - Cache invalidation strategy

### Expected Output
- Pipeline stage table
- Dependency DAG
- Failure/fallback matrix
- Incremental update protocol

---

## MEGAPROMPT 10: CORRECTNESS DEFINITIONS

### Context
What does it mean for the Standard Code knowledge graph to be "correct"?

### Your Task
Define correctness across multiple dimensions.

### Instructions

1. **Structural Correctness**:
   - All `calls` edges are real call relationships (no false positives)
   - All `imports` edges are real import relationships
   - All `contains` edges are valid containment
   - **Metric**: Precision/Recall vs. ground truth call graph

2. **Semantic Correctness**:
   - Role assignments are accurate (match human judgment)
   - Layer assignments are accurate
   - **Metric**: Accuracy vs. human-labeled gold set

3. **Epistemic Correctness**:
   - Confidence scores are calibrated
   - Provenance is traceable
   - **Metric**: ECE (Expected Calibration Error), audit pass rate

4. **Completeness**:
   - All entities in source code are represented
   - All relationships are captured
   - **Metric**: Coverage %

5. **Consistency**:
   - No logical contradictions (e.g., X is_a Repository AND is_a Controller)
   - All constraints satisfied
   - **Metric**: Constraint violation count

6. **Minimum Thresholds** (propose for each):
   - Structural: Precision ≥ X%, Recall ≥ Y%
   - Semantic: Accuracy ≥ Z%
   - Epistemic: ECE ≤ W%

### Expected Output
- Correctness taxonomy
- Metric definitions
- Minimum acceptable thresholds
- Test protocols for each

---

## MEGAPROMPT 11: BENCHMARK DATASET DESIGN

### Context
To validate Standard Code, we need a high-quality benchmark dataset.

### Your Task
Design the "Validation Pack."

### Instructions

1. **Repository Selection Criteria**:
   - Size: Small (1K LOC), Medium (10K LOC), Large (100K+ LOC)
   - Architecture: Monolith, Microservices, DDD, Clean Architecture
   - Languages: Python, TypeScript, Java (minimum)
   - Popularity: At least 1K stars (quality signal)
   - Diversity: Different domains (web, CLI, data, infrastructure)

2. **Sampling Strategy**:
   - Per repo: 50 functions across all layers
   - Stratified: Equal representation of roles (as much as possible)
   - Edge cases: Intentionally include ambiguous code

3. **Annotation**:
   - Human annotators assign: Atom, Role, Layer, and one Semantic Edge
   - Confidence rating from annotator (self-assessed certainty)
   - Disagreement resolution protocol

4. **Gold Set Structure**:
   ```json
   {
     "entity_id": "repo:file:function_name",
     "atom": "LOG.FNC.M",
     "role": "Repository",
     "layer": "Infrastructure",
     "confidence": 0.95,
     "annotator_notes": "..."
   }
   ```

5. **Regression Suite**:
   - When taxonomy changes, re-run on gold set
   - Track accuracy over versions
   - Alert on regression

### Expected Output
- Repo selection list (10+ repos)
- Sampling protocol
- Annotation guidelines
- Gold set schema
- Regression protocol

---

## MEGAPROMPT 12: SEMANTIC SIMILARITY ON 8D MANIFOLD

### Context
If every code entity is a point in 8D space, we can compute "distances" between entities.
This enables search, clustering, and impact analysis.

### Your Task
Design similarity metrics for the 8D manifold.

### Instructions

1. **Distance Metrics**:
   - **Hamming Distance**: Count of differing dimensions
   - **Weighted Hamming**: Different weights per dimension
   - **Embedding Distance**: Learn embeddings, use cosine similarity
   - **Graph Distance**: Shortest path in the call/dependency graph

2. **Weighting Scheme**:
   - Which dimensions matter more for similarity?
   - Task-dependent weights (search vs. refactor impact)

3. **Embedding Strategies**:
   - One-hot encode each dimension, concatenate → 8D vector
   - Train an autoencoder on code → learned embedding
   - Use pre-trained code embeddings (CodeBERT, etc.)

4. **Validation**:
   - "Nearest neighbor" test: Do developers agree similar entities are similar?
   - Task: "Given function X, find most similar functions"
   - Metric: Developer satisfaction score (1-5)

5. **Use Cases**:
   - **Search**: "Find all Repositories that are Stateless and Pure"
   - **Clustering**: Automatically group similar functions
   - **Impact Analysis**: "If I change X, what else is similar and might need change?"

### Expected Output
- Distance metric definitions
- Weighting scheme proposal
- Embedding architecture
- Validation protocol
- Use case examples

---

## MEGAPROMPT 13: ENTROPY & COMPLEXITY MEASURES

### Context
Standard Code enables measuring complexity at multiple scales:
- L3 (function): How complex is this function?
- L4 (class): How complex is this class?
- L5 (file): How complex is this file?
- L7 (system): How complex is this system?

### Your Task
Define mathematically sound complexity measures.

### Instructions

1. **Entropy Definition**:
   - Shannon entropy over atom type distribution:
     $H(level) = -\sum P(atom_i) \log_2 P(atom_i)$
   - High entropy = diverse atoms = less predictable

2. **Complexity Measures**:
   - **Structural Complexity**: Edge count, depth, cyclomatic
   - **Semantic Complexity**: Role diversity, layer mixing
   - **Cognitive Complexity**: Estimated human effort to understand

3. **Aggregation Across Levels**:
   - L3 complexity → average → L4 complexity
   - L4 complexity → weighted sum → L5 complexity
   - ...and so on

4. **Correlation with Outcomes**:
   - Hypothesis: High entropy correlates with bugs
   - Hypothesis: High complexity correlates with slow pull request reviews
   - Test against historical data (if available)

5. **Actionable Thresholds**:
   - Propose "too complex" thresholds (e.g., "Function entropy > 4.0 = warning")

### Expected Output
- Entropy formula
- Complexity measures per level
- Aggregation rules
- Correlation hypotheses
- Threshold recommendations

---

## MEGAPROMPT 14: GOVERNANCE & EVOLUTION PROTOCOL

### Context
Standard Code is a living theory. Atoms, roles, and dimensions will evolve as we learn more.

### Your Task
Design a governance and evolution process.

### Instructions

1. **Versioning Scheme**:
   - Schema version: `2.0.0` (MAJOR.MINOR.PATCH)
   - MAJOR: Breaking changes (atom removed, role redefined)
   - MINOR: Additive changes (new atom, new dimension value)
   - PATCH: Bug fixes (typo in definition)

2. **Change Proposal Process**:
   - RFC (Request for Comments) template
   - Evidence required for change (data, annotation results, etc.)
   - Approval criteria (consensus? empirical threshold?)

3. **Migration Rules**:
   - If atom A is removed, all A classifications become Unknown? or mapped to B?
   - If role X is split into X1 and X2, how is historical data updated?
   - Provide migration scripts or rules

4. **Backward Compatibility**:
   - Analysis outputs must declare schema version
   - Tools must handle multiple versions gracefully
   - Deprecation warnings before removal

5. **Scientific Log**:
   - Document: "We hypothesized X. We tested by Y. Result was Z. Decision: ..."
   - Make uncertainty explicit: "ROLE=33 is our current best model, not proven truth"

6. **Communication**:
   - CHANGELOG.md for each version
   - Uncertainty disclosure in documentation
   - User-facing impact summary

### Expected Output
- Version scheme document
- RFC template
- Migration protocol
- Compatibility policy
- Scientific log template

---

## USAGE

### To Execute a Megaprompt:

1. Copy the megaprompt text
2. Append the relevant context (e.g., `STANDARD_CODE.md` content)
3. Send to an LLM (Claude, GPT-4, etc.)
4. Review output and iterate

### Recommended Order:

| Phase | Prompts | Goal |
|-------|---------|------|
| **Foundation** | 1, 3, 4 | Validate core definitions |
| **Taxonomy** | 2, 5 | Validate lenses and roles |
| **Implementation** | 6, 7, 9 | Build detection and pipeline |
| **Validation** | 10, 11 | Build test infrastructure |
| **Advanced** | 8, 12, 13 | Edge semantics and metrics |
| **Governance** | 14 | Long-term sustainability |

---

> **"A theory without a validation plan is just a hypothesis. These prompts turn Standard Code into a testable scientific model."**
