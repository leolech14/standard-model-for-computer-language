# Roadmap 5: Publication & Dissemination

**Goal:** Publish results at top-tier venue (ICSE/OOPSLA)

**Dependencies:** All previous roadmaps complete

**Timeline:** 12-16 weeks (includes review cycle)

**Effort:** 2-3 researchers

---

## Milestones

### M5.1: Paper Writing (Week 1-4) ✓ INDEPENDENT (can start early)
**Deliverable:** `paper/draft_v1.0.pdf`

**Structure (ICSE format):**
1. **Abstract** (200 words)
2. **Introduction** (2 pages) — Motivation, claims, contributions
3. **Background** (1 page) — Standard Model overview
4. **Approach** (2 pages) — 167 atoms, 27 roles, RPBL, pipeline
5. **Evaluation** (4 pages) — RQs, dataset, metrics, results
6. **Threats to Validity** (1 page) — Internal, external, construct
7. **Related Work** (2 pages) — Code analysis tools, LLM approaches
8. **Conclusion** (0.5 pages) — Summary, future work

**Total:** 12-14 pages (ICSE limit: 14 pages + references)

**Parallel work:** Can draft intro/background while experiments run

---

### M5.2: Results Integration (Week 5) ✓ DEPENDS ON M3.7
**Deliverable:** `paper/draft_v2.0.pdf` with results

**Tasks:**
- [ ] Insert tables (metrics, baselines, ablation)
- [ ] Insert plots (confusion matrix, calibration)
- [ ] Write results narrative (RQ1-RQ4 answers)

**Example:**
```markdown
### RQ1: Completeness
Our 167-atom taxonomy achieved **100% coverage** on all 1M test elements.
No element was unclassifiable (Table 3).
```

---

### M5.3: Internal Review (Week 6) ✓ INDEPENDENT
**Deliverable:** Revised draft after feedback

**Tasks:**
- [ ] Circulate to 2-3 colleagues
- [ ] Collect feedback (clarity, claims, gaps)
- [ ] Revise based on comments

**Checklist:**
- [ ] Claims clearly stated
- [ ] Evidence sufficient
- [ ] Writing clear and concise
- [ ] Figures readable

---

### M5.4: Submission Preparation (Week 7) ✓ INDEPENDENT
**Deliverable:** Camera-ready submission

**Tasks:**
- [ ] Format to venue style (ACM SIG/IEEE)
- [ ] Check page limit (14 pages for ICSE)
- [ ] Prepare supplementary material (if allowed)
- [ ] Write artifact abstract (if artifact track)

**Artifact Abstract (1 page):**
- What the artifact contains
- How to run it
- Expected results
- DOI link

---

### M5.5: Conference Submission (Week 8) ✓ DEADLINE-DRIVEN
**Deliverable:** Submitted to ICSE 2026 or OOPSLA 2025

**Tasks:**
- [ ] Submit via conference system (HotCRP/EasyChair)
- [ ] Upload artifact to Zenodo (if required)
- [ ] Pay submission fee ($75)
- [ ] Notify co-authors

**Deadlines (estimate):**
- ICSE 2026: August 2025
- OOPSLA 2025: April 2025

---

### M5.6: Review Response (Week 12-14) ✓ DEPENDS ON REVIEWS
**Deliverable:** Rebuttal and revision

**Tasks:**
- [ ] Read reviews (typically 3-4 reviewers)
- [ ] Draft rebuttal (1-2 pages)
- [ ] Address major concerns
- [ ] Revise paper if minor revision requested

**Common reviewer concerns:**
- "Dataset too small" → Show 1M nodes
- "Baselines weak" → Add LLM comparison
- "Threats unclear" → Expand validity section

---

### M5.7: Camera-Ready Revision (Week 15-16) ✓ IF ACCEPTED
**Deliverable:** Final published version

**Tasks:**
- [ ] Incorporate reviewer feedback
- [ ] Final proofread
- [ ] Copyright form
- [ ] Upload final PDF

**Output:** Paper appears in conference proceedings

---

## Alternative: Preprint Strategy (PARALLEL)

**If submission is rejected or delayed:**

### M5.8: arXiv Preprint (Anytime) ✓ INDEPENDENT
**Tasks:**
- [ ] Upload to arXiv.org (category: cs.SE)
- [ ] Get arXiv ID (e.g., arXiv:2025.12345)
- [ ] Share on social media (Twitter, LinkedIn)

**Benefit:** Early visibility, citable before publication

---

## Success Criteria

- [ ] Paper submitted to top venue
- [ ] Artifact publicly available (DOI)
- [ ] Reviews received
- [ ] Rebuttal submitted (if needed)
- [ ] (Goal) Accepted for publication

---

## Quick Start (Can Begin Early)

1. Write abstract (1 day)
2. Draft introduction (2 days)
3. Outline evaluation section (1 day)
4. Create figure placeholders (1 hour)

**Non-blocking:** Can start writing before all experiments finish

---

## Conference Options

| Venue | Tier | Acceptance | Deadline | Audience |
|-------|------|------------|----------|----------|
| **ICSE** | A* | ~20% | Aug | Software Engineering |
| **OOPSLA** | A* | ~25% | Apr | Programming Languages |
| **FSE** | A* | ~20% | Mar | Foundations of SE |
| **ASE** | A | ~22% | May | Automated SE |
| **MSR** | A | ~30% | Jan | Mining Software Repos |

**Recommendation:** ICSE (broad SE audience) or OOPSLA (PL focus)
