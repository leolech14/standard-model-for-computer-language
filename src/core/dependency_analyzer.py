#!/usr/bin/env python3
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ResolvedDependency:
    kind: str
    target: str
    line: int
    category: str
    package: str | None = None
    resolved_file: str | None = None


def _posix(path: Path) -> str:
    return path.as_posix()


def _try_rel(repo_root: Path, file_path: Path) -> str:
    try:
        return _posix(file_path.relative_to(repo_root))
    except ValueError:
        return _posix(file_path)


def _python_stdlib_roots() -> set[str]:
    stdlib = getattr(sys, "stdlib_module_names", None)
    if isinstance(stdlib, (set, frozenset)):
        return set(stdlib)
    return {
        "__future__",
        "abc",
        "argparse",
        "asyncio",
        "base64",
        "collections",
        "concurrent",
        "contextlib",
        "csv",
        "dataclasses",
        "datetime",
        "functools",
        "hashlib",
        "http",
        "importlib",
        "inspect",
        "io",
        "itertools",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "random",
        "re",
        "sqlite3",
        "statistics",
        "string",
        "subprocess",
        "sys",
        "tempfile",
        "threading",
        "time",
        "typing",
        "uuid",
    }


NODE_BUILTINS = {
    "assert",
    "buffer",
    "child_process",
    "cluster",
    "console",
    "constants",
    "crypto",
    "dgram",
    "dns",
    "domain",
    "events",
    "fs",
    "http",
    "http2",
    "https",
    "module",
    "net",
    "os",
    "path",
    "perf_hooks",
    "process",
    "punycode",
    "querystring",
    "readline",
    "repl",
    "stream",
    "string_decoder",
    "timers",
    "tls",
    "tty",
    "url",
    "util",
    "v8",
    "vm",
    "worker_threads",
    "zlib",
}


def _python_candidate_roots(repo_root: Path) -> list[Path]:
    roots = [repo_root]
    for name in ("src", "app", "lib"):
        p = repo_root / name
        if p.is_dir():
            roots.append(p)
    return roots


def _python_module_from_rel(rel: Path) -> str:
    if rel.name == "__init__.py":
        rel = rel.parent
    else:
        rel = rel.with_suffix("")
    mod = _posix(rel).replace("/", ".")
    return mod.strip(".")


def _build_python_module_index(repo_root: Path, file_paths: Iterable[Path]) -> tuple[dict[str, str], dict[str, str]]:
    """Build module->file and file->module maps for Python files."""
    module_to_file: dict[str, str] = {}
    file_to_module: dict[str, str] = {}
    roots = _python_candidate_roots(repo_root)

    for p in file_paths:
        if p.suffix != ".py":
            continue
        for root in roots:
            try:
                rel = p.relative_to(root)
            except ValueError:
                continue
            mod = _python_module_from_rel(rel)
            if not mod:
                continue
            rel_to_repo = _try_rel(repo_root, p)
            module_to_file.setdefault(mod, rel_to_repo)
            # Prefer the shortest module for a given file (avoids "src." prefix when present)
            prev = file_to_module.get(rel_to_repo)
            if prev is None or len(mod.split(".")) < len(prev.split(".")):
                file_to_module[rel_to_repo] = mod

    return module_to_file, file_to_module


def _python_resolve_relative(
    file_module: str | None,
    *,
    level: int,
    target_module: str,
    is_init: bool,
) -> str:
    if not level:
        return target_module
    if not file_module:
        return target_module

    # Determine the current package: for a module a.b.c, package is a.b
    if is_init:
        file_package = file_module
    elif "." in file_module:
        file_package = file_module.rsplit(".", 1)[0]
    else:
        file_package = ""

    base_parts = file_package.split(".") if file_package else []
    up = max(0, level - 1)
    if up:
        base_parts = base_parts[: max(0, len(base_parts) - up)]
    base = ".".join([p for p in base_parts if p])
    if target_module:
        return f"{base}.{target_module}".strip(".") if base else target_module
    return base


def _npm_package_name(spec: str) -> str:
    if spec.startswith("@"):
        parts = spec.split("/")
        return "/".join(parts[:2]) if len(parts) >= 2 else spec
    return spec.split("/")[0]


def _resolve_js_relative(repo_root: Path, src_file: Path, spec: str) -> str | None:
    base = src_file.parent.resolve()
    candidate = (base / spec).resolve()
    candidates: list[Path] = []

    if candidate.suffix:
        candidates.append(candidate)
    else:
        for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json"):
            candidates.append(candidate.with_suffix(ext))
        candidates.append(candidate / "index.ts")
        candidates.append(candidate / "index.tsx")
        candidates.append(candidate / "index.js")
        candidates.append(candidate / "index.jsx")

    for c in candidates:
        if c.exists() and c.is_file():
            rel = _try_rel(repo_root, c)
            return rel if not rel.startswith("..") else None
    return None


