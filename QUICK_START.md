# Quick Start

```bash
# 1. Boot (shows your options, current state, rules)
./concierge

# 2. Work (pick from the deck or describe your task)

# 3. Done (tests pass, changes committed, summary provided)
```

## Rules (Priority 0)
- Never leave uncommitted changes
- Run tests before claiming done
- Provide summary with rationale

## Commands
| Task | Command |
|------|---------|
| Analyze | `./collider full <path> --output <dir>` |
| Test | `cd standard-model-of-code && pytest tests/ -q` |
| AI Query | `doppler run -- python context-management/tools/ai/analyze.py "query"` |

## Need More?
- Theory: `standard-model-of-code/docs/MODEL.md`
- Deep docs: `context-management/docs/deep/`
