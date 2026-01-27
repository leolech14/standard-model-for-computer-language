# Ontological Foundations of the Standard Model of Code

**Status:** ACTIVE
**Date:** 2026-01-27
**Scope:** Formal axioms, cross-disciplinary mappings, fundamentality stances
**Depends on:** MODEL.md, CODOME.md, CONTEXTOME.md, PROJECTOME.md, CONCORDANCES.md

---

## 1. The SMoC Ontological Partition: Axioms

Let **P** be the set of all project artifacts.

### Axiom A1 -- MECE Partition

```
P = C ⊔ X                    PROJECTOME = CODOME ⊔ CONTEXTOME
C ∩ X = ∅                    Mutually Exclusive
C ∪ X = P                    Collectively Exhaustive
```

| Universe | Definition | Membership Test |
|----------|-----------|-----------------|
| **CODOME (C)** | Executable, parseable artifacts | tree-sitter can extract an AST |
| **CONTEXTOME (X)** | Non-executable artifacts | Cannot be parsed into an executable AST |
| **PROJECTOME (P)** | All project contents | Exists in the repository |

This is a **disjoint union** (coproduct in category theory, sum type in type theory). Every file belongs to exactly one universe. The partition is decidable: the membership test is a computable predicate.

### Axiom A2 -- Different Analyzers Imply Different Semantics

CODOME admits **syntactic decomposition**: AST, symbols, edges, deterministic pipeline (Collider, 29 stages).

CONTEXTOME admits **rhetorical/semantic decomposition**: sections, paragraphs, sentences, words, semantic inference (ACI tiers, LLM reasoning).

Same project, two distinct kinds of internal structure. The analyzer difference is not incidental -- it reflects a fundamental difference in what "structure" means for each universe.

### Axiom A3 -- Concordances Are Not a Third Universe

A **Concordance** is a cross-cut: a purpose-aligned region spanning both sides.

```
k = <pi, C_pi, X_pi, sigma>
```

Where:
- **pi** = purpose (the shared WHY)
- **C_pi** ⊆ C = the CODOME slice serving pi
- **X_pi** ⊆ X = the CONTEXTOME slice describing pi
- **sigma** = alignment score function

Concordances **cover** but do not **partition**: a file may belong to multiple concordances. This makes Concordances a **covering** of P, not a decomposition.

```
Union(k_i) = P               Every file in at least one concordance
k_i ∩ k_j ≠ ∅  (allowed)    Overlap permitted
```

### Axiom A4 -- The 2x2 Concordance State Space

The four concordance health states are the cells of a definability/realizability grid:

```
                  | Docs Exist       | Docs Missing
------------------+------------------+-----------------
Code Exists       | CONCORDANT       | UNVOICED
                  | (purposes match) | (undocumented)
------------------+------------------+-----------------
                  | DISCORDANT       | (impossible for
Code Exists       | (purposes clash) | this cell)
------------------+------------------+-----------------
Code Missing      | UNREALIZED       | (empty -- no
                  | (spec w/o impl)  | artifact at all)
```

Simplified:

| State | Code? | Docs? | Purposes? |
|-------|-------|-------|-----------|
| **CONCORDANT** | Yes | Yes | Agree |
| **DISCORDANT** | Yes | Yes | Conflict |
| **UNVOICED** | Yes | No | N/A |
| **UNREALIZED** | No | Yes | N/A |

This becomes powerful when formalized as functor properties (Section 4), completeness measures (Section 2), or logical satisfiability.

---

## 2. Mathematics I: Sets, Relations, and Measures

### Coverage and Symmetry as Measures

Let **F** be a documentation mapping from code entities to doc entities.

- Dom(F) ⊆ C = entities for which docs exist
- Im(F) ⊆ X = docs that are "about" some code

```
Doc Coverage (complement of unvoiced rate):
    coverage = |Dom(F)| / |C|

Realizability (complement of unrealized rate):
    realizability = |Im(F)| / |X|

Symmetry:
    symmetry = harmonic_mean(coverage, realizability)
```

### Concordance Drift as a Distance

Let purpose embeddings live in a vector space **V**. Define:

