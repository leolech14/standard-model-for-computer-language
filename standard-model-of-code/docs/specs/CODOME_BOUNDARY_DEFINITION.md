# Codome Boundary Definition (CBD)

> **Status:** DRAFT
> **Date:** 2026-01-23
> **Core Principle:** Define WHAT the thing is BEFORE measuring it.

---

## The Fundamental Question

Before analyzing a codebase, we must answer:

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   WHAT IS THIS CODOME?                                       │
│                                                              │
│   • Where does it START?                                     │
│   • Where does it END?                                       │
│   • What IS it?                                              │
│   • What ISN'T it?                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Only after defining boundaries can we measure with certainty.**

---

## The Survey as Ontological Inquiry

The Survey module is not just "exclude vendor." It's a complete **ontological definition** of the codome:

```
SURVEY PHASE (Stage 0)
│
├── Q1: IDENTITY
│   ├── What is this project?
│   ├── What language(s)?
│   ├── What framework(s)?
│   └── What ecosystem?
│
├── Q2: BOUNDARIES
│   ├── Where does OUR code start?
│   ├── Where does VENDOR code live?
│   ├── Where does GENERATED code live?
│   └── Where does BUILD output go?
│
├── Q3: NATURE
│   ├── What file types are CODE?
│   ├── What file types are CONFIG?
│   ├── What file types are DATA?
│   └── What file types are ARTIFACTS?
│
├── Q4: POLLUTION
│   ├── What shouldn't be here?
│   ├── What's in wrong location?
│   ├── What's mislabeled?
│   └── What's orphaned?
│
└── Q5: ADAPTATION
    ├── Which parsers to use?
    ├── What thresholds apply?
    ├── What patterns to expect?
    └── What health norms?
```

---

## Boundary Categories

### 1. Spatial Boundaries (WHERE)

```yaml
spatial_boundaries:
  root: /path/to/project

  included:
    - src/           # Source code
    - lib/           # Internal libraries
    - app/           # Application code
    - packages/      # Monorepo packages

  excluded:
    - node_modules/  # External dependencies
    - vendor/        # Third-party code
    - dist/          # Build output
    - .git/          # Version control
    - coverage/      # Test artifacts

  ambiguous:
    - lib/vendor/    # Vendored into lib? Investigate.
    - src/generated/ # Generated but in src? Investigate.
```

### 2. Type Boundaries (WHAT)

```yaml
type_boundaries:
  code_files:
    primary:
      - "*.js"
      - "*.ts"
      - "*.py"
      - "*.go"
    secondary:
      - "*.jsx"
      - "*.tsx"
      - "*.vue"
      - "*.svelte"

  config_files:
    - "*.json"
    - "*.yaml"
    - "*.toml"
    - "*.env"

  data_files:
    - "*.csv"
    - "*.sql"
    - "*.graphql"

  documentation:
    - "*.md"
    - "*.rst"
    - "*.txt"

  artifacts:
    - "*.min.js"      # Minified
    - "*.bundle.js"   # Bundled
    - "*.d.ts"        # Generated types
    - "*.map"         # Source maps

  binary:
    - "*.png"
    - "*.jpg"
    - "*.woff"
    - "*.wasm"
```

### 3. Ownership Boundaries (WHOSE)

```yaml
ownership_boundaries:
  ours:
    indicators:
      - In git history with project authors
      - No "DO NOT EDIT" markers
      - No version/license headers from other projects
      - Matches project coding style

  vendor:
    indicators:
      - In node_modules/, vendor/, third_party/
      - Has external license header
      - Version number in filename
      - "DO NOT EDIT - GENERATED" marker

  generated:
    indicators:
      - "AUTO-GENERATED" comment
      - "@generated" annotation
      - Matches known generator patterns
      - .generated. in filename

  forked:
    indicators:
      - Originally vendor, modified by us
      - Has git history showing our changes
      - Partial license headers
```

### 4. Size Boundaries (HOW BIG)

