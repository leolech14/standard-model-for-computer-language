# Research: We have a multi-agent coordination problem. After context compaction (session restore), two Claude C...

> **Date:** 2026-01-23 04:41:01
> **Source:** gemini
> **Model:** gemini-2.5-pro
> **Checksum:** `sha256:559a467a1c2ebe693eaa12e82673081f0d669d463787deefe1ffcea1656e4f30`
> **Raw JSON:** `raw/20260123_044101_we_have_a_multi_agent_coordination_problem__after.json`

---

## Query

We have a multi-agent coordination problem. After context compaction (session restore), two Claude Code agents both started working on the same task (TASK-103) simultaneously because neither checked the claim system (.agent/tools/claim_task.sh).

Existing infrastructure:
- .agent/tools/claim_task.sh (atomic mv-based locking)
- .agent/tools/release_task.sh 
- .agent/tools/check_stale.sh (>30 min detection)
- .agent/registry/claimed/ directory
- KERNEL.md boot protocol
- Task state machine: DISCOVERY → SCOPED → PLANNED → EXECUTING → COMPLETE

The problem: Context compaction summaries don't preserve claim state, so restored sessions don't know what was in-progress.

Questions:
1. How should we modify the boot protocol to prevent this?
2. Should the claim state be in the summary, or should agents always check on restore?
3. Generate a Perplexity query to validate this approach against industry best practices for distributed task coordination.

---

## Response

As a senior software engineer, I've analyzed the situation. This is a classic distributed systems problem: a race condition caused by relying on stale, cached state after a disconnect. The core issue is that the context summary is a snapshot, but the task claim system is a live, shared resource.

Here is a multi-layered solution to make your multi-agent system robust against this failure mode.

### Executive Summary

The root cause is a state synchronization failure. Agents are acting on stale information from a restored context. The solution is **not** to put the claim state in the summary, as that can also become stale instantly.

The correct approach is to **always treat the file system as the single source of truth for task claims** and to enforce this verification at critical points in the agent lifecycle, especially after session restore.

---

### 1. How to Modify the Boot Protocol

The `AGENT_BOOT.md` protocol and its associated `boot.sh` script must be enhanced to handle task state verification. This makes checking the claim a non-negotiable part of agent initialization.

#### Proposed Modification to `AGENT_BOOT.md`

Add a new step to the boot checklist:

```markdown
### C) Verify Task State
- [ ] If resuming a task, verify the claim lock is still valid.
- [ ] If starting a new task, ensure no other task is currently claimed.
```

#### Proposed `boot.sh` Logic Enhancement

The boot script should be modified to perform this check automatically.

```bash
#!/bin/bash

# ... existing boot steps (checking repo root, branch, etc.) ...

# --- NEW: TASK STATE VERIFICATION ---
echo "Verifying task state..."

# Assume the task ID is passed to the agent, e.g., via an env var
if [ -n "$CURRENT_TASK_ID" ]; then
    CLAIM_FILE_PATH=".agent/registry/claimed/$CURRENT_TASK_ID"
    
    echo "Agent believes it is working on task: $CURRENT_TASK_ID"

    if [ -f "$CLAIM_FILE_PATH" ]; then
        # The claim file exists. Check who owns it.
        OWNER_AGENT_ID=$(cat "$CLAIM_FILE_PATH")
        if [ "$OWNER_AGENT_ID" == "$AGENT_ID" ]; then
            echo "✅ Confirmed: This agent ($AGENT_ID) still holds the claim for task $CURRENT_TASK_ID."
            # Optionally, update a timestamp in the file
            # echo "$AGENT_ID:$(date +%s)" > "$CLAIM_FILE_PATH"
        else
            echo "❌ FATAL: Task $CURRENT_TASK_ID was claimed by another agent ($OWNER_AGENT_ID). Aborting."
            exit 1 # Critical failure, stop execution
        fi
    else
        echo "❌ FATAL: This agent was supposed to be working on $CURRENT_TASK_ID, but the claim lock is missing. The task may have been released or become stale. Aborting."
        exit 1 # Critical failure, stop execution
    fi
else
    echo "ℹ️ No current task ID set. Agent is starting fresh."
fi

# --- END OF NEW LOGIC ---

# ... continue with the rest of the boot script ...

echo "✅ Initiation complete. Agent is ready."
```

**Implementation Note:** This requires that each agent has a unique ID (`$AGENT_ID`) and knows the ID of the task it's supposed to be working on (`$CURRENT_TASK_ID`). It also assumes the claim file contains the ID of the claiming agent. Your `claim_task.sh` should be updated to do this: `echo "$AGENT_ID" > ".agent/registry/claimed/$TASK_ID"`.

---

### 2. State in Summary vs. Live Check

You should **always perform a live check**. Relying on the summary is fundamentally unsafe for resource locking.

Here is a breakdown of the trade-offs:

| Approach | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- |
| **State in Summary (Data-Based)** | - Fast (no I/O on restore)<br>- Agent has immediate knowledge | - **Fundamentally Unsafe**: The summary is stale the moment it's created.<br>- **Race Condition**: Agent A's summary says TASK-103 is free. Milliseconds later, Agent B claims it. Agent A restores and starts work, causing a conflict.<br>- **Complex Reconciliation**: Requires a complex process to handle conflicts when the summary and reality diverge. | **REJECT** |
| **Live Check (Action-Based)** | - **Always Correct**: Verifies the actual state at the moment of execution.<br>- **Atomic**: The `mv` command in `claim_task.sh` is an atomic operation, preventing two agents from succeeding simultaneously.<br>- **Simple Logic**: The agent's logic is "try to claim; if fail, stop." | - Requires a file system I/O operation on restore.<br>- Slightly slower than reading from memory. | **ACCEPT** |

