# Node Count Ground Truth

**Date:** 2026-01-23
**Status:** CANONICAL
**Purpose:** Prevent drift in Collider's self-measurement

## Problem

Node counts drifted from 700 → 1800 → 2700 → 5200 due to:
1. Broken survey import (vendor files not excluded)
2. `.repos_cache/` analyzed (test repository data)
3. Scope creep (tests, tools, viz added to analysis)

## Canonical Scopes

| Scope | Count | What It Includes |
|-------|-------|------------------|
| **Collider Core** | ~1,179 | Python analysis engine + pipeline stages |
| **Collider Full** | ~1,961 | Core + JavaScript visualization |
| **With Tests** | ~2,353 | Full + test suite |
| **Everything** | ~2,787 | All code in repo |

## Breakdown (2026-01-23)

```
📦 CORE ENGINE (Python):
    1009  src/core/ (analysis engine)
     170  pipeline/stages/ (27 stage classes)
       0  src/patterns/
   ────────
    1179  SUBTOTAL

🎨 VISUALIZATION (JS):
     782  viz/assets/ (48 JS modules)

🧪 TESTS:
     392  tests/

🔧 TOOLING:
     165  tools/
      37  scripts/
      40  schema/
   ────────
     242  SUBTOTAL

⚙️  OTHER:
       6  __codome__ (synthetic boundaries)
       3  root files (cli.py, setup.py)
```

## Node Types (Syntactic)

| Kind | Count | Description |
|------|-------|-------------|
| function | 1,113 | Standalone functions |
| method | 992 | Class methods |
| class | 311 | Class definitions |
| module | 167 | Module/file-level constructs |
| unknown | 198 | JS patterns not yet classified |
| boundary | 6 | Synthetic codome boundaries |

## Historical Context

- **700-800**: Original core engine (before pipeline stages, before viz analysis)
- **+170**: Pipeline stages added (2026-01-23)
- **+782**: JavaScript visualization now analyzed
- **+392**: Tests now analyzed
- **5242**: Bug - vendor files + .repos_cache included

## Exclusions (Survey Stage 0)

These paths are EXCLUDED from analysis:
- `node_modules/`
- `vendor/`
- `.repos_cache/` (test data)
- `dist/`, `build/`, `out/`
- `*.min.js`, `*.min.css`
- `.git/`, `__pycache__/`, `.venv/`

## Validation Command

```bash
# Run collider on itself and verify count
./collider full . --output .collider

# Check node count
python3 -c "
import json
d = json.load(open('.collider/output_llm-oriented_*.json'))
print(f'Total nodes: {len(d[\"nodes\"])}')"
```

## CI Check (Future)

```bash
# Expected ranges (±10% tolerance)
CORE_MIN=1060   # 1179 * 0.9
CORE_MAX=1297   # 1179 * 1.1
FULL_MIN=1765   # 1961 * 0.9
FULL_MAX=2157   # 1961 * 1.1

# Fail build if outside range
```

## When Count Changes

If the node count changes significantly:
1. **Identify cause** - new feature? bug? scope change?
2. **Update this document** with new breakdown
3. **Update CI thresholds** if legitimate change
4. **Do NOT accept drift silently**