```yaml
size_boundaries:
  file_size:
    normal: < 50KB        # Typical source file
    large: 50KB - 500KB   # Might be generated or minified
    huge: > 500KB         # Almost certainly not hand-written

  line_length:
    normal: < 200 chars   # Human-readable
    long: 200-1000 chars  # Suspicious
    minified: > 1000 chars # Definitely minified

  line_count:
    normal: < 1000 lines  # Typical file
    large: 1000-5000      # God file?
    massive: > 5000       # Split this
```

### 5. Content Boundaries (WHAT'S INSIDE)

```yaml
content_boundaries:
  language_markers:
    javascript:
      - "function "
      - "const "
      - "class "
      - "import "
      - "export "
    python:
      - "def "
      - "class "
      - "import "
      - "from "
    go:
      - "func "
      - "type "
      - "package "

  pollution_markers:
    minified:
      - Average line length > 500
      - No whitespace between tokens
      - Single-letter variable names throughout
    generated:
      - "DO NOT EDIT"
      - "@generated"
      - "AUTO-GENERATED"
    binary_in_text:
      - Non-UTF8 sequences
      - Control characters
      - Base64 blocks > 1KB
```

---

## The Boundary Definition Report

```yaml
# .codome/boundary_definition.yaml
# Generated by: collider survey
# Date: 2026-01-23T12:00:00Z

project:
  name: my-project
  root: /path/to/my-project
  detected_type: nodejs_monorepo

identity:
  primary_language: typescript
  secondary_languages: [javascript, json]
  framework: nextjs
  ecosystem: npm

spatial:
  total_paths: 4,521
  included_paths: 892
  excluded_paths: 3,629

  breakdown:
    source: 856 paths
    config: 24 paths
    docs: 12 paths
    vendor: 3,540 paths (node_modules)
    build: 45 paths (dist, .next)
    artifacts: 44 paths (coverage, logs)

type:
  total_files: 4,521
  by_category:
    code: 892
    config: 67
    data: 23
    docs: 45
    binary: 156
    artifacts: 3,338

  by_extension:
    ".ts": 623
    ".tsx": 189
    ".js": 80
    ".json": 67
    ".md": 45
    ".css": 34
    # ...

ownership:
  ours: 892 files
  vendor: 3,540 files
  generated: 45 files
  forked: 0 files
  ambiguous: 12 files  # Need investigation

size:
  total_bytes: 245,678,901
  our_code_bytes: 2,345,678
  vendor_bytes: 243,000,000

  our_files:
    normal: 856
    large: 32
    huge: 4

  suspicious_files:
    - path: src/legacy/bundle.js
      size: 1.2MB
      reason: "Huge file in src/"
    - path: lib/utils.min.js
      size: 89KB
      reason: "Minified in lib/"

pollution:
  detected: 3
  issues:
    - type: vendor_in_src
      path: src/vendor/lodash.js
      recommendation: "Move to node_modules or vendor/"
    - type: minified_unmarked
      path: lib/crypto.js
      recommendation: "Rename to crypto.min.js or exclude"
    - type: generated_in_src
      path: src/types/generated.ts
      recommendation: "Move to generated/ or mark clearly"

adaptation:
  recommended_parsers:
    typescript: tree-sitter-typescript
    javascript: tree-sitter-javascript
    json: native

  recommended_exclusions:
    - node_modules/**
    - dist/**
    - .next/**
    - coverage/**
    - "*.min.js"
    - "*.bundle.js"

  recommended_thresholds:
    max_file_size: 100KB
    max_line_length: 500
    min_comment_ratio: 0.05

  expected_patterns:
    module_system: esm
    component_style: functional
    state_management: redux

verdict:
  boundary_confidence: 98%
  pollution_level: LOW (0.3%)
  ready_for_analysis: true

  warnings:
    - "12 ambiguous files need manual review"
    - "4 huge files may slow analysis"
```

---

