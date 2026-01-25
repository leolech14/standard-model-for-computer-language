# Research Schemas: Multi-Configuration Query Orchestration

**Version:** 1.0.0
**Location:** `context-management/config/research_schemas.yaml`
**Engine:** `context-management/tools/ai/aci/research_orchestrator.py`

---

## Overview

Research Schemas are reusable patterns that orchestrate multiple ACI queries with different configurations to produce validated, multi-perspective answers.

**Target Audience:** AI Agents (not humans)

**Purpose:** Transform "investigation" into "procedure" - reduce improvisation, increase reproducibility.

---

## Quick Start

```bash
# List available schemas
python analyze.py --list-research-schemas

# Describe a schema
python analyze.py --describe-schema validation_trio

# Show all capabilities
python analyze.py --research-capabilities

# Execute (dry run)
python analyze.py --research validation_trio "How many subsystems exist?"

# Execute with overrides
python analyze.py --research validation_trio \
  --override "runs[0].token_budget=200000" \
  "Your query here"
```

---

## Available Schemas

| Schema | Purpose | Runs | Strategy | Has External |
|--------|---------|------|----------|--------------|
| `validation_trio` | Detect hallucinations | 3 | consensus | Yes |
| `depth_ladder` | Find optimal context size | 4 | quality_gradient | No |
| `adversarial_pair` | Stress-test claims | 2 | dialectic | No |
| `forensic_investigation` | Root cause analysis | 4 | triangulation | No |
| `confidence_calibration` | Bayesian evidence scoring | 4 | bayesian | Yes |
| `semantic_probe` | Multi-scale analysis (L3/L5/L7) | 3 | hierarchical | No |
| `quick_validate` | Fast sanity check | 2 | consensus | No |

---

## Schema Selection Guide

| Need | Use Schema |
|------|------------|
| High confidence answer | `validation_trio` |
| Optimize token budget | `depth_ladder` |
| Test hypothesis robustness | `adversarial_pair` |
| Debug complex issue | `forensic_investigation` |
| Precise confidence score | `confidence_calibration` |
| Explore across scale levels | `semantic_probe` |
| Quick sanity check | `quick_validate` |

---

## Architecture

### Run Types

| Type | Description | Membrane Rules |
|------|-------------|----------------|
| `internal` | Uses repo context | sets, token_budget allowed |
| `external` | Web/API only | sets/token_budget IGNORED, query sanitized |

### Tiers

| Tier | Description | Cost | Time |
|------|-------------|------|------|
| `instant` | Cached truths | $0 | <100ms |
| `rag` | File Search with citations | $0.01 | ~5s |
| `long_context` | Full Gemini reasoning | $0.10 | ~60s |
| `perplexity` | External web research | $0.05 | ~30s |
| `flash_deep` | 2M context window | $0.20 | ~90s |
| `hybrid` | Internal + external combined | $0.15 | ~120s |

### Synthesis Strategies

| Strategy | Description |
|----------|-------------|
| `consensus` | Majority voting across runs |
| `quality_gradient` | Compare quality at different depths |
| `dialectic` | Thesis + antithesis → synthesis |
| `triangulation` | Cross-reference multiple angles |
| `bayesian` | Update confidence based on evidence weights |
| `hierarchical` | Multi-scale aggregation (L3/L5/L7) |

---

## Condition DSL

Runs can have conditions that determine whether they execute:

```yaml
condition:
  scope_in: ["EXTERNAL", "HYBRID"]   # Scope must be one of these
  scope_not: "INTERNAL"               # Scope must NOT be this
  intent_in: ["EXPLAIN", "ANALYZE"]   # Intent must match
  complexity_gte: 3                   # Complexity >= threshold
```

If condition fails:
- `fallback: "skip"` - Run is skipped entirely
- `fallback: "<run_name>"` - Use another run instead

---

## External Membrane

Runs with `type: external` have strict rules enforced by the loader:

1. `sets`: IGNORED (external queries don't use repo context)
2. `token_budget`: IGNORED (no context to budget)
3. `system_prompt`: SANITIZED (no repo-specific phrases allowed)
4. Query passed through `prepare_perplexity_query()` ALWAYS

**Banned phrases in external prompts:**
- "file:line"
- "cite specific code"
- "reference the repository"
- "look in the codebase"

---

## Guardrails

```yaml
guardrails:
  max_token_budget_per_run: 1000000
  max_token_budget_per_schema: 2000000
  max_runs_per_schema: 10
  rate_limit_per_minute: 30
  cost_alert_threshold_usd: 1.00
```

---

## Validation (Preflight)

The schema loader validates:

1. **Model IDs** - Must be in `model_catalog`
2. **Tier names** - Must be in `TIER_CATALOG`
3. **Run names** - Must be unique within schema
4. **Fallback references** - Must point to existing run or "skip"
5. **External membrane** - Banned phrases checked
6. **Guardrails** - Token budgets within limits

Validation errors are logged and the schema is skipped.

---

## Consensus and Distinct Sources

When using `consensus` strategy with `distinct_sources_required: true`:

- Runs are grouped by `model:tier` to identify truly distinct sources
- If not enough distinct sources, a warning is added to `disagreements`
- Prevents artificial agreement from fallback duplicating a run

---

## Decision Trace (Observability)

Every execution produces a `decision_trace`:

```yaml
decision_trace:
  schema_name: validation_trio
  overrides_applied: {}
  runs_executed: [reasoning, fast]
  runs_skipped: [external]
  timestamp: "2026-01-24T23:15:00"
```

---

## Custom Schemas

For ad-hoc research, use `--research-custom`:

```bash
python analyze.py --research-custom '{
  "runs": [
    {"name": "a", "type": "internal", "model": "gemini-3-pro-preview", "sets": ["theory"]},
    {"name": "b", "type": "external", "tier": "perplexity"}
  ],
  "synthesis": {"strategy": "consensus", "distinct_sources_required": true}
}' "Your query here"
```

---

## Programmatic Usage

```python
from aci import get_research_engine, execute_research

# Get engine
engine = get_research_engine()

# List schemas
schemas = engine.list_schemas()

# Describe schema
desc = engine.describe_schema("validation_trio")

# Execute
result = engine.execute("validation_trio", "query here")

# Or use convenience function
result = execute_research("validation_trio", "query here")
```

---

## Files

| File | Purpose |
|------|---------|
| `config/research_schemas.yaml` | Schema definitions |
| `tools/ai/aci/research_orchestrator.py` | Orchestration engine |
| `tools/ai/aci/__init__.py` | Exports |
| `tools/ai/analyze.py` | CLI handlers |

---

## Status

| Feature | Status |
|---------|--------|
| Schema loading | DONE |
| Preflight validation | DONE |
| CLI handlers | DONE |
| Dry run | DONE |
| Actual execution | PENDING |
| Override parsing | PENDING |
| Semantic comparison for consensus | PENDING |
