#!/usr/bin/env python3
"""
Laboratory Facade (Scientist)

The stable interface between Wave (Agent) and Particle (Scientist).

Goal:
- ONE entry point for all "measurement" experiments
- Internals can evolve (scripts -> modules) without changing Agent code
- Both Python API and CLI supported

Usage:
    # Python API
    from laboratory import run_experiment, ExperimentRequest
    result = run_experiment(ExperimentRequest(...))

    # CLI
    python laboratory.py run --unified-analysis path/to/unified_analysis.json

Design:
- Experiments executed via command templates (no script refactoring required today)
- Output always: experiment_result.json with pointers to artifacts
- Templates support placeholders: {python} {repo_root} {unified_analysis} {out_dir} etc.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import shlex
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


# =============================================================================
# TYPES
# =============================================================================

@dataclass
class ExperimentRequest:
    """Request to run a Laboratory experiment.

    Provide EITHER:
    - unified_analysis_path (if you already have Collider output)
    - repo_path + collider_cmd_template (to generate it)

    Optional:
    - hypothesis: Label for hypothesis evaluation
    - hypothesis_cmd_template: Command to evaluate hypothesis
    - coverage_cmd_template: Command to compute coverage metrics
    """
    repo_path: Optional[Path] = None
    unified_analysis_path: Optional[Path] = None
    hypothesis: Optional[str] = None
    out_dir: Path = field(default_factory=lambda: Path(".laboratory_runs") / "latest")
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    # Command templates (optional)
    collider_cmd_template: Optional[str] = None
    hypothesis_cmd_template: Optional[str] = None
    coverage_cmd_template: Optional[str] = None

    # Execution settings
    timeout_sec: int = 60 * 20  # 20 minutes default


@dataclass
class ExperimentResult:
    """Result returned from Laboratory experiment."""
    run_id: str
    created_at_utc: str
    ok: bool
    confirmed: Optional[bool]  # Hypothesis verdict (if evaluated)
    summary: Dict[str, Any]
    artifacts: Dict[str, str]  # name -> filepath
    logs: Dict[str, str]       # step -> log filepath
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


# =============================================================================
# HELPERS
# =============================================================================

def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _ensure_dir(path.parent)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_cmd_template(template: str, ctx: Mapping[str, str]) -> List[str]:
    """Parse command template with placeholder substitution.

    Supports:
    - JSON list: ["python", "script.py", "--arg", "{value}"]
    - Shell string: python script.py --arg "{value}"
    """
    substituted = template.format(**ctx)
    s = substituted.strip()

    # JSON list format
    if s.startswith("[") and s.endswith("]"):
        arr = json.loads(s)
        if not isinstance(arr, list) or not all(isinstance(x, str) for x in arr):
            raise ValueError("Command template JSON must be a list[str].")
        return arr

    # Shell string format
    return shlex.split(substituted)


def _run_cmd(
    argv: List[str],
    *,
    cwd: Optional[Path],
    timeout_sec: int,
    log_path: Path
) -> int:
    """Run command, capture output to log file, return exit code."""
    _ensure_dir(log_path.parent)

    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"$ {' '.join(shlex.quote(x) for x in argv)}\n\n")
        f.flush()
        try:
            proc = subprocess.run(
                argv,
                cwd=str(cwd) if cwd else None,
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout_sec,
                check=False,
                env=os.environ.copy(),
            )
            return int(proc.returncode)
        except subprocess.TimeoutExpired:
            f.write(f"\n[LABORATORY] TIMEOUT after {timeout_sec}s\n")
            return 124


def _infer_confirmed(payload: Any) -> Optional[bool]:
    """Best-effort extraction of hypothesis verdict from unknown JSON schema."""
    if isinstance(payload, dict):
        # Direct "confirmed" field
        if "confirmed" in payload and isinstance(payload["confirmed"], bool):
            return payload["confirmed"]

        # String verdict
        verdict = payload.get("verdict")
        if isinstance(verdict, str):
            v = verdict.strip().lower()
            if v in {"confirmed", "true", "pass", "passed", "yes"}:
                return True
            if v in {"rejected", "false", "fail", "failed", "no"}:
                return False

        # Nested search
        for key in ("result", "summary", "hypothesis", "evaluation"):
            sub = payload.get(key)
            c = _infer_confirmed(sub)
            if c is not None:
                return c

    return None


def _find_repo_root() -> Path:
    """Find standard-model-of-code repo root from this file location."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "docs").exists() and (parent / "tools").exists() and (parent / "src").exists():
            return parent
    # Fallback: assume tools/research/laboratory.py structure
    return here.parents[2]


