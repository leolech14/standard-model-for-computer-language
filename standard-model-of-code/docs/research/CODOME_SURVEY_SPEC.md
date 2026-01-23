# Codome Survey Specification

> **Purpose:** Define the survey questions we ask each repository before structural analysis
> **Status:** DRAFT (Validated by Gemini Architect - 8/10)
> **Date:** 2026-01-23
> **Version:** 0.2.0

---

## Overview

The Codome (complete code genome) analysis has three phases:

| Phase | Name | Speed | Purpose |
|-------|------|-------|---------|
| 0 | **Codome Survey** | <10 sec | Measure the container before analyzing contents |
| 1 | Structural Analysis | 2-10 min | Extract atoms, edges, metrics |
| 2 | Semantic Synthesis | <1 min | Generate insights and patterns |

**Survey** = measuring the repository's macroscopic properties before deep analysis.

Phase 0 answers: "What is the shape and texture of this codebase?"

---

## Phase 0: Survey Questions (Q1-Q9)

### Q1: Repository Identity

| Question | Method | Output Field |
|----------|--------|--------------|
| What is this project? | README.md first line | `project_name` |
| What does it do? | README.md + LLM summary | `project_purpose` |
| Who maintains it? | git log, CODEOWNERS | `maintainers` |
| How active is it? | Last commit date | `last_activity` |
| How mature is it? | Tag history, version | `maturity_stage` |

### Q2: Size and Complexity Estimation

| Question | Method | Output Field |
|----------|--------|--------------|
| Total files | `find . -type f \| wc -l` | `total_files` |
| Source files | Filter by extension | `source_files` |
| Lines of code | `cloc` or estimate | `loc_estimate` |
| Estimated nodes | LOC / 10 (heuristic) | `node_estimate` |
| Analysis time estimate | nodes * 0.01 sec | `time_estimate` |

### Q3: Language Mix

| Question | Method | Output Field |
|----------|--------|--------------|
| Primary language | Extension frequency | `primary_language` |
| Secondary languages | Extension distribution | `language_mix` |
| Has tree-sitter support? | Check query directory | `query_support` |
| Multi-language repo? | >2 languages >10% each | `is_polyglot` |

### Q4: Structure Detection

| Question | Method | Output Field |
|----------|--------|--------------|
| Is it a monorepo? | Multiple package manifests | `is_monorepo` |
| Has generated code? | Pattern matching | `generated_ratio` |
| Has vendored deps? | node_modules, vendor | `has_vendored` |
| Has tests? | test/, tests/, *_test.* | `has_tests` |
| Has docs? | docs/, README | `has_docs` |
| Has CI/CD? | .github/workflows, .gitlab-ci | `has_ci` |

### Q5: Content Taxonomy

For each file, classify into:

```yaml
taxonomy:
  source_code:
    - path: "src/**/*.py"
      treatment: "full_ast_parse"
      parser: "tree-sitter-python"

  configuration:
    - path: "package.json"
      treatment: "dependency_extraction"
      parser: "json"
    - path: "Dockerfile"
      treatment: "build_stage_extraction"
      parser: "dockerfile"

  documentation:
    - path: "README.md"
      treatment: "llm_summary"
      parser: "markdown"

  data:
    - path: "migrations/*.sql"
      treatment: "schema_extraction"
      parser: "sql"
    - path: "*.csv"
      treatment: "schema_inference"
      parser: "csv"

  notebooks:
    - path: "*.ipynb"
      treatment: "cell_extraction"
      parser: "jupyter"

  binaries:
    - path: "*.so, *.dll, *.jar, *.wasm"
      treatment: "presence_only"
      parser: "none"

  lockfiles:
    - path: "pnpm-lock.yaml, poetry.lock, Cargo.lock"
      treatment: "dependency_graph"
      parser: "lockfile"

  skip:
    - path: "node_modules/**"
      reason: "vendored"
    - path: "dist/**"
      reason: "generated"
```

### Q6: Chunking Strategy

Based on survey findings, decide:

| Repo Size | Strategy | Reason |
|-----------|----------|--------|
| Small (<5K LOC) | Single pass | Fast enough |
| Medium (5K-50K) | Single pass, parallel files | Moderate |
| Large (50K-500K) | Chunk by directory | Memory management |
| Huge (>500K) | Chunk + background | Interactive feedback |

### Q7: Expected Challenges

Flag potential issues before analysis:

