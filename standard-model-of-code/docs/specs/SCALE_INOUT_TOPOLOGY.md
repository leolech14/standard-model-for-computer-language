# SCALE as IN/OUT Topology

> The 16 SCALE levels represent an INTERNAL/EXTERNAL axis, not a vertical hierarchy.
>
> **Status:** PARTIALLY VALIDATED (THE LOOP, 2026-01-23)

---

## Validation Summary (THE LOOP)

**Research:** `docs/research/perplexity/20260123_172843_validate_hypothesis__the_16_scale_levels_in_standa.md`

| Claim | Status | Evidence |
|-------|--------|----------|
| Internal scales (Bit→Function) are code-proximal | ✅ CONFIRMED | Computing hierarchies Level-0 to Level-5 [1][2] |
| External scales (Project→Universe) are context-dependent | ✅ CONFIRMED | Terraform levels, enterprise integration [4][5] |
| Boundary at Project/Workspace | ✅ CONFIRMED | AST hierarchies → interoperability [1][3][4] |
| RG flow parallel (UV→IR) | ✅ CONFIRMED | Bottom-up merging, layered abstraction [1][2] |
| Information theory parallel | ✅ CONFIRMED | H(X) code-intrinsic, H(Y|X) conditional [1][2][4] |

**Perplexity verdict:**
> "The axis reinterpretation is **plausible and adds insight** but lacks explicit confirmation."

**Interpretation:** Our IN/OUT axis is a **novel contribution** that maps to real patterns in computing hierarchies, but is not established terminology in literature.

---

## The Diagram

```
                            EXTERNAL (World/Context)
                                     ↑
    ════════════════════════════════════════════════════════════════════

    UNIVERSE ─────────────────────────────────────────────────────────┐
    ECOSYSTEM ────────────────────────────────────────────────────────┤
    PLATFORM ─────────────────────────────────────────────────────────┤ PERPLEXITY
    ORGANIZATION ─────────────────────────────────────────────────────┤ ZONE
    PROJECT ──────────────────────────────────────────────────────────┤ (External
                                                                      │  Knowledge)
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ THE BOUNDARY ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
                                                                      │
    WORKSPACE ────────────────────────────────────────────────────────┤
    MODULE ───────────────────────────────────────────────────────────┤ GEMINI
    FILE ─────────────────────────────────────────────────────────────┤ ZONE
    CLASS ────────────────────────────────────────────────────────────┤ (Internal
    FUNCTION ─────────────────────────────────────────────────────────┤  Context)
                                                                      │
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ THE CORE ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
                                                                      │
    BLOCK ────────────────────────────────────────────────────────────┤
    STATEMENT ────────────────────────────────────────────────────────┤ COLLIDER
    TOKEN ────────────────────────────────────────────────────────────┤ ZONE
    BYTE ─────────────────────────────────────────────────────────────┤ (Pure
    BIT ──────────────────────────────────────────────────────────────┘ Analysis)

    ════════════════════════════════════════════════════════════════════
                                     ↓
                            INTERNAL (Code/Encoding)
```

---

## Knowledge Source Mapping

| Scale Range | Zone | Knowledge Source | Tool |
|-------------|------|------------------|------|
| Universe → Project | EXTERNAL | World knowledge, standards, best practices | Perplexity |
| Workspace → Function | INTERNAL | Code context, relationships, patterns | Gemini + Context |
| Block → Bit | CORE | Pure syntax, encoding, invariants | Collider Analysis |

---

## The Boundary

The **BOUNDARY** (Project ↔ Workspace) is where code meets world:

```
    EXTERNAL                    BOUNDARY                    INTERNAL
    ─────────────────────────────────────────────────────────────────

    Standards    ──────►   APIs / Configs   ◄──────    Implementation
    Best Practices ────►   Documentation    ◄──────    Algorithms
    Ecosystem    ──────►   Dependencies     ◄──────    Modules

    ─────────────────────────────────────────────────────────────────
    (Perplexity)              (Both)                    (Gemini)
```

---

## Centripetal Scan Flow

The scan spirals **INWARD** from External to Internal:

