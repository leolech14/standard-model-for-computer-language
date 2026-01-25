# Batch Grade Learnings (From Degraded Results)

**Source:** 590 successful `collider grade` runs on top GitHub repos
**Date:** 2026-01-24/25
**Status:** DEGRADED (grades only, no unified_analysis.json)

Despite being degraded, these results reveal significant insights about the Health Model.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Repos analyzed | 590 (of 999 attempted) |
| Grade distribution | B=1.7%, C=67.5%, D=30.2%, F=0.7% |
| Health index range | 4.52 - 8.29 |
| Mean health | 7.13 |
| Median health | 7.23 |

**Key Finding:** CYCLES score is the primary differentiator between grades.

---

## 1. Grade Distribution

```
A:    0 (  0.0%)
B:   10 (  1.7%) ██
C:  398 ( 67.5%) █████████████████████████████████████████████████████████████████
D:  178 ( 30.2%) ██████████████████████████████
F:    4 (  0.7%)
```

**Interpretation:** Most real-world repos score C (average health). Only 1.7% achieve B grade.

---

## 2. What Separates Good from Bad

| Component | Grade B | Grade C | Grade D | Grade F |
|-----------|---------|---------|---------|---------|
| **cycles** | **9.40** | 6.63 | 4.10 | **1.00** |
| gradients | 10.00 | 9.99 | 9.57 | 5.00 |
| isolation | 8.98 | 8.69 | 7.91 | 7.88 |
| elevation | 4.94 | 4.94 | 4.92 | 4.98 |
| coupling | 7.47 | 7.47 | 7.46 | 7.49 |

**PRIMARY DIFFERENTIATOR: CYCLES (Betti number b1)**
- Grade B: cycles = 9.40
- Grade F: cycles = 1.00
- 9.4x difference explains ~90% of grade variance

**SECONDARY: GRADIENTS**
- Grade B: gradients = 10.00
- Grade F: gradients = 5.00

**CONSTANT (Not Differentiating):**
- elevation (~5.0 for all)
- coupling (~7.5 for all)

---

## 3. Health Model Validation

The data suggests the formula weights may need adjustment:

```
Current:  H = 0.25*T + 0.25*E + 0.25*Gd + 0.25*A
          (equal weights)

Evidence: cycles explains most variance, elevation/coupling are constant

Proposed: H = 0.40*T + 0.10*E + 0.30*Gd + 0.20*A
          (weight by discriminating power)
```

---

## 4. Golden Repo Candidates (Grade B)

| Health | Nodes | Edges | Language | Repo |
|--------|-------|-------|----------|------|
| 8.29 | 3141 | 3395 | Python | mingrammer/diagrams |
| 8.17 | 14 | 16 | JavaScript | resume/resume.github.com |
| 8.17 | 73 | 76 | JavaScript | jashkenas/backbone |
| 8.12 | 8 | 8 | JavaScript | VincentGarreau/particles.js |
| 8.08 | 4 | 2 | Python | vinta/awesome-python |
| 8.08 | 62 | 86 | JavaScript | maboloshi/github-chinese |
| 8.05 | 3291 | 3358 | Go | helm/charts |
| 8.04 | 13 | 20 | JavaScript | jamiebuilds/the-super-tiny-compiler |
| 8.04 | 2834 | 7306 | Go | samber/lo |
| 8.02 | 29 | 44 | JavaScript | JakeChampion/fetch |

