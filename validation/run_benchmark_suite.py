#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


def _posix(path: Path) -> str:
    return path.as_posix()


def _safe_name(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", text.strip())
    return cleaned.strip("._-") or "run"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class ExpectedComponent:
    rel_file: str
    symbol: str
    symbol_kind: str | None
    expected_type: str
    notes: str | None


def _load_bench_spec(path: Path) -> dict[str, Any]:
    obj = _read_json(path)
    if not isinstance(obj, dict) or obj.get("version") != 1:
        raise ValueError(f"Invalid bench spec (expected version=1): {path}")
    required = {"name", "repo_dir", "scored_types", "expected_components"}
    missing = required - set(obj.keys())
    if missing:
        raise ValueError(f"Invalid bench spec (missing {sorted(missing)}): {path}")
    if not isinstance(obj["expected_components"], list):
        raise ValueError(f"Invalid bench spec (expected_components must be a list): {path}")
    return obj


def _normalize_pred_file(repo_root: Path, particle_file_path: str) -> str | None:
    if not particle_file_path:
        return None

    p = Path(particle_file_path)
    if p.is_absolute():
        try:
            return _posix(p.resolve().relative_to(repo_root.resolve()))
        except Exception:
            return None

    normalized = particle_file_path.replace("\\", "/")
    prefix = _posix(repo_root.resolve()).rstrip("/") + "/"
    if normalized.startswith(prefix):
        return normalized[len(prefix) :]
    return normalized


def _score_expected_vs_predicted(
    *,
    expected: list[ExpectedComponent],
    predicted_particles: list[dict[str, Any]],
    scored_types: set[str],
    repo_root: Path,
    ignored_files: set[str],
) -> dict[str, Any]:
    expected_map: dict[tuple[str, str], str] = {(e.rel_file, e.symbol): e.expected_type for e in expected}

    predicted_map: dict[tuple[str, str], str] = {}
    for p in predicted_particles:
        ptype = str(p.get("type") or "")
        if ptype not in scored_types:
            continue
        rel_file = _normalize_pred_file(repo_root, str(p.get("file_path") or ""))
        if not rel_file:
            continue
        if rel_file in ignored_files:
            continue
        name = str(p.get("name") or "")
        if not name:
            continue
        predicted_map[(rel_file, name)] = ptype

    correct: list[dict[str, Any]] = []
    missed: list[dict[str, Any]] = []
    wrong: list[dict[str, Any]] = []
    for key, exp_type in expected_map.items():
        pred_type = predicted_map.get(key)
        if pred_type is None:
            missed.append({"file": key[0], "symbol": key[1], "expected": exp_type})
            continue
        if pred_type == exp_type:
            correct.append({"file": key[0], "symbol": key[1], "type": exp_type})
        else:
            wrong.append({"file": key[0], "symbol": key[1], "expected": exp_type, "predicted": pred_type})

    extras: list[dict[str, Any]] = []
    for key, pred_type in predicted_map.items():
        if key not in expected_map:
            extras.append({"file": key[0], "symbol": key[1], "predicted": pred_type})

    # Per-type metrics
    from collections import Counter

    expected_by_type = Counter(expected_map.values())
    predicted_by_type = Counter(predicted_map.values())
    correct_by_type = Counter([c["type"] for c in correct])

    metrics_by_type: dict[str, Any] = {}
    for t in sorted(scored_types):
        exp = expected_by_type.get(t, 0)
        pred = predicted_by_type.get(t, 0)
        corr = correct_by_type.get(t, 0)
        recall = (corr / exp) if exp else None
        precision = (corr / pred) if pred else None
        f1 = None
        if precision is not None and recall is not None and (precision + recall) > 0:
            f1 = 2 * precision * recall / (precision + recall)
        metrics_by_type[t] = {
            "expected": exp,
            "predicted": pred,
            "correct": corr,
            "recall": recall,
            "precision": precision,
            "f1": f1,
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
        "missed": missed,
        "wrong": wrong,
        "extras": extras,
    }


def _run_detector(repo_root: Path, target_repo_root: Path, *, output_dir: Path) -> dict[str, Any]:
    # Try multiple possible locations for core directory
    core_candidates = [
        repo_root / "core",
        repo_root / "spectrometer_v12_minimal" / "core",
    ]
    core_dir = None
    for candidate in core_candidates:
        if candidate.exists():
            core_dir = candidate
            break
    if core_dir is None:
        raise FileNotFoundError(f"Missing core dir. Tried: {[str(c) for c in core_candidates]}")

    core_dir_str = str(core_dir)
    if core_dir_str not in sys.path:
        sys.path.insert(0, core_dir_str)
    from universal_detector import UniversalPatternDetector  # type: ignore

    detector = UniversalPatternDetector()
    return detector.analyze_repository(str(target_repo_root), output_dir=output_dir)


def _extract_expected_components(spec_obj: dict[str, Any]) -> list[ExpectedComponent]:
    out: list[ExpectedComponent] = []
    for row in spec_obj.get("expected_components") or []:
        rel_file = str(row.get("rel_file") or "").replace("\\", "/")
        symbol = str(row.get("symbol") or "")
        if not rel_file or not symbol:
            continue
        out.append(
            ExpectedComponent(
                rel_file=rel_file,
                symbol=symbol,
                symbol_kind=(str(row.get("symbol_kind")) if row.get("symbol_kind") else None),
                expected_type=str(row.get("type") or ""),
                notes=(str(row.get("notes")) if row.get("notes") else None),
            )
        )
    return out


def _unknown_samples(particles: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for p in particles:
        if str(p.get("type") or "") != "Unknown":
            continue
        # Filter unknowns from ignored files when possible.
        # (We keep file_path absolute in samples for quick navigation.)
        samples.append(
            {
                "symbol_kind": p.get("symbol_kind"),
                "name": p.get("name"),
                "file_path": p.get("file_path"),
                "line": p.get("line"),
                "evidence": (str(p.get("evidence") or "")[:200]),
            }
        )
        if len(samples) >= limit:
            break
    return samples


def _build_ignore_set(repo_root: Path, patterns: list[str]) -> set[str]:
    ignored: set[str] = set()
    for pattern in patterns:
        for p in repo_root.glob(pattern):
            if p.is_file():
                try:
                    ignored.add(_posix(p.relative_to(repo_root)))
                except ValueError:
                    continue
    return ignored


def _run_one(spec_path_str: str, *, repo_root_str: str, repos_dir_str: str, run_root_str: str) -> dict[str, Any]:
    repo_root = Path(repo_root_str).resolve()
    repos_dir = Path(repos_dir_str).resolve()
    run_root = Path(run_root_str).resolve()

    spec_path = Path(spec_path_str).resolve()
    spec = _load_bench_spec(spec_path)

    name = str(spec["name"])
    safe = _safe_name(name)
    repo_dir_name = str(spec["repo_dir"])
    target_repo = (repos_dir / repo_dir_name).resolve()
    if not target_repo.exists():
        raise FileNotFoundError(f"Missing repo_dir for spec {name!r}: {target_repo}")

    run_dir = (run_root / safe).resolve()
    detector_out = run_dir / "detector_output"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Run detector (writes files under detector_out)
    detector_result = _run_detector(repo_root, target_repo, output_dir=detector_out)
    particles = detector_result["comprehensive_results"]["particles"]

    scored_types = set(spec.get("scored_types") or [])
    expected = _extract_expected_components(spec)
    ignored_files = _build_ignore_set(target_repo, list(spec.get("ignore_path_globs") or []))

    report = _score_expected_vs_predicted(
        expected=expected,
        predicted_particles=particles,
        scored_types=scored_types,
        repo_root=target_repo,
        ignored_files=ignored_files,
    )

    unknown_all = _unknown_samples(particles, limit=500)
    unknown = []
    for u in unknown_all:
        rel = _normalize_pred_file(target_repo, str(u.get("file_path") or ""))
        if rel and rel in ignored_files:
            continue
        unknown.append(u)
        if len(unknown) >= 200:
            break

    out = {
        "spec": {
            "name": name,
            "repo_dir": repo_dir_name,
            "scored_types": sorted(scored_types),
            "spec_path": _posix(spec_path),
            "ignore_path_globs": list(spec.get("ignore_path_globs") or []),
        },
        "run": {
            "run_dir": _posix(run_dir),
            "detector_output_dir": _posix(detector_out),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "detector_summary": detector_result.get("summary") or {},
        "score": report,
        "unknown_samples": unknown,
    }

    (run_dir / "bench.report.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return {
        "name": name,
        "run_dir": _posix(run_dir),
        "summary": report["summary"],
        "unknown_count": (detector_result.get("comprehensive_results") or {}).get("summary", {}).get("unknown_particles"),
        "unknown_samples": unknown,
    }


def _iter_bench_specs(folder: Path) -> list[Path]:
    specs: list[Path] = []
    for p in sorted(folder.glob("*.bench.json")):
        if p.name.startswith("_"):
            continue
        specs.append(p)
    return specs


def _write_suite_markdown(out_path: Path, *, run_id: str, rows: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# Benchmark Suite Summary")
    lines.append("")
    lines.append(f"- Run: `{run_id}`")
    lines.append(f"- Specs: {len(rows)}")
    lines.append("")
    lines.append("| spec | expected | predicted | correct | missed | wrong | extras | accuracy |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        s = r["summary"]
        acc = s["accuracy_on_expected"]
        acc_txt = f"{acc:.1%}" if isinstance(acc, (float, int)) else "n/a"
        lines.append(
            f"| `{r['name']}` | {s['expected_total']} | {s['predicted_total']} | {s['correct_total']} | {s['missed_total']} | {s['wrong_total']} | {s['extra_total']} | {acc_txt} |"
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_unknowns_markdown(out_path: Path, *, rows: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# Unknown Component Samples (Across Suite)")
    lines.append("")
    lines.append("| spec | kind | name | file | line | evidence |")
    lines.append("|---|---|---|---|---:|---|")
    total = 0
    for r in rows:
        name = r["name"]
        for item in r.get("unknown_samples") or []:
            file_path = str(item.get("file_path") or "").replace("|", "\\|")
            ev = str(item.get("evidence") or "").replace("|", "\\|")
            lines.append(
                f"| `{name}` | {item.get('symbol_kind') or '—'} | `{item.get('name') or ''}` | `{file_path}` | {item.get('line') or 0} | `{ev}` |"
            )
            total += 1
            if total >= 200:
                break
        if total >= 200:
            break
    if total == 0:
        lines.append("| — | — | — | — | — | — |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run benchmark specs against local repos, in parallel.")
    parser.add_argument(
        "--repos-dir",
        default="spectrometer_v12_minimal/validation/benchmarks/repos",
        help="Folder containing benchmark repos (subfolders).",
    )
    parser.add_argument(
        "--specs-dir",
        default="spectrometer_v12_minimal/validation/benchmarks/specs",
        help="Folder containing *.bench.json specs.",
    )
    parser.add_argument(
        "--out-dir",
        default="spectrometer_v12_minimal/validation/benchmarks/runs",
        help="Folder to write run outputs (per-spec detector outputs + reports).",
    )
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers.")
    args = parser.parse_args(argv)

    repo_root = Path.cwd().resolve()
    repos_dir = Path(args.repos_dir).resolve()
    specs_dir = Path(args.specs_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    spec_paths = _iter_bench_specs(specs_dir)
    if not spec_paths:
        print("No *.bench.json specs found.")
        return 0

    run_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_root = (out_dir / run_id).resolve()
    run_root.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max(1, int(args.workers))) as ex:
        futures = [
            ex.submit(
                _run_one,
                str(p),
                repo_root_str=str(repo_root),
                repos_dir_str=str(repos_dir),
                run_root_str=str(run_root),
            )
            for p in spec_paths
        ]
        for fut in as_completed(futures):
            rows.append(fut.result())

    rows.sort(key=lambda r: r["name"].lower())

    # Write aggregated outputs
    (run_root / "suite_summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    _write_suite_markdown(run_root / "suite_summary.md", run_id=run_id, rows=rows)
    _write_unknowns_markdown(run_root / "unknowns.md", rows=rows)

    print(f"Wrote: {run_root / 'suite_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(os.sys.argv[1:]))
