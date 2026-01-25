# Research: We have multiple agents working on this codebase simultaneously. What coordination protocol should w...

> **Date:** 2026-01-24 23:36:39
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:f33572824e3327e26b39a1433cc949e94a1bbbb68fb2d44d239cc467c4a674b8`
> **Raw JSON:** `raw/20260124_233639_we_have_multiple_agents_working_on_this_codebase_s.json`

---

## Query

We have multiple agents working on this codebase simultaneously. What coordination protocol should we follow for Phase 2 dead code cleanup? Current situation: research_engine.py deletion was attempted but files are being modified by other agents. What is the safest approach?

---

## Response

Based on the `PROJECT_elements` architecture and the `AGENT_KERNEL.md` directives, here is the coordination protocol for **Phase 2 Dead Code Cleanup** in a multi-agent environment.

### 🛑 CRITICAL WARNING regarding `research_engine.py`

**DO NOT DELETE `research_engine.py` YET.**

According to **`context-management/docs/RESEARCH_SCHEMAS.md`**, this file is the active engine for the Research Schema system:
> **Location:** `context-management/config/research_schemas.yaml`
> **Engine:** `context-management/tools/ai/aci/research_engine.py`

If you are deleting it, you must first verify that `analyze.py` no longer imports it. Deleting it while other agents are running `analyze.py` research commands will cause immediate crashes.

---

### The Protocol: "Atomic Claim & Isolation"

To handle high-concurrency cleanup without stepping on other agents, use the **Task Registry + Branch Isolation** method.

#### 1. The Claim (Semantic Lock)
Before touching a single file, you must semantically lock the intent in the registry.

1.  **Check Active Tasks**: Read `.agent/registry/INDEX.md` or list active tasks.
2.  **Claim the Cleanup**: Run the claim tool to signal intent.
    ```bash
    # If a task exists (e.g., TASK-125), claim it
    .agent/tools/claim_task.sh TASK-125 agent-cleanup-01
    ```
    *If no task exists, create `TASK-CLEANUP-PHASE2.yaml` in `.agent/registry/active/`.*

#### 2. The Isolation (Git Branching)
Do **NOT** perform destructive cleanup directly on `main` while other agents are active.

1.  **Create a Branch**:
    ```bash
    git checkout -b chore/phase2-dead-code-cleanup
    ```
2.  **Why**: This isolates your deletions. If another agent modifies `research_engine.py` on `main`, you will face a merge conflict later (which is safe) rather than a runtime crash now (which is fatal).

#### 3. The Verification (The Forensic Check)
Use the "Surgeon" mode to prove the code is dead before deletion.

```bash
# 1. Search for references (excluding the file itself)
grep -r "research_engine" . --exclude="research_engine.py" --exclude-dir=".git"

# 2. Check imports in the ACI module
grep "research_engine" context-management/tools/ai/aci/__init__.py
```
*If these return hits, the code is ALIVE. Do not delete.*

#### 4. The Execution (Atomic Deletion)
If verification passes (0 hits or only legacy docs):

1.  **Delete**: `rm context-management/tools/ai/aci/research_engine.py`
2.  **Test Immediately**:
    ```bash
    # Run the brain tests to ensure no import errors
    cd standard-model-of-code
    pytest ../context-management/tests/ -q  # Or equivalent path if tests exist
    # OR run the tool to check for import crashes
    python ../context-management/tools/ai/analyze.py --help
    ```
3.  **Commit Immediately**:
    ```bash
    git add .
    git commit -m "chore: delete dead code research_engine.py (verified unused)"
    ```

#### 5. The Merge (Resolution)
Switch back to main and merge.

```bash
git checkout main
git pull origin main  # Get changes from other agents
git merge chore/phase2-dead-code-cleanup
```
*If a conflict occurs (because another agent modified the file you just deleted), **keep the deletion** only if you are 100% sure their changes were to a dead file. Otherwise, abort and investigate.*

### Summary Checklist for Agent

1.  [ ] **Claim** task in `.agent/registry`.
2.  [ ] **Branch** to `chore/cleanup`.
3.  [ ] **Verify** usage via `grep` (Found references in `RESEARCH_SCHEMAS.md`? **STOP**).
4.  [ ] **Delete** & **Run** `analyze.py --help` to verify runtime integrity.
5.  [ ] **Commit** & **Merge**.

---

## Citations

_No citations provided_
