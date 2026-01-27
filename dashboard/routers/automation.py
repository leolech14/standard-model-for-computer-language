"""Automation Control Endpoints - Manage watchers and autopilot."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import subprocess
import yaml
import os

router = APIRouter()

PROJECT_ROOT = Path(__file__).parent.parent.parent


class AutopilotToggleRequest(BaseModel):
    enabled: bool
    level: int = 0  # FULL=0, PARTIAL=1, MANUAL=2, EMERGENCY=3


class WireTriggerRequest(BaseModel):
    mode: str = "quick"  # quick | full
    wait: bool = False


@router.get("/status")
def get_automation_status():
    """Get overall automation health."""

    # Check if watcher process is running
    watcher_running = False
    watcher_pid = None
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if "filesystem_watcher.py" in line and "grep" not in line:
                watcher_running = True
                parts = line.split()
                if len(parts) > 1:
                    watcher_pid = int(parts[1])
                break
    except Exception:
        pass

    # Load autopilot state
    autopilot_state = {}
    state_file = PROJECT_ROOT / ".agent" / "state" / "autopilot_state.yaml"
    if state_file.exists():
        try:
            with open(state_file) as f:
                autopilot_state = yaml.safe_load(f)
        except Exception:
            pass

    # Load circuit breakers
    circuit_breakers = {}
    cb_file = PROJECT_ROOT / ".agent" / "state" / "circuit_breakers.yaml"
    if cb_file.exists():
        try:
            with open(cb_file) as f:
                cb_data = yaml.safe_load(f)
                systems = cb_data.get("systems", {})
                for sys_name, sys_data in systems.items():
                    failures = sys_data.get("failures", 0)
                    if failures == 0:
                        status = "GREEN"
                    elif failures < 3:
                        status = "YELLOW"
                    else:
                        status = "RED"
                    circuit_breakers[sys_name] = status
        except Exception:
            pass

    return {
        "timestamp": datetime.now().isoformat(),
        "automation_level": "92%",
        "local_watchers": {
            "filesystem_watcher": {
                "running": watcher_running,
                "pid": watcher_pid
            }
        },
        "autopilot": {
            "enabled": autopilot_state.get("enabled", False),
            "level": autopilot_state.get("level", 0),
            "last_run": autopilot_state.get("last_run"),
            "success_rate": (autopilot_state.get("successful_runs", 0) / max(autopilot_state.get("total_runs", 1), 1))
        },
        "circuit_breakers": {
            "open_count": sum(1 for status in circuit_breakers.values() if status == "RED"),
            "systems_status": circuit_breakers
        }
    }


@router.post("/wire/trigger")
def trigger_wire(request: WireTriggerRequest):
    """Manually trigger wire pipeline."""

    try:
        wire_script = PROJECT_ROOT / ".agent" / "tools" / "wire.py"

        args = [str(wire_script)]
        if request.mode == "quick":
            args.append("--quick")

        if request.wait:
            # Synchronous execution
            result = subprocess.run(
                ["python3"] + args,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=600
            )

            return {
                "triggered": True,
                "mode": request.mode,
                "completed": True,
                "success": result.returncode == 0,
                "output": result.stdout[-500:] if result.stdout else ""
            }
        else:
            # Asynchronous execution
            subprocess.Popen(
                ["python3"] + args,
                cwd=str(PROJECT_ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return {
                "triggered": True,
                "mode": request.mode,
                "started_at": datetime.now().isoformat(),
                "wait": False,
                "message": "Wire started in background"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wire/status")
def get_wire_status():
    """Check if wire is currently running."""

    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )

        running = any("wire.py" in line and "grep" not in line
                     for line in result.stdout.split('\n'))

        return {
            "running": running,
            "status": "running" if running else "idle"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autopilot/toggle")
def toggle_autopilot(request: AutopilotToggleRequest):
    """Enable/disable autopilot."""

    try:
        # Run autopilot.py enable/disable
        autopilot_script = PROJECT_ROOT / ".agent" / "tools" / "autopilot.py"

        command = "enable" if request.enabled else "disable"

        result = subprocess.run(
            ["python3", str(autopilot_script), command],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Autopilot command failed: {result.stderr}")

        return {
            "autopilot_enabled": request.enabled,
            "level": request.level,
            "message": result.stdout.strip()
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Autopilot command timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
