# How I (Claude/Gemini) Would Annotate Particles

**User asked:** "If YOU have to provide the LLM processing for annotation, how would you do it?"

---

## My Annotation Process

### Input: What I Need to See

For each of the 100 samples, give me:

```
Sample #1:
- Name: get_user_by_id
- Kind: Function (FNC)
- File: src/repositories/user_repository.py
- Signature: def get_user_by_id(user_id: int) -> Optional[User]
- Docstring: "Retrieves a user from the database by ID"
- Collider's prediction: Query (confidence: 85%)

Context (if available):
- Repo: Django web app
- Layer: Infrastructure (repository pattern)
- Related code: Part of UserRepository class
```

---

## My Decision Framework

### Step 1: Quick Pattern Match (2 seconds)

**Name analysis:**
- `get_*` → Likely Query
- `save_*`, `create_*`, `update_*`, `delete_*` → Likely Command
- `*Service`, `*Manager` → Likely Service
- `*Repository`, `*DAO` → Likely Repository
- `validate_*`, `is_*`, `check_*` → Likely Validator

**Kind analysis:**
- Function with `get_` → Query
- Class ending in `Service` → Service
- Class ending in `Repository` → Repository

### Step 2: Context Check (3 seconds)

**File location:**
- `/repositories/` → Repository
- `/services/` → Service
- `/controllers/` → Controller
- `/models/` → Entity
- `/utils/` → Utility

**Signature analysis:**
- Returns data, no side effects → Query
- Modifies state (save, update) → Command
- Pure data class → Entity
- Orchestrates multiple operations → Service

### Step 3: Verify or Correct (2 seconds)

**Compare with Collider's prediction:**
- If my classification matches Collider → CONFIRM
- If different → Use my classification (explain why)

**Example decisions:**

```
Sample: get_user_by_id
My analysis:
- Name: get_* → Query pattern
- Signature: Returns Optional[User], no modification
- File: user_repository.py → Data access
- Verdict: Query ✅

Collider said: Query (85%)
My answer: Query (CONFIRM)
```

```
Sample: UserService
My analysis:
- Name: *Service → Service pattern
- File: services/user_service.py
- Contains: create_user(), update_profile(), delete_account()
- Orchestrates business logic
- Verdict: Service ✅

Collider said: Utility (45%)
My answer: Service (CORRECT to Service)
Reason: Despite low confidence, this clearly orchestrates business logic
```

---

## My Output Format

For each sample, I'd provide:

```json
{
  "sample_id": 1,
  "element_name": "get_user_by_id",
  "my_classification": "Query",
  "confidence": 95,
  "reasoning": "Retrieves data without modification, classic Query pattern",
  "matches_collider": true,
  "notes": null
}
```

**Batch format (all 100):**

```json
{
  "annotator": "Claude-3.5-Sonnet",
  "timestamp": "2025-12-23T01:58:00Z",
  "total_samples": 100,
  "annotations": [
    {"sample_id": 1, "my_classification": "Query", "confidence": 95, ...},
    {"sample_id": 2, "my_classification": "Service", "confidence": 90, ...},
    ...
  ],
  "summary": {
    "high_confidence": 85,
    "medium_confidence": 12,
    "low_confidence": 3
  }
}
```

---

## How to Use Me

### Option 1: Interactive (You paste samples, I classify)

**You:**
```
Sample #1:
Name: get_user_by_id
Kind: Function
Signature: def get_user_by_id(id: int) -> User
File: src/repositories/user_repo.py
```

**Me:**
```
Classification: Query
Confidence: 95%
Reasoning: Retrieves user by ID, no side effects. Classic query pattern.
```

### Option 2: Batch Processing (Script calls my API)

```python
# Use my API (Anthropic Claude)
import anthropic

client = anthropic.Anthropic(api_key="...")

for sample in samples:
    prompt = f"""
    Classify this code element's semantic role:
    
    Name: {sample['name']}
    Signature: {sample['signature']}
    File: {sample['file']}
    
    Role options: Query, Command, Service, Repository, Entity, ...
    
    Respond with ONLY the role name.
    """
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=10
    )
    
    role = response.content[0].text.strip()
    print(f"{sample['name']}: {role}")
```

### Option 3: Manual Review (Best Quality)

**Process:**
1. You share a Google Sheet with 100 samples
2. I go through each row
3. I fill in "LLM_Classification" column
4. You compare against Collider's prediction
5. Calculate accuracy

---

## Time Estimates

**Per sample:**
- Read: 5 seconds
- Analyze: 3 seconds  
- Classify: 2 seconds
- **Total: 10 seconds/sample**

**For 100 samples:**
- Interactive: 20 minutes (if you paste them)
- API batch: 5 minutes (automated)
- Manual spreadsheet: 25 minutes (includes typing)

---

## My Accuracy Estimate

**On these samples, I expect:**
- My accuracy: 90-95% (I'm good at pattern recognition)
- Collider's accuracy: 85-90% (pattern-based)
- Agreement: 85-88% (we'll agree most of the time)

**Where we might disagree:**
- Ambiguous cases (Service vs Utility)
- Unconventional naming (does_thing vs do_thing)
- Context-dependent (could be Query OR Repository)

---

**Bottom line: Give me the 100 samples (paste here or via API), I'll classify them in 20 minutes.**
