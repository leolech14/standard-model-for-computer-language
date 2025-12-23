# Roadmap 1: Benchmark Dataset Assembly

**Goal:** Build a diverse, public dataset of 100+ repositories

**Dependencies:** None (can start immediately)

**Timeline:** 6-8 weeks

**Effort:** 1 person, part-time

---

## Milestones

### M1.1: Dataset Design (Week 1) ✓ INDEPENDENT
**Deliverable:** `docs/benchmark/design.md`

**Tasks:**
- [ ] Define selection criteria (language, size, domain, stars)
- [ ] Create diversity matrix (ensure coverage)
- [ ] Document exclusion criteria (no proprietary, no unmaintained)

**Output:** Clear rules for repo selection

---

### M1.2: Candidate List (Week 2) ✓ INDEPENDENT
**Deliverable:** `data/candidate_repos.csv`

**Tasks:**
- [ ] Search GitHub for candidates (Python, JavaScript, TypeScript)
- [ ] Filter by criteria (>1k stars, active, open-source)
- [ ] Collect metadata (language, LOC, domain, last commit)

**Output:** 200+ candidate repos (will filter to 100)

**Script:**
```bash
python scripts/collect_candidates.py --min-stars 1000 --languages python,javascript
# Output: candidate_repos.csv
```

---

### M1.3: Stratified Sampling (Week 3) ✓ INDEPENDENT
**Deliverable:** `data/benchmark_repos.csv` (100 repos)

**Tasks:**
- [ ] Sort candidates by diversity scores
- [ ] Select 100 repos ensuring language/domain balance
- [ ] Verify accessibility (all cloneable)

**Output:** Final 100-repo list

**Validation:**
```python
# Assert diversity
assert languages.count('python') >= 30
assert languages.count('javascript') >= 20
assert domains.is_diverse()  # No single domain >30%
```

---

### M1.4: Download & Preprocess (Week 4-5) ✓ INDEPENDENT
**Deliverable:** `data/repos/` (cloned repos)

**Tasks:**
- [ ] Clone all 100 repos
- [ ] Run Collider on each
- [ ] Store raw output (`unified_analysis.json` per repo)

**Script:**
```bash
./scripts/download_benchmark.sh
# Output: data/repos/{repo_name}/
#         data/raw/{repo_name}/unified_analysis.json
```

**Error handling:** Log failed repos, retry with backoff

---

### M1.5: Quality Check (Week 6) ✓ INDEPENDENT
**Deliverable:** `data/quality_report.md`

**Tasks:**
- [ ] Verify all 100 repos processed
- [ ] Check for outliers (e.g., 100% Utility)
- [ ] Compute dataset statistics (total nodes, avg per repo)

**Metrics:**
```
Total repos: 100
Total nodes: 1,000,000+
Avg nodes/repo: 10,000
Languages: Python (40%), JS (25%), TS (20%), others (15%)
```

---

### M1.6: Publication (Week 7-8) ✓ INDEPENDENT
**Deliverable:** Public Zenodo/OSF archive

**Tasks:**
- [ ] Package dataset with README
- [ ] Upload to Zenodo (get DOI)
- [ ] Update `docs/VALIDATION_PLAN.md` with DOI

**Output:** 
```
DOI: 10.5281/zenodo.XXXXXXX
Dataset: Standard Model of Code Benchmark v1.0
```

---

## Success Criteria

- [ ] 100 repos selected
- [ ] All repos cloned and analyzed
- [ ] >1M nodes total
- [ ] Diversity matrix balanced
- [ ] Public DOI available

---

## Quick Start (Next Actions)

1. Create `docs/benchmark/design.md` (2 hours)
2. Run GitHub search script (1 day)
3. Review candidate list manually (2 hours)

**Blocker-free:** Can proceed immediately
