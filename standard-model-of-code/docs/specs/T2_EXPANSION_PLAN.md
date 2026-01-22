# T2 Atom Expansion Plan: 20 → 600+

> **Goal:** Expand T2 (ecosystem-specific) atoms from ~20 to 600+ using pattern library mining.
> **Timeline:** ~2-3 days of implementation
> **Strategy:** Mine existing validated pattern libraries, not generate from scratch

---

## Current State

| Metric | Count |
|--------|-------|
| T2 atoms in AtomRegistry | 7 |
| T2 atoms in YAML | 17 |
| T2 ecosystem patterns defined | 6 (React, ML, Django, Flask, FastAPI, + base) |
| **Target** | **600+** |

---

## Source Inventory (VERIFIED 2026-01-22)

| Source | Rules/Patterns | Confidence | Notes |
|--------|---------------|------------|-------|
| **Semgrep Rules** | **2,085** | **99.5%** | Cloned & parsed - 10/2095 errors |
| ESLint React | 104 | **99%** | Verified via GitHub API |
| ESLint Vue | 250 | **99%** | Verified via GitHub API |
| ESLint Angular | ~50 | 80% | API structure differs |
| Pylint | 300+ | 90% | Well-documented |
| RuboCop | 400+ | 90% | Well-documented |
| **TOTAL POOL** | **3,200+** | | |

### Semgrep Ecosystem Breakdown (VERIFIED)

| Ecosystem | Rules | T2 Potential |
|-----------|-------|--------------|
| terraform | 360 | ~80 atoms |
| python | 152 | ~40 atoms |
| django | 77 | ~25 atoms |
| java | 96 | ~30 atoms |
| express | 72 | ~25 atoms |
| go | 74 | ~25 atoms |
| rails | 56 | ~20 atoms |
| flask | 48 | ~18 atoms |
| php | 45 | ~15 atoms |
| solidity | 50 | ~18 atoms |
| **20+ more** | 1,055 | ~250 atoms |

**Categories:**
- security: 1,585 (76%)
- best-practice: 207 (10%)
- correctness: 124 (6%)
- Other: 169 (8%)

**Realistic yield after deduplication:** 500-700 unique T2 atoms

---

## Detailed Plan

### Phase 1: Semgrep Mining (Primary Source)

#### Step 1.1: Clone Semgrep Rules Repository
```bash
git clone --depth 1 https://github.com/semgrep/semgrep-rules /tmp/semgrep-rules
```

| Metric | Value |
|--------|-------|
| Confidence | **99%** |
| Risk | None - public repo, MIT-compatible |
| Time | ~30 seconds |
| Blocker | None |

#### Step 1.2: Parse YAML Rules → Extract Metadata

**Script:** `tools/mine_semgrep.py`

```python
# Pseudocode
for yaml_file in glob("**/*.yaml"):
    rule = yaml.load(yaml_file)
    extract:
        - rule['id'] → atom_id
        - rule['metadata']['technology'] → ecosystem
        - rule['message'] → description
        - rule['patterns'] → detection_hints (simplified)
        - rule['metadata']['category'] → category
```

| Metric | Value |
|--------|-------|
| Confidence | **95%** |
| Risk | YAML parsing edge cases |
| Time | ~2 hours (script + testing) |
| Blocker | None - format is well-documented |
| Validation | Parse 10 random rules first, verify extraction |

**Confidence Boosters:**
- [x] Verified rule format via actual fetch (see above)
- [x] Rules have consistent structure: `id`, `patterns`, `message`, `metadata`
- [ ] TODO: Validate 10 rules from each ecosystem

#### Step 1.3: Convert to T2 Atom Format

**Input:** Semgrep rule
```yaml
id: python-django-security-sql-injection
metadata:
  technology: [django]
  category: security
message: "SQL injection vulnerability detected"
```

