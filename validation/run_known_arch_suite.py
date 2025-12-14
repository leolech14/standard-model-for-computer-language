#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from validate_known_architecture import _load_spec, _extract_python_classes, _run_detector, _score  # type: ignore


def _iter_spec_files(folder: Path) -> list[Path]:
    specs = []
    for p in sorted(folder.glob("*.json")):
        if p.name.endswith(".report.json"):
            continue
        specs.append(p)
    return specs


def _print_suite_summary(rows: list[dict[str, Any]]) -> None:
    print("KNOWN-ARCH SUITE")
    print("=" * 100)
    for r in rows:
        s = r["summary"]
        acc = f"{s['accuracy_on_expected']:.1%}" if s["accuracy_on_expected"] is not None else "n/a"
        print(
            f"- {r['name']}: expected={s['expected_total']} predicted={s['predicted_total']} "
            f"correct={s['correct_total']} missed={s['missed_total']} wrong={s['wrong_total']} extras={s['extra_total']} "
            f"accuracy={acc}"
        )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run all known-architecture validation specs.")
    parser.add_argument(
        "--folder",
        default="spectrometer_v12_minimal/validation/known_architectures",
        help="Folder containing known-architecture specs (*.json)",
    )
    parser.add_argument("--write-json", action="store_true", help="Write per-spec .report.json files")
    args = parser.parse_args(argv)

    repo_root = Path.cwd().resolve()
    folder = (repo_root / args.folder).resolve() if not Path(args.folder).is_absolute() else Path(args.folder).resolve()
    if not folder.exists():
        raise FileNotFoundError(str(folder))

    spec_files = _iter_spec_files(folder)
    if not spec_files:
        print("No spec files found.")
        return 0

    suite_rows: list[dict[str, Any]] = []

    for spec_path in spec_files:
        spec = _load_spec(spec_path)
        spec_repo_root = (repo_root / spec["repo_path"]).resolve()
        expected = _extract_python_classes(repo_root, spec_repo_root, spec)
        predicted = _run_detector(repo_root, spec_repo_root)
        report = _score(
            expected,
            predicted,
            scored_types=set(spec["scored_types"]),
            spec_repo_root=spec_repo_root,
        )

        suite_rows.append({"name": spec["name"], "summary": report["summary"]})

        if args.write_json:
            out_path = spec_path.with_suffix(".report.json")
            out_path.write_text(
                json.dumps(
                    {
                        "spec": {
                            "name": spec["name"],
                            "repo_path": spec["repo_path"],
                            "scored_types": spec["scored_types"],
                        },
                        "report": report,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    _print_suite_summary(suite_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
