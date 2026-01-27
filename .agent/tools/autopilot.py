#!/usr/bin/env python3
"""
AUTOPILOT - Self-Running Repository Orchestrator
=================================================
SMoC Role: Orchestrator | Domain: Automation

The master controller that makes the repo run itself.
Wires together: TDJ, Trigger Engine, Enrichment Pipeline, Drift Guard.

DESIGN PRINCIPLES:
1. GRACEFUL DEGRADATION - If one system fails, others continue
2. CIRCUIT BREAKERS - Prevent cascade failures
3. IDEMPOTENT - Safe to run multiple times
4. OBSERVABLE - Full logging and status reporting
5. MANUAL OVERRIDE - Always escapable

FALLBACK HIERARCHY:
    Level 0: Full automation (all systems green)
    Level 1: Partial automation (some systems degraded)
    Level 2: Manual mode (automation paused, human intervention)
    Level 3: Emergency stop (all automation halted)

Usage:
    ./autopilot.py status          # Show all systems status
    ./autopilot.py run             # Run full cycle once
    ./autopilot.py run --safe      # Run with extra safety checks
    ./autopilot.py enable          # Enable post-commit automation
    ./autopilot.py disable         # Disable automation (manual mode)
    ./autopilot.py health          # Deep health check all systems
    ./autopilot.py recover         # Attempt recovery of failed systems

Hook Integration:
    # In .agent/hooks/post-commit, add:
    python3 .agent/tools/autopilot.py post-commit --safe
"""

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

from utils.yaml_utils import load_yaml, save_yaml

# =============================================================================
# CONFIGURATION
# =============================================================================

REPO_ROOT = Path(__file__).parent.parent.parent
AGENT_DIR = REPO_ROOT / ".agent"
TOOLS_DIR = AGENT_DIR / "tools"
STATE_DIR = AGENT_DIR / "state"
INTELLIGENCE_DIR = AGENT_DIR / "intelligence"
LOGS_DIR = INTELLIGENCE_DIR / "autopilot_logs"

# Tool paths
TDJ_PATH = REPO_ROOT / "context-management/tools/maintenance/tdj.py"
TRIGGER_ENGINE_PATH = TOOLS_DIR / "trigger_engine.py"
ENRICHMENT_PATH = TOOLS_DIR / "enrichment_orchestrator.py"
DRIFT_GUARD_PATH = REPO_ROOT / "context-management/tools/drift_guard.py"
COMM_FABRIC_PATH = INTELLIGENCE_DIR / "comms" / "fabric.py"

# State files
AUTOPILOT_STATE = STATE_DIR / "autopilot_state.yaml"
CIRCUIT_BREAKER_STATE = STATE_DIR / "circuit_breakers.yaml"

# Thresholds
MAX_FAILURES_BEFORE_CIRCUIT_BREAK = 3
CIRCUIT_BREAKER_COOLDOWN_SECONDS = 300  # 5 minutes
MAX_EXECUTION_TIME_SECONDS = 120  # 2 minutes per system
THROTTLE_SECONDS = 60  # Minimum time between full runs

# =============================================================================
# ENUMS
# =============================================================================

class SystemStatus(Enum):
    GREEN = "green"      # Fully operational
    YELLOW = "yellow"    # Degraded but functional
    RED = "red"          # Failed, circuit broken
    UNKNOWN = "unknown"  # Not yet checked

class AutopilotLevel(Enum):
    FULL = 0        # All systems automated
    PARTIAL = 1     # Some systems degraded
    MANUAL = 2      # Automation paused
    EMERGENCY = 3   # All automation halted

# =============================================================================
# UTILITIES
# =============================================================================

def ensure_dirs():
    """Ensure required directories exist."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

def log_event(event: str, details: dict = None):
    """Log an autopilot event."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_file = LOGS_DIR / f"autopilot_{datetime.now().strftime('%Y%m%d')}.jsonl"

    entry = {
        "timestamp": timestamp,
        "event": event,
        "details": details or {}
    }

    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception:
        pass  # Silent fail for logging

def log_error(message: str):
    """Log an error."""
    log_event("error", {"message": message})
    print(f"[ERROR] {message}", file=sys.stderr)

# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitBreaker:
    """Prevents cascade failures by tracking system health."""

    def __init__(self):
        self.state = load_yaml(CIRCUIT_BREAKER_STATE)
        if not self.state:
            self.state = {
                "systems": {},
                "global_level": AutopilotLevel.FULL.value
            }

    def record_success(self, system: str):
        """Record a successful execution."""
        if system not in self.state["systems"]:
            self.state["systems"][system] = {"failures": 0, "last_success": None, "broken_until": None}

        self.state["systems"][system]["failures"] = 0
        self.state["systems"][system]["last_success"] = datetime.now(timezone.utc).isoformat()
        self.state["systems"][system]["broken_until"] = None
        self._save()

    def record_failure(self, system: str, error: str):
        """Record a failed execution."""
        if system not in self.state["systems"]:
            self.state["systems"][system] = {"failures": 0, "last_success": None, "broken_until": None}

        self.state["systems"][system]["failures"] += 1
        self.state["systems"][system]["last_error"] = error
        self.state["systems"][system]["last_failure"] = datetime.now(timezone.utc).isoformat()

        # Trip circuit breaker if too many failures
        if self.state["systems"][system]["failures"] >= MAX_FAILURES_BEFORE_CIRCUIT_BREAK:
            cooldown_until = datetime.now(timezone.utc) + timedelta(seconds=CIRCUIT_BREAKER_COOLDOWN_SECONDS)
            self.state["systems"][system]["broken_until"] = cooldown_until.isoformat()
            log_event("circuit_breaker_tripped", {"system": system, "until": cooldown_until.isoformat()})

        self._save()

    def is_broken(self, system: str) -> bool:
        """Check if a system's circuit breaker is tripped."""
        if system not in self.state["systems"]:
            return False

        broken_until = self.state["systems"][system].get("broken_until")
        if not broken_until:
            return False

        try:
            until = datetime.fromisoformat(broken_until.replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > until:
                # Cooldown expired, reset
                self.state["systems"][system]["broken_until"] = None
                self.state["systems"][system]["failures"] = 0
                self._save()
                return False
            return True
        except Exception:
            return False

    def get_status(self, system: str) -> SystemStatus:
        """Get the status of a system."""
        if self.is_broken(system):
            return SystemStatus.RED

        sys_state = self.state["systems"].get(system, {})
        failures = sys_state.get("failures", 0)

        if failures == 0:
            return SystemStatus.GREEN
        elif failures < MAX_FAILURES_BEFORE_CIRCUIT_BREAK:
            return SystemStatus.YELLOW
        else:
            return SystemStatus.RED

    def reset(self, system: str = None):
        """Reset circuit breaker for a system or all systems."""
        if system:
            if system in self.state["systems"]:
                self.state["systems"][system] = {"failures": 0, "last_success": None, "broken_until": None}
        else:
            self.state["systems"] = {}
        self._save()

    def _save(self):
        save_yaml(CIRCUIT_BREAKER_STATE, self.state)

# =============================================================================
# SYSTEM RUNNERS
# =============================================================================

def run_with_timeout(cmd: List[str], timeout: int = MAX_EXECUTION_TIME_SECONDS) -> Tuple[bool, str]:
    """Run a command with timeout and capture output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO_ROOT
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout}s"
    except Exception as e:
        return False, str(e)

def run_tdj(circuit_breaker: CircuitBreaker) -> Tuple[bool, str]:
    """Run TDJ scan with fallback."""
    system = "tdj"

    if circuit_breaker.is_broken(system):
        return False, "Circuit breaker tripped"

    if not TDJ_PATH.exists():
        circuit_breaker.record_failure(system, "TDJ script not found")
        return False, "TDJ script not found"

    success, output = run_with_timeout([sys.executable, str(TDJ_PATH), "--scan", "--quiet"])

    if success:
        circuit_breaker.record_success(system)
        log_event("tdj_success", {"output": output[:500]})
    else:
        circuit_breaker.record_failure(system, output[:200])
        log_event("tdj_failure", {"error": output[:500]})

    return success, output

def run_trigger_engine(circuit_breaker: CircuitBreaker, trigger_type: str = "post-commit") -> Tuple[bool, str]:
    """Run trigger engine with fallback."""
    system = "trigger_engine"

    if circuit_breaker.is_broken(system):
        return False, "Circuit breaker tripped"

    if not TRIGGER_ENGINE_PATH.exists():
        circuit_breaker.record_failure(system, "Trigger engine not found")
        return False, "Trigger engine not found"

    success, output = run_with_timeout([sys.executable, str(TRIGGER_ENGINE_PATH), trigger_type])

    if success:
        circuit_breaker.record_success(system)
        log_event("trigger_engine_success", {"type": trigger_type, "output": output[:500]})
    else:
        circuit_breaker.record_failure(system, output[:200])
        log_event("trigger_engine_failure", {"type": trigger_type, "error": output[:500]})

    return success, output

def run_enrichment(circuit_breaker: CircuitBreaker, dry_run: bool = False) -> Tuple[bool, str]:
    """Run enrichment pipeline with fallback."""
    system = "enrichment"

    if circuit_breaker.is_broken(system):
        return False, "Circuit breaker tripped"

    if not ENRICHMENT_PATH.exists():
        circuit_breaker.record_failure(system, "Enrichment orchestrator not found")
        return False, "Enrichment orchestrator not found"

    args = [sys.executable, str(ENRICHMENT_PATH)]
    if dry_run:
        args.append("--dry-run")

    # Enrichment can take longer
    success, output = run_with_timeout(args, timeout=300)

    if success:
        circuit_breaker.record_success(system)
        log_event("enrichment_success", {"dry_run": dry_run, "output": output[:500]})
    else:
        circuit_breaker.record_failure(system, output[:200])
        log_event("enrichment_failure", {"dry_run": dry_run, "error": output[:500]})

    return success, output

def run_comm_fabric(circuit_breaker: CircuitBreaker) -> Tuple[bool, str]:
    """Record Communication Fabric state vector."""
    system = "comm_fabric"

    if circuit_breaker.is_broken(system):
        return False, "Circuit breaker tripped"

    if not COMM_FABRIC_PATH.exists():
        circuit_breaker.record_failure(system, "Communication Fabric module not found")
        return False, "Communication Fabric module not found"

    success, output = run_with_timeout([sys.executable, str(COMM_FABRIC_PATH), "--record"])

    if success:
        circuit_breaker.record_success(system)
        log_event("comm_fabric_success", {"output": output[:500]})
    else:
        circuit_breaker.record_failure(system, output[:200])
        log_event("comm_fabric_failure", {"error": output[:500]})

    return success, output

# =============================================================================
# AUTOPILOT STATE
# =============================================================================

class AutopilotState:
    """Manages autopilot operational state."""

    def __init__(self):
        self.state = load_yaml(AUTOPILOT_STATE)
        if not self.state:
            self.state = {
                "enabled": True,
                "level": AutopilotLevel.FULL.value,
                "last_run": None,
                "last_run_result": None,
                "total_runs": 0,
                "successful_runs": 0
            }

    def is_enabled(self) -> bool:
        return self.state.get("enabled", True)

    def get_level(self) -> AutopilotLevel:
        return AutopilotLevel(self.state.get("level", 0))

    def set_enabled(self, enabled: bool):
        self.state["enabled"] = enabled
        self._save()

    def set_level(self, level: AutopilotLevel):
        self.state["level"] = level.value
        self._save()

    def record_run(self, success: bool):
        self.state["last_run"] = datetime.now(timezone.utc).isoformat()
        self.state["last_run_result"] = "success" if success else "failure"
        self.state["total_runs"] = self.state.get("total_runs", 0) + 1
        if success:
            self.state["successful_runs"] = self.state.get("successful_runs", 0) + 1
        self._save()

    def should_throttle(self) -> bool:
        """Check if we should throttle execution."""
        last_run = self.state.get("last_run")
        if not last_run:
            return False

        try:
            last = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
            elapsed = (datetime.now(timezone.utc) - last).total_seconds()
            return elapsed < THROTTLE_SECONDS
        except Exception:
            return False

    def _save(self):
        save_yaml(AUTOPILOT_STATE, self.state)

# =============================================================================
# COMMANDS
# =============================================================================

def cmd_status():
    """Show status of all systems."""
    ensure_dirs()
    circuit_breaker = CircuitBreaker()
    autopilot_state = AutopilotState()

    print("=" * 60)
    print("AUTOPILOT STATUS")
    print("=" * 60)
    print()

    # Overall status
    level = autopilot_state.get_level()
    enabled = autopilot_state.is_enabled()

    level_colors = {
        AutopilotLevel.FULL: "\033[92m",      # Green
        AutopilotLevel.PARTIAL: "\033[93m",   # Yellow
        AutopilotLevel.MANUAL: "\033[94m",    # Blue
        AutopilotLevel.EMERGENCY: "\033[91m"  # Red
    }

    print(f"Autopilot:    {'ENABLED' if enabled else 'DISABLED'}")
    print(f"Level:        {level_colors.get(level, '')}{level.name}\033[0m")
    print(f"Last Run:     {autopilot_state.state.get('last_run', 'Never')}")
    print(f"Success Rate: {autopilot_state.state.get('successful_runs', 0)}/{autopilot_state.state.get('total_runs', 0)}")
    print()

    # System status
    print("Systems:")
    systems = [
        ("tdj", "Timestamp Daily Journal", TDJ_PATH.exists()),
        ("trigger_engine", "Trigger Engine", TRIGGER_ENGINE_PATH.exists()),
        ("enrichment", "Enrichment Pipeline", ENRICHMENT_PATH.exists()),
        ("comm_fabric", "Communication Fabric", COMM_FABRIC_PATH.exists()),
    ]

    status_icons = {
        SystemStatus.GREEN: "\033[92m●\033[0m",
        SystemStatus.YELLOW: "\033[93m●\033[0m",
        SystemStatus.RED: "\033[91m●\033[0m",
        SystemStatus.UNKNOWN: "\033[90m●\033[0m"
    }

    for sys_id, sys_name, exists in systems:
        status = circuit_breaker.get_status(sys_id) if exists else SystemStatus.RED
        icon = status_icons[status]
        exists_str = "✓" if exists else "✗"
        broken = " [CIRCUIT BROKEN]" if circuit_breaker.is_broken(sys_id) else ""
        print(f"  {icon} {sys_name}: {exists_str}{broken}")

    print()
    print("=" * 60)

def cmd_run(safe_mode: bool = False, dry_run: bool = False):
    """Run a full autopilot cycle."""
    ensure_dirs()
    circuit_breaker = CircuitBreaker()
    autopilot_state = AutopilotState()

    # Pre-flight checks
    if not autopilot_state.is_enabled():
        print("Autopilot is DISABLED. Use 'autopilot.py enable' to enable.")
        return False

    if autopilot_state.get_level() == AutopilotLevel.EMERGENCY:
        print("Autopilot is in EMERGENCY STOP mode. Use 'autopilot.py recover' first.")
        return False

    if safe_mode and autopilot_state.should_throttle():
        print("Throttled: Last run was too recent. Use --force to override.")
        return False

    print("=" * 60)
    print("AUTOPILOT RUN" + (" [DRY RUN]" if dry_run else "") + (" [SAFE MODE]" if safe_mode else ""))
    print("=" * 60)
    print()

    results = {}
    overall_success = True

    # TDJ removed from post-commit - it's on-demand only (11ms, no need to pre-compute)
    # Run manually: python context-management/tools/maintenance/tdj.py --scan

    # Step 1: Trigger Engine
    print("[1/3] Trigger Engine - Checking for macro triggers...")
    if not circuit_breaker.is_broken("trigger_engine"):
        if dry_run:
            print("  [DRY RUN] Would check triggers")
            results["trigger_engine"] = True
        else:
            success, output = run_trigger_engine(circuit_breaker)
            results["trigger_engine"] = success
            if success:
                print("  ✓ Triggers checked")
            else:
                print(f"  ✗ Trigger engine failed: {output[:100]}")
                # Don't fail overall for trigger engine - it's optional
    else:
        print("  ⊘ Trigger engine skipped (circuit broken)")
        results["trigger_engine"] = None

    # Step 2: Enrichment (only on full runs, not post-commit)
    print("\n[2/3] Enrichment - Processing opportunities...")
    if not safe_mode:  # Skip enrichment in safe mode (too heavy for post-commit)
        if not circuit_breaker.is_broken("enrichment"):
            if dry_run:
                print("  [DRY RUN] Would run enrichment pipeline")
                results["enrichment"] = True
            else:
                success, output = run_enrichment(circuit_breaker, dry_run=False)
                results["enrichment"] = success
                if success:
                    print("  ✓ Enrichment complete")
                else:
                    print(f"  ✗ Enrichment failed: {output[:100]}")
                    # Don't fail overall for enrichment - it's enhancement
        else:
            print("  ⊘ Enrichment skipped (circuit broken)")
            results["enrichment"] = None
    else:
        print("  ⊘ Enrichment skipped (safe mode)")
        results["enrichment"] = None

    # Step 3: Communication Fabric - Record state vector
    print("\n[3/3] Communication Fabric - Recording state vector...")
    if not circuit_breaker.is_broken("comm_fabric"):
        if dry_run:
            print("  [DRY RUN] Would record Communication Fabric metrics")
            results["comm_fabric"] = True
        else:
            success, output = run_comm_fabric(circuit_breaker)
            results["comm_fabric"] = success
            if success:
                print("  ✓ Communication Fabric recorded")
            else:
                print(f"  ✗ Communication Fabric failed: {output[:100]}")
                # Don't fail overall - it's observability
    else:
        print("  ⊘ Communication Fabric skipped (circuit broken)")
        results["comm_fabric"] = None

    # Record run
    autopilot_state.record_run(overall_success)

    # Summary
    print()
    print("=" * 60)
    success_count = sum(1 for v in results.values() if v is True)
    skip_count = sum(1 for v in results.values() if v is None)
    fail_count = sum(1 for v in results.values() if v is False)

    print(f"Result: {success_count} succeeded, {skip_count} skipped, {fail_count} failed")
    print("=" * 60)

    log_event("autopilot_run_complete", {
        "results": {k: str(v) for k, v in results.items()},
        "overall_success": overall_success,
        "safe_mode": safe_mode,
        "dry_run": dry_run
    })

    return overall_success

def cmd_post_commit(safe_mode: bool = True):
    """Lightweight post-commit hook handler."""
    ensure_dirs()
    circuit_breaker = CircuitBreaker()
    autopilot_state = AutopilotState()

    if not autopilot_state.is_enabled():
        return True  # Silent exit if disabled

    if autopilot_state.get_level().value >= AutopilotLevel.MANUAL.value:
        return True  # Silent exit in manual/emergency mode

    log_event("post_commit_triggered")

    # Only run trigger engine on post-commit
    # TDJ removed - on-demand only (11ms, run when needed)
    results = []

    # Trigger engine (check for macro triggers)
    if not circuit_breaker.is_broken("trigger_engine"):
        success, _ = run_trigger_engine(circuit_breaker, "post-commit")
        results.append(success)

    # Periodic enrichment: run if stale (>24h since last run)
    # This processes inbox opportunities, auto-promotes high-confidence items
    if _should_run_enrichment(autopilot_state):
        log_event("enrichment_stale_trigger")
        if not circuit_breaker.is_broken("enrichment"):
            success, _ = run_enrichment(circuit_breaker, dry_run=False)
            if success:
                _mark_enrichment_run(autopilot_state)
            results.append(success)

    return all(results) if results else True


def _should_run_enrichment(state: AutopilotState) -> bool:
    """Check if enrichment should run (>24h since last run)."""
    last_enrichment = state.state.get("last_enrichment_run")
    if not last_enrichment:
        return True  # Never run before

    try:
        last = datetime.fromisoformat(last_enrichment.replace('Z', '+00:00'))
        elapsed_hours = (datetime.now(timezone.utc) - last).total_seconds() / 3600
        return elapsed_hours >= 24  # Run once per day
    except Exception:
        return True  # If parsing fails, assume stale


def _mark_enrichment_run(state: AutopilotState):
    """Mark that enrichment was run."""
    state.state["last_enrichment_run"] = datetime.now(timezone.utc).isoformat()
    state._save()

def cmd_enable():
    """Enable autopilot."""
    ensure_dirs()
    state = AutopilotState()
    state.set_enabled(True)
    state.set_level(AutopilotLevel.FULL)
    log_event("autopilot_enabled")
    print("Autopilot ENABLED at level FULL")

def cmd_disable():
    """Disable autopilot (manual mode)."""
    ensure_dirs()
    state = AutopilotState()
    state.set_enabled(False)
    state.set_level(AutopilotLevel.MANUAL)
    log_event("autopilot_disabled")
    print("Autopilot DISABLED (manual mode)")

def cmd_recover():
    """Attempt to recover from failures."""
    ensure_dirs()
    circuit_breaker = CircuitBreaker()
    state = AutopilotState()

    print("=" * 60)
    print("AUTOPILOT RECOVERY")
    print("=" * 60)
    print()

    # Reset all circuit breakers
    print("Resetting circuit breakers...")
    circuit_breaker.reset()
    print("  ✓ All circuit breakers reset")

    # Reset to partial mode (not full, to be safe)
    print("Setting level to PARTIAL...")
    state.set_level(AutopilotLevel.PARTIAL)
    state.set_enabled(True)
    print("  ✓ Autopilot enabled at PARTIAL level")

    # Run health check
    print("\nRunning health check...")
    cmd_health()

    log_event("autopilot_recovery_attempted")

    print()
    print("Recovery complete. Run 'autopilot.py run --safe' to test.")

def cmd_health():
    """Deep health check of all systems."""
    ensure_dirs()

    print("=" * 60)
    print("AUTOPILOT HEALTH CHECK")
    print("=" * 60)
    print()

    checks = []

    # Check TDJ
    print("TDJ:")
    if TDJ_PATH.exists():
        print(f"  ✓ Script exists: {TDJ_PATH}")
        # Check if JSONL exists and is recent
        tdj_data = INTELLIGENCE_DIR / "tdj.jsonl"
        if tdj_data.exists():
            age_hours = (time.time() - tdj_data.stat().st_mtime) / 3600
            if age_hours < 24:
                print(f"  ✓ Data fresh ({age_hours:.1f}h old)")
                checks.append(True)
            else:
                print(f"  ⚠ Data stale ({age_hours:.1f}h old)")
                checks.append(True)  # Still OK, just stale
        else:
            print("  ⚠ No data file (run --scan first)")
            checks.append(True)  # OK, just needs first run
    else:
        print(f"  ✗ Script missing: {TDJ_PATH}")
        checks.append(False)

    # Check Trigger Engine
    print("\nTrigger Engine:")
    if TRIGGER_ENGINE_PATH.exists():
        print(f"  ✓ Script exists: {TRIGGER_ENGINE_PATH}")
        checks.append(True)
    else:
        print(f"  ✗ Script missing: {TRIGGER_ENGINE_PATH}")
        checks.append(False)

    # Check Enrichment
    print("\nEnrichment Pipeline:")
    if ENRICHMENT_PATH.exists():
        print(f"  ✓ Script exists: {ENRICHMENT_PATH}")
        checks.append(True)
    else:
        print(f"  ✗ Script missing: {ENRICHMENT_PATH}")
        checks.append(False)

    # Check Communication Fabric
    print("\nCommunication Fabric:")
    if COMM_FABRIC_PATH.exists():
        print(f"  ✓ Script exists: {COMM_FABRIC_PATH}")
        # Check if history exists
        comm_history = INTELLIGENCE_DIR / "comms" / "state_history.jsonl"
        if comm_history.exists():
            import time as time_module
            age_hours = (time_module.time() - comm_history.stat().st_mtime) / 3600
            print(f"  ✓ State history exists ({age_hours:.1f}h old)")
        else:
            print("  ⚠ No state history yet (run --record first)")
        checks.append(True)
    else:
        print(f"  ✗ Script missing: {COMM_FABRIC_PATH}")
        checks.append(False)

    # Check state files
    print("\nState Files:")
    for name, path in [("Autopilot State", AUTOPILOT_STATE), ("Circuit Breakers", CIRCUIT_BREAKER_STATE)]:
        if path.exists():
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ⊘ {name}: Not yet created (OK)")

    # Summary
    print()
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    if passed == total:
        print(f"Health: GOOD ({passed}/{total} checks passed)")
    elif passed >= total * 0.6:
        print(f"Health: DEGRADED ({passed}/{total} checks passed)")
    else:
        print(f"Health: CRITICAL ({passed}/{total} checks passed)")
    print("=" * 60)

# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Autopilot - Self-Running Repository Orchestrator")
    parser.add_argument("command", nargs="?", default="status",
                       choices=["status", "run", "post-commit", "enable", "disable", "recover", "health"],
                       help="Command to run")
    parser.add_argument("--safe", action="store_true", help="Safe mode (extra checks, throttling)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview without executing")
    parser.add_argument("--force", action="store_true", help="Force execution, ignore throttle")

    args = parser.parse_args()

    try:
        if args.command == "status":
            cmd_status()
        elif args.command == "run":
            success = cmd_run(safe_mode=args.safe, dry_run=args.dry_run)
            sys.exit(0 if success else 1)
        elif args.command == "post-commit":
            success = cmd_post_commit(safe_mode=args.safe)
            sys.exit(0 if success else 1)
        elif args.command == "enable":
            cmd_enable()
        elif args.command == "disable":
            cmd_disable()
        elif args.command == "recover":
            cmd_recover()
        elif args.command == "health":
            cmd_health()
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)
    except Exception as e:
        log_error(f"Unhandled exception: {e}\n{traceback.format_exc()}")
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
