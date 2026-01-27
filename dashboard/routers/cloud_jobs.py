"""Cloud Jobs Endpoints - Control and monitor Cloud Run Jobs."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.cloud import run_v2
import os

router = APIRouter()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "elements-archive-2026")
REGION = "us-central1"


class ExecuteJobRequest(BaseModel):
    wait: bool = False


@router.get("")
def list_jobs():
    """List all Cloud Run Jobs."""
    # For MVP, return known jobs
    # Full implementation: Use run_v2.JobsClient().list_jobs()

    return {
        "jobs": [
            {
                "name": "socratic-audit-job",
                "region": REGION,
                "last_run": "2026-01-27T10:17:46Z",
                "status": "success",
                "next_scheduled": "2026-01-27T12:00:00Z",
                "execution_history_endpoint": "/api/cloud/jobs/socratic-audit-job/history"
            }
        ]
    }


@router.get("/{job_name}/history")
def get_job_history(job_name: str, limit: int = 20):
    """Get execution history for job."""
    # Full implementation: Use run_v2 API to list executions

    # For MVP: Return placeholder
    return {
        "job_name": job_name,
        "total_executions": 0,
        "returned": 0,
        "executions": [],
        "message": "Cloud Run API integration pending"
    }


@router.post("/{job_name}/execute")
def execute_job(job_name: str, request: ExecuteJobRequest):
    """Trigger job execution manually."""

    try:
        client = run_v2.JobsClient()
        job_path = f"projects/{PROJECT_ID}/locations/{REGION}/jobs/{job_name}"

        # Trigger execution
        operation = client.run_job(name=job_path)

        return {
            "job_name": job_name,
            "triggered": True,
            "operation_name": operation.name,
            "message": "Job execution started"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger job: {str(e)}")


@router.get("/{job_name}/status/{execution_id}")
def get_execution_status(job_name: str, execution_id: str):
    """Poll execution status."""
    # Full implementation: Query execution status

    return {
        "execution_id": execution_id,
        "status": "unknown",
        "message": "Status polling not yet implemented"
    }