## Pipeline Auto-Adaptation

Once boundaries are defined, the pipeline adapts:

```python
def adapt_pipeline(boundary_def: BoundaryDefinition) -> PipelineConfig:
    """
    Auto-configure pipeline based on boundary definition.
    """
    config = PipelineConfig()

    # 1. Select parsers based on detected languages
    for lang in boundary_def.identity.languages:
        config.add_parser(get_best_parser(lang))

    # 2. Set exclusions from spatial boundaries
    config.exclusions = boundary_def.spatial.excluded_paths

    # 3. Adjust thresholds based on size boundaries
    if boundary_def.size.avg_file_size > 20_000:
        config.large_file_mode = True
        config.chunk_size = 10_000

    # 4. Enable special handling for detected patterns
    if 'monorepo' in boundary_def.identity.detected_type:
        config.enable_workspace_resolution = True

    if boundary_def.identity.framework == 'nextjs':
        config.enable_nextjs_patterns = True

    # 5. Set health norms based on ecosystem
    config.health_norms = get_ecosystem_norms(
        boundary_def.identity.ecosystem
    )

    # 6. Configure for pollution handling
    for issue in boundary_def.pollution.issues:
        if issue.type == 'minified_unmarked':
            config.minified_detection = 'aggressive'

    return config
```

---

## The Survey Flow

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│                     USER RUNS COLLIDER                       │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               STAGE 0: SURVEY                         │   │
│  │                                                       │   │
│  │  1. DISCOVER         What's in this directory?        │   │
│  │     └── Scan all paths, extensions, sizes             │   │
│  │                                                       │   │
│  │  2. IDENTIFY         What kind of project is this?    │   │
│  │     └── Detect language, framework, ecosystem         │   │
│  │                                                       │   │
│  │  3. CLASSIFY         What's ours vs theirs?           │   │
│  │     └── Ownership, vendor, generated                  │   │
│  │                                                       │   │
│  │  4. DETECT           What pollution exists?           │   │
│  │     └── Misplaced files, unmarked minified            │   │
│  │                                                       │   │
│  │  5. DEFINE           Where are the boundaries?        │   │
│  │     └── Spatial, type, ownership, size                │   │
│  │                                                       │   │
│  │  6. ADAPT            How should pipeline behave?      │   │
│  │     └── Parsers, thresholds, patterns                 │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│            BOUNDARY DEFINITION COMPLETE                      │
│            Pipeline knows WHAT it's analyzing                │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          STAGES 1-N: ANALYSIS (with certainty)        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Why This Matters

### Without Boundary Definition

```
Input: /path/to/project
Parser: "Analyze everything"
Result: 45,000 nodes (including 42,000 from node_modules)
Confidence: ??? (how much is ours?)
Health metrics: Meaningless (comparing apples to vendor oranges)
```

### With Boundary Definition

```
Input: /path/to/project
Survey: "This is a Next.js TypeScript monorepo with 892 source files"
Parser: "Analyze only the 892 files that are OURS"
Result: 3,000 nodes (all from our code)
Confidence: 98% (we KNOW these are the boundaries)
Health metrics: Meaningful (comparing our code to professional norms)
```

---

## The Ontological Guarantee

```
IF Survey defines boundaries correctly
AND Pipeline respects those boundaries
THEN Analysis covers exactly the codome
AND Completeness is measurable
AND Health metrics are meaningful

Survey is not optimization.
Survey is DEFINITION.
Without it, we don't know what we're measuring.
```

---

## Implementation Status

| Component | Location | Status |
|-----------|----------|--------|
| Basic exclusion detection | `src/core/survey.py` | ✅ EXISTS |
| Full boundary definition | `src/core/survey.py` | TODO |
| Pipeline adaptation | `src/core/full_analysis.py` | TODO |
| Boundary report output | `src/core/survey.py` | TODO |
| CLI integration | `cli.py` | PARTIAL |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial draft - ontological framing |
