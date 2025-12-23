# Accuracy Benchmark Strategy

**Goal:** Measure Collider's accuracy on diverse, real-world repositories

---

## Current State

**What we have:**
- ✅ Analysis of `standard-model-of-code` itself
- ✅ 78,346 particles classified
- ✅ 500 samples ready for validation
- ✅ Annotation scripts (single LLM, multi-LLM consensus)

**Weakness:** Only tested on ITSELF (circular!)

---

## Benchmark Repo Selection Criteria

### 1. Diversity
- **Languages:** Python, JavaScript/TypeScript, Java, Rust, Go
- **Domains:** Web frameworks, data science, CLI tools, APIs
- **Sizes:** Small (1k LOC), medium (10k LOC), large (100k+ LOC)
- **Architectures:** MVC, microservices, monolith, functional

### 2. Quality
- **Well-documented:** README, good naming conventions
- **Popular:** Active development, many stars
- **Clean code:** Follows best practices
- **Open source:** Publicly accessible

### 3. Legitimacy
- **Real projects:** Not toy examples
- **Production use:** Actually deployed
- **Maintained:** Recent commits

---

## Recommended Benchmark Set (Python Focus)

### Tier 1: Web Frameworks (Architecture-heavy)
```
1. Django (https://github.com/django/django)
   - Size: ~300k LOC
   - Why: Rich MVC architecture, clear roles
   - Expected patterns: Repository, Controller, Model, Service
   
2. Flask (https://github.com/pallets/flask)
   - Size: ~20k LOC
   - Why: Minimal framework, decorator patterns
   - Expected patterns: Controller, Middleware, View
   
3. FastAPI (https://github.com/tiangolo/fastapi)
   - Size: ~30k LOC
   - Why: Modern async, type hints
   - Expected patterns: Controller, Validator, Transformer
```

### Tier 2: Data Science (Utility-heavy)
```
4. Pandas (https://github.com/pandas-dev/pandas)
   - Size: ~200k LOC
   - Why: Data manipulation, transformers
   - Expected patterns: Transformer, Query, Utility
   
5. Scikit-learn (https://github.com/scikit-learn/scikit-learn)
   - Size: ~150k LOC
   - Why: ML library, strategy patterns
   - Expected patterns: Strategy, Factory, Transformer
```

### Tier 3: CLI Tools (Command-heavy)
```
6. Click (https://github.com/pallets/click)
   - Size: ~10k LOC
   - Why: CLI framework, decorators
   - Expected patterns: Command, Decorator, Configuration
   
7. Rich (https://github.com/Textualize/rich)
   - Size: ~20k LOC
   - Why: Terminal rendering
   - Expected patterns: Presenter, View, Builder
```

### Tier 4: Infrastructure (Repository-heavy)
```
8. SQLAlchemy (https://github.com/sqlalchemy/sqlalchemy)
   - Size: ~200k LOC
   - Why: ORM, repository pattern
   - Expected patterns: Repository, Entity, Query, Command
   
9. Requests (https://github.com/psf/requests)
   - Size: ~10k LOC
   - Why: HTTP library, adapters
   - Expected patterns: Adapter, Builder, Utility
```

### Tier 5: Testing (Test-heavy)
```
10. Pytest (https://github.com/pytest-dev/pytest)
    - Size: ~40k LOC
    - Why: Testing framework
    - Expected patterns: Test, Fixture, Mock, Observer
```

---

## Multi-Language Benchmark (Optional)

### JavaScript/TypeScript
```
11. Express.js (Node - https://github.com/expressjs/express)
12. React (https://github.com/facebook/react)
```

### Java
```
13. Spring Boot (https://github.com/spring-projects/spring-boot)
14. Guava (https://github.com/google/guava)
```

### Rust
```
15. Tokio (https://github.com/tokio-rs/tokio)
```

### Go
```
16. Gin (https://github.com/gin-gonic/gin)
```

---

## Validation Workflow

### Phase 1: Quick Test (1-3 repos, 2 hours)
```bash
# Pick 1-2 small repos
repos=("flask" "requests")

for repo in "${repos[@]}"; do
  # Clone
  git clone https://github.com/org/$repo
  
  # Analyze
  collider analyze ./$repo --output output/$repo/
  
  # Sample 200 elements
  python scripts/sample_for_mini_validation.py \
    --output-dir output/$repo \
    --n 200
  
  # Annotate with consensus
  python scripts/annotate_consensus.py \
    --input data/${repo}_samples.csv \
    --output data/${repo}_annotated.csv
  
  # Validate
  python scripts/validate_annotations.py \
    --input data/${repo}_annotated.csv \
    --output results/${repo}_report.md
done

# Aggregate results
python scripts/aggregate_results.py results/*.md
```

**Output:**
```
Flask: 89.2% accuracy (178/200)
Requests: 91.5% accuracy (183/200)

Overall: 90.4% accuracy (361/400)
95% CI: [87.2%, 93.6%]
```

### Phase 2: Full Benchmark (10 repos, 1 week)
- Same workflow, scaled up
- 500 samples per repo = 5,000 total
- Multi-LLM consensus for quality
- Detailed per-repo reports

---

## Expected Results

**Pessimistic:**
- Small repos (Flask, Requests): 85-90%
- Large repos (Django, Pandas): 75-85%
- Overall: 82-87%

**Realistic:**
- Small repos: 88-92%
- Large repos: 82-88%
- Overall: 85-90%

**Optimistic:**
- Small repos: 90-95%
- Large repos: 85-90%
- Overall: 88-93%

---

## Quick Start (Do This First)

### Test 1: Flask (Small, Clean)
```bash
cd /tmp
git clone https://github.com/pallets/flask
cd flask

# Analyze
python ~/PROJECT_elements/standard-model-of-code/cli.py audit .

# Sample 100 for quick test
python ~/PROJECT_elements/standard-model-of-code/scripts/sample_for_mini_validation.py \
  --output-dir output/audit \
  --n 100

# Annotate (quick single LLM)
python ~/PROJECT_elements/standard-model-of-code/scripts/annotate_with_llm.py \
  --input data/mini_validation_samples.csv \
  --limit 100

# Measure
python ~/PROJECT_elements/standard-model-of-code/scripts/validate_annotations.py
```

**Time:** 30 minutes  
**Result:** Flask accuracy baseline

---

**Recommendation: Start with Flask (quick, clean, representative)**
