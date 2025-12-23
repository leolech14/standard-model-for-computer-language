# Complete Naming Schema: Standard Model of Code

**Version:** 2.0 (Physics-First)  
**Status:** Canonical Reference  
**Last Updated:** 2025-12-23

This document defines the **official terminology** for all concepts in the Standard Model of Code framework.

---

## Core Principle

**Physics Metaphor Throughout:**
- Analyzing code = Running a particle collider
- Code elements = Particles
- Issues = Antimatter
- Dependencies = Interactions

---

## 1. Fundamental Units

| Concept | Official Name | Aliases (Deprecated) | Definition |
|---------|---------------|---------------------|------------|
| **Code element** | `particle` | node, component, element, symbol | Any discrete unit of code (function, class, module) |
| **Collection of elements** | `particles` | nodes, components | Plural of particle |
| **Syntactic type** | `atom` | ast_type, kind | The 167-atom taxonomy classification |
| **Semantic role** | `role` | purpose, intent | The 27-role classification (Query, Command, etc.) |
| **Code container** | `codebase` | repository, project | The analyzed code |

---

## 2. Analysis Concepts

| Concept | Official Name | Aliases (Deprecated) | Definition |
|---------|---------------|---------------------|------------|
| **Analysis tool** | `Collider` | analyzer, scanner | The tool that analyzes code |
| **Analysis run** | `collision` | analysis, scan | One execution of the Collider |
| **Analysis output** | `collision_result` | analysis_result, output | The data produced by a collision |
| **Dependency** | `interaction` | edge, relationship, dependency | Link between two particles |
| **Call graph** | `interaction_network` | dependency_graph, call_graph | Graph of all interactions |

---

## 3. Classifications

### 3.1 Syntactic (WHAT)
| Concept | Official Name | Aliases (Deprecated) | Example |
|---------|---------------|---------------------|---------|
| **167 taxonomy** | `atoms` | syntactic_types | DAT.BIT.A, LOG.FNC.M |
| **Atom group** | `family` | category | 16 families (e.g., Logic, Data) |
| **Atom phase** | `phase` | dimension | 4 phases (Data, Logic, Org, Exec) |

### 3.2 Semantic (WHY)
| Concept | Official Name | Aliases (Deprecated) | Example |
|---------|---------------|---------------------|---------|
| **27 taxonomy** | `roles` | semantic_types, purposes | Query, Command, Entity |
| **Role group** | `archetype` | role_family | CRUD roles, Structural roles |

### 3.3 Behavioral (HOW)
| Concept | Official Name | Aliases (Deprecated) | Dimensions |
|---------|---------------|---------------------|------------|
| **RPBL scores** | `behavior` | behavioral_dimensions | R, P, B, L (1-10 each) |
| **Responsibility** | `R` | complexity_score | How much it does (1=focused, 10=bloated) |
| **Purity** | `P` | side_effect_score | Functional purity (1=impure, 10=pure) |
| **Boundary** | `B` | coupling_score | External dependencies (1=isolated, 10=coupled) |
| **Lifecycle** | `L` | lifecycle_score | Long-lived vs short-lived |

---

## 4. Architectural Concepts

| Concept | Official Name | Aliases (Deprecated) | Definition |
|---------|---------------|---------------------|------------|
| **Architecture layer** | `layer` | tier, level | Infrastructure, Domain, Application, Interface |
| **Layer violation** | `antimatter` | violation, smell | Cross-layer dependency (e.g., Domain → Infrastructure) |
| **God Class** | `massive_particle` | god_class, blob | Class with >10 methods + high coupling |
| **All violations** | `antimatter` | violations, issues, smells | Umbrella term for all detected problems |
| **Violation type** | `antimatter_type` | violation_kind | Massive particles, cross-layer, circular, etc. |

---

## 5. Pipeline Stages

