#!/usr/bin/env python3
"""
Laboratory Bridge (Agent-side)

Wave (Agent) -> Particle (Scientist)

This module:
- Locates standard-model-of-code
- Calls its Laboratory facade (tools/research/laboratory.py)
- Returns parsed ExperimentResult

Usage:
    # Python API
    from laboratory_bridge import run_laboratory
    result = run_laboratory(unified_analysis=Path("..."))

    # CLI
    python laboratory_bridge.py --unified-analysis path/to/unified_analysis.json

Design:
- Agent never imports Scientist internals directly
- Single stable interface: run_laboratory() -> dict
- Transport is subprocess (can be swapped for imports later)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def find_smc_root(start: Optional[Path] = None) -> Path:
    """Find standard-model-of-code directory.

    Search order:
    1. SMC_ROOT environment variable
    2. Walk upwards from start (or this file) looking for sibling directory
    """
    env = os.environ.get("SMC_ROOT")
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"SMC_ROOT set but does not exist: {p}")

    here = (start or Path(__file__)).resolve()

    # Check for monorepo structure (PROJECT_elements/standard-model-of-code)
    for parent in here.parents:
        candidate = parent / "standard-model-of-code"
        lab_script = candidate / "tools" / "research" / "laboratory.py"
        if candidate.exists() and lab_script.exists():
            return candidate

    raise FileNotFoundError(
        "Could not locate standard-model-of-code. "
        "Set env SMC_ROOT=/path/to/standard-model-of-code "
        "or ensure repos are siblings in the monorepo."
    )


def run_laboratory(
    *,
    repo: Optional[Path] = None,
    unified_analysis: Optional[Path] = None,
    hypothesis: Optional[str] = None,
    out_dir: Optional[Path] = None,
    collider_cmd_template: Optional[str] = None,
    hypothesis_cmd_template: Optional[str] = None,
    coverage_cmd_template: Optional[str] = None,
    timeout_sec: int = 60 * 20,
) -> Dict[str, Any]:
    """Invoke the Laboratory facade and return parsed result.

    This is THE stable interface for Agent -> Scientist communication.

    Args:
        repo: Target repository path (optional if unified_analysis provided)
        unified_analysis: Path to existing unified_analysis.json
        hypothesis: Hypothesis label/id to evaluate
        out_dir: Output directory for experiment artifacts
        collider_cmd_template: Template for Collider invocation
        hypothesis_cmd_template: Template for hypothesis evaluation
        coverage_cmd_template: Template for coverage computation
        timeout_sec: Maximum execution time

    Returns:
        Parsed experiment_result.json as dict

    Raises:
        FileNotFoundError: If standard-model-of-code cannot be located
        RuntimeError: If Laboratory invocation fails
    """
    smc_root = find_smc_root()
    lab_script = smc_root / "tools" / "research" / "laboratory.py"

    if not lab_script.exists():
        raise FileNotFoundError(f"Laboratory script not found: {lab_script}")

    # Build command
    argv = [
        sys.executable,
        str(lab_script),
        "run",
        "--timeout-sec", str(timeout_sec),
    ]

    if out_dir is not None:
        argv += ["--out-dir", str(out_dir)]
    else:
        argv += ["--out-dir", ".laboratory_runs_agent"]

    if repo is not None:
        argv += ["--repo", str(repo)]

    if unified_analysis is not None:
        argv += ["--unified-analysis", str(unified_analysis)]

    if hypothesis:
        argv += ["--hypothesis", hypothesis]

    if collider_cmd_template:
        argv += ["--collider-cmd-template", collider_cmd_template]

    if hypothesis_cmd_template:
        argv += ["--hypothesis-cmd-template", hypothesis_cmd_template]

    if coverage_cmd_template:
        argv += ["--coverage-cmd-template", coverage_cmd_template]

    # Execute
    proc = subprocess.run(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()

    # Laboratory returns 0 (ok) or 2 (errors but structured result)
    if proc.returncode not in (0, 2):
        raise RuntimeError(
            f"Laboratory invocation failed.\n"
            f"cmd: {' '.join(argv)}\n"
            f"exit: {proc.returncode}\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}"
        )

    if not stdout:
        raise RuntimeError(f"Laboratory returned no result path.\nstderr:\n{stderr}")

    result_path = Path(stdout).expanduser().resolve()
    if not result_path.exists():
        raise FileNotFoundError(f"Laboratory result path does not exist: {result_path}")

    # Parse and augment result
    payload = json.loads(result_path.read_text(encoding="utf-8"))

    # Add bridge metadata (transport-level info, doesn't change Scientist output)
    payload["_bridge"] = {
        "result_path": str(result_path),
        "smc_root": str(smc_root),
    }
    if stderr:
        payload["_bridge"]["stderr"] = stderr

    return payload


def measure_coverage(unified_analysis: Path) -> Dict[str, Any]:
    """Convenience: Run coverage analysis on existing unified_analysis.json.

    Returns coverage metrics or raises on failure.
    """
    # Use default coverage template that maps to existing script
    coverage_template = (
        "{python} {repo_root}/tools/research/atom_coverage.py "
        "{unified_analysis} --output {coverage_out}"
    )

    result = run_laboratory(
        unified_analysis=unified_analysis,
        coverage_cmd_template=coverage_template,
    )

    if not result.get("ok"):
        raise RuntimeError(f"Coverage analysis failed: {result.get('errors')}")

    # Try to load coverage metrics
    coverage_path = result.get("artifacts", {}).get("coverage_result")
    if coverage_path and Path(coverage_path).exists():
        return json.loads(Path(coverage_path).read_text(encoding="utf-8"))

    return result


def evaluate_hypothesis(
    unified_analysis: Path,
    hypothesis: str,
) -> Dict[str, Any]:
    """Convenience: Evaluate a specific hypothesis.

    Returns evaluation result including 'confirmed' verdict.
    """
    hypothesis_template = (
        "{python} {repo_root}/tools/research/evaluate_hypotheses.py "
        "{unified_analysis} --output {hypothesis_out}"
    )

    result = run_laboratory(
        unified_analysis=unified_analysis,
        hypothesis=hypothesis,
        hypothesis_cmd_template=hypothesis_template,
    )

    return result


# =============================================================================
# CLI
# =============================================================================

def main() -> int:
    p = argparse.ArgumentParser(
        prog="laboratory_bridge.py",
        description="Agent-side bridge to the Laboratory (Scientist)."
    )
    p.add_argument("--repo", default=None, help="Target repository path.")
    p.add_argument("--unified-analysis", default=None, help="Path to unified_analysis.json.")
    p.add_argument("--hypothesis", default=None, help="Hypothesis to evaluate.")
    p.add_argument("--out-dir", default=".laboratory_runs_agent", help="Output directory.")
    p.add_argument("--timeout-sec", type=int, default=60 * 20)

    # Optional templates (pass-through to Laboratory)
    p.add_argument("--collider-cmd-template", default=None)
    p.add_argument("--hypothesis-cmd-template", default=None)
    p.add_argument("--coverage-cmd-template", default=None)

    args = p.parse_args()

    try:
        payload = run_laboratory(
            repo=Path(args.repo).expanduser().resolve() if args.repo else None,
            unified_analysis=Path(args.unified_analysis).expanduser().resolve() if args.unified_analysis else None,
            hypothesis=args.hypothesis,
            out_dir=Path(args.out_dir).expanduser().resolve(),
            collider_cmd_template=args.collider_cmd_template,
            hypothesis_cmd_template=args.hypothesis_cmd_template,
            coverage_cmd_template=args.coverage_cmd_template,
            timeout_sec=args.timeout_sec,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    except Exception as e:
        print(json.dumps({"error": str(e), "ok": False}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
