# MEGAPROMPT 06: DETECTION SIGNALS & EVIDENCE MODEL

## Context
Classification in Standard Code is based on multiple signals:
- Name patterns (prefix/suffix)
- File path patterns
- Decorators/annotations
- Call graph position
- Import dependencies
- Field analysis (stateful/stateless)
- Scope analysis (lifetime)
- LLM inference (fallback)

## Your Task
Create a formal evidence model for classification.

## Instructions

1. **For Each Dimension and Role**, list all detection features:
   ```
   Dimension/Role → [Feature1: weight, Feature2: weight, ...]
   ```

2. **Define an Evidence Record Schema**:
   ```json
   {
     "entity_id": "...",
     "dimension": "ROLE",
     "candidate_value": "Repository",
     "evidence": [
       {"feature": "suffix_match", "value": "Repository", "strength": 0.95},
       {"feature": "imports_db_module", "strength": 0.7},
       {"feature": "call_graph_position", "value": "leaf", "strength": 0.3}
     ],
     "counter_evidence": [
       {"feature": "no_persistence_calls", "strength": -0.5}
     ],
     "final_confidence": 0.78,
     "confidence_update_rule": "weighted_sum_with_counter"
   }
   ```

3. **Confidence Update Rules**:
   - Simple weighted sum
   - Bayesian update
   - Rule-based overrides (e.g., decorator always wins)

4. **Provenance Tracking**:
   - Every classification must trace back to evidence
   - Support for "explain this classification" queries

## Expected Output
- Feature catalog (all signals with weights)
- Evidence record schema
- Confidence computation algorithm
- Provenance query examples