**Recommendation:** Use these 10 for regression harness (Task #31, #35).

---

## 5. Failure Analysis

| Failure Type | Count | % |
|--------------|-------|---|
| timeout | 288 | 70.4% |
| skipped_too_large | 99 | 24.2% |
| grade_failed | 22 | 5.4% |

**Too Large Repos:** min=505MB, max=19GB, mean=1.8GB

**Implication:** 3-minute timeout insufficient for large repos. Consider:
- Increasing timeout to 5-10 min
- Pre-filtering by size more aggressively
- Sampling large repos instead of full analysis

---

## 6. Language Performance

| Language | Count | Avg Health | Grade Distribution |
|----------|-------|------------|-------------------|
| JavaScript | 183 | 7.08 | B:6, C:108, D:68, F:1 |
| Python | 140 | **7.48** | B:2, C:131, D:7 |
| Go | 135 | 7.28 | B:2, C:127, D:6 |
| TypeScript | 132 | **6.65** | C:32, D:97, F:3 |

**Observations:**
- Python repos have highest average health (7.48)
- TypeScript repos have lowest (6.65) and most D/F grades
- This may reflect TypeScript's tendency toward complex dependency graphs

---

## 7. Size vs Health

| Size Bucket | Count | Avg Health |
|-------------|-------|------------|
| 0-10MB | 244 | 7.22 |
| 10-50MB | 202 | 7.08 |
| 50-100MB | 68 | 6.94 |
| 100-500MB | 76 | 7.11 |

**Finding:** Weak inverse correlation. Smaller repos slightly healthier, but effect is minor.

---

## 8. Famous Repos Performance

| Grade | Repo | Health | Cycles |
|-------|------|--------|--------|
| C | pallets/flask | 7.56 | 6.8 |
| C | angular/angular.js | 7.49 | 7.7 |
| C | lodash/lodash | 7.32 | 7.4 |
| C | docker/compose | 7.20 | 6.2 |
| C | eslint/eslint | 7.20 | 6.3 |
| D | **expressjs/express** | 6.99 | 4.5 |
| D | **axios/axios** | 6.72 | 3.5 |
| D | **vuejs/vue** | 6.68 | 5.2 |
| D | ReactiveX/rxjs | 6.41 | 3.7 |

**Insight:** Even famous, well-maintained repos mostly score C/D. The Health Model is harsh but consistent.

---

## 9. Anomalies Worth Investigating

### High Connectivity, Good Grade
These repos have high edge/node ratios but still score well:
- julienschmidt/httprouter (ratio 3.2, grade C)
- eriklindernoren/ML-From-Scratch (ratio 3.0, grade C)

### Low Nodes, High Health
Very small repos that score well:
- resume/resume.github.com (14 nodes, B grade)
- particles.js (8 nodes, B grade)
- the-super-tiny-compiler (13 nodes, B grade)

### High Nodes, Low Health
Large repos that score poorly:
- DavidHDev/react-bits (1104 nodes, D grade)
- neoclide/coc.nvim (1281 nodes, D grade)

---

## 10. Worst Performers (Grade F)

| Repo | Health | Nodes | Edges | Issue |
|------|--------|-------|-------|-------|
| simple-icons/simple-icons | 4.52 | 4 | 163 | 40:1 edge ratio |
| gothinkster/realworld | 4.56 | 5 | 122 | 24:1 edge ratio |
| ItzCrazyKns/Perplexica | 4.68 | 4 | 427 | 107:1 edge ratio |
| AykutSarac/jsoncrack.com | 4.87 | 13 | 646 | 50:1 edge ratio |

**Pattern:** All Grade F repos have extremely high edge/node ratios (>20:1). These are likely:
- Massive re-export hubs
- Index files aggregating many modules
- Auto-generated code

---

## 11. Actionable Insights

### For Health Model (Task #18)
1. Consider weighting cycles higher (0.40 vs 0.25)
2. Elevation appears constant - investigate why
3. Coupling appears constant - investigate why

### For Golden Repos (Task #31, #35)
1. Use the 10 Grade B repos for regression harness
2. Include 2 Grade F repos as "known bad" baselines
3. Include 5 famous repos (flask, express, vue, axios, lodash) as "industry standard" benchmarks

### For Batch System (Task #37)
1. Increase timeout from 3 to 5-10 minutes
2. Pre-filter repos >500MB before clone
3. Consider sampling strategy for large repos

### For Future Research
1. Why is elevation constant at ~5.0?
2. Why is coupling constant at ~7.5?
3. What makes TypeScript repos score lower?
4. Investigate the 107:1 edge ratio anomalies

---

## 12. Data Location

| Data | Path |
|------|------|
| Raw results | `final_results_20260125_005603.json` |
| This analysis | `LEARNINGS.md` |
| Degradation marker | `DEGRADED.md` |
| Full scans target | `../full_scans/` |

---

## Next Steps

1. Run full `collider full` on Grade B repos (10 repos, ~2 hrs, ~$0.05)
2. Validate learnings with unified_analysis.json data
3. Update Health Model weights based on findings
4. Create regression harness with golden repos
