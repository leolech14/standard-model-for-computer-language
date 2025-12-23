# Validation Execution Plan

**Status:** READY TO EXECUTE  
**Goal:** Measure actual accuracy, validate 87.6% claim

---

## What We Have

✅ **100 samples generated** (`data/mini_validation_samples.csv`)
- Stratified random sample from 78,346 particles
- Mix of repos: Django, Pydantic, Flask, our code
- Distribution: 60% FNC, 21% AGG, 19% HDL

---

## Options to Complete Annotation

### Option 1: Use Me (Claude) - Interactive ⭐ FASTEST
**Method:** You paste samples, I classify them one by one

**Process:**
```
1. You copy 10-20 samples at a time from CSV
2. Paste here with: name, signature, file
3. I respond with role classification
4. You update CSV with my answers
5. Repeat 5-6 times (total: 30 min)
```

**Pros:** Free, immediate, interactive  
**Cons:** Manual copy-paste

---

### Option 2: API Script (If you have OpenAI key)
**Method:** Automated GPT-4 annotation

**Process:**
```bash
export OPENAI_API_KEY="sk-..."
python scripts/annotate_with_llm.py --method openai --limit 100
# 10 minutes, $0.50 cost
```

**Pros:** Fully automated  
**Cons:** Costs money, needs API key

---

### Option 3: Manual Spreadsheet
**Method:** You classify them yourself

**Process:**
```
1. Open data/mini_validation_samples.csv in Excel
2. For each row, look at name/signature
3. Fill "annotated_role" column
4. Takes ~2 hours for 100 samples
```

**Pros:** Free, your judgment  
**Cons:** Slow, tedious

---

## Recommended: Option 1 (Use Me)

**Let's start now:**

I'll classify in batches. Give me the first 10 samples in this format:

```
1. Name: get_user_by_id
   Signature: def get_user_by_id(id: int) -> User
   File: repositories/user_repo.py
   
2. Name: UserService
   Signature: class UserService(BaseService)
   File: services/user_service.py
   
... (up to 10)
```

I'll respond with classifications, you update the CSV.

---

## After Annotation

Once CSV is complete:
```bash
python scripts/validate_annotations.py
# Outputs: results/mini_validation_report.md
# Shows: Actual accuracy, per-role metrics, verdict
```

**Timeline:** 30-45 minutes total

**Ready to start?** Paste first 10 samples or choose another option.
