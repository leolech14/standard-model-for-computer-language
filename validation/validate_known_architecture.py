#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any


@dataclass(frozen=True)
class LabeledClass:
    rel_file: str
    name: str
    lineno: int
    expected_type: str


def _posix(path: Path) -> str:
    return path.as_posix()


def _load_spec(spec_path: Path) -> dict[str, Any]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    required = {"name", "language", "repo_path", "rules", "scored_types"}
    missing = required - set(spec.keys())
    if missing:
        raise ValueError(f"Invalid spec (missing {sorted(missing)}): {spec_path}")
    if spec["language"] != "python":
        raise ValueError(f"Only python specs are supported right now (got {spec['language']!r})")
    return spec


def _build_file_match_sets(spec_repo_root: Path, rules: list[dict[str, Any]]) -> list[set[str] | None]:
    """Precompute which files match each rule's path_glob (supports ** via Path.glob)."""
    match_sets: list[set[str] | None] = []
    for rule in rules:
        path_glob = rule.get("path_glob")
        if not path_glob:
            match_sets.append(None)
            continue
        matches: set[str] = set()
        for p in spec_repo_root.glob(path_glob):
            if p.is_file():
                matches.add(_posix(p.relative_to(spec_repo_root)))
        match_sets.append(matches)
    return match_sets


def _build_ignore_set(spec_repo_root: Path, ignore_globs: list[str]) -> set[str]:
    ignored: set[str] = set()
    for pattern in ignore_globs:
        for p in spec_repo_root.glob(pattern):
            if p.is_file():
                ignored.add(_posix(p.relative_to(spec_repo_root)))
    return ignored


def _pick_expected_type(
    class_name: str,
    rel_file: str,
    rules: list[dict[str, Any]],
    rule_match_sets: list[set[str] | None],
) -> str | None:
    for idx, rule in enumerate(rules):
        match_set = rule_match_sets[idx]
        if match_set is not None and rel_file not in match_set:
            continue

        name_regex = rule.get("name_regex")
        if name_regex and not re.match(name_regex, class_name):
            continue

        return rule["type"]

    return None


def _extract_python_classes(repo_root: Path, spec_repo_root: Path, spec: dict[str, Any]) -> list[LabeledClass]:
    rules = spec["rules"]
    scored_types = set(spec["scored_types"])
    ignore_files = _build_ignore_set(spec_repo_root, spec.get("ignore_path_globs", []))
    rule_match_sets = _build_file_match_sets(spec_repo_root, rules)

    labeled: list[LabeledClass] = []

    for file_path in spec_repo_root.rglob("*.py"):
        rel_to_spec = file_path.relative_to(spec_repo_root)
        rel_file = _posix(rel_to_spec)

        if rel_file in ignore_files:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
        except Exception:
            continue

        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue

            expected = _pick_expected_type(node.name, rel_file, rules, rule_match_sets)
            if not expected or expected not in scored_types:
                continue

            labeled.append(
                LabeledClass(
                    rel_file=rel_file,
                    name=node.name,
                    lineno=getattr(node, "lineno", 0) or 0,
                    expected_type=expected,
                )
            )

    return labeled


def _run_detector(
    repo_root: Path,
    spec_repo_root: Path,
    *,
    output_dir: Path | None = None,
) -> list[dict[str, Any]]:
    core_dir = repo_root / "spectrometer_v12_minimal" / "core"
    if not core_dir.exists():
        raise FileNotFoundError(f"Missing core dir: {core_dir}")

    import sys

    sys.path.insert(0, str(core_dir))
    from universal_detector import UniversalPatternDetector  # type: ignore

    detector = UniversalPatternDetector()
    results = detector.analyze_repository(str(spec_repo_root), output_dir=output_dir)
    return results["comprehensive_results"]["particles"]


def _normalize_pred_file(spec_repo_root: Path, particle_file_path: str) -> str | None:
    if not particle_file_path:
        return None

    p = Path(particle_file_path)
    if p.is_absolute():
        try:
            return _posix(p.relative_to(spec_repo_root))
        except ValueError:
            return None

    normalized = particle_file_path.replace("\\", "/")
    prefix = _posix(spec_repo_root).rstrip("/") + "/"
    if normalized.startswith(prefix):
        return normalized[len(prefix) :]

    return normalized


