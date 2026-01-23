#!/usr/bin/env python3
"""
Corpus Runner for Phase 2 Research

Clones repos from a corpus manifest, runs Collider analysis,
and produces coverage metrics with full metadata for reproducibility.

Usage:
    python tools/research/run_corpus.py artifacts/atom-research/corpus_pilot.yaml
    python tools/research/run_corpus.py corpus.yaml --output artifacts/2026-01-22/
    python tools/research/run_corpus.py corpus.yaml --repos fastapi,httpx
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def get_git_sha(repo_path: Path) -> str:
    """Get current commit SHA of a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()[:12]
    except subprocess.CalledProcessError:
        return "unknown"


def get_collider_sha() -> str:
    """Get Collider tool commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()[:12]
    except subprocess.CalledProcessError:
        return "unknown"


def clone_or_fetch(repo: dict, repos_cache: Path) -> Path:
    """Clone repo if not exists, or fetch + checkout ref."""
    name = repo["name"]
    url = repo["url"]
    ref = repo.get("ref", "main")

    repo_path = repos_cache / name

    if repo_path.exists():
        print(f"  Fetching {name}...")
        subprocess.run(
            ["git", "fetch", "--all"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
    else:
        print(f"  Cloning {name}...")
        subprocess.run(
            ["git", "clone", "--depth", "100", url, str(repo_path)],
            capture_output=True,
            check=True,
        )

    # Checkout ref
    subprocess.run(
        ["git", "checkout", ref],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )

    return repo_path


def run_collider(repo_path: Path, output_dir: Path, deterministic: bool = True) -> bool:
    """Run Collider analysis on a repo."""
    cmd = ["./collider", "full", str(repo_path), "--output", str(output_dir)]

    # In deterministic mode, don't add --ai-insights
    if not deterministic:
        cmd.append("--ai-insights")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout per repo
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT after 10 minutes")
        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def run_coverage(analysis_file: Path, output_file: Path) -> dict | None:
    """Run coverage analysis script."""
    try:
        result = subprocess.run(
            [
                sys.executable,
                "tools/research/atom_coverage.py",
                str(analysis_file),
                "--json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        coverage = json.loads(result.stdout)
        with open(output_file, "w") as f:
            json.dump(coverage, f, indent=2)
        return coverage
    except Exception as e:
        print(f"    Coverage analysis failed: {e}")
        return None


def create_run_metadata(
    repo: dict,
    repo_sha: str,
    collider_sha: str,
    config: dict,
    outputs: dict,
) -> dict:
    """Create run metadata for reproducibility."""
    return {
        "repo": {
            "name": repo["name"],
            "url": repo["url"],
            "ref": repo.get("ref", "main"),
            "actual_sha": repo_sha,
            "language": repo.get("language", "unknown"),
            "domain": repo.get("domain", "unknown"),
            "size": repo.get("size", "unknown"),
        },
        "run": {
            "utc": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": None,  # Could add timing
        },
        "tooling": {
            "collider_commit": collider_sha,
            "research_tooling_commit": get_git_sha(Path(".")),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        "config": {
            "deterministic": config.get("deterministic", True),
            "ai_insights": config.get("ai_insights", False),
        },
        "outputs": outputs,
    }


def run_corpus(corpus_file: Path, output_base: Path, only_repos: list[str] | None = None):
    """Run analysis on all repos in corpus."""
    # Load corpus manifest
    with open(corpus_file) as f:
        corpus = yaml.safe_load(f)

    repos = corpus.get("repos", [])
    config = corpus.get("config", {})

    if only_repos:
        repos = [r for r in repos if r["name"] in only_repos]

    if not repos:
        print("No repos to process")
        return

    # Create output directories
    date_str = datetime.now().strftime("%Y-%m-%d")
    run_dir = output_base / date_str
    repos_dir = run_dir / "repos"
    repos_cache = output_base / ".repos_cache"

    run_dir.mkdir(parents=True, exist_ok=True)
    repos_dir.mkdir(exist_ok=True)
    repos_cache.mkdir(exist_ok=True)

    # Copy corpus manifest
    shutil.copy(corpus_file, run_dir / "corpus.yaml")

    collider_sha = get_collider_sha()
    results = []

    print(f"Processing {len(repos)} repos...")
    print(f"Output: {run_dir}")
    print(f"Collider commit: {collider_sha}")
    print(f"Mode: {'Deterministic' if config.get('deterministic', True) else 'Augmented'}")
    print()

    for i, repo in enumerate(repos, 1):
        name = repo["name"]
        print(f"[{i}/{len(repos)}] {name}")

        try:
            # Clone/fetch repo
            repo_path = clone_or_fetch(repo, repos_cache)
            repo_sha = get_git_sha(repo_path)

            # Create output dir for this repo
            repo_output = repos_dir / name / repo_sha
            repo_output.mkdir(parents=True, exist_ok=True)

            # Run Collider
            print(f"  Running Collider...")
            success = run_collider(
                repo_path, repo_output, deterministic=config.get("deterministic", True)
            )

            if not success:
                print(f"  FAILED: Collider analysis")
                results.append({"name": name, "status": "failed", "error": "collider"})
                continue

            # Find the analysis output file (Collider outputs timestamped files)
            # Look for output_llm-oriented_*.json pattern
            analysis_files = list(repo_output.glob("output_llm-oriented_*.json"))
            if not analysis_files:
                # Fallback to unified_analysis.json for compatibility
                analysis_file = repo_output / "unified_analysis.json"
                if not analysis_file.exists():
                    print(f"  FAILED: No analysis output found")
                    results.append({"name": name, "status": "failed", "error": "no_output"})
                    continue
            else:
                # Use the most recent one (by filename, which includes timestamp)
                analysis_file = sorted(analysis_files)[-1]
                # Create symlink for consistency
                unified_link = repo_output / "unified_analysis.json"
                if not unified_link.exists():
                    unified_link.symlink_to(analysis_file.name)

            coverage_file = repo_output / "coverage.json"

            print(f"  Running coverage analysis...")
            coverage = run_coverage(analysis_file, coverage_file)

            if coverage is None:
                results.append({"name": name, "status": "failed", "error": "coverage"})
                continue

            # Create metadata
            metadata = create_run_metadata(
                repo=repo,
                repo_sha=repo_sha,
                collider_sha=collider_sha,
                config=config,
                outputs={
                    "unified_analysis": "unified_analysis.json",
                    "coverage": "coverage.json",
                },
            )

            with open(repo_output / "run_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            # Collect result
            metrics = coverage.get("metrics", {})
            results.append({
                "name": name,
                "status": "success",
                "sha": repo_sha,
                "n_nodes": metrics.get("n_nodes", 0),
                "top_4_mass": metrics.get("top_4_mass", 0),
                "unknown_rate": metrics.get("unknown_rate", 0),
                "t2_rate": metrics.get("t2_enrichment_rate", 0),
            })

            print(f"  SUCCESS: {metrics.get('n_nodes', 0)} nodes, top-4: {metrics.get('top_4_mass', 0)}%, unknown: {metrics.get('unknown_rate', 0)}%")

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"name": name, "status": "failed", "error": str(e)})

    # Write results summary
    with open(run_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print()
    print("=" * 60)
    print("CORPUS RUN SUMMARY")
    print("=" * 60)
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    print(f"Successful: {len(successful)}/{len(results)}")
    print(f"Failed: {len(failed)}/{len(results)}")

    if successful:
        print()
        print("SUCCESSFUL REPOS:")
        for r in successful:
            print(f"  {r['name']:20} nodes={r['n_nodes']:5} top4={r['top_4_mass']:5.1f}% unknown={r['unknown_rate']:4.1f}%")

    if failed:
        print()
        print("FAILED REPOS:")
        for r in failed:
            print(f"  {r['name']:20} error={r.get('error', 'unknown')}")

    print()
    print(f"Results saved to: {run_dir}")


def main():
    parser = argparse.ArgumentParser(description="Run Collider on corpus")
    parser.add_argument("corpus_file", type=Path, help="Path to corpus YAML manifest")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("artifacts/atom-research"),
        help="Output base directory",
    )
    parser.add_argument(
        "--repos",
        type=str,
        help="Comma-separated list of repo names to run (subset)",
    )

    args = parser.parse_args()

    if not args.corpus_file.exists():
        print(f"Error: Corpus file not found: {args.corpus_file}", file=sys.stderr)
        sys.exit(1)

    only_repos = args.repos.split(",") if args.repos else None

    run_corpus(args.corpus_file, args.output, only_repos)


if __name__ == "__main__":
    main()