| Stage | Official Name | Aliases (Deprecated) | Output |
|-------|---------------|---------------------|--------|
| **Stage 1** | `Classification` | Atom Detection | Atoms assigned |
| **Stage 2** | `Role Assignment` | Semantic Analysis | Roles assigned |
| **Stage 3** | `Antimatter Detection` | Violation Scan | Violations found |
| **Stage 4** | `Prediction` | Missing Component Detection | Predictions made |
| **Stage 5** | `Insight Generation` | Actionable Recommendations | Insights generated |
| **Stage 6** | `Purpose Field Detection` | Layer Analysis | Layers assigned |
| **Stage 7** | `Execution Flow Tracing` | Flow Analysis | Entry points, orphans |
| **Stage 8** | `Performance Prediction` | Cost Estimation | Hotspots identified |
| **Stage 9** | `Summary Generation` | Proof Document | JSON summary |
| **Stage 10** | `Visualization` | Report Generation | Interactive HTML |

---

## 6. Data Structures

### 6.1 Core Schema
| Concept | Official Name | Type | Required Fields |
|---------|---------------|------|-----------------|
| **Single element** | `Particle` | Object | `{id, name, kind, atom, role, layer}` |
| **Single dependency** | `Interaction` | Object | `{source, target, type}` |
| **Full analysis** | `CollisionResult` | Object | `{particles, interactions, antimatter, stats}` |

### 6.2 File Outputs
| File | Official Name | Contents |
|------|---------------|----------|
| **Main output** | `collider_output.json` | Complete collision result |
| **CSV export** | `particles.csv` | Flat particle list |
| **Visualization** | `collider_report.html` | Interactive visualization |
| **Summary** | `proof_output.json` | Pipeline proof document |

---

## 7. Antimatter Types

| Type | Official Name | Detection Criteria | Example |
|------|---------------|-------------------|---------|
| **God class** | `massive_particle` | >10 methods + high coupling | UserService with DB, UI, logic |
| **Cross-layer** | `layer_breach` | Domain → Infrastructure | User imports Database |
| **Circular dependency** | `feedback_loop` | A → B → A | Module1 ↔ Module2 |
| **High coupling** | `entanglement` | >20 dependencies | Util class used everywhere |
| **Long method** | `elongated_particle` | >50 lines | 200-line function |

---

## 8. Metrics & Scores

| Metric | Official Name | Range | Interpretation |
|--------|---------------|-------|----------------|
| **Overall quality** | `atomic_compliance` | 0-100 | How well-structured the code is |
| **Violation severity** | `antimatter_density` | 0-1 | % of particles that are violations |
| **Performance risk** | `hotspot_intensity` | 0-10 | Computational bottleneck risk |
| **Coverage** | `detection_coverage` | 0-100% | % of code analyzed |
| **Confidence** | `classification_confidence` | 0-100% | How sure the classifier is |

---

## 9. API & Code

### 9.1 Python API
```python
from collider import analyze

# Run collision
result = analyze("./my_repo")

# Access particles
for particle in result.particles:
    print(f"{particle.name}: {particle.role} ({particle.atom})")

# Check antimatter
if result.antimatter.massive_particles:
    print(f"Found {len(result.antimatter.massive_particles)} massive particles")

# Interactions
network = result.interaction_network
```

### 9.2 CLI
```bash
# Run collision
collider analyze ./my_repo

# Output: collider_output.json
```

### 9.3 JSON Schema
```json
{
  "codebase": "standard-model-of-code",
  "collision_timestamp": "2025-12-23T01:00:00Z",
  "particles": [
    {
      "id": "unique_id",
      "name": "function_name",
      "atom": "LOG.FNC.M",
      "role": "Query",
      "layer": "Infrastructure",
      "behavior": {"R": 7, "P": 9, "B": 3, "L": 5}
    }
  ],
  "interactions": [
    {"source": "id1", "target": "id2", "type": "CALLS"}
  ],
  "antimatter": {
    "massive_particles": [...],
    "layer_breaches": [...],
    "feedback_loops": [...]
  },
  "stats": {
    "particle_count": 78346,
    "antimatter_density": 0.12,
    "atomic_compliance": 94.2
  }
}
```

---

## 10. Documentation Terms

| Document Type | Official Name | Purpose |
|---------------|---------------|---------|
| **Main doc** | `README.md` | Project overview |
| **Theory doc** | `THEORY_MAP.md` | Theoretical foundations |
| **Schema doc** | `CANONICAL_SCHEMA.md` | Data structure reference |
| **Atom list** | `ATOMS_REFERENCE.md` | 167-atom taxonomy |
| **Math proof** | `FORMAL_PROOF.md` | Mathematical completeness proof |
| **Lean proofs** | `mechanized_proofs/` | Machine-verified theorems |

