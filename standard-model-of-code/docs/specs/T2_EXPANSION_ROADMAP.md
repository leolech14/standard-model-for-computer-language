# T2 ECOSYSTEM EXPANSION ROADMAP

> **Goal:** 17 T2 atoms → 1,000+ T2 atoms across 79 ecosystems
> **Timeline:** 5 days
> **Result:** Universal ecosystem coverage ("all languages")

---

## EXECUTIVE SUMMARY

```
DAY 1: Semgrep extraction pipeline      → 600 atoms
DAY 2: ESLint extraction (frontend)     → +150 atoms
DAY 3: Gap filling (must-haves)         → +100 atoms
DAY 4: Integration & deduplication      → ~850 unique atoms
DAY 5: Testing & documentation          → SHIP
```

---

## PHASE 1: SEMGREP EXTRACTION (Day 1)

### 1.1 Write Extraction Script
**Time:** 2 hours
**Output:** `tools/mine_semgrep.py`

```python
# Pseudocode
def extract_t2_atoms():
    for yaml_file in semgrep_rules:
        rule = parse(yaml_file)
        structures = extract_patterns(rule)
        ecosystem = rule.metadata.technology

        for struct in structures:
            atom = {
                "id": generate_id(ecosystem, struct),
                "name": humanize(struct),
                "ecosystem": ecosystem,
                "pattern": struct,
                "source": f"semgrep:{rule.id}"
            }
            yield atom
```

**Deliverable:** Working extraction script

### 1.2 Run Extraction
**Time:** 30 minutes
**Command:**
```bash
python tools/mine_semgrep.py \
    --input /tmp/semgrep-rules \
    --output src/patterns/t2_mined/
```

**Deliverable:** Raw extracted atoms (~1,700 structures)

### 1.3 Deduplicate & Cluster
**Time:** 2 hours
**Method:**
- Group by ecosystem
- Cluster similar patterns (Levenshtein distance)
- Keep representative from each cluster
- Target: 60% reduction (1,700 → ~600)

**Deliverable:** `src/patterns/ATOMS_T2_SEMGREP.yaml`

### 1.4 Day 1 Checkpoint
```
□ mine_semgrep.py written and tested
□ 2,085 rules processed
□ ~600 unique T2 atoms extracted
□ YAML output validated
```

---

## PHASE 2: ESLINT EXTRACTION (Day 2)

### 2.1 Clone ESLint Plugin Repos
**Time:** 10 minutes
```bash
git clone --depth 1 https://github.com/jsx-eslint/eslint-plugin-react
git clone --depth 1 https://github.com/vuejs/eslint-plugin-vue
git clone --depth 1 https://github.com/angular-eslint/angular-eslint
```

### 2.2 Write ESLint Extraction Script
**Time:** 3 hours
**Output:** `tools/mine_eslint.py`

**Challenge:** ESLint rules are JS, not YAML
**Solution:** Parse `meta.docs` object from each rule file

**Deliverable:** Working extraction script

### 2.3 Run Extraction
**Time:** 1 hour

| Plugin | Rules | Est. Atoms |
|--------|-------|------------|
| React | 104 | ~60 |
| Vue | 250 | ~80 |
| Angular | 50 | ~30 |
| **Total** | **404** | **~150** |

**Deliverable:** `src/patterns/ATOMS_T2_FRONTEND.yaml`

### 2.4 Day 2 Checkpoint
```
□ mine_eslint.py written and tested
□ React atoms extracted (jsx patterns, hooks, lifecycle)
□ Vue atoms extracted (directives, composition API)
□ Angular atoms extracted (decorators, modules)
□ ~150 frontend atoms added
□ Running total: ~750 atoms
```

---

## PHASE 3: GAP FILLING (Day 3)

### 3.1 Identify Critical Gaps
From coverage analysis:

| Missing | Priority | Source |
|---------|----------|--------|
| FastAPI | HIGH | Manual + docs |
| TensorFlow | HIGH | API docs |
| PyTorch | HIGH | API docs |
| Docker | MEDIUM | Dockerfile patterns |
| Kubernetes | MEDIUM | YAML patterns |
| Rust | MEDIUM | Clippy lints |
| Laravel | MEDIUM | Framework docs |
| Swift | LOW | SwiftLint |
| Flutter | LOW | Dart lints |

### 3.2 Manual Atom Definitions
**Time:** 4 hours
**Method:** Define core patterns from official documentation

**FastAPI (15 atoms):**
```yaml
- id: EXT.FASTAPI.ROUTE
  pattern: "@app.get|@app.post|@app.put|@app.delete"
- id: EXT.FASTAPI.DEPENDS
  pattern: "Depends("
- id: EXT.FASTAPI.BASEMODEL
  pattern: "class X(BaseModel)"
# ... 12 more
```

**TensorFlow (20 atoms):**
```yaml
- id: EXT.TF.MODEL
  pattern: "tf.keras.Model|keras.Model"
- id: EXT.TF.LAYER
  pattern: "tf.keras.layers.*"
# ... 18 more
```

**PyTorch (20 atoms):**
```yaml
- id: EXT.TORCH.MODULE
  pattern: "nn.Module"
- id: EXT.TORCH.TENSOR
  pattern: "torch.tensor|torch.Tensor"
# ... 18 more
```

### 3.3 Day 3 Checkpoint
```
□ FastAPI: 15 atoms defined
□ TensorFlow: 20 atoms defined
□ PyTorch: 20 atoms defined
□ Docker: 10 atoms defined
□ Kubernetes: 15 atoms defined
□ Other gaps: 20 atoms defined
□ Running total: ~850 atoms
```

---

