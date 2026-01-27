"""Butler Status Endpoints - Real-time butler monitoring."""

from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, List

router = APIRouter()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
INTELLIGENCE_DIR = PROJECT_ROOT / ".agent" / "intelligence"
CHUNKS_DIR = INTELLIGENCE_DIR / "chunks"


def get_fabric_status() -> Dict[str, Any]:
    """Query Communication Fabric butler."""
    try:
        # Run fabric.py to get current state
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / ".agent" / "intelligence" / "comms" / "fabric.py"), "--json"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(PROJECT_ROOT)
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                "name": "Communication Fabric",
                "type": "ai",
                "healthy": data.get("stability_margin", 0) > 0,
                "last_update": data.get("timestamp"),
                "summary": f"{data.get('health_tier')} tier, {data.get('stability_margin'):+.2f} margin",
                "details": data
            }
    except Exception as e:
        return {
            "name": "Communication Fabric",
            "type": "ai",
            "healthy": False,
            "last_update": None,
            "summary": f"Error: {str(e)[:50]}",
            "details": {}
        }

    return {"name": "Communication Fabric", "healthy": False, "summary": "Unknown"}


def get_refinery_status() -> Dict[str, Any]:
    """Query Refinery butler."""
    metadata_file = CHUNKS_DIR / "metadata.json"

    if not metadata_file.exists():
        return {
            "name": "Refinery",
            "type": "ai",
            "healthy": False,
            "last_update": None,
            "summary": "No metadata found",
            "details": {}
        }

    try:
        with open(metadata_file) as f:
            data = json.load(f)

        # Check freshness (stale if >1 hour old)
        last_update = datetime.fromisoformat(data["timestamp"])
        age_hours = (datetime.now() - last_update).total_seconds() / 3600
        is_fresh = age_hours < 1

        return {
            "name": "Refinery",
            "type": "ai",
            "healthy": is_fresh,
            "last_update": data["timestamp"],
            "summary": f"{data['total_chunks']:,} chunks, {data['total_tokens']:,} tokens",
            "details": data
        }
    except Exception as e:
        return {
            "name": "Refinery",
            "type": "ai",
            "healthy": False,
            "last_update": None,
            "summary": f"Error: {str(e)[:50]}",
            "details": {}
        }


def get_autopilot_status() -> Dict[str, Any]:
    """Query Autopilot butler."""
    state_file = PROJECT_ROOT / ".agent" / "state" / "autopilot_state.yaml"

    if not state_file.exists():
        return {
            "name": "Autopilot",
            "type": "orchestrator",
            "healthy": False,
            "last_update": None,
            "summary": "State file missing",
            "details": {}
        }

    try:
        import yaml
        with open(state_file) as f:
            data = yaml.safe_load(f)

        return {
            "name": "Autopilot",
            "type": "orchestrator",
            "healthy": data.get("enabled", False),
            "last_update": data.get("last_run"),
            "summary": f"Level {data.get('level', 0)}, {data.get('successful_runs', 0)}/{data.get('total_runs', 0)} success",
            "details": data
        }
    except Exception as e:
        return {
            "name": "Autopilot",
            "type": "orchestrator",
            "healthy": False,
            "last_update": None,
            "summary": f"Error: {str(e)[:50]}",
            "details": {}
        }


def get_git_status() -> Dict[str, Any]:
    """Query Git butler."""
    try:
        # Get branch
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=str(PROJECT_ROOT),
            text=True
        ).strip()

        # Get uncommitted count
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=str(PROJECT_ROOT),
            text=True
        ).strip()

        uncommitted = len([l for l in status.split('\n') if l.strip()]) if status else 0

        return {
            "name": "Git",
            "type": "deterministic",
            "healthy": True,
            "last_update": datetime.now().isoformat(),
            "summary": f"{branch} ({uncommitted} uncommitted)",
            "details": {
                "branch": branch,
                "uncommitted": uncommitted,
                "clean": uncommitted == 0
            }
        }
    except Exception as e:
        return {
            "name": "Git",
            "type": "deterministic",
            "healthy": False,
            "last_update": None,
            "summary": f"Error: {str(e)[:50]}",
            "details": {}
        }


# Placeholder butlers (implement more as needed)
def get_placeholder_butler(name: str, butler_type: str = "deterministic") -> Dict[str, Any]:
    """Placeholder for butlers not yet implemented."""
    return {
        "name": name,
        "type": butler_type,
        "healthy": None,
        "last_update": None,
        "summary": "Not yet implemented in API",
        "details": {}
    }


@router.get("")
def list_butlers():
    """List all butlers with current status."""

    butlers = [
        get_fabric_status(),
        get_refinery_status(),
        get_autopilot_status(),
        get_git_status(),
        # Add more butlers
        get_placeholder_butler("LOL", "deterministic"),
        get_placeholder_butler("TDJ", "deterministic"),
        get_placeholder_butler("Collider", "deterministic"),
        get_placeholder_butler("Trigger Engine", "orchestrator"),
        get_placeholder_butler("Enrichment", "ai"),
        # ... more as needed
    ]

    healthy = [b for b in butlers if b["healthy"] is True]
    unhealthy = [b for b in butlers if b["healthy"] is False]

    return {
        "timestamp": datetime.now().isoformat(),
        "total_butlers": len(butlers),
        "healthy_count": len(healthy),
        "unhealthy_count": len(unhealthy),
        "unknown_count": len(butlers) - len(healthy) - len(unhealthy),
        "butlers": butlers
    }


@router.get("/{butler_id}")
def get_butler_details(butler_id: str):
    """Get detailed status for specific butler."""

    # Map butler_id to getter function
    butler_map = {
        "comm_fabric": get_fabric_status,
        "refinery": get_refinery_status,
        "autopilot": get_autopilot_status,
        "git": get_git_status,
    }

    getter = butler_map.get(butler_id)
    if not getter:
        raise HTTPException(status_code=404, detail=f"Butler '{butler_id}' not found")

    return getter()


@router.get("/{butler_id}/history")
def get_butler_history(butler_id: str, hours: int = Query(24, ge=1, le=168)):
    """Get time-series history for butler."""

    if butler_id == "comm_fabric":
        # Load from state_history.jsonl
        history_file = PROJECT_ROOT / ".agent" / "intelligence" / "comms" / "state_history.jsonl"

        if not history_file.exists():
            return {"butler": "comm_fabric", "data_points": 0, "series": []}

        try:
            from datetime import timedelta

            cutoff = datetime.now() - timedelta(hours=hours)
            records = []

            with open(history_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            record = json.loads(line)
                            ts = datetime.fromisoformat(record["ts"])
                            if ts >= cutoff:
                                records.append(record)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue

            return {
                "butler": "comm_fabric",
                "period_hours": hours,
                "data_points": len(records),
                "series": records
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    else:
        raise HTTPException(status_code=404, detail=f"History not available for '{butler_id}'")
