# Roadmap Index: Standard Model Validation

**Overview:** 5 independent tracks to validate and publish the Standard Model of Code

---

## 🎯 Roadmap Summary

| # | Track | Timeline | Dependencies | Start Now? |
|---|-------|----------|--------------|------------|
| **1** | [Benchmark Dataset](1_BENCHMARK_DATASET.md) | 6-8 weeks | None | ✅ Yes |
| **2** | [Ground Truth](2_GROUND_TRUTH.md) | 4-6 weeks | Roadmap 1 (M1.4) | After M1.4 |
| **3** | [Statistical Analysis](3_STATISTICAL_ANALYSIS.md) | 3-4 weeks | Roadmap 2 (M2.6) | After M2.6 |
| **4** | [Reproduction Package](4_REPRODUCTION_PACKAGE.md) | 2-3 weeks | Roadmap 3 (M3.7) | After M3.7 |
| **5** | [Publication](5_PUBLICATION.md) | 12-16 weeks | All complete | Can draft early |

**Total Timeline:** ~6 months (critical path: 1 → 2 → 3 → 4 → 5)

---

## 📊 Dependency Graph

```
Roadmap 1: Benchmark
    ├─> (M1.4: Download repos)
    │       ↓
    └─> Roadmap 2: Ground Truth
            ├─> (M2.6: Validated labels)
            │       ↓
            └─> Roadmap 3: Analysis
                    ├─> (M3.7: Results)
                    │       ↓
                    └─> Roadmap 4: Reproduction
                            │
                            ↓
                        Roadmap 5: Publication
                            (can draft intro/background in parallel)
```

---

## 🚀 Quick Start Guide

### Week 1: Immediate Actions
1. **Start Roadmap 1** (no dependencies)
   - Create benchmark design doc
   - Search GitHub for candidates
   - **Deliverable:** `candidate_repos.csv`

2. **Start Roadmap 5 (draft)** (parallel)
   - Write abstract
   - Outline introduction
   - **Deliverable:** `paper/outline.md`

---

### Weeks 2-8: Dataset Collection
- Focus: Roadmap 1 (M1.1 → M1.6)
- **Blocker-free:** Can proceed independently
- **Deliverable:** 100-repo benchmark on Zenodo

---

### Weeks 9-14: Annotation
- Focus: Roadmap 2 (M2.1 → M2.6)
- **Blocker:** Needs M1.4 (repos downloaded)
- **Deliverable:** 2,000 ground truth labels

---

### Weeks 15-18: Analysis
- Focus: Roadmap 3 (M3.1 → M3.7)
- **Blocker:** Needs M2.6 (ground truth)
- **Deliverable:** Metrics, plots, significance tests

---

### Weeks 19-21: Package
- Focus: Roadmap 4 (M4.1 → M4.7)
- **Blocker:** Needs M3.7 (all results)
- **Deliverable:** Reproduction package on Zenodo

---

### Weeks 22-36: Publication
- Focus: Roadmap 5 (M5.1 → M5.7)
- **Blocker:** Needs all roadmaps complete
- **Deliverable:** Accepted paper at ICSE/OOPSLA

---

## 🎯 Minimum Viable Validation

**If time/budget limited, focus on:**

1. **Roadmap 1 (Essential):** Must have benchmark
2. **Roadmap 2 (Essential):** Must have ground truth
3. **Roadmap 3 (Essential):** Must have metrics
4. **Roadmap 4 (Nice-to-have):** Helpful but not blocking
5. **Roadmap 5 (Goal):** Publication is the deliverable

**MVP Timeline:** 3 months (Roadmaps 1-3 only)

---

## 📋 Checklist: Are We Ready?

### Before Starting
- [ ] Collider tool is stable (`collider analyze` works)
- [ ] Budget allocated (~$10k for annotation)
- [ ] Team assembled (2-3 researchers)

### Before Roadmap 1
- [ ] None (can start immediately)

### Before Roadmap 2
- [ ] Roadmap 1 M1.4 complete (repos downloaded)
- [ ] Annotators recruited (3 people)

### Before Roadmap 3
- [ ] Roadmap 2 M2.6 complete (ground truth validated)
- [ ] Statistical tools ready (Python, R)

### Before Roadmap 4
- [ ] Roadmap 3 M3.7 complete (all results)
- [ ] Docker/VM for testing

### Before Roadmap 5
- [ ] All roadmaps complete
- [ ] Target venue selected (ICSE/OOPSLA)

---

## 🔄 Iteration Strategy

**Each roadmap is self-contained:**
- Can be revised independently
- Failure in one doesn't block others (mostly)
- Can loop back if needed

**Example:** If ground truth quality is low (κ < 0.7):
- Revise Roadmap 2 (annotation guidelines)
- Re-run pilot
- Does NOT affect Roadmap 1 (already done)

---

## 🎯 Success Metrics

| Milestone | Target | Current |
|-----------|--------|---------|
| Benchmark size | 100 repos, 1M nodes | 33 repos, 212k nodes ✓ |
| Ground truth | 2,000 labels, κ > 0.8 | 0 (not started) |
| Accuracy | >85% | 87.6% (claimed) ⚠️ |
| Public DOIs | 2 (dataset + repro) | 0 |
| Publication | Accepted at A* venue | Draft in progress |

---

**Next Action:** Start Roadmap 1, Milestone 1 (Benchmark Design)
