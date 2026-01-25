#!/usr/bin/env python3
"""
Fact Loader
===========
SMoC Role: Loader | Domain: Fact

Loads and validates facts about the repository.
Extracts ground truth metrics from codebase analysis.

Part of S6 (BARE subsystem).
See: .agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Repository root (relative to this script)
REPO_ROOT = Path(__file__).parent.parent.parent
INTELLIGENCE_DIR = REPO_ROOT / ".agent" / "intelligence" / "truths"
COLLIDER_OUTPUT = REPO_ROOT / ".collider" / "unified_analysis.json"


def count_files_by_extension(root: Path, extensions: dict[str, list[str]]) -> dict[str, int]:
    """Count files by extension category."""
    counts = {category: 0 for category in extensions}

    # Directories to skip
    skip_dirs = {
        "node_modules", "__pycache__", "venv", ".venv", "dist", "build",
        "archive", ".git", ".collider", "artifacts", "benchmarks"
    }

    for category, exts in extensions.items():
        for ext in exts:
            pattern = f"**/*{ext}"
            # Exclude common non-source directories
            files = [
                f for f in root.glob(pattern)
                if not any(
                    part.startswith(".") or part in skip_dirs
                    for part in f.parts
                )
            ]
            counts[category] += len(files)

    return counts


def count_lines_of_code(root: Path) -> int:
    """Count total lines of code (approximation)."""
    extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".yaml", ".yml"]
    # Exclude .json - often large data files
    total_lines = 0

    # Directories to skip
    skip_dirs = {
        "node_modules", "__pycache__", "venv", ".venv", "dist", "build",
        "archive", ".git", ".collider", "artifacts", "benchmarks"
    }

    for ext in extensions:
        for filepath in root.glob(f"**/*{ext}"):
            # Skip if any part starts with . or is in skip list
            if any(
                part.startswith(".") or part in skip_dirs
                for part in filepath.parts
            ):
                continue
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    total_lines += sum(1 for _ in f)
            except (OSError, IOError):
                pass

    return total_lines


def load_collider_output() -> dict | None:
    """Load Collider unified_analysis.json if available."""
    if COLLIDER_OUTPUT.exists():
        try:
            with open(COLLIDER_OUTPUT, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def extract_atom_counts(collider_data: dict) -> dict:
    """Extract atom counts from Collider output."""
    nodes = collider_data.get("nodes", [])

    # Count by atom tier
    tier_counts = {"tier0_core": 0, "tier1_stdlib": 0, "tier2_ecosystem": 0, "unclassified": 0}

    for node in nodes:
        atom = node.get("atom", "")
        if atom.startswith("T0."):
            tier_counts["tier0_core"] += 1
        elif atom.startswith("T1."):
            tier_counts["tier1_stdlib"] += 1
        elif atom.startswith("T2."):
            tier_counts["tier2_ecosystem"] += 1
        elif atom:
            tier_counts["unclassified"] += 1

    return {
        "total": len(nodes),
        **tier_counts,
        "coverage": round(sum(1 for n in nodes if n.get("body_source")) / max(len(nodes), 1), 2)
    }


def extract_role_counts(collider_data: dict) -> dict:
    """Extract role counts from Collider output."""
    nodes = collider_data.get("nodes", [])

    roles = set()
    for node in nodes:
        role = node.get("role", "")
        if role:
            roles.add(role)

    return {
        "implemented": len(roles),
        "canonical": 33,  # From CLAUDE.md
        "gap": 33 - len(roles)
    }


def count_functions_and_classes(collider_data: dict | None) -> dict:
    """Count functions and classes."""
    if collider_data:
        nodes = collider_data.get("nodes", [])
        functions = sum(1 for n in nodes if n.get("type") == "function")
        classes = sum(1 for n in nodes if n.get("type") == "class")
        return {"functions": functions, "classes": classes}

    # Fallback: rough grep-based estimate
    try:
        def_count = subprocess.run(
            ["grep", "-r", "-c", "^def ", str(REPO_ROOT / "standard-model-of-code" / "src")],
            capture_output=True, text=True
        )
        class_count = subprocess.run(
            ["grep", "-r", "-c", "^class ", str(REPO_ROOT / "standard-model-of-code" / "src")],
            capture_output=True, text=True
        )

        functions = sum(int(line.split(":")[-1]) for line in def_count.stdout.strip().split("\n") if line)
        classes = sum(int(line.split(":")[-1]) for line in class_count.stdout.strip().split("\n") if line)

        return {"functions": functions, "classes": classes, "source": "grep_estimate"}
    except Exception:
        return {"functions": -1, "classes": -1, "source": "unknown"}


def get_pipeline_info() -> dict:
    """Get pipeline stage information."""
    # Read from full_analysis.py or hardcode known value
    return {
        "stages": 18,
        "source": "CLAUDE.md"  # This is documented
    }


def generate_truths() -> dict:
    """Generate validated repository truths."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # File counts
    file_extensions = {
        "python": [".py"],
        "javascript": [".js", ".jsx", ".ts", ".tsx"],
        "yaml": [".yaml", ".yml"],
        "markdown": [".md"],
        "json": [".json"],
        "html": [".html"],
        "css": [".css"]
    }

    file_counts = count_files_by_extension(REPO_ROOT, file_extensions)
    loc = count_lines_of_code(REPO_ROOT)

    # Load Collider output for richer data
    collider_data = load_collider_output()

    # Build truths document
    truths = {
        "version": timestamp,
        "validated_by": "BARE/TruthValidator",
        "confidence": 0.90 if collider_data else 0.70,  # Higher confidence with Collider data

        "counts": {
            "files": file_counts,
            "lines_of_code": loc,
            **count_functions_and_classes(collider_data)
        },

        "pipeline": get_pipeline_info()
    }

    # Add Collider-derived data if available
    if collider_data:
        truths["atoms"] = extract_atom_counts(collider_data)
        truths["roles"] = extract_role_counts(collider_data)
        truths["_collider_source"] = str(COLLIDER_OUTPUT)
    else:
        truths["_note"] = "Run './collider full . --output .collider' for richer data"

    return truths


def save_truths(truths: dict) -> Path:
    """Save truths to YAML file."""
    INTELLIGENCE_DIR.mkdir(parents=True, exist_ok=True)

    output_path = INTELLIGENCE_DIR / "repo_truths.yaml"

    with open(output_path, "w") as f:
        yaml.dump(truths, f, default_flow_style=False, sort_keys=False)

    # Also save to history
    history_dir = INTELLIGENCE_DIR / "history"
    history_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_path = history_dir / f"truths_{timestamp}.yaml"

    with open(history_path, "w") as f:
        yaml.dump(truths, f, default_flow_style=False, sort_keys=False)

    return output_path


def main():
    """Run TruthValidator."""
    print("BARE/TruthValidator - Generating repository truths...")
    print(f"Repository root: {REPO_ROOT}")

    truths = generate_truths()
    output_path = save_truths(truths)

    print(f"\nTruths saved to: {output_path}")
    print(f"Confidence: {truths['confidence'] * 100:.0f}%")
    print(f"\nSummary:")
    print(f"  Files: {sum(truths['counts']['files'].values())} total")
    print(f"  Python: {truths['counts']['files']['python']}")
    print(f"  JavaScript: {truths['counts']['files']['javascript']}")
    print(f"  Lines of code: {truths['counts']['lines_of_code']:,}")

    if "atoms" in truths:
        print(f"  Atoms: {truths['atoms']['total']} (coverage: {truths['atoms']['coverage']*100:.0f}%)")
        print(f"  Roles: {truths['roles']['implemented']}/{truths['roles']['canonical']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
