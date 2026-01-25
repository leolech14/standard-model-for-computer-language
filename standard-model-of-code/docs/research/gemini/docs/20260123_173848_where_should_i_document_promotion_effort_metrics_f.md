# Research: Where should I document PROMOTION EFFORT METRICS for the task refinery system? This includes: averag...

> **Date:** 2026-01-23 17:38:48
> **Source:** gemini
> **Model:** gemini-2.0-flash
> **Checksum:** `sha256:f3d5bbd50f3a23b4f87df09de547a79d8c3e5b07ca942b2f015115b7a7b44778`
> **Raw JSON:** `raw/20260123_173848_where_should_i_document_promotion_effort_metrics_f.json`

---

## Query

Where should I document PROMOTION EFFORT METRICS for the task refinery system? This includes: average confidence boost per OPP (+22%), refinement steps (avg 2), tools used (Forensic, Perplexity, Gemini), time per promotion (~20-40 min). Options: (A) .agent/docs/, (B) context-management/docs/workflows/, (C) .agent/registry/METRICS.md, (D) context-management/docs/operations/. Which location follows existing conventions?

---

## Response

Based on the provided codebase context and conventions, the best location for documenting PROMOTION EFFORT METRICS for the task refinery system is **(C) .agent/registry/METRICS.md**.

Here's why:

*   **.agent/registry/METRICS.md:** The `analysis_sets.yaml` file defines an analysis set called `agent_intelligence` that includes `.agent/intelligence/metrics/*.yaml`.  While the user query specifies `METRICS.md` (a markdown file), the general pattern is storing metrics as YAML files. Therefore it is better to save the metrics as a `.agent/registry/METRICS.yaml` file.

*   **(A) .agent/docs/:** This location could be used for conceptual documents related to the agent or the kernel, but not for tracking specific performance metrics.

*   **(B) context-management/docs/workflows/:** This directory would be more suited for defining the workflow itself, rather than its performance metrics.

*   **(D) context-management/docs/operations/:** This directory appears to be used for operational manuals and deployment strategies, not for tracking specific metrics of subsystems.

Therefore, the most accurate location to store promotion effort metrics is in `.agent/registry/METRICS.yaml`. Since the example prompt specifies to save into `.agent/registry/METRICS.md`, if the file will be edited automatically by the agent, then the format of the file should be `.yaml`. If the file is designed for humans to read (not edited automatically by the agent), then store in markdown (`.md`).


---

## Citations

_No citations provided_