# =============================================================================
# CORE FACADE
# =============================================================================

def run_experiment(req: ExperimentRequest) -> ExperimentResult:
    """Execute a Laboratory experiment.

    This is THE stable interface. Everything else is implementation detail.
    """
    out_dir = req.out_dir / req.run_id
    _ensure_dir(out_dir)

    logs_dir = out_dir / "logs"
    artifacts_dir = out_dir / "artifacts"
    _ensure_dir(logs_dir)
    _ensure_dir(artifacts_dir)

    errors: List[str] = []
    artifacts: Dict[str, str] = {}
    logs: Dict[str, str] = {}
    confirmed: Optional[bool] = None

    # Build template context
    repo_root = _find_repo_root()
    ctx: Dict[str, str] = {
        "python": sys.executable,
        "repo_root": str(repo_root),
        "out_dir": str(out_dir),
        "artifacts_dir": str(artifacts_dir),
        "logs_dir": str(logs_dir),
        "run_id": req.run_id,
        "hypothesis": req.hypothesis or "",
        "repo_path": str(req.repo_path) if req.repo_path else "",
    }

    # Step 0: Acquire unified_analysis.json
    unified_path: Optional[Path] = None
    if req.unified_analysis_path is not None:
        unified_path = req.unified_analysis_path.expanduser().resolve()
        if not unified_path.exists():
            errors.append(f"unified_analysis_path does not exist: {unified_path}")
            unified_path = None

    if unified_path is None and req.repo_path is not None:
        if not req.collider_cmd_template:
            errors.append(
                "repo_path provided but collider_cmd_template is missing. "
                "Provide --collider-cmd-template or set LAB_COLLIDER_CMD_TEMPLATE."
            )
        else:
            unified_path = artifacts_dir / "unified_analysis.json"
            ctx["unified_analysis"] = str(unified_path)

            log_path = logs_dir / "collider.log"
            logs["collider"] = str(log_path)

            try:
                argv = _parse_cmd_template(req.collider_cmd_template, ctx)
                code = _run_cmd(argv, cwd=req.repo_path, timeout_sec=req.timeout_sec, log_path=log_path)
                if code != 0:
                    errors.append(f"Collider command failed (exit {code}). See {log_path}")
                    unified_path = None
                elif not unified_path.exists():
                    errors.append(f"Collider ran but did not produce {unified_path}")
                    unified_path = None
                else:
                    artifacts["unified_analysis"] = str(unified_path)
            except Exception as e:
                errors.append(f"Collider command failed: {e}")
                unified_path = None

    if unified_path is None and req.unified_analysis_path is None and req.repo_path is None:
        errors.append("No unified_analysis_path and no repo_path provided.")

    if unified_path is not None:
        artifacts["unified_analysis"] = str(unified_path)
        ctx["unified_analysis"] = str(unified_path)

    # Step 1: Hypothesis evaluation (optional)
    if req.hypothesis_cmd_template and unified_path is not None and not errors:
        hyp_out = artifacts_dir / "hypothesis_result.json"
        ctx["hypothesis_out"] = str(hyp_out)

        log_path = logs_dir / "hypothesis.log"
        logs["hypothesis"] = str(log_path)

        try:
            argv = _parse_cmd_template(req.hypothesis_cmd_template, ctx)
            code = _run_cmd(argv, cwd=repo_root, timeout_sec=req.timeout_sec, log_path=log_path)
            if code != 0:
                errors.append(f"Hypothesis command failed (exit {code}). See {log_path}")
            elif hyp_out.exists():
                artifacts["hypothesis_result"] = str(hyp_out)
                try:
                    payload = _read_json(hyp_out)
                    confirmed = _infer_confirmed(payload)
                except Exception as e:
                    errors.append(f"Could not parse hypothesis output: {e}")
        except Exception as e:
            errors.append(f"Hypothesis command failed: {e}")

    # Step 2: Coverage metrics (optional)
    if req.coverage_cmd_template and unified_path is not None and not errors:
        cov_out = artifacts_dir / "coverage_result.json"
        ctx["coverage_out"] = str(cov_out)

        log_path = logs_dir / "coverage.log"
        logs["coverage"] = str(log_path)

        try:
            argv = _parse_cmd_template(req.coverage_cmd_template, ctx)
            code = _run_cmd(argv, cwd=repo_root, timeout_sec=req.timeout_sec, log_path=log_path)
            if code != 0:
                errors.append(f"Coverage command failed (exit {code}). See {log_path}")
            elif cov_out.exists():
                artifacts["coverage_result"] = str(cov_out)
        except Exception as e:
            errors.append(f"Coverage command failed: {e}")

    # Build result
    ok = len(errors) == 0

    summary: Dict[str, Any] = {
        "hypothesis": req.hypothesis,
        "repo_path": str(req.repo_path) if req.repo_path else None,
        "unified_analysis_path": str(unified_path) if unified_path else None,
    }

    result = ExperimentResult(
        run_id=req.run_id,
        created_at_utc=_utc_now_iso(),
        ok=ok,
        confirmed=confirmed,
        summary=summary,
        artifacts=artifacts,
        logs=logs,
        errors=errors,
    )

    # Persist result
    result_path = out_dir / "experiment_result.json"
    _write_json(result_path, result.to_dict())
    result.artifacts["experiment_result"] = str(result_path)

    return result