```
p_C : C -> V          (purpose vector extracted from code)
p_X : X -> V          (purpose vector extracted from docs)
sim(v, w) = cos(v, w)  (cosine similarity)
```

Then for a code entity **c**:

```
drift(c) = | 1 - sim(p_C(c), p_X(F(c)))    if F(c) exists (CONCORDANT or DISCORDANT)
           | 1                               if unvoiced (F(c) undefined)
```

This turns discordance into a **metric geometry problem**: drift hotspots are regions of high curvature in purpose-alignment space.

---

## 3. Mathematics II: The Level Lattice as an Order Structure

### The Fundamentality Chain

The 16-level holarchy is a **total order** (chain):

```
L-3 < L-2 < L-1 < L0 < L1 < L2 < L3 < L4 < L5 < L6 < L7 < L8 < L9 < L10 < L11 < L12
```

Because it is total, it is a lattice (every pair has a meet and join). This is the **fundamentality lattice** of the Standard Model.

### Zone Boundaries as Phase Transitions

```
PHYSICAL    |  L-3  L-2  L-1  |
            |--- event horizon ---|  (what invariants survive?)
SYNTACTIC   |       L0          |
            |--- meaning boundary ---|
SEMANTIC    |  L1   L2   L3    |
            |--- architecture boundary ---|
SYSTEMIC    |  L4   L5   L6  L7 |
            |--- scope boundary ---|
COSMOLOGICAL|  L8  L9  L10 L11 L12 |
```

At each zone boundary, the **type of morphisms that matter** changes:

| Boundary | Below | Above |
|----------|-------|-------|
| L-1 \| L0 | Encoding relations (byte order, charset) | Syntactic adjacency |
| L0 \| L1 | Token adjacency | Statement sequencing, control flow |
| L3 \| L4 | Function-level semantics | Containment, composition |
| L7 \| L8 | Intra-system coupling | Inter-system boundaries |

This is the kind of structure that becomes natural in:
- **Domain theory / CPOs**: fixed points under abstraction
- **Formal Concept Analysis**: lattice-based classification
- **Multi-scale analysis**: renormalization-style coarse-graining
- **Effective Field Theory**: different effective descriptions at different scales

The SEP "fundamentality" literature frames fundamentality as a priority ordering -- often a strict partial order (asymmetric, transitive, irreflexive) -- and discusses termination vs loops (foundationalism vs coherentism). The SMoC level chain is well-founded (it terminates at L-3), making it foundationalist in the order-theoretic sense.

---

## 4. Mathematics III: Category Theory -- Functors and Purpose Preservation

### 4.1 Two Categories (Two-Sorted Ontology)

**Category C (CODOME)**
- Objects: code entities across levels (tokens, statements, nodes, containers, files, packages, subsystems)
- Morphisms: containment (part-of), dependency (imports, calls, type-use, dataflow)

**Category X (CONTEXTOME)**
- Objects: doc entities (words, sentences, paragraphs, headings, files, spec-groups)
- Morphisms: containment, reference/citation/link edges, defines/claims/specifies edges

This is standard applied category theory: structured collections become categories where morphisms represent structure-preserving maps.

### 4.2 The Documentation Map as Partial Functor

In reality, some code has no docs. So **F** is often partial. Two clean formalisms:

**Option A -- Total functor into extended category with bottom**

Add a null-doc object **bot** (representing "missing documentation"):

```
F : C -> X_bot

F(c) = bot       exactly when c is UNVOICED
```

**Option B -- Kleisli functor for the Maybe monad**

Treat documentation as an effect: mapping may fail. Then F lands in "Maybe X".

Either way, the 2x2 concordance table becomes **functor algebra**:

| State | Functor Condition |
|-------|-------------------|
| UNVOICED | F(c) = bot |
| UNREALIZED | exists x in X such that x not in Im(F) |
| DISCORDANT | F(c) exists, purpose mismatch |
| CONCORDANT | F(c) exists, purpose match |

### 4.3 Purpose Preservation as Approximate Naturality

Introduce a semantic space category **Sem** (objects are vectors, morphisms are similarity-preserving maps).

Define purpose extractors:

```
Psi_C : C -> Sem          (purpose from code)
Psi_X : X -> Sem          (purpose from docs)
```

The ideal condition (perfect concordance) is:

