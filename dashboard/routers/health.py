"""Health Endpoints - Communication Fabric metrics."""

from fastapi import APIRouter, Query, HTTPException
from pathlib import Path
import json
import subprocess
import sys
from datetime import datetime, timedelta

router = APIRouter()

PROJECT_ROOT = Path(__file__).parent.parent.parent
FABRIC_SCRIPT = PROJECT_ROOT / ".agent" / "intelligence" / "comms" / "fabric.py"
HISTORY_FILE = PROJECT_ROOT / ".agent" / "intelligence" / "comms" / "state_history.jsonl"


@router.get("/current")
def get_current_health():
    """Get current system health snapshot."""

    if not FABRIC_SCRIPT.exists():
        raise HTTPException(status_code=503, detail="Communication Fabric not available")

    try:
        # Run fabric.py to get current state
        result = subprocess.run(
            [sys.executable, str(FABRIC_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(PROJECT_ROOT)
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Fabric execution failed")

        data = json.loads(result.stdout)

        # Extract alerts if available
        alerts = data.get("alerts", [])

        return {
            "timestamp": data.get("timestamp"),
            "health_tier": data.get("health_tier"),
            "stability_margin": data.get("stability_margin"),
            "status": "STABLE" if data.get("stability_margin", 0) > 0 else "UNSTABLE",
            "metrics": {
                "F": data.get("F"),
                "MI": data.get("MI"),
                "N": data.get("N"),
                "SNR": data.get("SNR"),
                "R_auto": data.get("R_auto"),
                "R_manual": data.get("R_manual"),
                "delta_H": data.get("delta_H")
            },
            "alerts": alerts,
            "recommendations": []  # Could extract from components
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Fabric timeout")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON from fabric: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
def get_health_trends(hours: int = Query(24, ge=1, le=168)):
    """Get health metrics over time."""

    if not HISTORY_FILE.exists():
        return {
            "period_hours": hours,
            "data_points": 0,
            "message": "No history data available"
        }

    try:
        cutoff = datetime.now() - timedelta(hours=hours)
        records = []

        with open(HISTORY_FILE) as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        ts = datetime.fromisoformat(record["ts"])
                        if ts >= cutoff:
                            records.append(record)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

        if len(records) < 2:
            return {
                "period_hours": hours,
                "data_points": len(records),
                "message": "Insufficient data for trends"
            }

        # Calculate deltas
        first = records[0]
        last = records[-1]

        deltas = {}
        for key in ["F", "MI", "N", "SNR", "R_auto", "dH", "margin"]:
            if key in first and key in last:
                deltas[key] = round(last[key] - first[key], 4)

        # Current state
        current = {k: last.get(k) for k in ["F", "MI", "N", "SNR", "R_auto", "dH", "margin"]}

        # Trend alerts
        alerts = []
        if deltas.get("margin", 0) < -0.1:
            alerts.append(f"Stability margin declining: {deltas['margin']:+.4f}")
        if deltas.get("N", 0) > 0.1:
            alerts.append(f"Noise increasing: {deltas['N']:+.4f}")

        return {
            "period_hours": hours,
            "data_points": len(records),
            "current": current,
            "deltas": deltas,
            "trend_alerts": alerts,
            "series": records
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
