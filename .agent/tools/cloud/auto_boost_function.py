#!/usr/bin/env python3
"""
Cloud Function: Auto-Boost Opportunities

Runs on GCP Cloud Functions to automatically:
1. Scan inbox for opportunities
2. Assess confidence via Gemini
3. Auto-promote opportunities >= 90% confidence
4. Store results to GCS

Triggers:
- Cloud Scheduler (hourly)
- Pub/Sub (on new opportunity)
- HTTP (manual)

Environment Variables:
- GEMINI_API_KEY: API key for Gemini
- GCS_BUCKET: Target bucket (default: elements-archive-2026)
- Risk thresholds: A=90%, A+=95%, A++=99%

Deploy:
    gcloud functions deploy auto-boost \
        --runtime python311 \
        --trigger-http \
        --entry-point main \
        --set-env-vars GEMINI_API_KEY=xxx,GCS_BUCKET=elements-archive-2026
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Cloud Function dependencies
try:
    from google import genai
    from google.cloud import storage
    import yaml
    import functions_framework
    CLOUD_MODE = True
except ImportError:
    CLOUD_MODE = False

# Configuration
GCS_BUCKET = os.environ.get("GCS_BUCKET", "elements-archive-2026")

# Risk-based thresholds (higher risk = higher confidence required)
RISK_THRESHOLDS = {
    "A": 90,      # Standard tasks
    "A+": 95,     # Important tasks
    "A++": 99,    # Critical tasks (near-certainty required)
}
DEFAULT_RISK = "A"
REGISTRY_PREFIX = ".agent/registry"

# 4D Assessment Prompt
ASSESSMENT_PROMPT = """You are a STAFF ENGINEER reviewing a proposed task before execution.

TASK DETAILS:
- ID: {opp_id}
- Title: {title}
- Description: {description}
- Category: {category}
- Source: {source}

Evaluate this task across 4 dimensions (score each 0-100):

1. FACTUAL: Is the task description accurate and clear?
2. ALIGNMENT: Does this task serve the project's mission?
3. CURRENT: Does this task fit the codebase as it exists?
4. ONWARDS: Does this task align with the project's roadmap?

OUTPUT FORMAT (JSON only, no markdown):
{{
  "opp_id": "{opp_id}",
  "dimensions": {{
    "factual": {{"score": <0-100>, "reason": "<brief reason>"}},
    "alignment": {{"score": <0-100>, "reason": "<brief reason>"}},
    "current": {{"score": <0-100>, "reason": "<brief reason>"}},
    "onwards": {{"score": <0-100>, "reason": "<brief reason>"}}
  }},
  "composite_score": <min of 4 dimensions>,
  "recommendation": "ACCEPT|DEFER|REJECT",
  "summary": "<1-2 sentence summary>"
}}
"""


def get_gemini_client():
    """Initialize Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)


def get_storage_client():
    """Initialize GCS client."""
    return storage.Client()


def load_opportunities_from_gcs(client) -> list[dict]:
    """Load all opportunities from GCS bucket."""
    bucket = client.bucket(GCS_BUCKET)
    prefix = f"{REGISTRY_PREFIX}/inbox/"

    opportunities = []
    for blob in bucket.list_blobs(prefix=prefix):
        if blob.name.endswith(".yaml") and "OPP-" in blob.name:
            content = blob.download_as_text()
            opp = yaml.safe_load(content)
            opp["_blob_name"] = blob.name
            opportunities.append(opp)

    return opportunities