```
Psi_C ≈ Psi_X ∘ F
```

The "≈" is formalized as a bounded error constraint:

```
d(Psi_C(c), Psi_X(F(c))) <= epsilon
```

This is **exactly** what the concordance score measures. When the diagram commutes up to epsilon, the concordance is healthy. When it doesn't, we have drift.

```
        F
   C -------> X
   |           |
Psi_C       Psi_X
   |           |
   v    ≈      v
  Sem -------> Sem
        id
```

### 4.4 Why Lawvere/Tarski/Godel Belong Here

Diagonal arguments (Lawvere 1969, reprinted TAC No. 15, 2006) show that a system cannot fully contain its own truth predicate without contradiction.

SMoC's CODOME/CONTEXTOME separation aligns with this:

> The executable system (CODOME) cannot fully contain the meta-language needed to describe/validate itself (CONTEXTOME) without self-reference pathologies.

So the separation is not arbitrary engineering hygiene -- it is a **meta-language necessity**. You make the metalayer explicit, typed, and measurable via concordances.

---

## 5. Mathematics IV: Profunctors for Concordances

A Concordance is not just a mapping; it's a **many-to-many alignment with weights**.

This is naturally a **profunctor** (distributor / bimodule):

```
R : C^op x X -> [0, 1]
```

Interpretation: R(c, x) = "how strongly doc entity x matches code entity c for this purpose."

This is **enriched category theory**: instead of hom-sets being sets, they are similarity scores in the unit interval [0, 1].

The concordance system is therefore not "category theory inspired" -- it is literally a standard categorical construction: **weighted relations between categories**.

### Concordance as Enriched Profunctor

```
For concordance k with purpose pi:

R_k : C_pi^op x X_pi -> [0, 1]

R_k(c, x) = sim(Psi_C(c), Psi_X(x))    (cosine similarity of purpose vectors)

Concordance score:
    sigma(k) = (1 / |C_pi|) * Sum_{c in C_pi} max_{x in X_pi} R_k(c, x)
```

---

## 6. Semiotics I: Peirce -- Concordance as Triadic Sign Alignment

Peirce's basic structure is irreducibly triadic (SEP, "Peirce's Theory of Signs"):

| Component | Definition |
|-----------|-----------|
| **Sign** (representamen) | The vehicle that represents |
| **Object** | What is represented |
| **Interpretant** | The effect/understanding produced |

### The SMoC Mapping

For a purpose **pi**:

| Peirce | SMoC |
|--------|------|
| **Object** | The intended purpose pi (the shared WHY) |
| **Sign (system 1)** | CODOME slice C_pi (executable signs -- code that also runs) |
| **Sign (system 2)** | CONTEXTOME slice X_pi (discursive signs -- docs/specs) |
| **Interpretant** | The purpose vector(s) + alignment score (the concordance machinery) |

A **Concordance** is a measurable interpretant-agreement test between two sign systems about the same object.

### The Four Health States as Semiotic Pathologies

| State | Semiotic Diagnosis |
|-------|-------------------|
| **UNVOICED** | Sign exists (code), but interpretant cannot be socially stabilized -- discursive sign system is missing |
| **UNREALIZED** | Discursive sign exists (spec), but no executable sign instantiates it |
| **DISCORDANT** | Signs conflict; interpretants diverge (semiotic drift) |
| **CONCORDANT** | Interpretants converge across both sign systems |

---

## 7. Semiotics II: Morris -- Syntactics / Semantics / Pragmatics as Three Planes

Morris's classical trichotomy (1938, "Foundations of the Theory of Signs"):

| Dimension | Definition | Signs in relation to... |
|-----------|-----------|------------------------|
| **Syntactics** | Formal relations of signs to signs | Other signs |
| **Semantics** | Relations of signs to objects | What they denote |
| **Pragmatics** | Relations of signs to interpreters | Who uses them and why |

### The SMoC Mapping

| Morris | SMoC |
|--------|------|
| **Syntactics** | CODOME (AST structure, symbol relations, call edges) |
| **Semantics** | Shared: CODOME has behavioral semantics (execution); CONTEXTOME has declarative semantics (specifications) |
| **Pragmatics** | CONTEXTOME (intent, constraints, rationale, governance) |

