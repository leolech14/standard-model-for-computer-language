# Research: What are the implementation strategies for 'semantic design tokens' in data visualization engines to...

> **Date:** 2026-01-25 02:55:57
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:6bfb442b45c2bcf1dbfe6534977914042155e2f961d10ccf97d1e1460f3d3745`
> **Raw JSON:** `raw/20260125_025557_what_are_the_implementation_strategies_for__semant.json`

---

## Query

What are the implementation strategies for 'semantic design tokens' in data visualization engines to achieve 100% separation of style and logic? Looking for architectures where the rendering engine is purely functional and strictly adheres to a semantic definition file. Include sources from: Design Systems research (Adobe, Salesforce), CSS architecture papers, W3C Design Tokens Community Group.

---

## Response

**Semantic design tokens achieve 100% separation of style and logic in data visualization engines by defining styles as a semantic JSON file (with primitive values like colors and semantic aliases like "text-default") that a purely functional rendering engine consumes without embedding any hardcoded styles.** This architecture treats the token file as the single source of truth, using translation tools to generate platform-specific outputs while keeping rendering logic agnostic to visual details[1][3].

### Core Architecture Components
- **Token Structure**: Primitive tokens store raw values (e.g., "blue-500": "#1E40AF"), while **semantic tokens** reference primitives and encode meaning (e.g., "color-text-primary": "{color.blue-500}", "color-button-hover": "{color.gray-200}"). This builds an API-like layer for usage (text, backgrounds, states), eliminating ambiguity in application[1][2][4].
- **Semantic Definition File**: A JSON file organizes tokens in a grid (e.g., x-axis for states like default/hover, y-axis for roles like text/background), capturing all design decisions without visual rendering logic[1].
- **Purely Functional Rendering Engine**: The engine parses only semantic tokens, applying them based on context (e.g., component role + state). No inline styles or primitives in code; it resolves references at runtime or build-time for strict separation[1][3].

### Implementation Strategies
1. **Translation Pipeline**: Use tools like Style Dictionary or Theo to transform the semantic JSON into platform outputs (CSS variables, Swift, etc.). Filter by flags (e.g., "public: true") for scoped exports, ensuring the engine imports generated files without token knowledge[1][3].
2. **Token Resolution in Engine**: Rendering functions map semantic keys to visuals functionally, e.g.:
   ```
   renderChart(data, semantics) {
     return data.map(point => (
       <Bar fill={semantics['color-bar-positive']} />
     ));
   }
   ```
   Here, `semantics` loads from JSON, keeping logic data-only[1].
3. **Modes and States**: Semantic tokens include variants (e.g., "text-default-dark-mode"), swapped via mappings for theming without code changes[1][2].
4. **ETL Workflow**: Extract from design tools (Figma Tokens plugin), transform via pipelines, load into engine. Audit for duplicates to maintain purity[2].

### Sources Alignment
- **Design Systems Research (Adobe/Salesforce-like)**: Contentful and Nulab describe semantic layers mirroring Adobe Spectrum/Salesforce Lightning practices, using JSON for cross-platform consistency[1][2].
- **CSS Architecture**: Martin Fowler's token-based UI uses translation for CSS variables, enabling functional engines[3].
- **W3C Design Tokens CG**: Emphasizes aliases and references for semantic abstraction, foundational for spec-compliant separation[4].

Limitations: Search results focus on web/UI; data viz adaptations (e.g., D3/Vega) require custom resolvers for SVG/canvas, but principles apply directly[1][3]. No explicit Adobe/Salesforce docs surfaced, but patterns match industry standards.

---

## Citations

1. https://www.contentful.com/blog/design-token-system/
2. https://nulab.com/learn/design-and-ux/design-tokens/
3. https://martinfowler.com/articles/design-token-based-ui-architecture.html
4. https://thedesignsystem.guide/design-tokens
5. https://www.figma.com/blog/the-future-of-design-systems-is-semantic/
6. https://www.outframe.co/blog/how-we-apply-design-tokens-for-our-clients-a-guide
7. https://www.designsystemscollective.com/understanding-design-token-relationships-a-visual-approach-7911ec82f3c1
8. https://m3.material.io/foundations/design-tokens

---

## Usage Stats

- Prompt tokens: 70
- Completion tokens: 642
- Total tokens: 712
