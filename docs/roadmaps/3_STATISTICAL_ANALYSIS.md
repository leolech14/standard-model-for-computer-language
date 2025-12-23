# Roadmap 3: Statistical Analysis & Evaluation

**Goal:** Measure accuracy, compute metrics, run statistical tests

**Dependencies:** Roadmap 2 (M2.6: Ground truth validated)

**Timeline:** 3-4 weeks

**Effort:** 1 researcher, full-time

---

## Milestones

### M3.1: Train/Test Split (Week 1) ✓ INDEPENDENT
**Deliverable:** `data/train.csv`, `data/test.csv`

**Tasks:**
- [ ] Split 2,000 samples: 80% train (1,600), 20% test (400)
- [ ] Stratify by language/domain (same distribution in both)
- [ ] Seed for reproducibility

**Script:**
```python
python scripts/split_dataset.py --seed 42 --ratio 0.8
# Output: train.csv (1,600), test.csv (400)
```

**Validation:** Assert distribution match

---

### M3.2: Baseline Implementations (Week 1-2) ✓ INDEPENDENT
**Deliverable:** `scripts/baselines/` (4 baseline methods)

**Tasks:**
- [ ] Random: Random role assignment
- [ ] Majority: Always predict "Utility"
- [ ] Keyword: Simple prefix matching
- [ ] LLM: GPT-4 zero-shot (if budget allows)

**Output:** Predictions for all 400 test samples

**Script:**
```bash
python scripts/baselines/random.py --test data/test.csv
python scripts/baselines/majority.py --test data/test.csv
python scripts/baselines/keyword.py --test data/test.csv
# Output: predictions_{method}.csv
```

---

### M3.3: Collider Predictions (Week 2) ✓ INDEPENDENT
**Deliverable:** `predictions_collider.csv`

**Tasks:**
- [ ] Run Collider on test set (400 samples)
- [ ] Extract predicted roles
- [ ] Compare against ground truth

**Script:**
```python
python scripts/predict_collider.py --test data/test.csv
# Output: predictions_collider.csv (id, predicted_role, confidence)
```

---

### M3.4: Metric Computation (Week 2-3) ✓ INDEPENDENT (after M3.2, M3.3)
**Deliverable:** `results/metrics.csv`

**Tasks:**
- [ ] Accuracy (overall, per-role)
- [ ] Precision, Recall, F1 (per role)
- [ ] Confusion matrix
- [ ] Confidence calibration plot

**Script:**
```python
python scripts/compute_metrics.py \
  --ground_truth data/test.csv \
  --predictions predictions_collider.csv \
  --output results/metrics.csv
```

**Output:**
```
Accuracy: 87.6%
Precision (avg): 86.2%
Recall (avg): 85.8%
F1 (avg): 86.0%
```

---

### M3.5: Statistical Significance (Week 3) ✓ INDEPENDENT
**Deliverable:** `results/significance.txt`

**Tasks:**
- [ ] Paired t-test: Collider vs baselines
- [ ] Bootstrap confidence intervals (95% CI)
- [ ] Effect size (Cohen's d)

**Script:**
```python
python scripts/significance_test.py \
  --method1 predictions_collider.csv \
  --method2 predictions_keyword.csv \
  --output results/significance.txt
```

**Output:**
```
t-statistic: 12.4
p-value: < 0.001
Cohen's d: 2.1 (large effect)
Conclusion: Collider significantly better (p < 0.001)
```

---

### M3.6: Ablation Study (Week 3-4) ✓ INDEPENDENT
**Deliverable:** `results/ablation.csv`

**Tasks:**
- [ ] Remove each pattern type (prefix, suffix, inheritance, path)
- [ ] Re-run predictions
- [ ] Measure accuracy drop

**Script:**
```python
python scripts/ablation.py --remove prefix --test data/test.csv
python scripts/ablation.py --remove suffix --test data/test.csv
# Output: ablation.csv (pattern_removed, accuracy_drop)
```

**Output:**
```
No pattern removed: 87.6%
Remove prefix: 72.3% (-15.3%)
Remove suffix: 79.1% (-8.5%)
Remove inheritance: 82.4% (-5.2%)
```

---

### M3.7: Visualization (Week 4) ✓ INDEPENDENT
**Deliverable:** `results/plots/` (5 plots)

**Tasks:**
- [ ] Confusion matrix heatmap
- [ ] Accuracy by confidence (calibration)
- [ ] Precision-recall curves (per role)
- [ ] Baseline comparison bar chart
- [ ] Ablation study plot

**Script:**
```python
python scripts/visualize.py --results results/ --output results/plots/
# Output: confusion.png, calibration.png, etc.
```

---

## Success Criteria

- [ ] All metrics computed
- [ ] Significance tests show p < 0.05
- [ ] Collider beats all baselines
- [ ] Ablation shows patterns contribute
- [ ] Plots publication-ready

---

## Quick Start (After M2.6)

1. Split dataset (1 hour)
2. Implement random baseline (2 hours)
3. Run Collider predictions (1 day)
4. Compute accuracy (1 hour)

**Blocker:** Needs ground truth (M2.6)
