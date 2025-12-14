#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


def _posix(path: Path) -> str:
    return path.as_posix()


def _safe_rel(repo_root: Path, file_path: str) -> str:
    try:
        p = Path(file_path).resolve()
    except Exception:
        return file_path.replace("\\", "/")
    if p.is_absolute():
        try:
            return _posix(p.relative_to(repo_root))
        except ValueError:
            return _posix(p)
    return file_path.replace("\\", "/")


def _stable_id(*parts: str) -> str:
    h = hashlib.sha1()
    for part in parts:
        h.update(part.encode("utf-8", errors="ignore"))
        h.update(b"\0")
    return h.hexdigest()[:12]


def _group_key(rel_file: str) -> str:
    p = rel_file.replace("\\", "/").lower()
    if "/domain/" in f"/{p}/" or p.startswith("domain/"):
        return "domain"
    if "/usecase/" in f"/{p}/" or "/use_case/" in f"/{p}/" or "/application/" in f"/{p}/":
        return "usecase"
    if "/infrastructure/" in f"/{p}/":
        return "infrastructure"
    if "/presentation/" in f"/{p}/" or "/controllers/" in f"/{p}/" or "/api/" in f"/{p}/":
        return "presentation"
    first = p.split("/", 1)[0].strip()
    return first or "root"


def _mermaid_id(group: str) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in group)
    if not safe or safe[0].isdigit():
        safe = f"g_{safe}"
    return safe


@dataclass(frozen=True)
class ComponentRow:
    component_id: str
    type: str
    symbol_kind: str
    name: str
    rel_file: str
    line: int
    confidence: float
    evidence: str
    purpose: str
    internal_deps: int
    external_deps: int
    stdlib_deps: int


