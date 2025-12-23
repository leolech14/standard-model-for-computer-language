# Mini-Validation Quick Start

**Goal:** Validate 87.6% accuracy claim with 500 manual annotations

**Timeline:** 2-3 weeks  
**Cost:** $0 (your time only)  
**Risk:** Low (fail fast)

---

## Week 1: Annotation

### Step 1: Generate Samples (5 minutes)

```bash
# Run sampler
python scripts/sample_for_mini_validation.py

# Output: data/mini_validation_samples.csv (500 samples)
```

**What this does:**
- Randomly samples 500 elements from your existing 33-repo analysis
- Stratifies by type (functions, classes, methods)
- Includes Collider's predictions for comparison

---

---

### Step 2: Annotation

**Choose ONE option:**

#### Option A: LLM Annotation ⭐ FASTER (30 minutes)

**Use AI to annotate automatically:**

```bash
# Using GPT-4 (best quality, costs ~$2)
export OPENAI_API_KEY="sk-..."
python scripts/annotate_with_llm.py --method openai

# Or using local Ollama (free, needs model loaded)
# First: ollama pull llama3.2
python scripts/annotate_with_llm.py --method ollama
```

**Pros:** Fast, reproducible, consistent  
**Cons:** Costs money (GPT-4) or needs setup (Ollama)

---

#### Option B: Manual Annotation (16 hours)

**Open `data/mini_validation_samples.csv` in Excel**

For each row:
1. Read name, signature, docstring
2. Classify role (Query, Command, Entity, etc.)
3. Fill `annotated_role` column

**Pros:** Free, "true" ground truth  
**Cons:** Slow, tedious

---

## Week 2: Validation

### Step 3: Compute Accuracy (2 minutes)

```bash
# Run validator
python scripts/validate_annotations.py

# Output: results/mini_validation_report.md
```

**What this does:**
- Compares your annotations vs Collider's predictions
- Computes accuracy, precision, recall, F1
- Identifies most common errors
- Gives verdict: PASS/MARGINAL/FAIL

---

### Step 4: Review Results (15 minutes)

**Open `results/mini_validation_report.md`**

**Check:**
- Overall accuracy (target: ≥85%)
- Per-role performance (which roles are hard?)
- Common errors (what patterns fail?)

---

## Week 3: Decision

### Scenario A: Accuracy ≥ 85% ✅

**Verdict:** Claims validated!

**Next steps:**
1. Start Roadmap 1 (Benchmark Dataset)
2. Use these results in paper draft:
   ```
   "We validated our approach on 500 manually annotated 
   samples, achieving 87.2% accuracy (95% CI: 84.1-90.3%)."
   ```
3. Proceed with confidence to full validation

---

### Scenario B: Accuracy 75-85% ⚠️

**Verdict:** Marginal - needs refinement

**Next steps:**
1. Analyze errors (see report)
2. Refine pattern matching rules
3. Re-sample 200 new elements
4. Re-test until ≥85%

---

### Scenario C: Accuracy < 75% ❌

**Verdict:** Significant issues

**Next steps:**
1. Deep dive into errors
2. Rethink pattern approach
3. Consider LLM fallback
4. Do NOT proceed to full benchmark yet

---

## Annotation Guidelines

### Role Definitions (Quick Reference)

| Role | Pattern | Example |
|------|---------|---------|
| **Query** | Retrieves data | `get_user()` |
| **Command** | Modifies state | `save_user()` |
| **Repository** | Data access layer | `UserRepository` |
| **Entity** | Domain model | `User` class |
| **Service** | Business logic | `UserService` |
| **Factory** | Creates objects | `create_user()` |
| **Utility** | Helper functions | `format_name()` |

**Full list:** See `docs/ATOMS_REFERENCE.md` (27 roles total)

---

## FAQ

**Q: Do I need to annotate all 500?**  
A: No, but more is better. Minimum 300 for statistical significance.

**Q: What if I disagree with Collider?**  
A: Trust your judgment! That's the point of validation.

**Q: This is taking too long!**  
A: Aim for 10 seconds/sample. If unclear, write "skip" and move on.

**Q: Can I get help?**  
A: Yes! Recruit a friend (turns 16 hours → 8 hours each)

---

## Expected Output

```markdown
# Mini-Validation Results

## Summary
- Total samples: 500
- Correct predictions: 436
- Accuracy: 87.2%

✅ PASS: Accuracy ≥ 85% - Claims validated!

Recommendation: Proceed to full benchmark (Roadmap 1)

## Per-Role Performance
| Role | Precision | Recall | F1 | Support |
|------|-----------|--------|----|------------|
| Query | 92% | 89% | 90% | 120 |
| Command | 88% | 85% | 86% | 95 |
...
```

---

**Ready to start? Run Step 1 now:**

```bash
python scripts/sample_for_mini_validation.py
```