**Concordances** are the bridge between planes: the auditable interface between syntactic reality (what is there in code), semantic commitments (what it denotes/does), and pragmatic intention (why it exists / how it should be used).

The SMoC does not merely borrow Morris's three planes -- it implements an **engineering-grade plane alignment system**.

---

## 8. Semiotics III: Lotman -- PROJECTOME as Semiosphere

Lotman's "semiosphere" thesis (1984/2005, "On the Semiosphere", Sign Systems Studies) includes three claims that map to SMoC:

| Lotman | SMoC |
|--------|------|
| Semiosis requires a containing semiotic space | **PROJECTOME** is the semiosphere |
| Core/periphery organization | **CODOME** (core machine-semiotic layer) and **CONTEXTOME** (cultural-discursive periphery) |
| Boundaries are "bilingual translatable filters" | **Concordances** translate between execution language and intention language |

This is an unusually tight correspondence. Lotman provides language for "boundary translation" that SMoC turns into a first-class, measurable object (the Concordance with its alignment score).

---

## 9. Ontological Fundamentalism: What It Is, and What SMoC Does Differently

### 9.1 The Metaphysical Target

In contemporary metaphysics, **ontological fundamentalism** (as criticized by Markosian 2005, "Against Ontological Fundamentalism", Facta Philosophica 7(1): 69-83) holds:

> Only the mereological simples at the bottom level are maximally real; higher-level entities are less real or not real.

Markosian's critique: "degrees of reality" create serious problems -- quantifier confusion, common-sense counterexamples, and composition puzzles.

### 9.2 SMoC Uses Hierarchy Without Claiming "Degrees of Reality"

SMoC has levels (L-3 through L12), but need not claim higher levels are "less real." Instead, SMoC fits what the SEP entry on Fundamentality calls **relative fundamentality**: a priority ordering used for explanation, tied to dependence/grounding, without implying existence gradients.

**SMoC explicitly rejects:** "L0 tokens are more real than L7 systems."
**SMoC explicitly adopts:** "L0 tokens are more constructionally primitive than L7 systems."

### 9.3 Grounding as the Bridge Concept

The metaphysical grounding literature (SEP, "Metaphysical Grounding") emphasizes grounding as a hyperintensional explanatory relation.

SMoC can operationalize three kinds of grounding:

| Grounding Type | Definition | Direction |
|---------------|-----------|-----------|
| **Behavioral** | Runtime behavior grounds claims about the system | CODOME -> observable properties |
| **Intentional** | Specs/requirements ground what counts as correct | CONTEXTOME -> correctness criteria |
| **Structural** | Architecture constraints ground admissible implementations | Level structure -> design space |

This produces a **multi-grounding graph** across levels and across -omes.

### 9.4 The Fundamentality Lattice Is Task-Relative

In SMoC, "fundamental" means different things for different tasks:

| Task | Fundamental Levels | Why |
|------|-------------------|-----|
| Parsing | L0-L3 | Token/statement/function granularity |
| Refactoring | L3-L6 | Function/class/file/package scope |
| Architecture | L6-L9 | Package/system/platform decisions |
| Strategy | L9-L12 | Platform/domain/organization alignment |

This is **relative fundamentality** (in the SEP sense) expressed as operational policy.

### 9.5 Four Fundamentalism Stances (Operating Modes)

SMoC can name and measure four distinct stances without metaphysical confusion:

| Stance | Priority | Motto | Primary Metrics |
|--------|----------|-------|-----------------|
| **Executability Fundamentalism** | CODOME-first | "If it doesn't run, it's not real" | Test pass rate, coverage, runtime correctness |
| **Intentional Fundamentalism** | CONTEXTOME-first | "If it isn't specified, it's not legitimate" | Doc coverage, spec realizability, requirement traceability |
| **Structural Fundamentalism** | Concordance-first | "Relations are fundamental, not entities" | Alignment scores, drift metrics, symmetry |
| **Whole-first Fundamentalism** | PROJECTOME-first | "The project-as-whole is prior; slices derive meaning from role" | System health index, holistic Q-scores |

The fourth echoes Schaffer's "priority of the whole" (2010, "Monism: The Priority of the Whole", The Philosophical Review 119(1): 31-76).

