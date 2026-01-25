# Perplexity Research: Google Cloud Run Jobs 2025 2026:
- Maximum tasks limit per job
- Maximum task timeout (hours)
- CLOU...

> **Date:** 2026-01-24 14:49:42
> **Model:** sonar-pro
> **Query Length:** 326 chars

---

## Query

Google Cloud Run Jobs 2025 2026:
- Maximum tasks limit per job
- Maximum task timeout (hours)
- CLOUD_RUN_TASK_INDEX CLOUD_RUN_TASK_COUNT environment variables
- Memory and CPU limits
- Artifact Registry migration from gcr.io
- Pricing per vCPU-second and GiB-second
- Best practices for batch processing large number of items

---

## Response

Based on the provided search results, I can only partially address your questions about Google Cloud Run Jobs. The search results contain limited information on most of your specific queries.

## Available Information from Search Results

**Maximum task timeout duration:** Cloud Run Jobs currently has a **60-minute (1-hour) maximum execution time** per task[2][3]. The documentation states: "By default, each task runs for a maximum of 10 minutes: you can change this to a shorter time or a longer time up to 1 hour"[2].

**Current service maturity:** Cloud Run Jobs is in **Preview status**, not General Availability, which means it currently lacks SLAs and has limited support—a potential consideration for enterprise adoption[2].

## Information Gaps

The search results do not contain specific details on:

1. **Maximum number of tasks per Cloud Run Job** — Not addressed in provided sources
2. **`CLOUD_RUN_TASK_INDEX` and `CLOUD_RUN_TASK_COUNT` environment variables** — No documentation provided
3. **Configurable memory and CPU limits** — Not specified in results
4. **Migration path from `gcr.io` to Artifact Registry** — Not covered
5. **Pricing model (vCPU-second and GiB-second costs)** — Not included
6. **Best practices for batch processing large independent items** — Only general guidance available

## Related Guidance from Google Cloud Batch

The search results reference **Google Cloud Batch** (a different service), which provides parallel execution capabilities and autoscaling[5]. However, this is distinct from Cloud Run Jobs and may not align with your specific requirements.

**Recommendation:** To accurately address your architectural questions, you should consult the official Google Cloud documentation for Cloud Run Jobs, which would contain current specifications, pricing details, and best practices specific to the 2025-2026 timeframe. Given that Cloud Run Jobs is in Preview, you may also want to verify whether it has transitioned to GA status, which would affect SLA and support considerations for your pipeline.

---

## Citations

1. https://developers.google.com/google-ads/api/docs/batch-processing/best-practices
2. https://polleyg.dev/posts/batch-processing/
3. https://docs.cloud.google.com/run/quotas
4. https://discuss.google.dev/t/gcp-batch-jobs-parallelism/137545
5. https://cloud.google.com/batch

---

## Usage Stats

- Input tokens: 380
- Output tokens: 414
