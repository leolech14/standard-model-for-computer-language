# Research: What is the purpose of _log_turn function?

> **Date:** 2026-01-23 13:28:37
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:a5c0e90a04d44769b835d424b2c49a9fe938140b6183b53f4a4a5ef415305272`
> **Raw JSON:** `raw/20260123_132837_what_is_the_purpose_of__log_turn_function.json`

---

## Query

What is the purpose of _log_turn function?

---

## Response

Based on the **Adaptive Context Intelligence (ACI)** documentation provided in `context-management/docs/ACI_DATASET_MANAGEMENT.md` and the configuration in `aci_config.yaml`, the `_log_turn` function serves as the **recording mechanism for the ACI Feedback Loop**.

### Purpose
Its primary purpose is to persist metadata about a single AI interaction "turn" (a query and its response) to the feedback ledger. This allows the system to "learn" from past performance and optimize future tier routing (e.g., suggesting a stronger model if retries are high).

### What It Records
According to the Feedback Loop specification, `_log_turn` captures the following metrics for each query:

*   **Context**: Timestamp, Query (truncated), Intent (e.g., `DEBUG`, `ARCHITECTURE`), Complexity, Scope.
*   **Decisions**: The **Tier** selected (Instant, RAG, Long Context, Perplexity) and the **Analysis Sets** used.
*   **Cost**: Token usage (input/output).
*   **Performance**: Success status, retry count, fallback usage, and duration (ms).
*   **Outcome**: Error details (if failed).

### Storage Mechanism
It writes these records to the YAML file defined in `aci_config.yaml`:
> **Path:** `.agent/intelligence/aci_feedback.yaml`  
> **Constraint:** It likely enforces the `max_entries: 1000` limit defined in the config.

### Strategic Goal
This function feeds the data that allows the ACI system to generate **recommendations** (e.g., "Tier 'rag' has a high retry rate for 'debug' queries; upgrade to 'long_context'").

---

## Citations

_No citations provided_
