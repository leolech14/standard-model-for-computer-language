# Research: generate a mermaid diagram showing the full collider pipeline from start to output

> **Date:** 2026-01-23 12:19:32
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:39ec0888d3444c65d6341da9a10d49ea680b069148af3bcea3c38c8d9d1bfe1e`
> **Raw JSON:** `raw/20260123_121932_generate_a_mermaid_diagram_showing_the_full_collid.json`

---

## Query

generate a mermaid diagram showing the full collider pipeline from start to output

---

## Response

```mermaid
graph TD
    A[Source Code] --> B(Tree-Sitter Engine);
    B --> C{Parse Tree};
    C --> D(Python Extractor);
    C --> E(Universal Classifier);
    D --> F(Unified Analysis);
    E --> F;
    F --> G{Codebase State};
    G --> H(Edge Extractor);
    H --> F;
    F --> I(Full Analysis);
    I --> J(Standard Model Enricher);
    I --> K(Purpose Field);
    I --> L(Execution Flow);
    I --> M(Performance Predictor);
    I --> N(Topology Reasoning);
    I --> O(Semantic Cortex);
    J --> G;
    K --> G;
    L --> G;

    I --> P{Markov Matrix};
    I --> Q{Knot Detection};
    I --> R{Data Flow};
    I --> S{File Index};
    
    subgraph Analysis{
    F;I;J;K;L;M;N;O;P;Q;R;S
    }

    STYLE Analysis fill:#f9f,stroke:#333,stroke-width:2px

    subgraph Viz{
    
    T(Appearance Tokens);
    U(Controls Tokens);
    I --> T;
    I --> U;
    T --> V(Token Resolver);
    U --> V;
    V --> W(Appearance Engine);
    V --> X(Controls Engine);
    W --> Y[HTML Output];
    X --> Y;
    }

    STYLE Viz fill:#ccf,stroke:#333,stroke-width:2px
    

    I --> Z(Output Generator);
    Z --> AA(Normalize Output);
    Z --> Y;
    AA --> BB[JSON];

```


---

## Citations

_No citations provided_