**Conclusion:** The principle of a **single source of truth** is paramount. The `claimed/` directory *is* the truth. The agent's memory or context is just a cache, and caches must be invalidated or re-verified.

---

### Defense in Depth: Strengthening the Claim System

Beyond the boot protocol, we should harden the entire claim/release process.

#### Layer 1: Improve `claim_task.sh`

The script should be idempotent and provide clearer feedback. It must handle the case where a task is already claimed.

```bash
#!/bin/bash
# .agent/tools/claim_task.sh

TASK_ID=$1
AGENT_ID=$2 # The ID of the agent trying to claim the task

if [ -z "$TASK_ID" ] || [ -z "$AGENT_ID" ]; then
    echo "Usage: $0 <task_id> <agent_id>"
    exit 1
fi

TASK_FILE=".agent/registry/scoped/$TASK_ID"
CLAIM_DIR=".agent/registry/claimed"
CLAIM_FILE="$CLAIM_DIR/$TASK_ID"

if [ ! -f "$TASK_FILE" ]; then
    # Check if it's already claimed by us
    if [ -f "$CLAIM_FILE" ]; then
        OWNER_ID=$(cat "$CLAIM_FILE")
        if [ "$OWNER_ID" == "$AGENT_ID" ]; then
            echo "INFO: Task $TASK_ID already claimed by this agent ($AGENT_ID). Refreshing claim."
            # Update timestamp
            echo "$AGENT_ID:$(date +%s)" > "$CLAIM_FILE"
            exit 0 # Success
        else
             echo "ERROR: Task $TASK_ID is already claimed by another agent ($OWNER_ID)."
             exit 1 # Failure
        fi
    else
        echo "ERROR: Task $TASK_ID not found in scoped registry."
        exit 1 # Failure
    fi
fi

# Attempt to atomically move the file. This is the core locking mechanism.
if mv "$TASK_FILE" "$CLAIM_FILE"; then
    # On successful move, write owner ID and timestamp to the claim file.
    echo "$AGENT_ID:$(date +%s)" > "$CLAIM_FILE"
    echo "SUCCESS: Task $TASK_ID claimed by agent $AGENT_ID."
    exit 0 # Success
else
    # This block will likely not be hit due to the checks above, but is a good safeguard.
    echo "ERROR: Failed to claim task $TASK_ID. It might have been claimed by another agent simultaneously."
    exit 1 # Failure
fi
```

#### Layer 2: Enhance `check_stale.sh` (Dead Man's Switch)

The `check_stale.sh` script becomes more powerful if the claim file contains a timestamp.

```bash
#!/bin/bash
# .agent/tools/check_stale.sh

CLAIM_DIR=".agent/registry/claimed"
STALE_THRESHOLD_SECONDS=1800 # 30 minutes
NOW=$(date +%s)

for claim_file in "$CLAIM_DIR"/*; do
    if [ -f "$claim_file" ]; then
        CONTENT=$(cat "$claim_file")
        TIMESTAMP=$(echo "$CONTENT" | cut -d':' -f2)
        
        if [ -z "$TIMESTAMP" ]; then
            # Handle old format files without timestamps
            MOD_TIME=$(stat -f %m "$claim_file")
            TIMESTAMP=$MOD_TIME
        fi

        AGE=$((NOW - TIMESTAMP))

        if [ "$AGE" -gt "$STALE_THRESHOLD_SECONDS" ]; then
            TASK_ID=$(basename "$claim_file")
            OWNER_ID=$(echo "$CONTENT" | cut -d':' -f1)
            echo "STALE: Task $TASK_ID claimed by $OWNER_ID is stale (age: $AGE seconds). Releasing."
            
            # Move back to scoped for another agent to pick up
            mv "$claim_file" ".agent/registry/scoped/$TASK_ID"
        fi
    fi
done
```

---

### 3. Perplexity Query Generation

To validate this approach against industry best practices, here is a well-formed query for Perplexity:

```
Provide a comprehensive overview of best practices for distributed task coordination and locking in a multi-agent system where agents are stateless workers operating on a shared file system.

Context:
- Agents are shell-script-based and can be restarted, losing in-memory state (amnesiac property).
- A file-based locking mechanism is used, where claiming a task is an atomic 'mv' command.
- The system needs to be resilient to race conditions, especially after an agent restores its session and might have stale knowledge of a task it previously held.

Questions to answer:
1. What are the standard design patterns for ensuring only one agent works on a task at a time in this environment (e.g., leader election, distributed locks)? How does an atomic 'mv' fit into these patterns?
2. Compare the robustness of two approaches for state synchronization after an agent restores:
   a) Storing claim status in a context summary that is restored with the agent.
   b) Forcing the agent to always perform a live check-and-claim against the file system after restore.
3. What are the pitfalls of file-based locking (e.g., stale locks)?
4. Propose a "defense in depth" strategy, including mechanisms like heartbeats (timestamp updates) and stale lock detection (reapers/janitors), to make the system fault-tolerant.
5. Provide code examples or pseudo-code in shell script for implementing an idempotent and robust task claiming function.
```

---

## Citations

_No citations provided_