| Challenge | Detection | Mitigation |
|-----------|-----------|------------|
| No query support | Language not in queries/ | Use fallback parser |
| Heavy metaprogramming | Decorators, macros, eval | Higher unknown rate expected |
| Generated code | Patterns, file names | Exclude or flag separately |
| Circular dependencies | Pre-scan imports | May need special handling |
| Dynamic imports | eval(), __import__ | Document incompleteness |

### Q8: SMC Dimension Mapping (NEW)

Map survey findings to Standard Model of Code dimensions:

| Survey Finding | SMC Concept | Mapping |
|----------------|-------------|---------|
| `primary_language` | Dimension: D1_ECOSYSTEM | `"python"` → Python ecosystem |
| `maturity_stage` | Dimension: TRUST | `"stable"` → 90% trust baseline |
| `has_tests` | Ring: TESTING | `true` → confirms Testing Ring presence |
| `is_monorepo` | Level: L7-L8 | Multi-system holon |
| `generated_ratio` | Dimension: EFFECT (Purity) | High ratio → lower source purity |
| `has_ci` | Ring: DEPLOYMENT | `true` → confirms Deployment Ring |

### Q9: Dependency Analysis (NEW)

Parse manifests and lock files for dependency graph:

| Source | What We Extract | Output |
|--------|-----------------|--------|
| package.json | Direct dependencies | `dependencies.direct` |
| pnpm-lock.yaml | Transitive dependencies | `dependencies.transitive` |
| pyproject.toml | Python deps | `dependencies.direct` |
| poetry.lock | Full Python graph | `dependencies.transitive` |
| Cargo.toml | Rust deps | `dependencies.direct` |
| Cargo.lock | Full Rust graph | `dependencies.transitive` |
| go.mod | Go deps | `dependencies.direct` |
| go.sum | Go checksums | `dependencies.verified` |

**Value:** Identifies L8 Ecosystem membership and T2 atom sets to activate.

---

## File Type Treatment Matrix

### Source Code

| Extension | Language | Parser | Atoms | Edges | Body |
|-----------|----------|--------|-------|-------|------|
| .py | Python | tree-sitter | Yes | Yes | Yes |
| .ts, .tsx | TypeScript | tree-sitter | Yes | Yes | Yes |
| .js, .jsx | JavaScript | tree-sitter | Yes | Yes | Yes |
| .go | Go | tree-sitter | Yes | Yes | Yes |
| .rs | Rust | tree-sitter | Yes | Yes | Yes |
| .java | Java | fallback | Partial | Partial | Yes |
| .c, .cpp | C/C++ | fallback | Partial | Partial | Yes |
| .rb | Ruby | fallback | Partial | Partial | Yes |
| Other | Unknown | line-count | No | No | No |

### Configuration Files

