# MEGAPROMPT 11: BENCHMARK DATASET DESIGN

## Context
To validate Standard Code, we need a high-quality benchmark dataset.

## Your Task
Design the "Validation Pack."

## Instructions

1. **Repository Selection Criteria**:
   - Size: Small (1K LOC), Medium (10K LOC), Large (100K+ LOC)
   - Architecture: Monolith, Microservices, DDD, Clean Architecture
   - Languages: Python, TypeScript, Java (minimum)
   - Popularity: At least 1K stars (quality signal)
   - Diversity: Different domains (web, CLI, data, infrastructure)

2. **Sampling Strategy**:
   - Per repo: 50 functions across all layers
   - Stratified: Equal representation of roles (as much as possible)
   - Edge cases: Intentionally include ambiguous code

3. **Annotation**:
   - Human annotators assign: Atom, Role, Layer, and one Semantic Edge
   - Confidence rating from annotator (self-assessed certainty)
   - Disagreement resolution protocol

4. **Gold Set Structure**:
   ```json
   {
     "entity_id": "repo:file:function_name",
     "atom": "LOG.FNC.M",
     "role": "Repository",
     "layer": "Infrastructure",
     "confidence": 0.95,
     "annotator_notes": "..."
   }
   ```

5. **Regression Suite**:
   - When taxonomy changes, re-run on gold set
   - Track accuracy over versions
   - Alert on regression

## Expected Output
- Repo selection list (10+ repos)
- Sampling protocol
- Annotation guidelines
- Gold set schema
- Regression protocol
