#!/usr/bin/env python3
"""
Drift Guard
===========
SMoC Role: Guard | Domain: Drift

A 24/7 background service that continuously monitors the codebase,
detects semantic drift, and validates against Antimatter Laws.

Features:
- File system watching (triggers on code changes)
- Scheduled deep audits (configurable interval)
- Throttling to prevent audit storms
- JSON audit log output to GCS-syncable directory
- Graceful shutdown handling

Usage:
    # Run as foreground daemon
    python3 drift_guard.py

    # Run single pass (for cron/launchd)
    python3 drift_guard.py --once

    # Custom interval
    python3 drift_guard.py --interval 3600

    # Debug mode (verbose)
    python3 drift_guard.py --debug
"""
import sys
import os
import time
import signal
import json
import argparse
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
VENV_PYTHON = PROJECT_ROOT / ".tools_venv/bin/python"
ANALYZE_SCRIPT = PROJECT_ROOT / "context-management/tools/ai/analyze.py"
INTELLIGENCE_DIR = PROJECT_ROOT / "context-management/intelligence"
LOG_DIR = INTELLIGENCE_DIR / "logs"
STATE_FILE = INTELLIGENCE_DIR / "drift_guard_state.json"

# Watchlist: files/dirs that trigger audit on change
WATCH_PATHS = [
    PROJECT_ROOT / "context-management/config/semantic_models.yaml",
    PROJECT_ROOT / "standard-model-of-code/src/core",
    PROJECT_ROOT / "standard-model-of-code/docs",
]

# Throttle: minimum seconds between audits
THROTTLE_SECONDS = 300  # 5 minutes