---

## 11. Deprecated Terms (DO NOT USE)

| Old Term | New Term | Reason |
|----------|----------|--------|
| `node` | `particle` | Generic, overloaded |
| `component` | `particle` | Confusing (React components) |
| `element` | `particle` | Too generic |
| `symbol` | `particle` | Compiler-specific |
| `violation` | `antimatter` | Less evocative |
| `god_class` | `massive_particle` | Keep for familiarity |
| `edge` | `interaction` | Graph theory jargon |
| `dependency` | `interaction` | More specific than needed |
| `graph.json` | `collider_output.json` | Not descriptive |
| `unified_analysis.json` | `collider_output.json` | Verbose |

---

## 12. Migration Guide

### From Old to New
```python
# OLD
nodes = analysis.components
for node in nodes:
    if node.kind == "function":
        check_violations(node)

# NEW
particles = collision.particles
for particle in particles:
    if particle.atom.startswith("LOG.FNC"):
        check_antimatter(particle)
```

### File Renames
```bash
# OLD
output/graph.json
output/components.csv

# NEW
output/collider_output.json
output/particles.csv
```

---

## 13. Naming Conventions

### Code Style
- **Classes:** PascalCase (`Particle`, `CollisionResult`)
- **Functions:** snake_case (`analyze_codebase`, `detect_antimatter`)
- **Variables:** snake_case (`particle_count`, `antimatter_density`)
- **Constants:** UPPER_SNAKE_CASE (`MAX_PARTICLES`, `ANTIMATTER_THRESHOLD`)

### File Style
- **Data:** snake_case with extension (`collider_output.json`, `particles.csv`)
- **Docs:** UPPER_SNAKE_CASE or Title Case (`README.md`, `THEORY_MAP.md`)
- **Scripts:** snake_case (`analyze.py`, `validate_annotations.py`)

---

## 14. Visual/UI Terms

| UI Element | Official Name | Display Text |
|------------|---------------|--------------|
| **Main view** | Collision View | "Collision Results" |
| **Particle list** | Particle Browser | "Browse Particles" |
| **Violation panel** | Antimatter Detector | "Antimatter Detected" |
| **Graph view** | Interaction Network | "Interaction Network" |
| **Stats panel** | Collision Summary | "Collision Summary" |

---

## 15. Glossary (Quick Reference)

| Term | One-Line Definition |
|------|---------------------|
| **Particle** | A discrete unit of code (function, class, module) |
| **Atom** | Syntactic classification (1 of 167 types) |
| **Role** | Semantic classification (1 of 27 types) |
| **Behavior** | RPBL scores (4 dimensions, 1-10 each) |
| **Layer** | Architectural tier (Infrastructure, Domain, App, Interface) |
| **Interaction** | Dependency between two particles |
| **Antimatter** | Code that violates architectural principles |
| **Massive Particle** | Class/function doing too much (God Class) |
| **Collision** | One analysis run |
| **Collider** | The analysis tool |
| **Collision Result** | Output of an analysis |

---

## 16. Frequently-Used Concepts

### 16.1 Validation & Testing
| Concept | Official Name | Definition |
|---------|---------------|------------|
| **Manual annotation** | `ground_truth` | Human-labeled data for validation |
| **Accuracy measurement** | `validation` | Comparing predictions vs ground truth |
| **Test dataset** | `benchmark` | Collection of codebases for testing |
| **Sample for annotation** | `validation_sample` | Subset selected for manual review |
| **Annotation task** | `labeling` | Process of manually classifying particles |

### 16.2 Research & Academic
| Concept | Official Name | Definition |
|---------|---------------|------------|
| **Formal proof** | `mathematical_proof` | Logical derivation of theorems |
| **Mechanized proof** | `lean_proof` | Machine-verified proof in Lean 4 |
| **Axiom** | `axiom` | Unproven assumption (validated empirically) |
| **Theorem** | `theorem` | Proven mathematical statement |
| **Empirical validation** | `empirical_study` | Data-driven validation |
| **Research question** | `RQ` | Hypothesis to test (e.g., RQ1: Completeness) |

