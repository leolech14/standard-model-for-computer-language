> **EPISTEMIC STANCE**: This prompt validates a MAP, not the territory. Canonical sets (167 atoms, 33 roles, 8 dimensions) are *working sets*, not claims of totality. Finding gaps is expected and valuable. Unknown is first-class. All claims are postulates with validation obligations.

---

# MEGAPROMPT 12: SEMANTIC SIMILARITY ON 8D MANIFOLD

## Context
If every code entity is a point in 8D space, we can compute "distances" between entities.
This enables search, clustering, and impact analysis.

## Your Task
Design similarity metrics for the 8D manifold.

## Instructions

1. **Distance Metrics**:
   - **Hamming Distance**: Count of differing dimensions
   - **Weighted Hamming**: Different weights per dimension
   - **Embedding Distance**: Learn embeddings, use cosine similarity
   - **Graph Distance**: Shortest path in the call/dependency graph

2. **Weighting Scheme**:
   - Which dimensions matter more for similarity?
   - Task-dependent weights (search vs. refactor impact)

3. **Embedding Strategies**:
   - One-hot encode each dimension, concatenate → 8D vector
   - Train an autoencoder on code → learned embedding
   - Use pre-trained code embeddings (CodeBERT, etc.)

4. **Validation**:
   - "Nearest neighbor" test: Do developers agree similar entities are similar?
   - Task: "Given function X, find most similar functions"
   - Metric: Developer satisfaction score (1-5)

5. **Use Cases**:
   - **Search**: "Find all Repositories that are Stateless and Pure"
   - **Clustering**: Automatically group similar functions
   - **Impact Analysis**: "If I change X, what else is similar and might need change?"

## Expected Output
- Distance metric definitions
- Weighting scheme proposal
- Embedding architecture
- Validation protocol
- Use case examples