# Default deep audit interval
DEFAULT_INTERVAL = 3600  # 1 hour

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class DaemonState:
    """Persistent state for the daemon."""

    def __init__(self):
        self.last_audit_time: float = 0
        self.last_file_hashes: dict = {}
        self.audit_count: int = 0
        self.violation_count: int = 0
        self.load()

    def load(self):
        """Load state from disk."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.last_audit_time = data.get('last_audit_time', 0)
                    self.last_file_hashes = data.get('last_file_hashes', {})
                    self.audit_count = data.get('audit_count', 0)
                    self.violation_count = data.get('violation_count', 0)
            except Exception:
                pass

    def save(self):
        """Persist state to disk."""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        INTELLIGENCE_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump({
                'last_audit_time': self.last_audit_time,
                'last_file_hashes': self.last_file_hashes,
                'audit_count': self.audit_count,
                'violation_count': self.violation_count,
                'updated': datetime.now().isoformat()
            }, f, indent=2)

# ============================================================================
# CORE DAEMON LOGIC
# ============================================================================

class DriftGuard:
    """The Drift Guard - detects semantic drift between docs and implementation."""

    def __init__(self, interval: int = DEFAULT_INTERVAL, debug: bool = False):
        self.interval = interval
        self.debug = debug
        self.running = True
        self.state = DaemonState()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.log("🛑 Shutdown signal received. Saving state...")
        self.state.save()
        self.running = False

    def log(self, msg: str, level: str = "INFO"):
        """Log with timestamp."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌", "OK": "✅"}.get(level, "")
        print(f"[{ts}] {prefix} {msg}")

        if self.debug:
            # Also write to log file
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            with open(LOG_DIR / "drift_guard.log", 'a') as f:
                f.write(f"[{ts}] [{level}] {msg}\n")

    def _hash_file(self, path: Path) -> str:
        """Get hash of file for change detection."""
        try:
            return hashlib.md5(path.read_bytes()).hexdigest()[:16]
        except Exception:
            return ""

    def _hash_dir(self, path: Path) -> str:
        """Get composite hash of directory."""
        hashes = []
        try:
            for f in sorted(path.rglob("*.py")):
                hashes.append(self._hash_file(f))
            for f in sorted(path.rglob("*.ts")):
                hashes.append(self._hash_file(f))
            for f in sorted(path.rglob("*.yaml")):
                hashes.append(self._hash_file(f))
        except Exception:
            pass
        return hashlib.md5("".join(hashes).encode()).hexdigest()[:16]

    def check_for_changes(self) -> bool:
        """Check if any watched paths have changed."""
        changed = False
        new_hashes = {}

        for wp in WATCH_PATHS:
            if wp.is_file():
                h = self._hash_file(wp)
            elif wp.is_dir():
                h = self._hash_dir(wp)
            else:
                continue

            key = str(wp.relative_to(PROJECT_ROOT))
            new_hashes[key] = h

            if key in self.state.last_file_hashes:
                if self.state.last_file_hashes[key] != h:
                    if self.debug:
                        self.log(f"Change detected: {key}", "INFO")
                    changed = True

        self.state.last_file_hashes = new_hashes
        return changed

    def is_throttled(self) -> bool:
        """Check if we're within the throttle window."""
        return (time.time() - self.state.last_audit_time) < THROTTLE_SECONDS

    def run_audit(self, trigger: str = "scheduled") -> Optional[dict]:
        """Run the Socratic audit via analyze.py."""
        self.log(f"🧠 Starting Socratic Audit (trigger: {trigger})")

        # Determine python interpreter
        python_cmd = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

        try:
            result = subprocess.run(
                [python_cmd, str(ANALYZE_SCRIPT), "--verify", "pipeline"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(PROJECT_ROOT)
            )

            self.state.audit_count += 1
            self.state.last_audit_time = time.time()

            if result.returncode == 0:
                self.log("Audit completed successfully", "OK")
            else:
                self.log(f"Audit returned non-zero: {result.returncode}", "WARN")

            # Parse output for violations (simplified)
            violations = result.stdout.count("VIOLATION") + result.stdout.count("violation")
            if violations > 0:
                self.state.violation_count += violations
                self.log(f"Found {violations} potential violations", "WARN")

            self.state.save()

            return {
                "trigger": trigger,
                "timestamp": datetime.now().isoformat(),
                "duration": "completed",
                "violations": violations,
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            self.log("Audit timed out after 5 minutes", "ERROR")
            return None
        except Exception as e:
            self.log(f"Audit failed: {e}", "ERROR")
            return None

    def run_once(self):
        """Run a single audit pass."""
        self.log("=" * 50)
        self.log("🛡️  DRIFT GUARD - Single Pass")
        self.log("=" * 50)
        self.run_audit(trigger="manual")
        self.state.save()

    def run_forever(self):
        """Main daemon loop."""
        self.log("=" * 50)
        self.log("🛡️  DRIFT GUARD ACTIVATED")
        self.log(f"   Interval: {self.interval}s | Throttle: {THROTTLE_SECONDS}s")
        self.log(f"   Watching: {len(WATCH_PATHS)} paths")
        self.log("=" * 50)

        last_deep_audit = 0

        while self.running:
            now = time.time()

            # Check for file changes
            if self.check_for_changes():
                if not self.is_throttled():
                    self.run_audit(trigger="file_change")
                else:
                    self.log("Change detected but throttled", "INFO")

            # Time for scheduled deep audit?
            if (now - last_deep_audit) >= self.interval:
                if not self.is_throttled():
                    self.run_audit(trigger="scheduled")
                    last_deep_audit = now

            # Sleep before next check (30 second granularity)
            time.sleep(30)

        self.log("Daemon stopped gracefully", "OK")

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Drift Guard - detects semantic drift",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--once", action="store_true",
                        help="Run single audit and exit")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help=f"Deep audit interval in seconds (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")

    args = parser.parse_args()

    daemon = DriftGuard(interval=args.interval, debug=args.debug)

    if args.once:
        daemon.run_once()
    else:
        daemon.run_forever()

if __name__ == "__main__":
    main()