def assess_opportunity(client, opp: dict) -> dict:
    """Run Gemini assessment on an opportunity."""
    prompt = ASSESSMENT_PROMPT.format(
        opp_id=opp.get("id", "UNKNOWN"),
        title=opp.get("title", "Untitled"),
        description=opp.get("description", "No description"),
        category=opp.get("metadata", {}).get("category", "UNKNOWN"),
        source=opp.get("source", "UNKNOWN"),
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    # Parse JSON response
    text = response.text
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    return json.loads(text)


def promote_opportunity(storage_client, opp: dict, assessment: dict) -> str:
    """Promote an opportunity to a task in GCS."""
    bucket = storage_client.bucket(GCS_BUCKET)

    # Find next task ID
    prefix = f"{REGISTRY_PREFIX}/active/"
    existing = list(bucket.list_blobs(prefix=prefix))
    max_id = 0
    for blob in existing:
        if "TASK-" in blob.name:
            try:
                num = int(blob.name.split("TASK-")[1].split(".")[0])
                max_id = max(max_id, num)
            except (ValueError, IndexError):
                pass
    task_id = f"TASK-{max_id + 1:03d}"

    # Build task
    now = datetime.now(timezone.utc).isoformat()
    task = {
        "id": task_id,
        "title": opp.get("title"),
        "description": opp.get("description"),
        "status": "READY",
        "confidence": {
            "factual": assessment["dimensions"]["factual"]["score"],
            "alignment": assessment["dimensions"]["alignment"]["score"],
            "current": assessment["dimensions"]["current"]["score"],
            "onwards": assessment["dimensions"]["onwards"]["score"],
        },
        "created": now,
        "updated": now,
        "promoted_from": opp.get("id"),
        "promotion_summary": assessment.get("summary"),
        "runs": [],
        "output": {},
    }

    # Write task to GCS
    task_blob = bucket.blob(f"{REGISTRY_PREFIX}/active/{task_id}.yaml")
    task_blob.upload_from_string(yaml.dump(task, default_flow_style=False))

    # Mark opportunity as promoted
    opp["promoted_to"] = task_id
    opp["promoted_at"] = now
    opp_blob = bucket.blob(opp["_blob_name"])
    del opp["_blob_name"]
    opp_blob.upload_from_string(yaml.dump(opp, default_flow_style=False))

    return task_id


def save_report(storage_client, report: dict):
    """Save assessment report to GCS."""
    bucket = storage_client.bucket(GCS_BUCKET)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob = bucket.blob(f"intelligence/auto_boost/{timestamp}_report.json")
    blob.upload_from_string(json.dumps(report, indent=2))
    return blob.name


def run_auto_boost() -> dict:
    """Main auto-boost logic."""
    gemini = get_gemini_client()
    storage = get_storage_client()

    # Load opportunities
    opportunities = load_opportunities_from_gcs(storage)
    print(f"Found {len(opportunities)} opportunities in inbox")

    # Filter unpromoted only
    unpromoted = [o for o in opportunities if not o.get("promoted_to")]
    print(f"Processing {len(unpromoted)} unpromoted opportunities")

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "thresholds": RISK_THRESHOLDS,
        "total_scanned": len(unpromoted),
        "assessments": [],
        "promoted": [],
        "deferred": [],
        "errors": [],
    }

    for opp in unpromoted:
        opp_id = opp.get("id", "UNKNOWN")
        print(f"  Assessing {opp_id}...")

        try:
            assessment = assess_opportunity(gemini, opp)
            results["assessments"].append(assessment)

            composite = assessment.get("composite_score", 0)
            recommendation = assessment.get("recommendation", "DEFER")

            # Get risk level and threshold
            risk = opp.get("risk", opp.get("metadata", {}).get("risk", DEFAULT_RISK))
            threshold = RISK_THRESHOLDS.get(risk, RISK_THRESHOLDS[DEFAULT_RISK])

            if composite >= threshold and recommendation == "ACCEPT":
                task_id = promote_opportunity(storage, opp, assessment)
                results["promoted"].append({
                    "opp_id": opp_id,
                    "task_id": task_id,
                    "score": composite,
                })
                print(f"    PROMOTED to {task_id} [{composite}%]")
            else:
                results["deferred"].append({
                    "opp_id": opp_id,
                    "score": composite,
                    "reason": recommendation,
                })
                print(f"    DEFERRED [{composite}%] - {recommendation}")

        except Exception as e:
            results["errors"].append({
                "opp_id": opp_id,
                "error": str(e),
            })
            print(f"    ERROR: {e}")

    # Save report
    report_path = save_report(storage, results)
    results["report_path"] = report_path

    print(f"\nSummary:")
    print(f"  Promoted: {len(results['promoted'])}")
    print(f"  Deferred: {len(results['deferred'])}")
    print(f"  Errors: {len(results['errors'])}")
    print(f"  Report: gs://{GCS_BUCKET}/{report_path}")

    return results


# Cloud Function entry point
if CLOUD_MODE:
    @functions_framework.http
    def main(request):
        """HTTP Cloud Function entry point."""
        try:
            results = run_auto_boost()
            return json.dumps(results), 200, {"Content-Type": "application/json"}
        except Exception as e:
            return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


# Local execution
if __name__ == "__main__":
    if not CLOUD_MODE:
        print("Cloud dependencies not installed. Install with:")
        print("  pip install google-cloud-storage google-genai pyyaml functions-framework")
    else:
        results = run_auto_boost()
        print(json.dumps(results, indent=2))
