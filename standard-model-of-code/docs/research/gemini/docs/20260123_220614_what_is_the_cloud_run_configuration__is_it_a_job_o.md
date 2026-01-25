# Research: What is the Cloud Run configuration? Is it a Job or Service? What are the known constraints?

> **Date:** 2026-01-23 22:06:14
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:c87ad8f037d59510f5e58c81045e3107e11c4e403f26488571be7ab65e6cfb65`
> **Raw JSON:** `raw/20260123_220614_what_is_the_cloud_run_configuration__is_it_a_job_o.json`

---

## Query

What is the Cloud Run configuration? Is it a Job or Service? What are the known constraints?

---

## Response

Based on the provided codebase context, the Cloud Run configuration is for a **Job**, not a Service.

Here's the relevant information and known constraints:

*   **`HOLOGRAPHIC_DEPLOYMENT_MANUAL.md`**: This document describes the deployment procedure for the Holographic-Socratic Layer.
*   **Architecture:** States the system runs as a "Google Cloud Run Job (Batch processing), not a service."
*   **One-Click Deployment**: Details the `cloud-run-deploy.sh` script, confirming Cloud Run Job deployment.
*   **The Triggers:** Describes using Cloud Scheduler to trigger the Cloud Run Job every 6 hours, clearly establishing it as a scheduled batch process.
*   **Known Constraints**:
    *   The system needs a dedicated Service Account (`socratic-trigger-sa`) with the `roles/run.invoker` role for Cloud Scheduler to trigger the Job.
    *   Image building and job definition updates are handled by `./cloud-run-deploy.sh`, but the script might have sticky `apt-key` GPG issues, which the updated `Dockerfile` is supposed to fix.
    *   `PERMISSION_DENIED` errors on Cloud Build might occur, requiring granting the Cloud Build Service Account (`[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`) the `roles/run.admin` and `roles/iam.serviceAccountUser` roles.
    *   The "Quartet Watchdog" schedule runs every 6 hours which may be a constraint on the frequency of updates.

Therefore, based on the documentation, the system uses a Cloud Run Job triggered by Cloud Scheduler.  There are configuration constraints related to service accounts and potential GPG key issues during image builds.


---

## Citations

_No citations provided_
