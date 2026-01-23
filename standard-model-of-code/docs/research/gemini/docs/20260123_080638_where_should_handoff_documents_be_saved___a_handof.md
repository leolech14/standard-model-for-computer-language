# Research: WHERE SHOULD HANDOFF DOCUMENTS BE SAVED?

A handoff is knowledge transfer from one agent session to ...

> **Date:** 2026-01-23 08:06:38
> **Source:** gemini
> **Model:** gemini-2.5-pro
> **Checksum:** `sha256:7700902b8dbd561ceacfb5817668369d5f2d00ba7ef95dd118f8109498b220ef`
> **Raw JSON:** `raw/20260123_080638_where_should_handoff_documents_be_saved___a_handof.json`

---

## Query

WHERE SHOULD HANDOFF DOCUMENTS BE SAVED?

A handoff is knowledge transfer from one agent session to another. It includes:
- Current state of work
- Decisions made and rationale
- Next steps
- Research sources
- How to continue

Analyze the existing .agent/ structure and propose:
1. WHERE should handoffs live? (new directory? existing location?)
2. WHAT format? (YAML? Markdown? Both?)
3. HOW should they be named? (by date? by task? by agent?)
4. HOW do they relate to RUN records in .agent/runs/?

Consider the existing patterns:
- runs/ has session logs
- specs/ has design documents
- registry/ has tasks
- intelligence/ has truths

Propose a canonical location that fits the architecture.

---

## Response

As a senior software engineer, I have analyzed the provided codebase context. Here is my analysis and recommendation regarding handoff documents.

The existing architecture already has a clear and robust pattern for managing handoffs. Creating a new, separate location for "handoff documents" would be counter-productive and violate the established principles of the system.

**The handoff information is an integral part of the RUN record and should be saved within the `.agent/runs/RUN-*.yaml` file itself.**

Here is a detailed breakdown addressing your specific questions:

---

### 1. WHERE should handoffs live?

Handoffs live inside the existing `runs/` directory, specifically within the YAML file corresponding to the agent's session.

**Rationale:**

*   **Task/Run Separation:** The `KERNEL.md` document clearly defines a `RUN` as "One agent's attempt to advance a task". A handoff is the concluding state of that attempt. Therefore, it belongs within the `RUN` record to maintain a complete, atomic log of that session.
*   **Single Source of Truth:** The `KERNEL.md` states "Never skip the RUN record - Even quick fixes get documented." Placing handoff data inside the RUN record ensures that everything related to a single agent session (the log of what was done and the instructions for what to do next) is in one place. Creating a separate handoff file would introduce a second source of truth that could become desynchronized.
*   **Explicit Instructions:** The "Agent Responsibilities" section in `KERNEL.md` is unambiguous. Under "Ending a Session," it explicitly directs the agent to:
    > 1. Update RUN with:
    >    - `handoff.summary`: What was accomplished
    >    - `handoff.next_steps`: What the next agent should do
    >    - `handoff.artifacts`: Files created/modified

This confirms that the `handoff` is a structured data block *inside* the RUN record.

### 2. WHAT format?

The format is **YAML**, consistent with all other RUN records.

**Rationale:**

*   **Machine Readability:** The system is built on a "Concepts / Objects Duality" where objects are instances and records, often in YAML format (e.g., `TASK-001.yaml`, `RUN-*.yaml`). This structured format allows other tools and agents to parse the handoff information reliably.
*   **Schema Enforcement:** `manifest.yaml` points to a schema for runs: `.agent/schema/run.schema.yaml`. This implies the RUN record, including its `handoff` section, has a defined, machine-enforceable structure.
*   **Readability:** YAML fields can contain multi-line strings with Markdown for human-readable summaries and next steps, offering the best of both worlds. For example:
    ```yaml
    # In runs/RUN-20260124-103000-claude.yaml
    handoff:
      summary: |
        - Implemented the basic structure for the Discovery Inbox.
        - Created the `.agent/registry/inbox/` directory.
        - Wrote a draft `opportunity.schema.yaml`.
      next_steps: |
        1. Finalize the `opportunity.schema.yaml` by adding validation rules.
        2. Implement the `promote_opportunity.sh` script.
        3. Test the full promotion workflow.
      artifacts:
        - .agent/registry/inbox/.gitkeep
        - .agent/schema/opportunity.schema.yaml
    ```

### 3. HOW should they be named?

They are not named separately. They are part of a RUN record, which is named according to the established convention: `RUN-{timestamp}-{agent}.yaml`.

**Rationale:**

*   **Traceability:** The RUN file's name already provides critical metadata: *when* the session ended and *which agent* performed the work. This automatically links the handoff to its context.
*   **Consistency:** The `manifest.yaml` specifies a `run_id_pattern`: `^RUN-[0-9]{8}-[0-9]{6}-[a-z]+$`. Adhering to this prevents architectural drift and ensures all session records are discoverable by system tools.

### 4. HOW do they relate to RUN records?

The handoff is not merely "related" to a RUN record; **it is a dedicated section within the RUN record.** It represents the final state and forward-looking guidance of that specific run.

**The Workflow:**

1.  An agent claims a `TASK`.
2.  The agent creates a new `RUN-*.yaml` file in `.agent/runs/`.
3.  The agent logs its work in the `progress.step_log` section of the `RUN` file.
4.  Upon finishing its session, the agent populates the `handoff` section within that same `RUN-*.yaml` file.
5.  The agent sets the `status` of the `RUN` to `HANDOFF_READY`.
6.  The next agent assigned to the `TASK` can easily find the most recent `RUN` record associated with that task, read its `handoff` section, and resume work without ambiguity.

### Conclusion

The architecture is designed for the handoff to be an inseparable part of the session log (`RUN` record). This approach provides atomicity, traceability, and consistency, leveraging the existing structure without adding unnecessary complexity. Any attempt to create separate handoff documents would be a deviation from the core principles outlined in `KERNEL.md`.

---

## Citations

_No citations provided_