def _score(
    expected: list[LabeledClass],
    predicted_particles: list[dict[str, Any]],
    *,
    scored_types: set[str],
    spec_repo_root: Path,
) -> dict[str, Any]:
    expected_map = {(e.rel_file, e.name): e.expected_type for e in expected}

    predicted_map: dict[tuple[str, str], str] = {}
    for p in predicted_particles:
        ptype = p.get("type")
        if ptype not in scored_types:
            continue
        rel_file = _normalize_pred_file(spec_repo_root, p.get("file_path", ""))
        if not rel_file:
            continue
        name = p.get("name")
        if not name:
            continue
        predicted_map[(rel_file, name)] = str(ptype)

    correct = []
    missed = []
    wrong = []

    for key, exp_type in expected_map.items():
        pred_type = predicted_map.get(key)
        if pred_type is None:
            missed.append({"file": key[0], "name": key[1], "expected": exp_type})
            continue
        if pred_type == exp_type:
            correct.append({"file": key[0], "name": key[1], "type": exp_type})
        else:
            wrong.append({"file": key[0], "name": key[1], "expected": exp_type, "predicted": pred_type})

    extras = []
    for key, pred_type in predicted_map.items():
        if key not in expected_map:
            extras.append({"file": key[0], "name": key[1], "predicted": pred_type})

    expected_by_type = Counter(expected_map.values())
    predicted_by_type = Counter(predicted_map.values())

    correct_by_type: Counter[str] = Counter()
    for c in correct:
        correct_by_type[c["type"]] += 1

    wrong_by_expected: Counter[str] = Counter()
    for w in wrong:
        wrong_by_expected[w["expected"]] += 1

    metrics_by_type: dict[str, Any] = {}
    for t in sorted(scored_types):
        exp = expected_by_type.get(t, 0)
        pred = predicted_by_type.get(t, 0)
        corr = correct_by_type.get(t, 0)
        recall = (corr / exp) if exp else None
        precision = (corr / pred) if pred else None
        metrics_by_type[t] = {
            "expected": exp,
            "predicted": pred,
            "correct": corr,
            "recall": recall,
            "precision": precision,
        }

    return {
        "summary": {
            "expected_total": len(expected_map),
            "predicted_total": len(predicted_map),
            "correct_total": len(correct),
            "missed_total": len(missed),
            "wrong_total": len(wrong),
            "extra_total": len(extras),
            "accuracy_on_expected": (len(correct) / len(expected_map)) if expected_map else None,
        },
        "metrics_by_type": metrics_by_type,
        "expected_by_type": dict(expected_by_type),
        "predicted_by_type": dict(predicted_by_type),
        "correct_by_type": dict(correct_by_type),
        "wrong_by_expected_type": dict(wrong_by_expected),
        "missed": missed,
        "wrong": wrong,
        "extras": extras,
    }


def _print_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("KNOWN-ARCH VALIDATION")
    print("=" * 80)
    print(
        f"expected={summary['expected_total']}  "
        f"predicted={summary['predicted_total']}  "
        f"correct={summary['correct_total']}  "
        f"missed={summary['missed_total']}  "
        f"wrong={summary['wrong_total']}  "
        f"extras={summary['extra_total']}  "
        f"accuracy_on_expected={summary['accuracy_on_expected']:.1%}"
        if summary["accuracy_on_expected"] is not None
        else ""
    )
    print("")
    print("By type:")
    for t, m in report["metrics_by_type"].items():
        recall = f"{m['recall']:.1%}" if m["recall"] is not None else "n/a"
        precision = f"{m['precision']:.1%}" if m["precision"] is not None else "n/a"
        print(
            f"- {t:14} exp={m['expected']:3} pred={m['predicted']:3} corr={m['correct']:3}  recall={recall:>6}  precision={precision:>6}"
        )

    if report["wrong"]:
        print("")
        print("Wrong (first 20):")
        for item in report["wrong"][:20]:
            print(f"- {item['file']}::{item['name']}  expected={item['expected']} predicted={item['predicted']}")

    if report["missed"]:
        print("")
        print("Missed (first 20):")
        for item in report["missed"][:20]:
            print(f"- {item['file']}::{item['name']}  expected={item['expected']}")

    if report["extras"]:
        print("")
        print("Extras (first 20):")
        for item in report["extras"][:20]:
            print(f"- {item['file']}::{item['name']}  predicted={item['predicted']}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate detector output against a known-architecture spec.")
    parser.add_argument(
        "--spec",
        default="spectrometer_v12_minimal/validation/known_architectures/dddpy_real_onion_v1.json",
        help="Path to known-architecture spec JSON",
    )
    parser.add_argument("--write-json", action="store_true", help="Write JSON report next to the spec")
    args = parser.parse_args(argv)

    repo_root = Path.cwd().resolve()
    spec_path = (repo_root / args.spec).resolve() if not Path(args.spec).is_absolute() else Path(args.spec).resolve()
    spec = _load_spec(spec_path)

    spec_repo_root = (repo_root / spec["repo_path"]).resolve()
    if not spec_repo_root.exists():
        raise FileNotFoundError(f"Spec repo_path not found: {spec_repo_root}")

    expected = _extract_python_classes(repo_root, spec_repo_root, spec)
    predicted_particles = _run_detector(repo_root, spec_repo_root)

    report = {
        "spec": {
            "name": spec["name"],
            "repo_path": spec["repo_path"],
            "scored_types": spec["scored_types"],
        },
        "report": _score(
            expected,
            predicted_particles,
            scored_types=set(spec["scored_types"]),
            spec_repo_root=spec_repo_root,
        ),
    }

    _print_report(report["report"])

    if args.write_json:
        out_path = spec_path.with_suffix(".report.json")
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nWrote: {out_path.relative_to(repo_root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
