# Body (Collider) Context

## What is Collider?

The implementation that applies the Standard Model of Code theory to real codebases. Produces `output.md` - a structured report for LLM consumption.

## Entry Points

| File | Purpose |
|------|---------|
| `cli.py` | CLI entry (`./collider`) |
| `src/core/full_analysis.py` | Main pipeline |
| `src/core/brain_download.py` | Output generator |

## Output Sections

- **IDENTITY**: Node/edge counts, dead code %
- **CHARACTER (RPBL)**: Responsibility, Purity, Boundary, Lifecycle
- **ARCHITECTURE**: Type distribution, layers
- **HEALTH STATUS**: Traffic-light indicators
- **IMPROVEMENTS**: Actionable recipes

## HTML Visualization

Assets location: `src/core/viz/assets/`
- `template.html`
- `styles.css`
- `app.js`

**Critical**: Always regenerate before debugging. Old outputs are stale.

## Testing

```bash
pytest tests/ -v --tb=short
```

Coverage target: 60%+ for core modules.
