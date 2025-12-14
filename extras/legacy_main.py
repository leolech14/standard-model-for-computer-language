#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run Spectrometer V12 Minimal on a repository path.")
    parser.add_argument("repo_path", help="Path to the repository/directory to analyze")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to write outputs (default: spectrometer_v12_minimal/output)",
    )
    args = parser.parse_args(argv)

    core_dir = Path(__file__).parent / "core"
    sys.path.insert(0, str(core_dir.resolve()))
    from universal_detector import UniversalPatternDetector  # type: ignore

    detector = UniversalPatternDetector()
    results = detector.analyze_repository(args.repo_path, output_dir=args.output_dir)

    output_files = results.get("output_files") or {}
    if output_files:
        print("OUTPUT FILES")
        print("=" * 80)
        for k, v in sorted(output_files.items(), key=lambda kv: kv[0]):
            print(f"- {k}: {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