## PHASE 4: INTEGRATION (Day 4)

### 4.1 Consolidate YAML Files
**Time:** 1 hour

```
src/patterns/
├── ATOMS_TIER0_CORE.yaml      (existing - 42)
├── ATOMS_TIER1_STDLIB.yaml    (existing - 21)
├── ATOMS_TIER2_ECOSYSTEM.yaml (existing - 17)
└── t2_mined/
    ├── ATOMS_T2_PYTHON.yaml   (django, flask, fastapi)
    ├── ATOMS_T2_JAVASCRIPT.yaml (express, node)
    ├── ATOMS_T2_FRONTEND.yaml (react, vue, angular)
    ├── ATOMS_T2_JAVA.yaml     (spring, servlets)
    ├── ATOMS_T2_CLOUD.yaml    (aws, gcp, azure, terraform)
    ├── ATOMS_T2_ML.yaml       (tensorflow, pytorch)
    └── ATOMS_T2_OTHER.yaml    (go, ruby, php, etc.)
```

### 4.2 Update atom_loader.py
**Time:** 1 hour

```python
def build_unified_taxonomy():
    # Existing loaders...

    # Add mined T2 atoms
    t2_mined_dir = patterns_dir / "t2_mined"
    for yaml_file in t2_mined_dir.glob("ATOMS_T2_*.yaml"):
        atoms = load_yaml_atoms(yaml_file)
        for atom in atoms:
            _add_atom(taxonomy, atom)
```

### 4.3 Update atom_registry.py Detection
**Time:** 2 hours

```python
# Auto-generate ecosystem_patterns from mined atoms
def _load_mined_patterns(self):
    for atom in mined_atoms:
        eco = atom['ecosystem']
        if eco not in self.ecosystem_patterns:
            self.ecosystem_patterns[eco] = {
                "imports": [],
                "code_patterns": {}
            }
        self.ecosystem_patterns[eco]["code_patterns"][atom['id']] = [atom['pattern']]
```

### 4.4 Global Deduplication
**Time:** 2 hours

- Cross-ecosystem dedup (same pattern, different names)
- ID normalization (consistent naming)
- Validation (no orphan references)

### 4.5 Day 4 Checkpoint
```
□ All YAML files consolidated
□ atom_loader.py updated
□ atom_registry.py detection updated
□ Deduplication complete
□ Final count: ~850 unique T2 atoms
□ All tests passing
```

---

## PHASE 5: TESTING & DOCS (Day 5)

### 5.1 Test Against Real Repos
**Time:** 3 hours

| Repo | Ecosystem | Expected Detections |
|------|-----------|---------------------|
| django/django | Django | 50+ |
| pallets/flask | Flask | 30+ |
| tiangolo/fastapi | FastAPI | 25+ |
| facebook/react | React | 40+ |
| vuejs/vue | Vue | 35+ |
| expressjs/express | Express | 25+ |

```bash
./collider full /tmp/test-repos/django --output /tmp/django-analysis
# Verify T2 atoms detected in output
```

### 5.2 Update Documentation
**Time:** 2 hours

**Update CLAUDE.md:**
```markdown
| Atoms | 200 documented, 950 implemented, 79 ecosystems |
```

**Update MODEL.md:**
- Add T2 expansion section
- Document ecosystem coverage

**Create ECOSYSTEM_COVERAGE.md:**
- List all 79 ecosystems
- Show atom counts per ecosystem
- Detection examples

### 5.3 Final Validation
**Time:** 1 hour

```bash
# Run full test suite
pytest tests/ -v

# Verify atom counts
python -c "
from src.core.atom_loader import build_unified_taxonomy
t = build_unified_taxonomy()
print(f'Total atoms: {len(t[\"atoms\"])}')
print(f'T2 atoms: {sum(1 for a in t[\"atoms\"].values() if a.get(\"tier\")==\"T2\")}')
"

# Generate coverage report
python tools/ecosystem_coverage.py --output docs/ECOSYSTEM_COVERAGE.md
```

### 5.4 Day 5 Checkpoint
```
□ 6 real repos tested successfully
□ CLAUDE.md updated
□ MODEL.md updated
□ ECOSYSTEM_COVERAGE.md created
□ All tests passing
□ PR ready for review
```

---

## DELIVERABLES

| Deliverable | Location | Status |
|-------------|----------|--------|
| mine_semgrep.py | `tools/mine_semgrep.py` | ⏳ |
| mine_eslint.py | `tools/mine_eslint.py` | ⏳ |
| T2 YAML files | `src/patterns/t2_mined/*.yaml` | ⏳ |
| Updated loader | `src/core/atom_loader.py` | ⏳ |
| Updated registry | `src/core/atom_registry.py` | ⏳ |
| Coverage doc | `docs/ECOSYSTEM_COVERAGE.md` | ⏳ |
| Test validation | `tests/test_t2_detection.py` | ⏳ |

---

## SUCCESS METRICS

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| T2 Atoms | 17 | ~850 | 600+ ✓ |
| Ecosystems | 6 | 79 | 25+ ✓ |
| Must-have coverage | 52% | 100% | 100% ✓ |
| Detection accuracy | ? | >80% | >80% |

---

## RISK MITIGATION

| Risk | Mitigation |
|------|------------|
| Pattern quality varies | Manual review of top 20 ecosystems |
| ID collisions | Hash-based ID generation |
| Detection false positives | Threshold tuning, test on real repos |
| Semgrep format changes | Pin to specific commit |

---

## NEXT ACTION

**Start Phase 1.1:** Write `tools/mine_semgrep.py`

```bash
cd /Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code
touch tools/mine_semgrep.py
```