### 16.3 Workflow & Process
| Concept | Official Name | Definition |
|---------|---------------|------------|
| **Quick validation** | `mini_validation` | 500-sample quick test |
| **Full validation** | `benchmark_study` | 100+ repo comprehensive test |
| **Pipeline stage** | `stage` | One of 10 processing steps |
| **Analysis run** | `collision` | One execution of Collider |
| **Batch analysis** | `batch_collision` | Analyzing multiple codebases |

### 16.4 Quality Metrics
| Concept | Official Name | Range/Unit | Definition |
|---------|---------------|------------|------------|
| **Classification accuracy** | `accuracy` | 0-100% | % of correct role predictions |
| **Coverage** | `coverage` | 0-100% | % of particles successfully classified |
| **Confidence** | `confidence` | 0-100% | Classifier certainty score |
| **Inter-rater agreement** | `kappa` (κ) | -1 to 1 | Agreement between annotators |
| **Mutual information** | `MI` | bits | Statistical independence measure |

### 16.5 Data & Files
| Concept | Official Name | Format | Contains |
|---------|---------------|--------|----------|
| **Main output** | `collider_output.json` | JSON | Full collision result |
| **Flat export** | `particles.csv` | CSV | Particle list (spreadsheet) |
| **Visualization** | `collider_report.html` | HTML | Interactive report |
| **Annotation file** | `validation_samples.csv` | CSV | Samples for manual review |
| **Results file** | `validation_report.md` | Markdown | Accuracy metrics |

### 16.6 Development & Tools
| Concept | Official Name | Type | Purpose |
|---------|---------------|------|---------|
| **Command-line tool** | `collider` CLI | Binary | Run analysis from terminal |
| **Python API** | `collider` package | Library | Programmatic access |
| **Sampling script** | `sample_for_mini_validation.py` | Script | Generate validation samples |
| **Validation script** | `validate_annotations.py` | Script | Compute accuracy |
| **Proof verifier** | `lean` | Tool | Verify mechanized proofs |

### 16.7 Documentation Types
| Type | Official Name | Audience | Purpose |
|------|---------------|----------|---------|
| **User guide** | `README.md` | Users | Getting started |
| **Theory doc** | `THEORY_MAP.md` | Researchers | Theoretical foundations |
| **API reference** | `NAMING_SCHEMA.md` | Developers | Terminology reference |
| **Proof doc** | `FORMAL_PROOF.md` | Academics | Mathematical rigor |
| **Roadmap** | `roadmaps/*.md` | Contributors | Implementation plans |
| **Validation plan** | `VALIDATION_PLAN.md` | Researchers | Empirical methodology |

### 16.8 Common Abbreviations
| Abbreviation | Full Name | Usage |
|--------------|-----------|-------|
| **RPBL** | Responsibility-Purity-Boundary-Lifecycle | Behavioral dimensions |
| **MI** | Mutual Information | Orthogonality metric |
| **RQ** | Research Question | Hypothesis (e.g., RQ1, RQ2) |
| **CI** | Confidence Interval | Statistical range (95% CI) |
| **DAG** | Directed Acyclic Graph | Pipeline structure |
| **AST** | Abstract Syntax Tree | Code structure |
| **LOC** | Lines of Code | Size metric |
| **κ** (kappa) | Cohen's Kappa | Inter-rater reliability |

### 16.9 Particle States
| State | Official Name | Definition |
|-------|---------------|------------|
| **Classified** | `classified` | Has atom + role assigned |
| **Unclassified** | `unclassified` | Missing atom or role |
| **High-confidence** | `confident` | Confidence >75% |
| **Low-confidence** | `uncertain` | Confidence <50% |
| **Violated** | `antimatter` | Architectural violation detected |
| **Predicted** | `predicted` | Inferred (not directly observed) |

### 16.10 Common Phrases
| Phrase | Official Term | Example |
|--------|---------------|---------|
| "Run the analysis" | `Execute collision` | "Let's execute a collision on this repo" |
| "Check for issues" | `Scan for antimatter` | "Scanning for antimatter..." |
| "God Class detected" | `Massive particle found` | "Found 3 massive particles" |
| "Classify the code" | `Assign atoms and roles` | "Assigning roles to particles..." |
| "Dependency graph" | `Interaction network` | "Visualizing interaction network" |
| "Code smell" | `Antimatter signature` | "Detected antimatter signature" |

---

**This is the canonical reference. All code, docs, and communication should use these terms.**