class ReportGenerator:
    """Generate Markdown + Mermaid reports from analysis results."""

    def generate(
        self,
        *,
        repo_root: str,
        analysis_results: list[dict[str, Any]],
        comprehensive_results: dict[str, Any],
        output_dir: Path,
    ) -> dict[str, str]:
        root = Path(repo_root).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        deps_by_file: dict[str, dict[str, Any]] = {}
        for r in analysis_results:
            fp = r.get("file_path")
            if not fp:
                continue
            rel = _safe_rel(root, fp)
            deps = r.get("dependencies") or {}
            deps_by_file[rel] = deps

        components: list[ComponentRow] = []
        for p in comprehensive_results.get("particles", []):
            rel_file = _safe_rel(root, str(p.get("file_path") or ""))
            deps = deps_by_file.get(rel_file, {})
            internal = len(deps.get("internal") or [])
            external = len(deps.get("external") or [])
            stdlib = len(deps.get("stdlib") or [])
            ptype = str(p.get("type") or "Unknown")
            name = str(p.get("name") or "")
            symbol_kind = str(p.get("symbol_kind") or "")
            line = int(p.get("line") or 0)
            confidence = float(p.get("confidence") or 0.0)
            purpose = str(p.get("description") or "")
            evidence = str(p.get("evidence") or "")
            component_id = _stable_id(ptype, name, rel_file, str(line))

            components.append(
                ComponentRow(
                    component_id=component_id,
                    type=ptype,
                    symbol_kind=symbol_kind,
                    name=name,
                    rel_file=rel_file,
                    line=line,
                    confidence=confidence,
                    evidence=evidence[:200],
                    purpose=purpose,
                    internal_deps=internal,
                    external_deps=external,
                    stdlib_deps=stdlib,
                )
            )

        components_csv = output_dir / "components.csv"
        self._write_components_csv(components_csv, components)

        mermaid = self._build_mermaid(root.name, components, comprehensive_results.get("dependencies") or {})
        report_md = output_dir / "report.md"
        report_md.write_text(
            self._build_markdown(root, components, comprehensive_results, components_csv.name, mermaid),
            encoding="utf-8",
        )

        return {"report_md": str(report_md), "components_csv": str(components_csv)}

    def _write_components_csv(self, path: Path, rows: list[ComponentRow]) -> None:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "component_id",
                    "type",
                    "symbol_kind",
                    "name",
                    "rel_file",
                    "line",
                    "confidence",
                    "evidence",
                    "purpose",
                    "internal_deps",
                    "external_deps",
                    "stdlib_deps",
                ],
            )
            writer.writeheader()
            for r in rows:
                writer.writerow(r.__dict__)

    def _build_mermaid(self, repo_name: str, components: list[ComponentRow], dep_summary: dict[str, Any]) -> str:
        counts_by_group: dict[str, int] = {}
        for c in components:
            g = _group_key(c.rel_file)
            counts_by_group[g] = counts_by_group.get(g, 0) + 1

        edges_by_group: dict[tuple[str, str], int] = {}
        for edge in dep_summary.get("internal_edges") or []:
            src = str(edge.get("from") or "")
            dst = str(edge.get("to") or "")
            count = int(edge.get("count") or 0)
            if not src or not dst or count <= 0:
                continue
            gs = _group_key(src)
            gd = _group_key(dst)
            if gs == gd:
                continue
            edges_by_group[(gs, gd)] = edges_by_group.get((gs, gd), 0) + count

        lines: list[str] = []
        lines.append("graph LR")
        lines.append(f"  %% {repo_name}")

        for group in sorted(counts_by_group.keys()):
            gid = _mermaid_id(group)
            label = f"{group} ({counts_by_group[group]})"
            lines.append(f'  {gid}["{label}"]')

        for (gs, gd), count in sorted(edges_by_group.items(), key=lambda kv: kv[1], reverse=True)[:80]:
            lines.append(f"  {_mermaid_id(gs)} -->|{count}| {_mermaid_id(gd)}")

        return "\n".join(lines) + "\n"

    def _build_markdown(
        self,
        repo_root: Path,
        components: list[ComponentRow],
        comprehensive_results: dict[str, Any],
        components_csv_name: str,
        mermaid: str,
    ) -> str:
        summary = comprehensive_results.get("summary") or {}
        deps = comprehensive_results.get("dependencies") or {}

        typed = [c for c in components if c.type != "Unknown"]
        unknown = [c for c in components if c.type == "Unknown"]

        external = deps.get("external_packages") or []
        top_external = ", ".join([f"{d['package']}({d['count']})" for d in external[:15] if d.get("package")])

        lines: list[str] = []
        lines.append(f"# Spectrometer Report — {repo_root.name}")
        lines.append("")
        lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
        lines.append(f"- Repo root: `{repo_root}`")
        lines.append("")
        lines.append("## Summary")
        lines.append(f"- Files analyzed: {summary.get('files_analyzed', 0)}")
        lines.append(f"- Components extracted: {summary.get('total_particles_found', 0)}")
        if "recognized_percentage" in summary:
            lines.append(f"- Recognized (non-Unknown): {summary.get('recognized_percentage', 0):.1f}%")
        lines.append(f"- Typed components: {len(typed)}")
        lines.append(f"- Unclassified components: {len(unknown)}")
        lines.append("")
        lines.append("## Dependencies")
        lines.append(f"- External packages (top): {top_external or 'n/a'}")
        lines.append("")
        lines.append("## Outputs")
        lines.append(f"- Full component list: `{components_csv_name}`")
        lines.append("- Raw particles: `particles.csv` (no IDs/deps)")
        lines.append("- Full JSON: `results.json`")
        lines.append("")
        lines.append("## Architecture (Mermaid)")
        lines.append("```mermaid")
        lines.append(mermaid.rstrip())
        lines.append("```")
        lines.append("")
        lines.append("## Unclassified Samples")
        lines.append("| component_id | kind | name | file | line | evidence |")
        lines.append("|---|---|---|---|---|---|")
        for c in sorted(unknown, key=lambda x: (x.rel_file, x.line, x.name))[:50]:
            evidence = (c.evidence or "").replace("|", "\\|")
            lines.append(
                f"| `{c.component_id}` | {c.symbol_kind or '—'} | `{c.name}` | `{c.rel_file}` | {c.line} | `{evidence}` |"
            )
        if len(unknown) > 50:
            lines.append(f"\n(Showing 50/{len(unknown)} unclassified components; full list in `{components_csv_name}`.)")
        lines.append("")
        return "\n".join(lines)
