# SCALE as IN/OUT Axis Hypothesis

**Date:** 2026-01-23
**Status:** VALIDATED (conceptually)
**Source:** THE LOOP (Perplexity + Gemini synthesis)

## Hypothesis

The 16 SCALE levels in the Standard Model of Code might represent an **INTERNAL/EXTERNAL axis** rather than a vertical hierarchy:

- **INTERNAL** (code-proximal): Bit, Byte, Token, Statement, Block...
- **EXTERNAL** (world-distal): Ecosystem, Platform, Universe...

## Validation from Physics

| Concept | Internal | External |
|---------|----------|----------|
| **Renormalization Group** | UV (high-energy) | IR (low-energy) |
| **Quantum → Classical** | Microscales (particles) | Macroscales (galaxies) |
| **Field Theory** | Local interactions | Global geometry/entropy |

The RG flow treats scales **radially** from UV to IR - not as a linear hierarchy.

## Validation from Information Theory

| Concept | Internal | External |
|---------|----------|----------|
| **Encoding** | Bits, tokens (message itself) | Context, channels (environment) |
| **Compression** | Kolmogorov complexity (intrinsic) | Shannon capacity (extrinsic) |
| **Signal** | The code | The noise/context |

"Internal scales are self-contained, external ones depend on boundaries."

## Mapping to 16 SCALE Levels

```
                    EXTERNAL (World)
                         ↑
    ┌─────────────────────────────────────┐
    │  Universe   Ecosystem   Platform    │  ← World context
    │                                     │
    │     Organization   Project          │  ← Organizational context
    │                                     │
    │        Workspace   Module           │  ← Development context
    │                                     │
    │           File   Class   Function   │  ← Code structure
    │                                     │
    │              Block   Statement      │  ← Syntax
    │                                     │
    │                 Token   Byte   Bit  │  ← Encoding
    └─────────────────────────────────────┘
                         ↓
                    INTERNAL (Code)
```

## Implications

1. **INTERNAL knowledge** = What the code says (analyzable by Collider)
2. **EXTERNAL knowledge** = What the world says (researchable by Perplexity)

3. **The boundary** = Where code meets context (APIs, configs, docs)

4. **Centripetal scan** = Moving from EXTERNAL → INTERNAL (macro → nano)

## Two Knowledge Sources Mapped

| Source | Scale Range | Tools |
|--------|-------------|-------|
| **INTERNAL** | Bit → Module | Collider, Gemini (local context) |
| **EXTERNAL** | Project → Universe | Perplexity, Web research |

The **seam** where internal meets external is at the **Project/Workspace** level - where code becomes a product that exists in the world.

## Next Steps

1. [ ] Update SCALE documentation in MODEL.md
2. [ ] Add IN/OUT axis to the 8-dimensional space
3. [ ] Modify visualization to show radial scale
4. [ ] Update ACI to route by scale position (internal → Gemini, external → Perplexity)
