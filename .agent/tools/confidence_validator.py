#!/usr/bin/env python3
"""
Confidence Validator
====================
SMoC Role: Validator | Domain: Confidence

AI-powered task confidence assessment and validation.

Validated Architecture (Gemini + Perplexity 2026-01-23):
- Generates REPORTS, does not auto-update scores
- Uses task_assessment prompt from prompts.yaml
- 4D scoring: Factual, Alignment, Current, Onwards
- Human/Lead Agent reviews report → decides to update

Usage:
    ./confidence_validator.py TASK-126              # Assess single task
    ./confidence_validator.py TASK-126 --output report.json
    ./confidence_validator.py --all                 # Assess all pending tasks
    ./confidence_validator.py TASK-126 --verbose    # Show full context sent

Part of S6 (BARE subsystem).
See: .agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md
"""

import argparse
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# --- Auto-detect and use correct venv ---
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
TOOLS_VENV = REPO_ROOT / ".tools_venv"
VENV_PYTHON = TOOLS_VENV / "bin" / "python"


def _in_correct_venv():
    """Check if we're running from .tools_venv"""
    return TOOLS_VENV.as_posix() in sys.prefix


if not _in_correct_venv():
    if VENV_PYTHON.exists():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)
    else:
        print("=" * 60)
        print("ERROR: Required virtual environment not found!")
        print("=" * 60)
        print(f"Expected: {TOOLS_VENV}")
        print()
        print("To fix, run from PROJECT_elements root:")
        print("  python -m venv .tools_venv")
        print("  source .tools_venv/bin/activate")
        print("  pip install google-genai pyyaml ruamel.yaml")
        print("=" * 60)
        sys.exit(1)

# --- Now safe to import deps (we're in correct venv) ---
import yaml
from google import genai

# --- Config Paths ---
TASKS_DIR = REPO_ROOT / ".agent" / "registry" / "active"
ARCHIVE_DIR = REPO_ROOT / ".agent" / "registry" / "archive"
PROMPTS_CONFIG = REPO_ROOT / "context-management" / "config" / "prompts.yaml"
ANALYSIS_SETS_CONFIG = REPO_ROOT / "context-management" / "config" / "analysis_sets.yaml"
REPORTS_DIR = REPO_ROOT / ".agent" / "intelligence" / "confidence_reports"

# Category to analysis set mapping
CATEGORY_TO_SET = {
    "REPO-ORG": "brain",
    "PIPELINE": "pipeline",
    "BODY": "body",
    "BRAIN": "brain",
    "THEORY": "theory",
    "RESEARCH": "brain",
    "BARE": "agent_full",
    "DEFAULT": "brain",
}


def load_prompts():
    """Load prompts from prompts.yaml."""
    if not PROMPTS_CONFIG.exists():
        raise FileNotFoundError(f"Prompts config not found: {PROMPTS_CONFIG}")

    with open(PROMPTS_CONFIG) as f:
        data = yaml.safe_load(f)

    return data.get("analysis_prompts", {})


def load_analysis_sets():
    """Load analysis sets configuration."""
    if not ANALYSIS_SETS_CONFIG.exists():
        return {}

    with open(ANALYSIS_SETS_CONFIG) as f:
        return yaml.safe_load(f)


def load_task(task_id: str) -> tuple[Path, dict]:
    """Load a task file by ID."""
    # Normalize ID
    if not task_id.startswith("TASK-"):
        task_id = f"TASK-{task_id}"

    task_file = TASKS_DIR / f"{task_id}.yaml"
    if task_file.exists():
        with open(task_file) as f:
            return task_file, yaml.safe_load(f)

    # Check archive
    archive_file = ARCHIVE_DIR / f"{task_id}.yaml"
    if archive_file.exists():
        with open(archive_file) as f:
            return archive_file, yaml.safe_load(f)

    raise FileNotFoundError(f"Task {task_id} not found")


def get_pending_tasks() -> list[tuple[Path, dict]]:
    """Get all pending tasks that need boosting."""
    tasks = []
    for task_file in TASKS_DIR.glob("TASK-*.yaml"):
        with open(task_file) as f:
            data = yaml.safe_load(f)
            if not data:
                continue

            # Handle both schemas for status (new uses uppercase)
            status = data.get("status", "pending").lower()
            if status in ("complete", "archived", "deferred"):
                continue

            # Handle both schemas for score
            confidence = data.get("confidence", {})
            if confidence:
                scores = [confidence.get(k, 0) for k in ['factual', 'alignment', 'current', 'onwards'] if confidence.get(k)]
                score = min(scores) if scores else 0
            else:
                score = data.get("score", 0)

            risk = data.get("risk", "A")
            threshold = {"A": 85, "A+": 95, "A++": 99}.get(risk, 85)
            if score < threshold:
                tasks.append((task_file, data))
    return tasks