| File | What We Extract | Method |
|------|-----------------|--------|
| package.json | dependencies, scripts, name, version | JSON parse |
| pyproject.toml | dependencies, build system | TOML parse |
| Cargo.toml | dependencies, features | TOML parse |
| go.mod | module path, dependencies | Text parse |
| Dockerfile | base image, stages, ports | Line parse |
| docker-compose.yaml | services, networks, volumes | YAML parse |
| .github/workflows/*.yaml | jobs, triggers, steps | YAML parse |
| Makefile | targets, dependencies | Make parse |
| tsconfig.json | compiler options, paths | JSON parse |

### Documentation

| File | What We Extract | Method |
|------|-----------------|--------|
| README.md | Project purpose, setup instructions | LLM summary |
| ARCHITECTURE.md | Design decisions, component diagram | LLM extraction |
| CONTRIBUTING.md | Development workflow | LLM summary |
| API.md / OpenAPI | Endpoint definitions | Schema parse |
| Inline comments | Intent, warnings, TODOs | Regex + LLM |

### Data Files (EXPANDED)

| Pattern | What We Extract | Method |
|---------|-----------------|--------|
| migrations/*.sql | Schema evolution | SQL parse |
| fixtures/*.json | Data model shape | JSON schema inference |
| seeds/*.yaml | Test data structure | YAML parse |
| .env.example | Configuration keys | Line parse |
| *.csv | Column names, row count | CSV header parse |
| *.parquet | Schema | Parquet metadata |
| *.jsonl | Record structure | First-line parse |

### Notebooks (NEW)

| Pattern | What We Extract | Method |
|---------|-----------------|--------|
| *.ipynb | Code cells, markdown, outputs | Jupyter parse |

### Binaries (NEW)

| Pattern | What We Extract | Method |
|---------|-----------------|--------|
| *.so, *.dll | Presence, size | File stat |
| *.jar | Manifest, size | JAR metadata |
| *.wasm | Presence, size | File stat |

### Lock Files (NEW)

| Pattern | What We Extract | Method |
|---------|-----------------|--------|
| package-lock.json | Full dependency tree | JSON parse |
| pnpm-lock.yaml | Full dependency tree | YAML parse |
| poetry.lock | Full dependency tree | TOML parse |
| Cargo.lock | Full dependency tree | TOML parse |
| go.sum | Dependency checksums | Text parse |

---

## Survey Output Schema

```json
{
  "repo_id": "github.com/org/repo",
  "survey_at_utc": "2026-01-23T10:00:00Z",
  "survey_version": "0.2.0",

  "identity": {
    "name": "repo-name",
    "purpose": "A library for...",
    "primary_language": "python",
    "maturity": "stable"
  },

  "size": {
    "total_files": 523,
    "source_files": 312,
    "loc_estimate": 45000,
    "node_estimate": 4500,
    "time_estimate_seconds": 45
  },

  "languages": {
    "python": 0.75,
    "javascript": 0.15,
    "yaml": 0.10
  },

  "structure": {
    "is_monorepo": false,
    "generated_ratio": 0.02,
    "has_vendored": true,
    "has_tests": true,
    "has_docs": true,
    "has_ci": true
  },

  "taxonomy": {
    "source_code": 312,
    "configuration": 45,
    "documentation": 23,
    "data": 12,
    "notebooks": 5,
    "binaries": 2,
    "lockfiles": 1,
    "skip": 131
  },

  "dependencies": {
    "direct": 45,
    "transitive": 380,
    "has_lockfile": true,
    "ecosystems": ["npm", "pip"]
  },

  "strategy": {
    "chunking": "single_pass",
    "parallel_files": true,
    "background_tasks": []
  },

  "challenges": [
    {"type": "metaprogramming", "severity": "medium", "files": ["src/magic.py"]},
    {"type": "dynamic_imports", "severity": "low", "files": ["src/plugins/"]}
  ],

  "query_support": {
    "full": ["python", "javascript"],
    "partial": [],
    "none": ["yaml"]
  },

  "smc_implications": {
    "trust_baseline": 0.85,
    "primary_ecosystem": "python",
    "rings_present": ["CORE", "TESTING", "DEPLOYMENT"],
    "scale_level": "L7_SYSTEM",
    "expected_atom_distribution": "library_pattern"
  },

  "confidence": {
    "is_monorepo": 0.95,
    "generated_ratio": 0.70,
    "maturity": 0.80,
    "loc_estimate": 0.90
  }
}
```

---

## Integration with Collider

### Current Flow
```
clone → collider full → output
```

### Proposed Flow
```
clone → survey → strategy → collider full → output
           ↓
     survey.json (saved for research)
```

### Implementation Priority

| Feature | Effort | Value | Priority |
|---------|--------|-------|----------|
| File extension scan | Low | High | P0 |
| Size estimation | Low | High | P0 |
| Language detection | Low | High | P0 |
| Monorepo detection | Medium | High | P1 |
| Generated code detection | Medium | High | P1 |
| Dependency parsing | Medium | High | P1 |
| Content taxonomy | Medium | Medium | P2 |
| Chunking strategy | High | Medium | P2 |
| SMC mapping | Medium | Medium | P2 |
| LLM pre-summary | High | Low | P3 |

---

## Research Value

Survey data from 999 repos enables:

| Question | Data Source |
|----------|-------------|
| What's the average repo size by language? | size.loc_estimate × languages |
| How common are monorepos? | structure.is_monorepo frequency |
| What % of code is generated? | structure.generated_ratio distribution |
| Which languages are often mixed? | languages co-occurrence |
| How much docs do projects have? | taxonomy.documentation / total |
| What's the average dependency count? | dependencies.direct distribution |
| Which ecosystems dominate? | smc_implications.primary_ecosystem |
| How many repos have CI/CD? | structure.has_ci frequency |

This metadata layer ADDS to the structural analysis, creating a richer dataset.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial draft as "Ontological Exposition" |
| 0.2.0 | 2026-01-23 | Renamed to "Codome Survey", added Q8 (SMC Mapping), Q9 (Dependencies), expanded file taxonomy, added confidence scores |
