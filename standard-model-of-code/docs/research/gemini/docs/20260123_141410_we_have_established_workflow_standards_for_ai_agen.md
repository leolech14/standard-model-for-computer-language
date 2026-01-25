# Research: We have established workflow standards for AI agents:

1. At 85%+ confidence, tasks MUST have full s...

> **Date:** 2026-01-23 14:14:10
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:410e5a574669babec8a30b313637095bf9df181c6af80b9f5b87b8c868d9e8e0`
> **Raw JSON:** `raw/20260123_141410_we_have_established_workflow_standards_for_ai_agen.json`

---

## Query

We have established workflow standards for AI agents:

1. At 85%+ confidence, tasks MUST have full step decomposition (TASK-XXX-S01, S02...)
2. Every session end MUST have path forward priority matrix with confidence scores
3. 4D confidence (factual/alignment/current/onwards) must be verified with evidence
4. Never stop without recommendations

PROBLEM: These standards exist in docs (AGENT_KERNEL.md, DOD.md, CLAUDE.md) but agents don't consistently follow them.

QUESTION: How do we make these standards PERSISTENT and SEAMLESSLY INTEGRATED into the workflow? Options:
1. Pre-commit hooks that validate task files?
2. A gate in promote_opportunity.py that requires step count at 85%+?
3. A post-session validator that checks for path forward?
4. Integration with boost_confidence.py?

Recommend the best approach with implementation steps.

---

## Response

Based on the codebase context and the "Alien Architecture" philosophy (Body vs. Brain), relying on the agent's memory or willingness to read `DOD.md` is insufficient. Agents suffer from context myopia.

To make these standards persistent, you must move enforcement from **Passive Documentation** (text files) to **Active Tooling** (scripts that refuse to proceed without compliance).

I recommend a **Hybrid Tooling Approach** focused on two specific interaction points: **The Promotion Gate** (Start) and **The Exit Protocol** (End).

Here is the implementation plan.

### 1. The Strategy: "Tool-Enforced Workflow"

Instead of asking the agent to *remember* to decompose tasks or write matrices, we update the tools so the agent *cannot* proceed without doing so.

| Requirement | Implementation Point | Mechanism |
| :--- | :--- | :--- |
| **1. Step Decomposition** | `promote_opportunity.py` | **Hard Gate**: Script raises error if `confidence > 85` and `subtasks < 2`. |
| **2. Path Forward Matrix** | `finish_session.py` (New) | **Generator**: Interactive script prompts agent for rows, generates MD table. |
| **3. 4D Verification** | `boost_confidence.py` | **Validator**: Script requires file citations for every score increase. |
| **4. Recommendations** | `finish_session.py` | **Mandatory Field**: Script prompts for "Next Actions". |

---

### 2. Implementation Steps

#### Step A: Modify `promote_opportunity.py` (The Entry Gate)
*Loc: `context-management/tools/agent/promote_opportunity.py` (assumed path)*

Add logic to enforce the 85% rule physically.

```python
# Pseudo-code implementation logic
def promote_task(task_id, confidence_score):
    # Load task data
    task = load_task(task_id)
    
    # REQUIREMENT 1: Decompisition Enforcement
    if confidence_score >= 85:
        subtasks = task.get('subtasks', [])
        if not subtasks:
            raise WorkflowViolationError(
                f"⛔ BLOCKED: Task {task_id} has High Confidence ({confidence_score}%). "
                "The Standard Model requires explicit step decomposition (S01, S02...) "
                "before promotion. Please define execution steps."
            )
            
    # ... proceed with promotion
```

#### Step B: Create `finish_session.py` (The Exit Protocol)
*Loc: `context-management/tools/agent/finish_session.py`*

Don't ask the agent to write the "Path Forward" matrix. Give them a tool that generates it. This ensures standard compliance and reduces hallucination.

```python
#!/usr/bin/env python3
import sys
import json

def main():
    print("🛑 SESSION EXIT PROTOCOL INITIATED")
    print("-----------------------------------")
    
    # 1. Enforce Path Forward
    print("Generating Path Forward Matrix...")
    matrix_items = []
    while True:
        action = input("Next Action (or 'done'): ")
        if action == 'done': break
        priority = input("Priority (P0-P3): ")
        confidence = input("Confidence (0-100%): ")
        matrix_items.append({"p": priority, "a": action, "c": confidence})
    
    if not matrix_items:
        print("❌ ERROR: You cannot stop without a Path Forward.")
        sys.exit(1)

    # 2. Enforce Recommendations
    recs = input("Recommendations for next session: ")
    if len(recs) < 10:
        print("❌ ERROR: Detailed recommendations required.")
        sys.exit(1)

    # Generate the Markdown Output
    print("\n✅ SESSION WRAP-UP (Copy this to output):")
    print("\n## Path Forward")
    print("| Priority | Next Action | Confidence |")
    print("|----------|-------------|------------|")
    for i in matrix_items:
        print(f"| {i['p']} | {i['a']} | {i['c']}% |")
    
    print(f"\n### Recommendations\n{recs}")
    
    # 3. Clean Git Check
    # (Insert logic to check git status here and warn if dirty)

if __name__ == "__main__":
    main()
```

#### Step C: Update `aci_config.yaml` (The Context Trigger)
*Loc: `context-management/config/aci_config.yaml`*

Add a trigger so that when an agent attempts to wrap up, ACI injects the instruction to use the tool.

```yaml
# ... existing config ...

agent_context:
  trigger_keywords:
    # ... existing keywords ...
    - "done"
    - "finish"
    - "wrap up"
    - "complete"
    - "summary"

  levels:
    # ... existing levels ...
    
    # NEW: Enforce the exit protocol
    workflow_enforcer:
      sets: ["agent_kernel"]
      description: "Workflow compliance injection"
      static_injection: |
        🛑 STOP. Do not write a manual summary.
        
        To complete this session, you MUST run:
        `python context-management/tools/agent/finish_session.py`
        
        This tool will generate the required Path Forward Matrix and Recommendations 
        to satisfy the Definition of Done.
```

### 3. Workflow Integration

Once implemented, the workflow becomes:

1.  **Agent starts task**: Runs `promote_opportunity.py`.
    *   *Result:* Script fails if they haven't decomposed a high-confidence task. Agent is forced to decompose.
2.  **Agent works**: Reads/Writes code.
3.  **Agent tries to finish**: Says "I am done, here is the summary..."
4.  **ACI Intervenes**: Injects the prompt: "🛑 STOP. Run `finish_session.py`."
5.  **Agent runs tool**: The tool prompts for the matrix data and prints the standardized markdown.
6.  **Agent outputs tool result**: Perfect compliance is achieved programmatically.

### 4. Recommendation

**Go with Option 5 (Hybrid Tooling).**

*   **Pre-commit hooks** are too late (frustrating) and too dumb (can't validate semantic intent).
*   **Validators** are passive.
*   **Tooling (Scripts)** is active. Agents prefer using tools to writing boilerplate.

**Immediate Action:**
1.  Create `context-management/tools/agent/finish_session.py`.
2.  Update `aci_config.yaml` to scream at the agent if they try to exit without running it.

---

## Citations

_No citations provided_
