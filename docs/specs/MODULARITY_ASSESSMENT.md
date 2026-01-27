# Modularity Assessment: Interproject Portability

> **Purpose:** Evaluate which modules can be "airdropped" into other projects
> **Generated:** 2026-01-27 | **Status:** Assessment Complete

---

## Executive Summary

| Verdict | Details |
|---------|---------|
| **Overall Portability** | 70% of modules are structurally portable |
| **Blocking Issues** | Hardcoded paths, config assumptions |
| **Airdrop-Ready** | 6 modules can be used TODAY |
| **Effort to Fix** | ~2 hours to make all tools portable |

---

## Module Inventory

### .agent/tools/ (39 Python tools)

| Status | Count | Example |
|--------|-------|---------|
| Self-contained (no internal imports) | 39/39 | `oklch_color.py`, `autopilot.py` |
| Has hardcoded paths | ~20 | References `standard-model-of-code/` |
| Truly portable (copy-paste works) | ~10 | `oklch_color.py`, `audit_unicode.py` |

### standard-model-of-code/src/core/ (30+ Python modules)

| Status | Count | Example |
|--------|-------|---------|
| Portable (no internal imports) | ~25 | `atom_loader.py`, `graph_metrics.py` |
| Coupled (orchestrators) | ~5 | `full_analysis.py` (4 imports) |

### viz/assets/modules/ (51 JS modules)

| Status | Count | Example |
|--------|-------|---------|
| Self-contained | 43 | `color-engine.js`, `event-bus.js` |
| Uses shared state | 8 | `flow.js` (3 deps), `layout-helpers.js` |

---

## Airdrop-Ready Modules (Use Today)

These modules can be copied into any project with minimal setup:

### 1. color-engine.js
```
Files: 1 (1,427 lines)
Dependencies: NONE
Export: window.COLOR
```
**How to use:**
```html
<script src="color-engine.js"></script>
<script>
  const color = COLOR.get('tier', 'T0');
</script>
```

### 2. oklch_color.py + hue_wheel.yaml
```
Files: 2 (~350 lines total)
Dependencies: pyyaml
```
**How to use:**
```python
from oklch_color import OKLCHColorMapper
mapper = OKLCHColorMapper(config_path="./hue_wheel.yaml")
hex_color = mapper.get_rgb_hex('.py', recency_days=7, importance=0.8)
```

### 3. event-bus.js
```
Files: 1 (~100 lines)
Dependencies: NONE
Export: window.EVENT_BUS
```
**How to use:**
```javascript
EVENT_BUS.on('my-event', (data) => console.log(data));
EVENT_BUS.emit('my-event', {foo: 'bar'});
```

### 4. atom_loader.py
```
Files: 1 (~200 lines)
Dependencies: pyyaml
```
Generic YAML/JSON loader for hierarchical config files.

### 5. graph_metrics.py
```
Files: 1 (~300 lines)
Dependencies: networkx
```
Generic graph analysis (centrality, clustering, paths).

### 6. data-manager.js
```
Files: 1 (~250 lines)
Dependencies: NONE
Export: window.DATA_MANAGER
```
Generic data loading and caching.

---

## Portability Blockers

### 1. Hardcoded Paths

**Problem:** 20+ files reference `standard-model-of-code/` directly:
```python
# Found in:
# - collider_coverage.py
# - enrichment_orchestrator.py
# - fact_loader.py
# - filesystem_watcher.py
# - import_legacy_tasks.py
# - etc.

SCHEMA_PATH = REPO_ROOT / "standard-model-of-code" / "schema"
```

**Fix:** Use environment variable or config:
```python
import os
SCHEMA_PATH = Path(os.environ.get('COLLIDER_SCHEMA', './schema'))
```

### 2. Config Location Assumptions

**Problem:** Tools assume `.agent/` directory exists:
```python
# Found in autopilot.py, trigger_engine.py, etc.
STATE_FILE = REPO_ROOT / ".agent" / "state" / "autopilot_state.yaml"
```

**Fix:** Accept config directory as parameter:
```python
def __init__(self, config_dir: Path = None):
    config_dir = config_dir or Path.cwd() / ".agent"
```

### 3. PROJECT_elements References

**Problem:** Some tools reference project name directly:
```python
# deal_cards_ui.py
return Path.home() / "PROJECTS_all" / "PROJECT_elements"
```

**Fix:** Use git root detection or env var:
```python
def find_repo_root():
    return Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode().strip())
```

### 4. Missing Package Structure

**Problem:** No formal Python package:
- No `pyproject.toml`
- No `__init__.py` with exports
- No dependency pinning

**Fix:** Create package:
```
elements-tools/
├── pyproject.toml
├── src/
│   └── elements_tools/
│       ├── __init__.py
│       ├── oklch.py
│       └── ...
└── README.md
```

---

## Portability Matrix

| Module | Copy Files | Install Deps | Configure | Works? |
|--------|------------|--------------|-----------|--------|
| color-engine.js | 1 | None | None | ✅ |
| oklch_color.py | 2 | pyyaml | config path | ✅ |
| event-bus.js | 1 | None | None | ✅ |
| autopilot.py | 1 | pyyaml | config dir | ⚠️ needs .agent/ |
| full_analysis.py | 10+ | many | paths | ❌ coupled |

---

## Recommended Actions

### Quick Wins (< 30 min each)

1. **Add `--config-dir` to all tools**
   ```python
   parser.add_argument('--config-dir', default='.agent')
   ```

2. **Replace hardcoded project name**
   ```python
   # Before
   Path.home() / "PROJECTS_all" / "PROJECT_elements"
   # After
   find_repo_root()  # git-based
   ```

3. **Document airdrop-ready modules**
   - Add header comment: `# PORTABLE: Copy this file + deps to any project`

### Medium Effort (2-4 hours)

4. **Create standalone packages**
   ```
   elements-colors/     # oklch_color.py + color-engine.js + config
   elements-automation/ # autopilot.py + trigger_engine.py + circuit breakers
   ```

5. **Add environment variable fallbacks**
   ```python
   REPO_ROOT = Path(os.environ.get('ELEMENTS_ROOT', find_repo_root()))
   ```

### Full Portability (1 day)

6. **Publish to PyPI/npm**
   ```bash
   pip install elements-colors
   npm install @elements/color-engine
   ```

---

## Integration Pattern: "Airdrop"

For projects that want to use Elements modules:

### Minimal (Color System Only)
```bash
# Copy these files:
cp color-engine.js my-project/lib/
cp oklch_color.py my-project/lib/
cp hue_wheel.yaml my-project/config/

# Use in JS:
<script src="lib/color-engine.js"></script>

# Use in Python:
from lib.oklch_color import OKLCHColorMapper
mapper = OKLCHColorMapper('config/hue_wheel.yaml')
```

### Full Agent Stack
```bash
# Copy .agent/ structure:
cp -r .agent/tools/ my-project/.agent/tools/
cp -r .agent/config/ my-project/.agent/config/

# Set environment:
export ELEMENTS_ROOT=$(pwd)

# Run tools:
python .agent/tools/autopilot.py status
```

---

## Conclusion

**Current state:** Most modules are _structurally_ portable but _practically_ blocked by path assumptions.

**Path to full portability:**
1. Fix hardcoded paths (2 hours)
2. Add config directory parameters (1 hour)
3. Document airdrop procedure (30 min)
4. Optional: Publish packages (4 hours)

**Recommendation:** Start with the 6 airdrop-ready modules. Fix blocking issues incrementally as other projects request them.
