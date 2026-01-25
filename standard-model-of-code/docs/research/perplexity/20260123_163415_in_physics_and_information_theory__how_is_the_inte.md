# Perplexity Research: In physics and information theory, how is the internal/external axis visualized? What are the best d...

> **Date:** 2026-01-23 16:34:15
> **Model:** sonar-pro
> **Query Length:** 338 chars

---

## Query

In physics and information theory, how is the internal/external axis visualized? What are the best diagram conventions for showing: 1) Renormalization group flow from UV to IR, 2) Scale hierarchies from microscopic to macroscopic, 3) Information flow from encoding (bits) to context (environment). Show ASCII diagram examples if possible.

---

## Response

In physics and information theory, the **internal/external axis** is visualized as a horizontal boundary separating a system's **internal states** (e.g., bits, mechanisms, or microscopic degrees of freedom) from its **external context** (e.g., environment, measurements, or observers), often using a vertical dashed line or Markov blanket to denote the interface where information crosses.[1][6][9]

### Best Diagram Conventions
Standard conventions draw from renormalization group (RG) flows, scale hierarchies, and information-theoretic diagrams (e.g., causal graphs, phase spaces). The **internal/external axis** runs horizontally: left = internal (system), right = external (environment). Vertical axes typically represent **scale** (UV high-energy/microscopic at top, IR low-energy/macroscopic at bottom) or **probability/entropy**. Arrows indicate flow directions.[1][6]

1. **Renormalization Group Flow (UV to IR)**: Vertical downward axis for energy scale (\(\Lambda\): high UV at top, low IR at bottom). Horizontal internal/external axis shows fixed points or couplings flowing left-to-right (internal operators to external probes). Gaussian fixed point (UV) flows to Wilson-Fisher (IR).[1] (No direct citation; standard QFT convention.)

   ASCII example (RG beta function flow):
   ```
   UV (high Λ)  ┌──────────────┐
                │ Gaussian FP  │ ← internal (free theory)
   ↓            │              │
   Scale        │   Flow →     │ ─── External (interactions)
   ↓            │              │
   IR (low Λ)   └──────┬───────┘
                       │
                  Wilson-Fisher FP
   ```

2. **Scale Hierarchies (Microscopic to Macroscopic)**: Vertical top-to-bottom for length/energy scale (micro at top, macro at bottom). Horizontal axis separates internal hierarchy levels (e.g., stationary points in informational structures) from external influences (e.g., parameters \(\alpha, \gamma\)). Arcs show transitive cause-effect relations.[1]

   ASCII example (adapted from informational structure hierarchy):
   ```
   Micro (high energy) ────────── External Env (γ params)
                  │
                  ├─ Internal Nodes: (0,0) unstable ──→
                  │                 (1,0) saddle
                  │                 (0,1) saddle
                  ↓ Scale
                  │                 (2.5,3) stable
   Macro (low energy) ──────────── Hierarchy base
   ```

3. **Information Flow (Encoding Bits to Context/Environment)**: Horizontal left-to-right for flow (internal bits → external context). Vertical axis for probability \(p(x)\) or mutual information \(I(X;Y)\). Encoding (compression) on left, decompression/context on right; mutual information bars visualize overlap.[6]

   ASCII example (mutual information flow):
   ```
   Internal Bits ────── Encoding ────→ I(X;Y) ────→ External Context
     H(X)                  ↓ Prob(p(x))              H(Y|X)
   ┌─────────────┐       ┌──────────┐             ┌─────────────┐
   │ X entropy   │──────▶│ Overlap   │────────────▶│ Environment │
   └─────────────┘       │  bars     │             └─────────────┘
                         └──────────┘   H(X,Y)
   ```

These conventions emphasize **directed causality** (arrows from past/UV/internal to future/IR/external) and **hierarchies** (vertical stratification), as in informational structures where stationary points form energy-level rows with arcs subset-related by non-zero values.[1] For precise plots, phase-space nullclines (orange/yellow lines intersecting at equilibria) curve the internal field toward external stability.[1]

---

## Citations

1. https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1006154
2. https://en.wikipedia.org/wiki/Feynman_diagram
3. https://www.physics.umd.edu/courses/Phys851/Luty/notes/diagrams.pdf
4. https://www.weizmann.ac.il/complex/falkovich/sites/complex.falkovich/files/uploads/PNI23.pdf
5. https://scgp.stonybrook.edu/wp-content/uploads/2023/08/PNI23.pdf
6. https://colah.github.io/posts/2015-09-Visual-Information/
7. https://web.stanford.edu/~montanar/RESEARCH/BOOK/partA.pdf
8. https://bayes.wustl.edu/etj/articles/theory.2.pdf
9. https://www.youtube.com/watch?v=RpOrRw4EhTo
10. http://dspace.mit.edu/bitstream/handle/1721.1/88853/46240721-MIT.pdf?sequence=2

---

## Usage Stats

- Input tokens: 73
- Output tokens: 828