# =============================================================================
# CLI
# =============================================================================

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="laboratory.py",
        description="Laboratory Facade - Scientist side of the Wave-Particle bridge."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run a laboratory experiment.")
    run.add_argument("--repo", default=None, help="Target repo path (optional if --unified-analysis).")
    run.add_argument("--unified-analysis", dest="unified_analysis", default=None,
                     help="Path to existing unified_analysis.json.")
    run.add_argument("--hypothesis", default=None, help="Hypothesis id/label.")
    run.add_argument("--out-dir", dest="out_dir", default=".laboratory_runs",
                     help="Output directory root.")
    run.add_argument("--timeout-sec", dest="timeout_sec", type=int, default=60 * 20)

    # Command templates
    run.add_argument(
        "--collider-cmd-template",
        dest="collider_cmd_template",
        default=os.environ.get("LAB_COLLIDER_CMD_TEMPLATE"),
        help="Command template to produce unified_analysis.json."
    )
    run.add_argument(
        "--hypothesis-cmd-template",
        dest="hypothesis_cmd_template",
        default=os.environ.get("LAB_HYPOTHESIS_CMD_TEMPLATE"),
        help="Command template to evaluate hypothesis."
    )
    run.add_argument(
        "--coverage-cmd-template",
        dest="coverage_cmd_template",
        default=os.environ.get("LAB_COVERAGE_CMD_TEMPLATE"),
        help="Command template to compute coverage metrics."
    )

    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.cmd == "run":
        req = ExperimentRequest(
            repo_path=Path(args.repo).expanduser().resolve() if args.repo else None,
            unified_analysis_path=Path(args.unified_analysis).expanduser().resolve() if args.unified_analysis else None,
            hypothesis=args.hypothesis,
            out_dir=Path(args.out_dir).expanduser().resolve(),
            collider_cmd_template=args.collider_cmd_template,
            hypothesis_cmd_template=args.hypothesis_cmd_template,
            coverage_cmd_template=args.coverage_cmd_template,
            timeout_sec=args.timeout_sec,
        )
        result = run_experiment(req)

        # Print canonical artifact path for Agent to parse
        print(result.artifacts.get("experiment_result", ""))
        return 0 if result.ok else 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
