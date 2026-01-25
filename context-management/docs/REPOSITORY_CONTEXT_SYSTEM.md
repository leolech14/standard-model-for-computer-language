# Repository Context System

> The always-fresh internal map of the codebase.

## Quick Start

```bash
# One-shot update (manual)
python context-management/tools/continuous_cartographer.py

# Start background daemon (15s debounce in local mode)
python context-management/tools/drift_guard.py --local --debug

# Run single pass then exit (for cron/launchd)
python context-management/tools/drift_guard.py --once
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DRIFT GUARD (File Watcher)                   │
│  Watches: src/, docs/, tools/, *.yaml                          │
│  Ignores: .collider/, intelligence/, reports/ (prevents loops) │
│  Throttle: 15s (local) / 300s (daemon)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ triggers
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               CONTINUOUS CARTOGRAPHER (Payload)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ OPTION A: Cartographer (ALWAYS RUNS)                    │   │
│  │ • Runs: collider full . --output .collider              │   │
│  │ • Output: .collider/unified_analysis.json (~25MB)       │   │
│  │ • Cost: FREE (local CPU)                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ OPTION B: Guardian (CONDITIONAL)                        │   │
│  │ • Triggers: *.py, *.ts, *.js, *.go changes              │   │
│  │ • Runs: analyze.py --verify pipeline                    │   │
│  │ • Output: reports/socratic_audit_latest.md              │   │
│  │ • Cost: 1 Gemini API call                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ OPTION C: Researcher (MANUAL ONLY)                      │   │
│  │ • Trigger: Explicit command or new dependencies         │   │
│  │ • Runs: analyze.py --aci --tier perplexity "<query>"    │   │
│  │ • Output: docs/research/perplexity/                     │   │
│  │ • Cost: Perplexity API call                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Commands

| Task | Command |
|------|---------|
| **Update context now** | `python continuous_cartographer.py` |
| **Update + verify** | `python continuous_cartographer.py --verify` |
| **Check what would run** | `python continuous_cartographer.py --dry-run` |
| **Start daemon (local)** | `python drift_guard.py --local --debug` |
| **Start daemon (production)** | `python drift_guard.py --interval 3600` |
| **Single pass** | `python drift_guard.py --once` |

## Output Files

| File | Purpose | Size |
|------|---------|------|
| `.collider/unified_analysis.json` | The knowledge graph | ~25MB |
| `.collider/output_human-readable_*.html` | Visual map | ~2MB |
| `reports/socratic_audit_latest.md` | Verification report | ~10KB |
| `intelligence/drift_guard_state.json` | Daemon state | ~1KB |

## File Change Detection

**Triggers Option B (semantic verification):**
- `.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.go`, `.rs`, `.java`, `.kt` files
- `semantic_models.yaml`, `analysis_sets.yaml`, `pyproject.toml`
- Any file in `src/`, `core/`, `lib/`, `packages/`

**Ignored (prevents infinite loops):**
- `.collider/` directory
- `intelligence/` directory
- `reports/` directory

## Daemon Modes

| Mode | Throttle | Check Interval | Use Case |
|------|----------|----------------|----------|
| `--local` | 15s | 10s | Active development |
| (default) | 300s | 30s | Background service |

## Agent Instructions

```
PRIMARY OBJECTIVE: Keep repository context current.

On each change event (15s debounce):
1. Run Collider → unified_analysis.json (always)
2. If code file changed → Run semantic verification (conditional)

CRITICAL: Never watch .collider/ - causes infinite loops.

The daemon handles all of this automatically.
Just run: python drift_guard.py --local --debug
```

## Troubleshooting

**Daemon not detecting changes:**
- Check `WATCH_PATHS` in `drift_guard.py:52`
- Ensure file isn't in `IGNORE_PATHS`

**Cartographer fails:**
- Check `.tools_venv` is active
- Run `pip install -e .` in `standard-model-of-code/`

**unified_analysis.json not updating:**
- Check `.collider/` directory permissions
- Run cartographer manually with verbose output
