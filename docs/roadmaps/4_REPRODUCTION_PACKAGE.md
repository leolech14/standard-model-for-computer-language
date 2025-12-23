# Roadmap 4: Reproduction Package

**Goal:** Create a complete, runnable artifact for independent verification

**Dependencies:** Roadmap 3 (M3.7: All analysis complete)

**Timeline:** 2-3 weeks

**Effort:** 1 engineer, full-time

---

## Milestones

### M4.1: Package Structure (Week 1) ✓ INDEPENDENT
**Deliverable:** `reproduction/` directory scaffold

**Tasks:**
- [ ] Create directory structure
- [ ] Add placeholder READMEs
- [ ] Initialize Git repo (separate from main project)

**Structure:**
```
standard-model-reproduction/
├── README.md                 # Main instructions
├── data/
│   ├── repos.csv            # 100-repo list
│   ├── ground_truth.csv     # 2,000 annotations
│   ├── train.csv            # 1,600 samples
│   └── test.csv             # 400 samples
├── scripts/
│   ├── 1_download.sh        # Clone repos
│   ├── 2_analyze.py         # Run Collider
│   ├── 3_evaluate.py        # Compute metrics
│   └── 4_visualize.py       # Generate plots
├── results/
│   └── expected/            # Expected outputs (for validation)
├── requirements.txt
└── LICENSE
```

---

### M4.2: Data Packaging (Week 1) ✓ INDEPENDENT
**Deliverable:** `data/` populated

**Tasks:**
- [ ] Copy datasets from main project
- [ ] Anonymize if needed (remove proprietary info)
- [ ] Compress large files (`.csv.gz`)

**Output:** All data ready for distribution

---

### M4.3: Script Consolidation (Week 1-2) ✓ INDEPENDENT
**Deliverable:** `scripts/` with 4 runnable scripts

**Tasks:**
- [ ] Extract scripts from main project
- [ ] Simplify (remove dev dependencies)
- [ ] Add error handling and logging
- [ ] Document parameters

**Example:**
```bash
#!/bin/bash
# 1_download.sh - Clone all benchmark repos

set -e  # Exit on error

echo "Downloading 100 benchmark repos..."
while IFS=, read -r repo_url clone_path; do
  git clone "$repo_url" "repos/$clone_path"
done < data/repos.csv

echo "Download complete: $(ls repos/ | wc -l) repos"
```

---

### M4.4: README Documentation (Week 2) ✓ INDEPENDENT
**Deliverable:** Comprehensive `README.md`

**Sections:**
1. **Overview**: What this package contains
2. **Requirements**: Python 3.10+, Collider installed
3. **Quick Start**: 4 commands to reproduce
4. **Expected Output**: What you should see
5. **Troubleshooting**: Common errors
6. **Citation**: How to cite

**Example:**
```markdown
## Quick Start

```bash
# Step 1: Download repos (30 min)
./scripts/1_download.sh

# Step 2: Analyze with Collider (2 hours)
python scripts/2_analyze.py

# Step 3: Evaluate (5 min)
python scripts/3_evaluate.py

# Step 4: Visualize (2 min)
python scripts/4_visualize.py
```

**Expected:** `results/metrics.csv` shows accuracy = 87.6% ± 0.2%
```

---

### M4.5: Validation Test (Week 2) ✓ INDEPENDENT
**Deliverable:** Proof that package works on fresh machine

**Tasks:**
- [ ] Spin up clean Docker container
- [ ] Follow README instructions
- [ ] Verify output matches expected

**Script:**
```bash
docker run -it python:3.10
git clone <repo>
cd standard-model-reproduction
./scripts/1_download.sh
# ... continue steps
diff results/metrics.csv results/expected/metrics.csv
# Should be identical (or within tolerance)
```

---

### M4.6: Publication (Week 3) ✓ INDEPENDENT
**Deliverable:** Public Zenodo archive + DOI

**Tasks:**
- [ ] Create release tag (v1.0)
- [ ] Upload to Zenodo
- [ ] Get DOI
- [ ] Update paper with DOI

**Output:**
```
DOI: 10.5281/zenodo.YYYYYYY
Artifact: Standard Model Reproduction Package v1.0
```

---

### M4.7: ICSE/OOPSLA Artifact Badge (Optional, Week 3) ✓ INDEPENDENT
**Deliverable:** "Artifact Available" badge

**Tasks:**
- [ ] Submit to artifact evaluation committee
- [ ] Provide DOI and test instructions
- [ ] Respond to reviewer feedback
- [ ] Obtain "Available" or "Functional" badge

**Criteria (ACM):**
- Available: Public DOI ✓
- Functional: Runs and produces claimed results ✓
- Reusable: Well-documented, extensible ✓

---

## Success Criteria

- [ ] Package runs on fresh machine
- [ ] Output matches expected (±2%)
- [ ] Public DOI available
- [ ] README complete and clear
- [ ] (Optional) Artifact badge obtained

---

## Quick Start (After M3.7)

1. Create directory structure (1 hour)
2. Copy data files (2 hours)
3. Extract and test scripts (1 day)
4. Write README (1 day)

**Blocker:** Needs all analysis complete (M3.7)