**Output:** T2 Atom
```json
{
  "id": "EXT.DJANGO.SEC.001",
  "name": "SQL Injection Pattern",
  "ecosystem": "django",
  "category": "security",
  "description": "SQL injection vulnerability detected",
  "source": "semgrep:python-django-security-sql-injection",
  "tier": "T2"
}
```

| Metric | Value |
|--------|-------|
| Confidence | **90%** |
| Risk | ID collision, naming conventions |
| Time | ~1 hour (mapping logic) |
| Blocker | Need ID generation scheme |

**Confidence Boosters:**
- [ ] Define ID generation: `EXT.{ECOSYSTEM}.{CATEGORY}.{SEQUENCE}`
- [ ] Create ecosystem → abbreviation map
- [ ] Handle multi-technology rules

#### Step 1.4: Deduplicate & Categorize

Many Semgrep rules detect variations of the same pattern.

**Strategy:**
1. Group by `ecosystem + category`
2. Cluster by semantic similarity (message/description)
3. Keep one representative per cluster
4. Est: 2,024 rules → ~500 unique atoms

| Metric | Value |
|--------|-------|
| Confidence | **85%** |
| Risk | Over-deduplication loses nuance |
| Time | ~2 hours |
| Blocker | Similarity threshold tuning |

**Confidence Boosters:**
- [ ] Test dedup on Python rules first (337 → expected ~100)
- [ ] Manual review of 20 random dedup decisions
- [ ] Keep `source` field to trace back to original rules

#### Step 1.5: Output to YAML/JSON

Write to `src/patterns/ATOMS_T2_MINED.yaml` or split by ecosystem:
- `ATOMS_T2_DJANGO.yaml`
- `ATOMS_T2_REACT.yaml`
- etc.

| Metric | Value |
|--------|-------|
| Confidence | **99%** |
| Risk | None |
| Time | ~30 minutes |
| Blocker | None |

---

### Phase 2: ESLint Mining (Frontend Ecosystems)

#### Step 2.1: Clone ESLint Plugin Repos

```bash
git clone --depth 1 https://github.com/jsx-eslint/eslint-plugin-react /tmp/eslint-react
git clone --depth 1 https://github.com/vuejs/eslint-plugin-vue /tmp/eslint-vue
```

| Metric | Value |
|--------|-------|
| Confidence | **99%** |
| Risk | None |
| Time | ~30 seconds |

#### Step 2.2: Parse JS Rule Files → Extract Metadata

ESLint rules are JS files with a `meta` object:

```javascript
module.exports = {
  meta: {
    docs: {
      description: 'Enforce boolean prop naming',
      category: 'Stylistic Issues',
    },
  },
  create(context) { ... }
}
```

| Metric | Value |
|--------|-------|
| Confidence | **85%** |
| Risk | JS parsing more complex than YAML |
| Time | ~3 hours |
| Blocker | Need AST parser or regex extraction |

**Confidence Boosters:**
- [ ] Use `tree-sitter-javascript` for reliable parsing
- [ ] Fallback: regex for `meta.docs.description`
- [ ] Test on 10 React rules first

#### Step 2.3: Convert to T2 Format

Same as Semgrep conversion.

| Metric | Value |
|--------|-------|
| Confidence | **90%** |
| Time | ~1 hour |

---

### Phase 3: Integration with Collider

#### Step 3.1: Update `atom_loader.py`

Add new YAML files to the loader:

```python
# In build_unified_taxonomy()
t2_mined_files = [
    "ATOMS_T2_DJANGO.yaml",
    "ATOMS_T2_FLASK.yaml",
    "ATOMS_T2_REACT.yaml",
    "ATOMS_T2_VUE.yaml",
    # ...
]
```

| Metric | Value |
|--------|-------|
| Confidence | **99%** |
| Risk | None - existing pattern |
| Time | ~30 minutes |

#### Step 3.2: Update `atom_registry.py` Detection

Add detection patterns from mined rules:

```python
ecosystem_patterns["django"]["code_patterns"].update(mined_patterns)
```

