# MEGAPROMPT 01: CLAIMS LEDGER & FALSIFIABILITY

## Context
You are a scientific auditor analyzing the "Standard Code" theory—a proposed universal ontology for software.
The theory makes many claims: some are definitions (unfalsifiable by design), some are empirical (testable), some are analogies (illustrative), and some are normative goals (aspirations).

## Your Task
Given the attached `STANDARD_CODE.md` document, systematically extract and categorize every claim.

## Instructions

1. **Extract Claims**: Read each section and extract every statement that asserts something about code, structure, or classification.

2. **Categorize Each Claim** as one of:
   - **Definition**: A term being defined (e.g., "A Node is L3") — unfalsifiable, evaluated for clarity and consistency
   - **Empirical Claim**: A testable assertion (e.g., "167 atoms cover all AST types") — requires evidence
   - **Analogy**: A comparison to another domain (e.g., "Functions are like atoms in physics") — evaluated for pedagogical value
   - **Normative Goal**: A desired outcome (e.g., "Every question should be answerable by one lens") — evaluated for feasibility
   - **Implementation Assumption**: A code/tooling dependency (e.g., "Tree-sitter is used for parsing") — evaluated for portability

3. **For Each Empirical Claim, Provide**:
   - (a) **Supporting Evidence**: What data/experiment would confirm this?
   - (b) **Falsification Criteria**: What observation would disprove this?
   - (c) **Confidence Interpretation**: What does "90% confidence" mean here?
   - (d) **Scope Limitations**: Under what conditions does this NOT apply?

4. **Output Format**: A structured table or JSON with columns:
   ```
   | Claim ID | Text | Section | Type | Evidence Required | Falsification | Scope |
   ```

## Expected Output
A "Claims Ledger" document that could be used as a scientific checklist for validation.

---

## Attachment Required
Attach the full `STANDARD_CODE.md` content when executing this prompt.