def load_context_for_task(task: dict, analysis_sets: dict) -> str:
    """Load relevant code context based on task category."""
    category = task.get("category", "DEFAULT").upper()
    set_name = CATEGORY_TO_SET.get(category, CATEGORY_TO_SET["DEFAULT"])

    # Get the set config (structure is analysis_sets: { set_name: {...} })
    all_sets = analysis_sets.get("analysis_sets", {})
    set_config = all_sets.get(set_name, {})
    if not set_config:
        return f"[No analysis set found for category: {category}]"

    # Collect files from set using glob patterns
    patterns = set_config.get("patterns", [])
    context_parts = []
    files_loaded = 0
    max_files = 10  # Limit to avoid token overflow

    for pattern in patterns:
        if files_loaded >= max_files:
            break
        # Expand glob pattern
        for file_path in REPO_ROOT.glob(pattern):
            if files_loaded >= max_files:
                break
            if file_path.is_file():
                try:
                    rel_path = file_path.relative_to(REPO_ROOT)
                    content = file_path.read_text()
                    # Truncate large files
                    if len(content) > 5000:
                        content = content[:5000] + "\n... [truncated]"
                    context_parts.append(f"=== {rel_path} ===\n{content}")
                    files_loaded += 1
                except Exception as e:
                    context_parts.append(f"=== {file_path.name} ===\n[Error reading: {e}]")

    if not context_parts:
        return f"[No files loaded for set: {set_name}]"

    return "\n\n".join(context_parts)


