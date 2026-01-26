# Tool Categorization Research Queries

**Date**: 2026-01-26
**Purpose**: Design a comprehensive tool taxonomy for AI-augmented development tooling

## Context

We have ~60+ tools across three domains:
- **Particle** (Collider): Code analysis, AST parsing, visualization
- **Wave** (Context): AI queries, research, orchestration
- **Observer** (.agent): Task management, automation, macros

## Observed Tool Patterns

### By Intelligence Source
| Pattern | Example | Description |
|---------|---------|-------------|
| **Deterministic** | `fact_loader.py` | Pure code logic, no AI, reproducible |
| **LLM-Based** | `centripetal_scan.py` | Requires AI for core function |
| **Hybrid** | `analyze.py` | Deterministic core + optional AI enrichment |

### By Execution Pattern
| Pattern | Example | Description |
|---------|---------|-------------|
| **Static/One-shot** | `fact_loader.py` | Run once, produce output |
| **Interactive** | `analyze.py --interactive` | REPL-style with user |
| **Daemon/Watcher** | `activity_watcher.py` | Continuous monitoring |
| **Event-Driven** | `trigger_engine.py` | Responds to git/file events |
| **Scheduled** | (cron jobs) | Time-based execution |

### By Data Flow
| Pattern | Example | Description |
|---------|---------|-------------|
| **Reader** | `fact_loader.py` | Consumes data, produces insights |
| **Writer** | `opp_generator.py` | Creates/transforms artifacts |
| **Orchestrator** | `centripetal_scan.py` | Coordinates other tools |
| **Validator** | `confidence_validator.py` | Checks invariants |

### By Scope
| Pattern | Example | Description |
|---------|---------|-------------|
| **Local** | File/function level | `atom_classifier.py` |
| **Project** | Codebase level | `full_analysis.py` |
| **External** | World knowledge | Perplexity queries |

---

## Perplexity Queries

### Query 1: Academic Taxonomy

```
What academic taxonomies exist for categorizing software development tools?
Specifically looking for:

1. Established classifications from software engineering research
2. How tools are categorized in MLOps/DevOps literature
3. The distinction between "static analysis" vs "dynamic analysis" tools
4. How AI-augmented tools are classified (deterministic vs stochastic)

Include citations from ACM, IEEE, or similar sources.
Focus on 2023-2026 literature.
```

### Query 2: Intelligence Axis

```
In AI-augmented development tools, what is the established terminology for:

1. Tools that use no AI (pure deterministic logic)
2. Tools that use AI for optional enrichment (hybrid)
3. Tools that require AI for core functionality
4. Tools that combine multiple AI sources (ensemble/multi-model)

What are the tradeoffs of each approach?
Include examples from popular tools (GitHub Copilot, Cursor, Cody, etc.)
```

### Query 3: Execution Pattern Axis

```
What is the correct terminology for categorizing tool execution patterns:

1. One-shot/batch tools (run once, exit)
2. Interactive/REPL tools (user dialog)
3. Daemon/background processes (always running)
4. Event-driven tools (triggered by hooks/events)
5. Scheduled tools (cron-based)

How do modern AI coding assistants handle these patterns?
What are best practices for combining patterns in a single tool?
```

### Query 4: Data Flow Architecture

```
In software tool design, what patterns exist for data flow:

1. Reader patterns (consume, analyze, report)
2. Writer patterns (generate, transform, emit)
3. Orchestrator patterns (coordinate multiple tools)
4. Validator patterns (check invariants, enforce rules)
5. Pipeline patterns (staged transformation)

How do these map to the Unix philosophy?
What are modern patterns for AI-augmented data flow?
```

### Query 5: Tool Composition

```
What are best practices for tool composition in AI-augmented codebases:

1. How should deterministic tools interoperate with LLM-based tools?
2. What is the "confidence handoff" pattern (deterministic → AI → human)?
3. How do tools in the same toolchain share state/context?
4. What metadata should tools emit for downstream consumption?

Include examples from language servers (LSP), build systems, or AI agents.
```

### Query 6: Taxonomy Design

```
I am designing a tool taxonomy for an AI-augmented code analysis system with ~60 tools.

Proposed axes:
- Intelligence: Deterministic | Hybrid | LLM-Required
- Execution: Static | Interactive | Daemon | Event | Scheduled
- Flow: Reader | Writer | Orchestrator | Validator
- Scope: Local | Project | External

Questions:
1. Are these axes orthogonal (independent)?
2. Are there missing important axes?
3. What naming conventions are used in industry?
4. Should the taxonomy be flat or hierarchical?

Provide examples of how real tools would be classified.
```

---

## Expected Output

After running these queries, we should have:
1. Academic grounding for our taxonomy
2. Industry-standard terminology
3. Validation of proposed axes
4. Missing dimensions to consider
5. Naming conventions to adopt

## Next Steps

1. Run queries through Perplexity (via MCP or manual)
2. Synthesize findings into `TOOL_TAXONOMY.md`
3. Classify all 60+ tools using the taxonomy
4. Add taxonomy to LOL.yaml as a new section