```
    Round 1-3 (MACRO)     ════►    EXTERNAL → BOUNDARY
         │                         Universe, Ecosystem, Project
         │                         "What does the world say?"
         ▼
    Round 4-6 (MESO)      ════►    BOUNDARY → INTERNAL
         │                         Workspace, Module, File
         │                         "Where does code meet world?"
         ▼
    Round 7-9 (MICRO)     ════►    INTERNAL → CORE
         │                         Class, Function, Block
         │                         "What does the code say?"
         ▼
    Round 10-12 (NANO)    ════►    CORE
                                   Statement, Token, Bit
                                   "What is the code?"
```

---

## Physics Analogy: RG Flow

```
    UV (High Energy)                              IR (Low Energy)
    ═══════════════════════════════════════════════════════════════

    EXTERNAL                                      INTERNAL
    ┌─────────────┐                              ┌─────────────┐
    │  Universe   │ ───── RG Flow ─────────────► │    Bit      │
    │  (Macro)    │                              │  (Micro)    │
    └─────────────┘                              └─────────────┘

    High entropy                                  Low entropy
    Many possibilities                            Specific encoding
    Context-dependent                             Self-contained

    ═══════════════════════════════════════════════════════════════
```

In physics:
- **UV (Ultraviolet)** = High energy, short distance, microscopic
- **IR (Infrared)** = Low energy, long distance, macroscopic

In code:
- **EXTERNAL** = High entropy, many possibilities, world-dependent
- **INTERNAL** = Low entropy, specific encoding, self-contained

The RG flow goes from UV → IR as we "zoom out".
Our centripetal scan goes EXTERNAL → INTERNAL as we "zoom in".

---

## Information Theory Analogy

```
    EXTERNAL (Context)                           INTERNAL (Signal)
    ═══════════════════════════════════════════════════════════════

    H(Y|X)                    I(X;Y)                    H(X)
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │ Environment │ ◄──── │  Mutual     │ ────► │   Message   │
    │   Noise     │       │ Information │       │   Bits      │
    └─────────────┘       └─────────────┘       └─────────────┘

    What the world adds                          What the code says

    ═══════════════════════════════════════════════════════════════
```

- **H(X)** = Entropy of the code itself (INTERNAL)
- **H(Y|X)** = Entropy added by context (EXTERNAL)
- **I(X;Y)** = Mutual information at the BOUNDARY

---

## Implementation: Two Knowledge Sources

```python
# ACI Tier Routing based on SCALE position

def route_by_scale(scale_level: str) -> str:
    """Route to knowledge source by scale position."""

    EXTERNAL_SCALES = ["universe", "ecosystem", "platform", "organization", "project"]
    INTERNAL_SCALES = ["workspace", "module", "file", "class", "function"]
    CORE_SCALES = ["block", "statement", "token", "byte", "bit"]

    scale = scale_level.lower()

    if scale in EXTERNAL_SCALES:
        return "perplexity"  # World knowledge
    elif scale in INTERNAL_SCALES:
        return "gemini"      # Code context
    elif scale in CORE_SCALES:
        return "collider"    # Pure analysis
    else:
        return "hybrid"      # Both sources
```

---

## References

### THE LOOP Validation (2026-01-23)
- **Full hypothesis validation:** `docs/research/perplexity/20260123_172843_validate_hypothesis__the_16_scale_levels_in_standa.md`
- **Earlier RG flow research:** `docs/research/perplexity/20260123_163415_in_physics_and_information_theory*.md`
- **Hypothesis document:** `docs/research/perplexity/20260123_scale_inout_axis_hypothesis.md`

### Citations from Perplexity
1. https://www.geeksforgeeks.org/computer-organization-architecture/computer-system-level-hierarchy/
2. https://www.emergentmind.com/topics/hierarchical-code-generation
3. https://www.maxqda.com/help-mx22/maxmaps/one-case-model-code-hierarchy
4. https://aztfmod.github.io/documentation/docs/fundamentals/lz-intro/
5. https://stackoverflow.blog/2022/07/28/measurable-and-meaningful-skill-levels-for-developers/
6. https://en.wikipedia.org/wiki/Standard_Model
7. https://arxiv.org/abs/1212.1417
8. https://www.cs.huji.ac.il/~feit/papers/Large19ICPC.pdf

### Theoretical Foundations
- RG flow conventions: UV (external) → IR (internal)
- Information theory: H(X) internal, H(Y|X) external, I(X;Y) boundary
- Standard Model of Code: 16 SCALE levels