**These are not philosophical truths. They are operating modes.** Each implies different metrics, thresholds, and pipeline behaviors. A healthy project may switch between stances depending on the task.

---

## 10. The Master Diagram: Unifying Math + Semiotics

The cleanest abstraction that matches the SMoC design:

```
                         PURPOSE (pi)
                        /     |      \
                       /      |       \
              CODOME (C)      |     CONTEXTOME (X)
              (executable     |     (non-executable
               signs)         |      signs)
                  |           |           |
                Psi_C         |         Psi_X
                  |           |           |
                  v           |           v
               Sem(C) -------|------- Sem(X)
                       R(c,x) = sim()
                    (profunctor / alignment)
```

| Framework | What It Sees |
|-----------|-------------|
| **Set Theory** | P = C ⊔ X (disjoint union, MECE partition) |
| **Category Theory** | Two categories linked by a partial functor F and profunctor R |
| **Metric Geometry** | Drift = 1 - sim(purpose_code, purpose_docs) |
| **Peirce** | Two sign systems, shared object (purpose), measured interpretant (concordance score) |
| **Morris** | Syntactics (CODOME) + Pragmatics (CONTEXTOME) with Semantics bridging both |
| **Lotman** | Semiosphere (PROJECTOME) with bilingual boundary filters (Concordances) |
| **Metaphysics** | Relative fundamentality via dependence/grounding, not degrees of being |
| **Lawvere/diagonal** | CODOME cannot be its own metalanguage; CONTEXTOME is the explicit meta-layer |

---

## 11. Practical Payoff

Once formalized this way, the following become tractable:

| Operation | Formal Basis |
|-----------|-------------|
| Detect undocumented code | Missing morphisms in F (sheaf-like incompleteness) |
| Measure documentation drift | Distance in purpose-embedding space |
| Validate refactors | Functorial rewrites must preserve concordance invariants |
| Find drift hotspots | Regions of high "semantic curvature" (concentrated drift) |
| Justify the CODOME/CONTEXTOME split | Meta-language necessity (diagonalization family) |
| Choose analysis strategy | Select fundamentalism stance based on task (Section 9.5) |
| Measure project health | Concordance coverage + realizability + symmetry (Section 2) |

---

## References

### Project Documents
- `docs/MODEL.md` -- The 16-level scale, 8 dimensions, atoms, roles
- `CODOME.md` -- Executable universe definition
- `CONTEXTOME.md` -- Non-executable universe definition
- `PROJECTOME.md` -- Complete project contents
- `CONCORDANCES.md` -- Purpose alignment regions
- `THEORY_AMENDMENT_2026-01.md` -- A1: Tools, A2: Dark Matter, A3: Confidence

### Semiotics
- Morris, C. W. (1938). "Foundations of the Theory of Signs." International Encyclopedia of Unified Science, Vol. 1, No. 2. University of Chicago Press.
- Peirce, C. S. -- Triadic sign theory. See: Atkin, A. (2010). "Peirce's Theory of Signs." Stanford Encyclopedia of Philosophy.
- Lotman, J. (1984/2005). "On the Semiosphere." Sign Systems Studies 33(1): 205-229.

### Metaphysics
- Markosian, N. (2005). "Against Ontological Fundamentalism." Facta Philosophica 7(1): 69-83.
- Tahko, T. E. (2018). "Fundamentality." Stanford Encyclopedia of Philosophy.
- Bliss, R. & Trogdon, K. (2014/2021). "Metaphysical Grounding." Stanford Encyclopedia of Philosophy.
- Schaffer, J. (2010). "Monism: The Priority of the Whole." The Philosophical Review 119(1): 31-76.

### Mathematics
- Lawvere, F. W. (1969/2006). "Diagonal Arguments and Cartesian Closed Categories." Lecture Notes in Mathematics 92, Springer-Verlag. Reprinted: Theory and Applications of Categories, No. 15, 2006.
- Mac Lane, S. (1971). Categories for the Working Mathematician. Springer.

---

*Created: 2026-01-27*
*The formal ontological foundations of the Standard Model of Code.*
*Axioms A1-A4 define the partition; mathematics and semiotics validate the structure.*
