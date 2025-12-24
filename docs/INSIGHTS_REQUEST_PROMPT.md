# Request for Insights: Standard Model of Code Benchmark Analysis

## Context

We've built a **deterministic code classification system** that analyzes source code and assigns semantic roles (Service, Repository, Factory, EventHandler, etc.) to every function and class. The system was tested against **313 top GitHub repositories** encompassing **2.6 million code nodes**.

---

## The Core Question

**How do we improve classification confidence from 66% to 80%+ across all languages?**

---

## Current Results

### What Works Well (75-85% confidence)
- **Python ML/Web projects**: Flask, Django, FastAPI, Langchain, PyTorch
- **Python libraries**: requests, scikit-learn, localstack
- **Why**: Python uses decorators (`@test`, `@api`), type hints, and strong OOP naming

### What Scores Low (55-62% confidence)
- **Go frameworks**: gin, caddy, rclone
- **Java libraries**: RxJava, guava, Spring Boot internals
- **JavaScript utilities**: moment, dayjs, axios, prettier
- **Why**: No decorators, framework-specific naming, internal module names

---

## Our Classification Approach

### Pattern-based Classification (current)
```python
# Prefix patterns
"create*" → Factory (85% confidence)
"get*" → Query (80% confidence)
"use*" → Hook (90% confidence)  # React hooks
"Handle*" → EventHandler (82% confidence)  # Go handlers

# Suffix patterns
"*Service" → Service (90% confidence)
"*Repository" → Repository (90% confidence)
"*Middleware" → Interceptor (88% confidence)
"*Provider" → Container (85% confidence)
```

### Structural Analysis (limited)
- Return type analysis: `def get_user() -> User` suggests Query
- Parameter patterns: High parameter count suggests Command
- Call graph: If A calls B and B is Repository, A might be Service

---

## Key Observations

1. **Python vs Other Languages**
   - Python: 75.9% average
   - Go: 59.3% average
   - Gap: 16.6%

2. **Application Code vs Framework Internals**
   - Flask (application): 83%
   - React internals: 60%
   - This seems correct—framework code IS different

3. **Naming Conventions Matter**
   - RxJava uses `flowable`, `observable`, `buffer` - not DDD patterns
   - Go uses `handleMain`, `ServeHTTP` - different naming idiom
   - These genuinely don't match our pattern repository

---

## Open Questions

1. **Should we create language-specific pattern sets?**
   - Go: `*Handler` → Controller, `With*` → Configuration
   - React: `use*` → Hook, `*Provider` → Container
   - Or is one universal set better?

2. **Is 66% confidence "correct" for diverse code?**
   - Maybe framework internals SHOULD score low
   - Maybe we need tiered confidence expectations by code type

3. **What signals are we missing?**
   - File path patterns: `src/services/`, `pkg/handlers/`
   - Import patterns: imports testing framework → Test
   - Comment/docstring analysis

4. **Should we use ML for pattern discovery?**
   - Train on high-confidence repos (Flask, Django)
   - Extract common patterns automatically
   - Risk: overfitting to Python idioms

5. **Is the current architecture optimal?**
   - Current: Tree-sitter → Pattern matching → Graph inference
   - Alternative: AST → Embeddings → Classifier
   - Trade-off: Determinism vs accuracy

---

## Specific Insights Requested

1. **Pattern Gaps**: What naming patterns are common in Go/JS/Java that we're missing?

2. **Structural Signals**: Beyond naming, what code structure indicates role? (e.g., return type, imports, file location)

3. **Confidence Calibration**: How should we adjust confidence based on code type/language?

4. **Framework Detection**: Should we detect "this is framework internal code" and classify differently?

5. **Ground Truth**: How can we validate our classifications are correct beyond pattern matching?

---

## Data Available

- Full benchmark results: 313 repos, 2.6M nodes
- Per-language confidence distributions
- Top/bottom 30 repos by confidence
- Pattern repository: 202 patterns
- Error logs: 38 failed repos

---

## Goals

- **Short-term**: Reach 70% average confidence
- **Medium-term**: Reach 80% for Python/TS, 70% for Go/Java
- **Long-term**: 85%+ with ground truth validation

What insights can you provide to help close the confidence gap?