class DependencyAnalyzer:
    """Classify per-file raw imports as internal/external/stdlib dependencies."""

    def analyze_repository(self, repo_root: str, analysis_results: list[dict[str, Any]]) -> dict[str, Any]:
        root = Path(repo_root).resolve()

        file_paths = []
        for r in analysis_results:
            fp = r.get("file_path")
            if fp:
                file_paths.append(Path(fp).resolve())

        py_module_to_file, py_file_to_module = _build_python_module_index(root, file_paths)
        py_stdlib = _python_stdlib_roots()

        external_packages: Counter[str] = Counter()
        stdlib_deps: Counter[str] = Counter()
        internal_edges: Counter[tuple[str, str]] = Counter()
        unknown_deps: int = 0

        for r in analysis_results:
            fp = r.get("file_path")
            if not fp:
                continue

            src_file = Path(fp).resolve()
            src_rel = _try_rel(root, src_file)
            language = r.get("language", "unknown")
            raw_imports = r.get("raw_imports") or []

            deps = {"internal": [], "external": [], "stdlib": [], "unknown": []}

            for imp in raw_imports:
                kind = str(imp.get("kind") or "import")
                target = str(imp.get("target") or "").strip()
                line = int(imp.get("line") or 0)

                if not target and language != "python":
                    continue

                if language == "python":
                    level = int(imp.get("level") or 0)
                    file_module = py_file_to_module.get(src_rel)
                    resolved_target = _python_resolve_relative(
                        file_module,
                        level=level,
                        target_module=target,
                        is_init=src_file.name == "__init__.py",
                    )
                    top = resolved_target.split(".", 1)[0] if resolved_target else ""

                    if top in py_stdlib:
                        deps["stdlib"].append(
                            ResolvedDependency(kind, resolved_target, line, "stdlib", package=top).__dict__
                        )
                        stdlib_deps[top] += 1
                        continue

                    internal_file = py_module_to_file.get(resolved_target)
                    if internal_file:
                        deps["internal"].append(
                            ResolvedDependency(kind, resolved_target, line, "internal", resolved_file=internal_file).__dict__
                        )
                        internal_edges[(src_rel, internal_file)] += 1
                        continue

                    if resolved_target and any(
                        m == resolved_target or m.startswith(resolved_target + ".") for m in py_module_to_file
                    ):
                        deps["internal"].append(
                            ResolvedDependency(kind, resolved_target, line, "internal", resolved_file=None).__dict__
                        )
                        continue

                    pkg = top if top else None
                    deps["external"].append(
                        ResolvedDependency(kind, resolved_target, line, "external", package=pkg).__dict__
                    )
                    if pkg:
                        external_packages[pkg] += 1
                    continue

                if language in {"javascript", "typescript"}:
                    if target.startswith((".", "/")):
                        resolved_file = _resolve_js_relative(root, src_file, target)
                        deps["internal"].append(
                            ResolvedDependency(kind, target, line, "internal", resolved_file=resolved_file).__dict__
                        )
                        if resolved_file:
                            internal_edges[(src_rel, resolved_file)] += 1
                        continue

                    pkg = _npm_package_name(target)
                    if pkg in NODE_BUILTINS:
                        deps["stdlib"].append(
                            ResolvedDependency(kind, target, line, "stdlib", package=pkg).__dict__
                        )
                        stdlib_deps[pkg] += 1
                        continue

                    deps["external"].append(
                        ResolvedDependency(kind, target, line, "external", package=pkg).__dict__
                    )
                    external_packages[pkg] += 1
                    continue

                # Best-effort classification for other languages
                deps["unknown"].append(ResolvedDependency(kind, target, line, "unknown").__dict__)
                unknown_deps += 1

            r["dependencies"] = deps

        top_external = [{"package": p, "count": c} for p, c in external_packages.most_common(50)]
        top_stdlib = [{"package": p, "count": c} for p, c in stdlib_deps.most_common(50)]
        top_internal_edges = [
            {"from": a, "to": b, "count": c} for (a, b), c in internal_edges.most_common(200)
        ]

        return {
            "external_packages": top_external,
            "stdlib_packages": top_stdlib,
            "internal_edges": top_internal_edges,
            "unknown_dependency_count": unknown_deps,
        }
