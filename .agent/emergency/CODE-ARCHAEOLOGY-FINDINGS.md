# CODE ARCHAEOLOGY FINDINGS

> **Purpose:** Document actual signs found in the codebase
> **Method:** grep, find, read - look at what exists, not what we think exists
> **Created:** 2026-01-26
> **Author:** Claude Opus 4.5

---

## EXECUTIVE SUMMARY

The codebase shows clear signs of organic growth:
- **Duplicate code** (SocraticValidator defined twice)
- **Inconsistent utilities** (8 different `load_yaml` implementations)
- **Mixed libraries** (yaml, pyyaml, ruamel.yaml)
- **Flat structure** (47 tools in one directory)
- **No shared utils** (each tool reinvents basic functions)

But also **pockets of good design**:
- ACI module is well-organized
- Collider core has clear structure
- Some tools have thoughtful docstrings

---

## 1. CODEBASE STATISTICS

```
Python files:        320
Total lines:         93,394
Largest files:
  - analyze.py       3,441 lines (GOD FILE)
  - full_analysis.py 2,441 lines
  - edge_extractor   1,785 lines
  - survey.py        1,411 lines

Tool files:          132
Agent tools:         47 (flat directory)
```

---

## 2. DUPLICATE CODE FOUND

### Critical: Same Class Defined Twice

```python
# context-management/tools/ai/analyze.py

Line 1668: class SocraticValidator:
Line 1995: class SocraticValidator:   # EXACT DUPLICATE!
```

**Impact:** Python uses the second definition, first is dead code.

### Widespread: Utility Functions Duplicated

```
def load_yaml() defined in 8 files:
  - .agent/tools/triage_inbox.py
  - .agent/tools/autopilot.py
  - .agent/tools/update_task_hierarchy.py
  - .agent/tools/opp_generator.py
  - .agent/tools/macro_executor.py
  - .agent/tools/add_task_steps.py
  - .agent/tools/batch_promote.py
  - .agent/tools/trigger_engine.py

def save_yaml() defined in same 8 files

def main() defined 85 times (every tool is standalone)
```

---

## 3. INCONSISTENT LIBRARIES

### YAML Handling

```python
# Three different approaches used:

16 files: import yaml
 8 files: import yaml as pyyaml
 8 files: from ruamel.yaml import YAML
```

**Problem:** No standard way to handle YAML across codebase.

### Path Handling

```python
37 files: from pathlib import Path

# But each constructs paths differently:
Path(__file__).parent.parent.parent / "config"
PROJECT_ROOT / ".agent" / "registry"
os.path.join(SCRIPT_DIR, "..", "config")
```

---

## 4. STRUCTURAL SIGNS

### Flat Directory (.agent/tools/)

```
47 files in one directory
├── Task-related:        21 files
├── Deck/Card-related:    7 files
├── Macro-related:        4 files
├── LOL-related:          4 files
├── Validation-related:   3 files
├── Other:                8 files

No sub-directories for grouping!
```

### Contrast: Well-Organized Module (ACI)

```
context-management/tools/ai/aci/
├── __init__.py          # Clean exports
├── intent_parser.py     # Single responsibility
├── tier_orchestrator.py # Single responsibility
├── context_builder.py   # Single responsibility
├── semantic_finder.py   # Single responsibility
├── context_cache.py     # Single responsibility
├── refinery.py          # Single responsibility
├── research_orchestrator.py  # Single responsibility
└── feedback_store.py    # Single responsibility
```

**Lesson:** Some parts were designed, some grew organically.

---

## 5. NAMING INCONSISTENCIES

### Files

```
deal_cards.py vs deal_cards_ui.py  # Why two?
opp_generator.py vs opp_to_deck.py # Inconsistent prefix
promote_opportunity.py AND promote_opportunity.sh # Duplicate purpose?
claim_task.sh vs release_task.sh   # Shell scripts among Python
```

### Functions

```
load_yaml() vs load_config() vs load_sets_config()
save_yaml() vs save_state() vs save_report()
log() vs print() vs logging.info()
```

---

## 6. TODO/FIXME MARKERS

```bash
$ grep -r "TODO\|FIXME" --include="*.py" | grep -v __pycache__ | wc -l
29

Notable:
# TODO: Implementar clone de repo          (Portuguese!)
# TODO: Replace with real detector call
# TODO: Expandir com 50+ repositórios reais
```

**Sign:** Unfinished work, multilingual comments.

---

## 7. DEAD CODE INDICATORS

### Files Not Modified in 30+ Days

```
standard-model-of-code/src/tools/extract_chat_insights.py
standard-model-of-code/src/tools/dedupe_insights.py
```

### Potential Orphans

```
check_stale.sh        # Last modified: Jan 23
release_task.sh       # Last modified: Jan 23
execute_cutting_phase1.sh  # One-time migration script?
```

---

## 8. IMPORT PATTERNS

### No Internal Import Structure

```
# Tools don't import from each other
# Each tool is standalone
# No shared utilities module

# Exception: ACI module does have clean imports
from .intent_parser import analyze_query
from .tier_orchestrator import route_query
```

---

## 9. DOCUMENTATION INCONSISTENCIES

### Good Docstrings

```python
# autopilot.py - Excellent docstring
"""
AUTOPILOT - Self-Running Repository Orchestrator
=================================================
SMoC Role: Orchestrator | Domain: Automation

The master controller that makes the repo run itself.
...
"""
```

### Missing Docstrings

```python
# Some tools have no docstring at all
# Or just one line
```

---

## 10. RECOMMENDATIONS FROM FINDINGS

### Quick Wins (No Major Refactor)

1. **Delete duplicate SocraticValidator** (line 1668-1770)
2. **Create shared YAML utility** in `.agent/tools/utils/yaml_utils.py`
3. **Standardize on one YAML library** (recommend `pyyaml`)
4. **Add sub-directories** to `.agent/tools/`:
   ```
   .agent/tools/
   ├── task/       # 21 task-related tools
   ├── deck/       # 7 deck/card tools
   ├── macro/      # 4 macro tools
   ├── lol/        # 4 LOL tools
   └── utils/      # Shared utilities
   ```

### Medium Effort

5. **Refactor analyze.py** (3,441 lines → multiple modules)
6. **Standardize logging** (log() vs print() vs logging)
7. **Remove dead code** (check files not modified in 30+ days)

### Architectural

8. **Document which tools belong to which subsystem**
9. **Create import structure** for internal dependencies
10. **Audit all TODO/FIXME** and create tasks or delete

---

## 11. THE GOOD PARTS

Not all is chaos. Well-designed areas:

| Area | Why It's Good |
|------|---------------|
| ACI module | Clean exports, single responsibility per file |
| Collider core | 28 stages but organized into phases |
| autopilot.py | Excellent docstring, clear design |
| BACKGROUND_SERVICES_ONTOLOGY.md | Uses SMoC 33 roles for naming |

**Lesson:** The codebase has both good and bad patterns. The good patterns should be replicated.

---

## 12. NEXT STEPS

1. **Fix critical:** Delete duplicate SocraticValidator
2. **Create:** `.agent/tools/utils/yaml_utils.py`
3. **Organize:** Create sub-directories in `.agent/tools/`
4. **Audit:** Check all TODO/FIXME markers
5. **Document:** Which tools belong to which subsystem

---

*Archaeology reveals the truth. The code doesn't lie.*
