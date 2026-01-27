# Research: Decision Deck Architecture Question:

I'm about to deduplicate MCP server configs across 3 files (~/...

> **Date:** 2026-01-27 05:22:56
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:1c0b26a01d34787ff07524bc82d7eae5e6b6e09ef8931475927df9a2841a88c2`
> **Raw JSON:** `raw/20260127_052256_decision_deck_architecture_question___i_m_about_to.json`

---

## Query

Decision Deck Architecture Question:

I'm about to deduplicate MCP server configs across 3 files (~/.claude/settings.json, ~/.claude.json, ~/.config/claude/mcp.json). This is a one-time cleanup: remove duplicates, remove deprecated entries, keep canonical source.

The Decision Deck has 25 cards covering:
- Analysis (Collider, Audit)
- Documentation (Write Spec)  
- Git (Commit)
- Research (Perplexity, Gemini)
- Infrastructure (Pipelines, Daemons, Health Models)
- Wildcard (catch-all for unmatched actions)

NO cards exist for:
- Config file maintenance
- Dependency cleanup
- Settings deduplication
- Environment hygiene

Question: Should the Deck have a reusable card for 'System Configuration Cleanup'? Or is this correctly handled by CARD-WLD-000 (Wildcard) because config deduplication is too context-specific to certify as a repeatable workflow?

Consider:
1. Would a 'Config Cleanup' card be used more than once?
2. Is config deduplication general enough to warrant certification?
3. Does adding too many specific cards dilute the Deck's value?
4. What's the right granularity for certified moves vs wildcard actions?

Read .agent/deck/CARD-WLD-000.yaml and .agent/deck/CARD-OPP-059.yaml for context on existing cards.

---

## Response

The Decision Deck is designed for "AI Governance" and "commit hygiene," providing "certified moves" to guide both human and AI agents and prevent improvisation. It acts as a canonical set of workflows for repeatable, well-understood operations.

Let's evaluate your questions in light of the project's architecture:

1.  **Would a 'Config Cleanup' card be used more than once?**
    While your current task of deduplicating MCP server configs is described as a "one-time cleanup" for *that specific set of files*, the broader category of "System Configuration Cleanup" is highly likely to be needed again. Codebases evolve, tools change, and configuration drift is a common form of technical debt.
    *   The `DEEP_GHOSTS_REPORT.md` already highlights potential "Config File Contradictions" and "Schema Duplication" (even if not critical in that audit), indicating that config hygiene is an ongoing concern.
    *   The project has various `.yaml` and `.json` config files (`context-management/config/`, atom definitions, schemas, `pre-commit-config.yaml`). As `BARE` evolves and new systems are integrated, more config files will appear, and older ones will become stale or redundant.
    *   **Verdict:** Yes, a general "System Configuration Cleanup" card would likely be used more than once for different configuration types or throughout the project's lifecycle.

2.  **Is config deduplication general enough to warrant certification?**
    "Config deduplication" as a *specific task* might seem too granular, but the underlying *process* of identifying redundant or deprecated configuration entries, determining a canonical source, and applying systematic cleanup is highly generalizable. It's a fundamental aspect of maintaining a clean, predictable, and robust system. Given the project's emphasis on structure ("Standard Model of Code"), defined schemas, and "truth validation" (`BARE/TruthValidator`), ensuring configuration consistency aligns perfectly with its core values.
    *   **Verdict:** The *process* of configuration cleanup and deduplication is general enough to warrant a certified workflow, even if the specific files change.

3.  **Does adding too many specific cards dilute the Deck's value?**
    Absolutely. The Decision Deck is meant to be a high-leverage guide, not an exhaustive checklist of every possible action. If every specific cleanup task (e.g., "clean up `node_modules`", "deduplicate `requirements.txt`", "clean old logs") gets its own card, the Deck would become unwieldy, making it harder for agents to find the appropriate "certified move." The goal is to provide guidance for *categories* of actions, allowing for context-specific parameters or sub-tasks within that card's workflow.
    *   **Verdict:** A card *specifically* for "MCP server config deduplication" would be too granular and dilute the Deck's value.

4.  **What's the right granularity for certified moves vs wildcard actions?**
    *   **Wildcard (`CARD-WLD-000`):** Should be reserved for truly novel, highly unique, or highly context-dependent actions that don't fit into any established, repeatable workflow. It implies a higher degree of improvisation and agent discretion, which the Decision Deck aims to minimize for common operations.
    *   **Certified Move:** Should represent a repeatable workflow that addresses a common problem or achieves a specific, valuable outcome, providing clear preconditions, steps, expected results, and rollback procedures. It abstracts the "how" into a standardized process.

    Your current task of "deduplicating MCP server configs" falls into a middle ground. It's not so unique that it *must* be a wildcard, nor is it so common and specific that it needs its own dedicated card. Instead, it suggests the need for a **higher-level, more generalized "System Configuration Cleanup" card.** This card would encapsulate the *process* of auditing, canonicalizing, and cleaning up various types of configuration files. Your specific task would then be an *instance* of executing this general card, with the MCP configs as the target scope.

**Recommendation:**

You should **create a reusable card for 'System Configuration Cleanup,' but at a higher level of abstraction than just 'config deduplication' or 'MCP server config cleanup.'**

This new card, perhaps named `CARD-SYS-0XX: System Configuration Audit & Cleanup` (or under an existing `Infrastructure` category), would define a general workflow for identifying and rectifying issues across various configuration files.

**Proposed Card Scope:**

*   **Card ID:** `CARD-SYS-0XX` (e.g., `CARD-SYS-001`)
*   **Name:** System Configuration Audit & Cleanup
*   **Category:** System Hygiene / Infrastructure
*   **Purpose:** To systematically identify, audit, and rectify inconsistencies, redundancies, deprecations, or misconfigurations within the project's various configuration files, ensuring system stability, predictability, and adherence to defined standards.
*   **Preconditions:**
    *   Specific configuration files or directories targeted for audit are identified (e.g., `mcp.json`, `context-management/config/`, `standard-model-of-code/src/patterns/`).
    *   Canonical sources or desired states for the targeted configurations are established (e.g., in related schema files or `MODEL.md`).
*   **Steps:**
    1.  **Define Scope:** Clearly specify the set of config files/areas to be audited.
    2.  **Scan for Issues:** Use appropriate tools (e.g., `grep`, `diff`, custom scripts, schema validators) to detect duplicates, deprecated entries, inconsistencies, or deviations from canonical sources.
    3.  **Analyze & Plan:** Review findings, propose a plan for cleanup (e.g., deduplication strategy, removal of deprecated entries, consolidation), and identify the canonical source(s) for each conflict.
    4.  **Implement Changes:** Apply modifications to the configuration files according to the approved plan.
    5.  **Validate:** Run relevant tests, `pre-commit` hooks, and `HSL` checks (if applicable) to ensure no regressions or new issues are introduced.
    6.  **Document:** Update any related documentation (`ARCHITECTURE_MAP.md`, `AGENTKNOWLEDGEDUMP.md`, or specific component READMEs) if canonical patterns or locations have changed.
*   **Expected Outcome:** Configuration files are clean, consistent, aligned with project standards, and free of redundancies or deprecated entries. Reduced technical debt.
*   **Rollback Procedures:** Standard Git revert for all changes made within this card's execution.

By doing this, your current task of deduplicating MCP server configs becomes a concrete *application* of this general `CARD-SYS-0XX`, making the Deck more useful without unnecessary bloat.

---

## Citations

_No citations provided_