def get_gemini_client():
    """Initialize Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        # Try doppler
        try:
            import subprocess
            result = subprocess.run(
                ["doppler", "secrets", "get", "GEMINI_API_KEY", "--plain"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                api_key = result.stdout.strip()
        except Exception:
            pass

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Set via environment or Doppler:\n"
            "  export GEMINI_API_KEY='your-key'\n"
            "  # or: doppler secrets set GEMINI_API_KEY='your-key'"
        )

    return genai.Client(api_key=api_key)


def assess_task(client, task_id: str, task: dict, prompts: dict, analysis_sets: dict, verbose: bool = False) -> dict:
    """Run AI assessment on a task and return report."""

    # Normalize task ID
    raw_id = str(task.get('id', '0'))
    normalized_tid = raw_id if raw_id.startswith('TASK-') else f"TASK-{raw_id}"

    # Get the prompt template
    prompt_template = prompts.get("task_assessment")
    if not prompt_template:
        raise ValueError("task_assessment prompt not found in prompts.yaml")

    # Load code context
    code_context = load_context_for_task(task, analysis_sets)

    # Handle both schemas
    task_subject = task.get("title") or task.get("subject") or "Untitled"

    confidence = task.get("confidence", {})
    if confidence:
        scores = [confidence.get(k, 0) for k in ['factual', 'alignment', 'current', 'onwards'] if confidence.get(k)]
        current_score = min(scores) if scores else 0
    else:
        current_score = task.get("score", 0)

    # Format the prompt
    formatted_prompt = prompt_template.format(
        task_id=normalized_tid,
        task_subject=task_subject,
        task_description=task.get("description", "No description"),
        current_score=current_score,
        code_context=code_context
    )

    if verbose:
        print("\n" + "=" * 60)
        print("PROMPT SENT TO GEMINI:")
        print("=" * 60)
        print(formatted_prompt[:2000] + "..." if len(formatted_prompt) > 2000 else formatted_prompt)
        print("=" * 60 + "\n")

    # Call Gemini
    print(f"  Assessing {normalized_tid}...", end=" ", flush=True)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=formatted_prompt
        )

        # Parse JSON response
        response_text = response.text

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        assessment = json.loads(response_text)
        print("OK")

        return {
            "task_id": normalized_tid,
            "assessed_at": datetime.now(timezone.utc).isoformat(),
            "current_score": task.get("score", 0),
            "assessment": assessment,
            "raw_response": response.text
        }

    except json.JSONDecodeError as e:
        print(f"PARSE ERROR: {e}")
        return {
            "task_id": normalized_tid,
            "assessed_at": datetime.now(timezone.utc).isoformat(),
            "error": f"JSON parse error: {e}",
            "raw_response": response.text if 'response' in dir() else None
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return {
            "task_id": normalized_tid,
            "assessed_at": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


def print_report(report: dict):
    """Pretty-print an assessment report."""
    print("\n" + "=" * 60)
    print(f"CONFIDENCE REPORT: {report['task_id']}")
    print("=" * 60)
    print(f"Assessed: {report['assessed_at']}")
    print(f"Current Score: {report.get('current_score', '?')}%")

    if "error" in report:
        print(f"\nERROR: {report['error']}")
        if report.get("raw_response"):
            print(f"\nRaw Response:\n{report['raw_response'][:500]}...")
        return

    assessment = report.get("assessment", {})

    # Dimensions
    dims = assessment.get("dimensions", {})
    if dims:
        print("\n4D SCORES:")
        for dim_name, dim_data in dims.items():
            score = dim_data.get("score", "?")
            print(f"  {dim_name.upper():12} [{score:>3}%] {dim_data.get('evidence', '')[:50]}")
            if dim_data.get("concerns"):
                print(f"               ^ {dim_data['concerns'][:50]}")

    # Composite
    composite = assessment.get("composite_score")
    recommendation = assessment.get("recommendation", "?")
    if composite:
        emoji = {"READY": "🟢", "NEEDS_WORK": "🟡", "REJECT": "🔴"}.get(recommendation, "⚪")
        print(f"\nCOMPOSITE: {composite}% → {emoji} {recommendation}")

    # Summary
    summary = assessment.get("summary")
    if summary:
        print(f"\nSUMMARY: {summary}")

    # Actions
    actions = assessment.get("suggested_actions", [])
    if actions:
        print("\nSUGGESTED ACTIONS:")
        for action in actions:
            print(f"  - {action}")

    print("=" * 60)


def save_report(report: dict, output_path: Path = None):
    """Save report to file."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        task_id = report["task_id"].replace("TASK-", "")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = REPORTS_DIR / f"{timestamp}_TASK-{task_id}_confidence.json"

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="AI-powered task confidence assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("task_id", nargs="?", help="Task ID (e.g., TASK-126 or 126)")
    parser.add_argument("--all", action="store_true", help="Assess all pending tasks below threshold")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full prompt sent to AI")
    parser.add_argument("--no-save", action="store_true", help="Don't save report to file")

    args = parser.parse_args()

    if not args.task_id and not args.all:
        parser.print_help()
        print("\nExample: ./boost_confidence.py TASK-126")
        return

    # Load configs
    prompts = load_prompts()
    analysis_sets = load_analysis_sets()

    # Initialize client
    try:
        client = get_gemini_client()
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    reports = []

    if args.all:
        # Assess all pending tasks
        pending = get_pending_tasks()
        if not pending:
            print("No pending tasks below threshold found.")
            return

        print(f"\nAssessing {len(pending)} pending tasks...")
        for task_path, task_data in pending:
            report = assess_task(client, f"TASK-{task_data['id']}", task_data, prompts, analysis_sets, args.verbose)
            reports.append(report)
            print_report(report)
    else:
        # Assess single task
        try:
            task_path, task_data = load_task(args.task_id)
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            return

        report = assess_task(client, args.task_id, task_data, prompts, analysis_sets, args.verbose)
        reports.append(report)
        print_report(report)

    # Save reports
    if not args.no_save:
        if len(reports) == 1:
            output_path = Path(args.output) if args.output else None
            save_report(reports[0], output_path)
        else:
            # Save combined report for --all
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            combined_path = REPORTS_DIR / f"{timestamp}_batch_confidence.json"
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            with open(combined_path, 'w') as f:
                json.dump(reports, f, indent=2)
            print(f"\nBatch report saved: {combined_path}")

    # Summary for --all
    if args.all and reports:
        print("\n" + "=" * 60)
        print("BATCH SUMMARY")
        print("=" * 60)
        ready = sum(1 for r in reports if r.get("assessment", {}).get("recommendation") == "READY")
        needs_work = sum(1 for r in reports if r.get("assessment", {}).get("recommendation") == "NEEDS_WORK")
        errors = sum(1 for r in reports if "error" in r)
        print(f"  READY: {ready} | NEEDS_WORK: {needs_work} | ERRORS: {errors}")


if __name__ == "__main__":
    main()