| Metric | Value |
|--------|-------|
| Confidence | **80%** |
| Risk | Pattern quality varies |
| Time | ~2 hours |

**Confidence Boosters:**
- [ ] Only import patterns with `confidence: HIGH` in Semgrep
- [ ] Validate detection on sample repos

#### Step 3.3: Run Full Test Suite

```bash
pytest tests/ -v
```

| Metric | Value |
|--------|-------|
| Confidence | **95%** |
| Risk | New atoms may break assumptions |
| Time | ~10 minutes |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Semgrep format changes | Medium | Low | Pin to specific commit |
| Deduplication too aggressive | Medium | Medium | Keep source references, manual review |
| ESLint parsing fails | Low | Medium | Fall back to Semgrep-only (still 500 atoms) |
| ID collisions | Medium | Low | Use hashing + sequence numbers |
| Detection patterns too broad | Medium | Medium | Test on real repos before merge |

---

## Confidence Summary (UPDATED 2026-01-22)

| Phase | Step | Confidence | Time Est | Validated |
|-------|------|------------|----------|-----------|
| 1 | Clone Semgrep | **99%** | 30s | ✅ DONE |
| 1 | Parse YAML | **99.5%** | 2h | ✅ 2085/2095 success |
| 1 | Convert format | **95%** | 1h | ✅ Format verified |
| 1 | Deduplicate | 85% | 2h | ⏳ Pending |
| 1 | Output | 99% | 30m | ⏳ Pending |
| 2 | Clone ESLint | 99% | 30s | ⏳ Pending |
| 2 | Parse JS | 85% | 3h | ⏳ Pending |
| 2 | Convert format | 90% | 1h | ⏳ Pending |
| 3 | Update loader | 99% | 30m | ⏳ Pending |
| 3 | Update registry | 80% | 2h | ⏳ Pending |
| 3 | Test suite | 95% | 10m | ⏳ Pending |

**Overall Confidence: 92%** (raised from 88% after validation)
**Total Time: ~13 hours (2 days)**

### What's Been Validated

1. ✅ Semgrep repo cloned successfully
2. ✅ 2,085 rules parsed with 99.5% success rate
3. ✅ Ecosystem distribution confirmed (20+ ecosystems)
4. ✅ Metadata extraction working (id, technology, category, message)
5. ✅ Django: 77 rules, Flask: 48 rules, Express: 72 rules available

---

## Deliverables

1. **Script:** `tools/mine_semgrep.py` - Semgrep → T2 converter
2. **Script:** `tools/mine_eslint.py` - ESLint → T2 converter
3. **Data:** `src/patterns/ATOMS_T2_*.yaml` - Mined atoms by ecosystem
4. **Updated:** `atom_loader.py` - Loads new atoms
5. **Updated:** `atom_registry.py` - Detection patterns
6. **Report:** Mining statistics and quality metrics

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| T2 atom count | 600+ | `len(taxonomy['atoms'])` where tier=T2 |
| Ecosystem coverage | 15+ | Unique ecosystems in mined atoms |
| Detection accuracy | >80% | Test on 10 sample repos |
| Test suite | 100% pass | `pytest tests/` |

---

## Next Action

**Raise confidence on Step 1.2 (Parse YAML):**

```bash
# Validate Semgrep rule parsing on 10 random files
python3 -c "
import yaml
from pathlib import Path
import random

rules_dir = Path('/tmp/semgrep-rules')
yaml_files = list(rules_dir.glob('**/*.yaml'))
sample = random.sample(yaml_files, 10)

for f in sample:
    with open(f) as fp:
        data = yaml.safe_load(fp)
        rules = data.get('rules', [])
        for r in rules:
            print(f'{r.get(\"id\", \"NO_ID\")} | {r.get(\"metadata\", {}).get(\"technology\", [])}')
"
```

Run this after cloning to validate parsing before building full pipeline.
