> **EPISTEMIC STANCE**: This prompt validates a MAP, not the territory. Canonical sets (167 atoms, 33 roles, 8 dimensions) are *working sets*, not claims of totality. Finding gaps is expected and valuable. Unknown is first-class. All claims are postulates with validation obligations.

---

# MEGAPROMPT 02: LENS SYSTEM VALIDATION

## Context
Standard Code defines 8 "Lenses" (perspectives) for understanding code:
1. Identity (What is it called?)
2. Ontology (What exists?)
3. Classification (What kind is it?)
4. Composition (How is it structured?)
5. Relationships (How is it connected?)
6. Transformation (What does it do?)
7. Semantics (What does it mean?)
8. Epistemology (How certain are we?)

The claim is that these 8 lenses are **complete** (answer every question) and **orthogonal** (non-overlapping).

## Your Task
Test this claim against real developer questions.

## Instructions

1. **Input**: A list of 50 real developer questions (examples below):
   - "Why is this function so slow?"
   - "What calls this method?"
   - "Is this safe to delete?"
   - "What is this variable for?"
   - "Who wrote this?"
   - "When was this last changed?"
   - "What would break if I renamed this?"

2. **For Each Question**:
   - Map it to a **primary lens** (the main perspective needed)
   - Map it to **secondary lenses** (if applicable)
   - Rate the fit: **Clean** (perfect match), **Stretched** (fits with interpretation), **Gap** (doesn't fit)

3. **Identify Gaps**:
   - Questions that don't fit any lens
   - Questions that require merging lenses in non-obvious ways

4. **Propose Fixes** (if gaps exist):
   - (a) Add a new lens (define it precisely)
   - (b) Redefine an existing lens to absorb the gap
   - (c) Create a "lens composition rule" for multi-perspective questions

## Expected Output
- Mapping table: Question → Lens(es) → Fit Rating
- Gap analysis with proposed fixes
- Verdict: Are 8 lenses sufficient? If not, what's the minimal extension?
