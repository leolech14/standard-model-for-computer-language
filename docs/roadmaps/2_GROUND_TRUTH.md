# Roadmap 2: Ground Truth Annotation

**Goal:** Create 2,000 manually annotated code elements as ground truth

**Dependencies:** Roadmap 1 (M1.4: Downloaded repos)

**Timeline:** 4-6 weeks

**Effort:** 3 annotators, part-time (~60 hours each)

---

## Milestones

### M2.1: Sampling Strategy (Week 1) ✓ INDEPENDENT
**Deliverable:** `data/samples_to_annotate.csv`

**Tasks:**
- [ ] Random stratified sample from benchmark (2,000 elements)
- [ ] Ensure coverage: classes, functions, methods
- [ ] Balance by language/domain

**Stratification:**
```
Python: 800 samples (40%)
JavaScript: 500 samples (25%)
TypeScript: 400 samples (20%)
Others: 300 samples (15%)
```

**Script:**
```python
python scripts/sample_for_annotation.py --n 2000 --stratify language
# Output: samples_to_annotate.csv (id, file, name, snippet)
```

---

### M2.2: Annotation Guidelines (Week 1-2) ✓ INDEPENDENT
**Deliverable:** `docs/annotation/guidelines.md`

**Tasks:**
- [ ] Define clear rules for each dimension:
  - Atom: "What syntactic type?" (167 options)
  - Role: "What semantic purpose?" (27 options)
  - RPBL: "Rate 1-10 on 4 scales"
- [ ] Provide examples (10 fully annotated cases)
- [ ] Edge case resolution (e.g., ambiguous names)

**Example:**
```markdown
### Example 1: Repository Pattern

```python
def get_user_by_id(user_id: int):
    return db.query(User).filter(id=user_id).first()
```

**Annotations:**
- Atom: `LOG.FNC.M` (Function)
- Role: `Query` (retrieves without modifying)
- RPBL: R=8, P=7, B=8, L=3
```

---

### M2.3: Pilot Annotation (Week 2) ✓ INDEPENDENT
**Deliverable:** 100 pilot annotations + inter-rater reliability

**Tasks:**
- [ ] 3 annotators independently annotate same 100 samples
- [ ] Compute Cohen's κ (inter-rater agreement)
- [ ] If κ < 0.7: Revise guidelines, retry

**Target:** κ > 0.8 (strong agreement)

**Script:**
```python
python scripts/compute_kappa.py \
  --annotator1 pilot_a1.csv \
  --annotator2 pilot_a2.csv \
  --annotator3 pilot_a3.csv
# Output: kappa_report.txt
```

---

### M2.4: Full Annotation (Week 3-5) ✓ INDEPENDENT (after pilot)
**Deliverable:** `data/ground_truth.csv` (2,000 annotations)

**Tasks:**
- [ ] Distribute 2,000 samples across 3 annotators (~667 each)
- [ ] Each annotator works independently
- [ ] Track progress (shared spreadsheet)

**Timeline:** 
- 60 hours/annotator ÷ 10 hours/week = 6 weeks
- Can parallelize with 3 people → 2-3 weeks

---

### M2.5: Conflict Resolution (Week 6) ✓ INDEPENDENT (after M2.4)
**Deliverable:** Consensus labels for all 2,000 samples

**Tasks:**
- [ ] For each sample, check if all 3 agree
- [ ] If disagreement: Discussion + majority vote
- [ ] Document ambiguous cases

**Expected:**
- 80% full agreement (κ > 0.8)
- 15% resolved via discussion
- 5% flagged as inherently ambiguous

---

### M2.6: Quality Audit (Week 6) ✓ INDEPENDENT
**Deliverable:** `data/ground_truth_validated.csv`

**Tasks:**
- [ ] Spot-check 10% of annotations (200 samples)
- [ ] Senior researcher reviews for consistency
- [ ] Fix any obvious errors

**Output:** Final validated ground truth

---

## Success Criteria

- [ ] 2,000 samples annotated
- [ ] Inter-rater reliability κ > 0.8
- [ ] <5% unresolved conflicts
- [ ] Guidelines documented
- [ ] Quality audit passed

---

## Quick Start (After M1.4)

1. Run sampling script (1 hour)
2. Write annotation guidelines (3 days)
3. Recruit 3 annotators (1 week)
4. Pilot annotation (1 week)

**Blocker:** Needs benchmark repos downloaded (M1.4)
