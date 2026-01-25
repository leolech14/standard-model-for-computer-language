# Research: RunPod API 2025 2026:
1. How to create a pod programmatically via API
2. How to run commands on a po...

> **Date:** 2026-01-24 15:26:45
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:32cb2bb6023b47c1f6d78e24387d17f0cac1a2ae11e4dbadecacf5ee9b44bf10`
> **Raw JSON:** `raw/20260124_152645_runpod_api_2025_2026__1__how_to_create_a_pod_progr.json`

---

## Query

RunPod API 2025 2026:
1. How to create a pod programmatically via API
2. How to run commands on a pod via API (not SSH)
3. How to get pod output/logs
4. Python SDK or REST API endpoints
5. How to stop/terminate pod via API
6. Pricing for API usage vs UI

I want to build a fully automated system where an AI agent can spin up a RunPod, run a batch job, collect results, and terminate - all via API without human intervention except for billing.

---

## Response

## Python SDK and REST API Overview
RunPod provides a **Python SDK** (`runpod-python` library) that wraps the REST API for managing pods, with methods like `create_pod`, `get_pods`, `stop_pod`, `terminate_pod`, and more[1][2]. The REST API base is `https://rest.runpod.io/v1/`; fetch the full OpenAPI schema via `GET /openapi.json` (with `Authorization: Bearer <API_KEY>`) for all endpoints, schemas, and examples[1]. Install the SDK via `pip install runpod` and set `runpod.api_key = "your_api_key"`[2].

## 1. Create a Pod Programmatically
Use the Python SDK:
```
import runpod
runpod.api_key = "your_runpod_api_key"
pod = runpod.create_pod(name="test", image_name="runpod/stack", instance_type="NVIDIA GeForce RTX 3070")
# Or for CPU: runpod.create_pod("test", "runpod/stack", instance_id="cpu3c-2-4")
```
This returns a pod object with `pod.id`. REST equivalent: `POST /pod` with JSON payload for name, image, instance type, etc. (see OpenAPI schema)[1][2].

## 2. Run Commands on a Pod (No SSH)
RunPod pods support SSH access programmatically, but direct command execution without SSH isn't detailed in core docs—instead, use **container entrypoint/Docker commands** at creation or **exec via pod's API server** if your image exposes one[1][2][4]. For batch jobs, prefer **Serverless endpoints** (deploy containerized jobs via `runpod.Endpoint("ID").run_sync(input_data)`), which handle execution without pods[2]. For pods, start with `resume_pod(pod.id)` then SSH or expose ports for API-based commands[2].

## 3. Get Pod Output/Logs
Use `runpod.get_pod(pod.id)` to fetch pod details, including status and logs if available via the pod object[2]. REST: `GET /pod/{podId}` returns JSON with logs/output fields (full schema in `/openapi.json`)[1]. For serverless jobs: `run_request.output()` or `status()` blocks until complete[2].

## 4. Python SDK vs REST Endpoints
- **Python SDK** (preferred for automation): Covers pods (`get_pods()`, `create_pod()`, etc.) and serverless (`Endpoint.run_sync()`). Supports concurrent use with per-endpoint keys[2].
- **REST API**: Full control via standard HTTP (e.g., `POST /pod`, `GET /pods`, `PATCH /pod/{id}/stop`). Authenticate with `Authorization: Bearer <key>`; all endpoints in `/openapi.json`[1][6].

## 5. Stop/Terminate Pod
```
runpod.stop_pod(pod.id)    # Stops (pause billing)
runpod.resume_pod(pod.id)  # Resumes
runpod.terminate_pod(pod.id)  # Deletes permanently
```
REST: `PATCH /pod/{podId}` with `{"action": "stop"}` or `{"action": "terminate"}`[1][2].

## 6. Pricing: API vs UI
No difference—pricing is identical for API and UI usage, based on pod runtime (GPU/CPU hours) and storage; API just enables programmatic control without dashboard[1][4]. Monitor via billing endpoints (`/billing` resources) or `runpod.get_pods()` for usage metrics[1].

## Fully Automated AI Agent Workflow
1. **Spin up**: `pod = runpod.create_pod(name="batch-job", image_name="your-docker-image", instance_type="RTX 4090")` (use templates for reuse)[1][2].
2. **Run batch job**: Resume pod, then either SSH programmatically, expose an API endpoint in your container, or switch to **Serverless** for true no-intervention jobs: `endpoint.run_sync({"command": "your-batch-args"})`[2][4].
3. **Collect results**: Poll `runpod.get_pod(pod.id)` for logs/output, or use network volumes/S3-compatible API for persistent storage[1][9].
4. **Terminate**: `runpod.terminate_pod(pod.id)` after job completion (poll status)[2].
Serverless is ideal for your use case (spin-run-collect-terminate) as it autoscales and avoids pod management[1][2][4]. Availability errors like "no instances" may occur—retry or specify spot/preemptible[5].

---

## Citations

1. https://docs.runpod.io/api-reference/overview
2. https://github.com/runpod/runpod-python
3. https://www.runpod.io/changelog-entries/july-2025
4. https://www.youtube.com/watch?v=iUrG3qjvwXA
5. https://community.n8n.io/t/http-node-runpod-api/228934
6. https://www.runpod.io/blog/runpod-rest-api-gpu-management
7. https://docs.runpod.io/hosting/partner-requirements
8. https://www.runpod.io/blog/runpod-ai-field-notes-december-2025
9. https://www.runpod.io/blog/streamline-ai-workflows-s3-api
10. https://docs.runpod.io

---

## Usage Stats

- Prompt tokens: 115
- Completion tokens: 984
- Total tokens: 1099
