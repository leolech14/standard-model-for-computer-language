# LLM Pipeline Integration Design

**Goal:** Define LLM as a refinement/validation stage WITHIN the Collider pipeline

---

## Pipeline Architecture

### Current Pipeline (10 stages)
```
1. Classification (AST → Atoms)
2. Role Assignment (Patterns → Roles)
3. Antimatter Detection
4. Prediction
5. Insight Generation
6. Purpose Field Detection
7. Execution Flow Tracing
8. Performance Prediction
9. Summary Generation
10. Visualization
```

### NEW: LLM-Assisted Pipeline
```
1. Classification (AST → Atoms) [DETERMINISTIC]
2. Role Assignment (Patterns → Roles) [DETERMINISTIC]
3. ✨ LLM Refinement (OPTIONAL) [AI-ASSISTED]
   ├─ Reviews uncertain classifications (confidence < 50%)
   ├─ Uses repo README for context
   ├─ Validates roles make sense
   └─ Flags conflicts
4. Antimatter Detection
5. [... rest of pipeline ...]
```

---

## Stage 3: LLM Refinement (Design)

### Purpose
**Refine pattern-based classifications using AI with full repo context**

### When It Runs
- **OPTIONAL** (can be disabled for speed/cost)
- **SELECTIVE** (only reviews low-confidence particles)
- **CONTEXT-AWARE** (uses README, docstrings, file structure)

### Input
```json
{
  "particles": [
    {
      "id": "user_service_123",
      "name": "UserService",
      "predicted_role": "Service",
      "confidence": 45,  // LOW - needs review
      "file_path": "domain/user_service.py",
      "signature": "class UserService(...)",
      "docstring": "Handles user operations",
      "context": {
        "repo_name": "my-app",
        "readme_summary": "E-commerce platform",
        "file_layer": "Domain"
      }
    }
  ],
  "review_threshold": 50  // Review if confidence < 50%
}
```

### LLM Instructions (Prompt)
```
You are a code architecture assistant integrated into the Collider analysis pipeline.

ROLE: Validate and refine semantic role classifications.

CONTEXT:
- Repository: {repo_name}
- Purpose: {readme_summary}
- Current particle: {name} in {file_path}

PATTERN-BASED CLASSIFICATION:
- Predicted Role: {predicted_role}
- Confidence: {confidence}%
- Evidence: {role_evidence}

YOUR TASK:
1. Review the classification
2. Consider:
   - Repository purpose (from README)
   - File location and layer
   - Element name and signature
   - Docstring
3. Validate or suggest correction

RULES:
- If pattern classification seems correct → CONFIRM
- If clearly wrong → SUGGEST alternative from 27-role taxonomy
- If ambiguous → FLAG for human review
- Always explain reasoning (1 sentence)

27-ROLE TAXONOMY:
{role_list}

OUTPUT FORMAT (JSON):
{
  "action": "CONFIRM|SUGGEST|FLAG",
  "refined_role": "role_name",
  "confidence": 85,
  "reasoning": "UserService orchestrates domain logic, typical Service pattern"
}
```

### Output
```json
{
  "id": "user_service_123",
  "original_role": "Service",
  "original_confidence": 45,
  "llm_action": "CONFIRM",
  "refined_role": "Service",
  "refined_confidence": 85,
  "llm_reasoning": "Orchestrates business logic, matches Service archetype",
  "final_role": "Service",  // Used going forward
  "validation_method": "llm_refined"
}
```

---

## Configuration

### User Controls
```python
# In collider config or CLI
collider analyze ./repo \
  --llm-refine           # Enable LLM stage
  --llm-threshold 50     # Review if confidence < 50%
  --llm-provider ollama  # ollama|openai|anthropic
  --llm-model llama3.2
```

### Cost/Time Tradeoffs
| Mode | Particles Reviewed | Time | Cost | Accuracy |
|------|-------------------|------|------|----------|
| **No LLM** | 0 | Fast | $0 | 85-87% |
| **Low threshold** | ~10% | +2 min | <$0.50 | 88-90% |
| **Medium threshold** | ~30% | +5 min | ~$1 | 90-92% |
| **High threshold** | ~60% | +10 min | ~$2 | 92-95% |
| **All particles** | 100% | +30 min | ~$10 | 93-96% |

---

## Implementation Strategy

### Phase 1: Core LLM Stage (Week 1)
```python
# core/llm_refiner.py

class LLMRefiner:
    def refine_particles(
        self,
        particles: List[Particle],
        repo_context: RepoContext,
        threshold: int = 50
    ) -> List[RefinedParticle]:
        """
        Refine low-confidence particle classifications.
        """
        # Filter particles needing review
        uncertain = [p for p in particles if p.confidence < threshold]
        
        # For each uncertain particle
        for particle in uncertain:
            # Build context-aware prompt
            prompt = self._build_prompt(particle, repo_context)
            
            # Query LLM
            response = self.llm.query(prompt)
            
            # Parse response
            refinement = self._parse_response(response)
            
            # Apply refinement
            if refinement.action == "CONFIRM":
                particle.confidence = refinement.confidence
            elif refinement.action == "SUGGEST":
                particle.role = refinement.refined_role
                particle.confidence = refinement.confidence
            elif refinement.action == "FLAG":
                particle.needs_human_review = True
        
        return particles
```

### Phase 2: Context Extraction (Week 2)
```python
# Extract rich context
repo_context = {
    "name": extract_repo_name(),
    "readme_summary": summarize_readme(),  # LLM or heuristic
    "tech_stack": detect_stack(),  # Python, Django, etc.
    "architecture": infer_architecture(),  # Layered, microservices
}
```

### Phase 3: Integration (Week 3)
```python
# In main pipeline
def analyze_with_llm(repo_path, llm_config=None):
    # Stages 1-2: Deterministic classification
    particles = classify_particles(repo_path)
    
    # Stage 3: LLM refinement (optional)
    if llm_config:
        particles = llm_refiner.refine_particles(
            particles,
            repo_context,
            llm_config.threshold
        )
    
    # Stages 4-10: Continue pipeline
    return complete_analysis(particles)
```

---

## Documentation for Users

### When to Use LLM Refinement

**Use LLM if:**
- ✅ Accuracy is critical (research, publication)
- ✅ Willing to pay $1-2 per analysis
- ✅ Can wait 5-10 extra minutes
- ✅ Repo has unusual naming conventions

**Skip LLM if:**
- ❌ Speed matters (CI/CD pipeline)
- ❌ Budget-constrained
- ❌ Standard codebase (common patterns)
- ❌ Privacy concerns (no API calls)

---

## Validation Strategy

### Self-Validation with LLM
```bash
# Use LLM refinement as "ground truth"
collider analyze ./repo --llm-refine --llm-threshold 0 > llm_results.json

# Compare against pattern-only
collider analyze ./repo --no-llm > pattern_results.json

# Measure agreement
python scripts/compare_results.py llm_results.json pattern_results.json

# Output: "Patterns achieve 87% of LLM quality"
```

---

**This design integrates LLM as a PIPELINE COMPONENT, not external validator.**
