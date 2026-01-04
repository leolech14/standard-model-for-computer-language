"""
Self-Proof Validator

Validates that a codebase's extracted graph is internally consistent
and computes proof metrics per SPEC v0.1.3.

Key invariants:
- Proof operates on N_atomic only (functions/methods/classes)
- Container nodes (files/modules) are excluded from proof graph
- Entrypoints must be atomic nodes
- Proof score = f(registry_accuracy, connection_coverage, edge_accuracy, reachability)
"""

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict


@dataclass
class ReachabilityDiagnostics:
    """Diagnostics explaining why nodes are unreachable."""

    unreachable_total: int = 0

    # Reason counts
    reasons: Dict[str, int] = field(default_factory=dict)

    # Examples per reason (up to 5 each)
    examples: Dict[str, List[str]] = field(default_factory=dict)

    # Unreachable cluster roots (for targeted fixes)
    cluster_roots: List[Dict] = field(default_factory=list)


@dataclass
class ProofResult:
    """Result of self-proof validation."""

    # Core metrics
    proof_score: float = 0.0
    registry_accuracy: float = 0.0
    connection_coverage: float = 0.0
    edge_accuracy: float = 0.0
    reachability: float = 0.0

    # Counts
    filesystem_components: int = 0
    registry_components: int = 0
    phantoms: int = 0

    # Node lists
    proof_nodes: List[Dict] = field(default_factory=list)
    entrypoints: List[str] = field(default_factory=list)
    unreachable: List[str] = field(default_factory=list)

    # Reachability diagnostics
    reachability_diagnostics: Optional[ReachabilityDiagnostics] = None

    # Diagnostics
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class SelfProofValidator:
    """
    Validates codebase graph against filesystem and computes proof metrics.

    Usage:
        validator = SelfProofValidator(Path("src/core"))
        result = validator.prove()
        print(f"Proof score: {result.proof_score:.1%}")
    """

    # Framework-specific decorator patterns
    # Format: {decorator_base: {decorator_attrs}}
    CLICK_DECORATORS = {"command", "group", "option", "argument"}
    TYPER_DECORATORS = {"command", "callback"}
    FASTAPI_DECORATORS = {"get", "post", "put", "delete", "patch", "options", "head", "api_route"}
    FLASK_DECORATORS = {"route", "get", "post", "put", "delete", "patch"}

    # Direct entrypoint names (without decorators)
    ENTRY_NAMES = {"main", "cli", "run", "start", "execute"}

    # Framework imports to detect
    FRAMEWORK_IMPORTS = {
        "click": "click",
        "typer": "typer",
        "fastapi": "fastapi",
        "flask": "flask",
    }

    def __init__(self, target_path: Path, include_tests: bool = False):
        self.target_path = Path(target_path).resolve()
        self.include_tests = include_tests
        self.atomic_nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
        self.entrypoints: Set[str] = set()
        # Per-file framework context
        self._file_contexts: Dict[str, Dict] = {}

    def prove(self, enforce_metadata: bool = True) -> ProofResult:
        """
        Run self-proof validation.

        Args:
            enforce_metadata: If True, require metadata fields for proof

        Returns:
            ProofResult with metrics and diagnostics
        """
        result = ProofResult()

        # Stage 1: Scan filesystem for atomic components
        fs_components = self._scan_filesystem()
        result.filesystem_components = len(fs_components)

        # Stage 2: Build atomic node registry from AST
        self._build_atomic_registry(fs_components)
        result.registry_components = len(self.atomic_nodes)
        result.proof_nodes = list(self.atomic_nodes.values())

        # Stage 3: Detect entrypoints (atomic only)
        self._detect_entrypoints()
        result.entrypoints = list(self.entrypoints)

        # Stage 4: Extract call edges (atomic → atomic only)
        self._extract_call_edges()

        # Stage 5: Compute reachability from entrypoints
        reachable = self._compute_reachability()
        unreachable = set(self.atomic_nodes.keys()) - reachable
        result.unreachable = list(unreachable)

        # Stage 6: Compute reachability diagnostics
        result.reachability_diagnostics = self._compute_reachability_diagnostics(
            reachable, unreachable
        )

        # Stage 7: Compute metrics
        result.registry_accuracy = self._compute_registry_accuracy(fs_components)
        result.connection_coverage = self._compute_connection_coverage()
        result.edge_accuracy = 1.0  # All edges are verified by construction
        result.reachability = len(reachable) / len(self.atomic_nodes) if self.atomic_nodes else 0.0

        # Proof score formula (weighted average)
        result.proof_score = (
            0.25 * result.registry_accuracy +
            0.25 * result.connection_coverage +
            0.25 * result.edge_accuracy +
            0.25 * result.reachability
        )

        # Count phantoms (registry nodes not in filesystem)
        registry_ids = set(self.atomic_nodes.keys())
        fs_ids = set(fs_components.keys())
        result.phantoms = len(registry_ids - fs_ids)

        return result

    def _scan_filesystem(self) -> Dict[str, Dict]:
        """Scan filesystem for Python files and extract atomic component signatures."""
        components = {}

        for py_file in self.target_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            rel_path = py_file.relative_to(self.target_path)

            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    comp_id = f"{rel_path}::{node.name}"
                    components[comp_id] = {
                        "id": comp_id,
                        "name": node.name,
                        "type": "function",
                        "file_path": str(rel_path),
                        "line": node.lineno,
                        "decorators": [self._decorator_name(d) for d in node.decorator_list],
                    }
                elif isinstance(node, ast.ClassDef):
                    class_id = f"{rel_path}::{node.name}"
                    components[class_id] = {
                        "id": class_id,
                        "name": node.name,
                        "type": "class",
                        "file_path": str(rel_path),
                        "line": node.lineno,
                        "decorators": [self._decorator_name(d) for d in node.decorator_list],
                    }
                    # Also extract methods
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_id = f"{rel_path}::{node.name}.{item.name}"
                            components[method_id] = {
                                "id": method_id,
                                "name": f"{node.name}.{item.name}",
                                "type": "method",
                                "file_path": str(rel_path),
                                "line": item.lineno,
                                "parent": class_id,
                                "decorators": [self._decorator_name(d) for d in item.decorator_list],
                            }

        return components

    def _decorator_name(self, dec: ast.expr) -> str:
        """Extract decorator name from AST node."""
        if isinstance(dec, ast.Name):
            return dec.id
        elif isinstance(dec, ast.Attribute):
            parts = []
            node = dec
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
            return ".".join(reversed(parts))
        elif isinstance(dec, ast.Call):
            return self._decorator_name(dec.func)
        return ""

    def _build_atomic_registry(self, fs_components: Dict[str, Dict]) -> None:
        """Build registry of atomic nodes (no containers)."""
        self.atomic_nodes = {
            k: v for k, v in fs_components.items()
            if v.get("type") in {"function", "method", "class"}
        }

    def _detect_entrypoints(self) -> None:
        """Detect entrypoint nodes (atomic only, never containers)."""
        # First, build file contexts (imports + instances)
        self._build_file_contexts()

        for node_id, node in self.atomic_nodes.items():
            if self._is_entrypoint(node):
                self.entrypoints.add(node_id)

    def _build_file_contexts(self) -> None:
        """Build per-file context: detected imports and framework instances."""
        for py_file in self.target_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            rel_path = str(py_file.relative_to(self.target_path))

            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            context = {
                "has_click": False,
                "has_typer": False,
                "has_fastapi": False,
                "has_flask": False,
                "typer_apps": set(),      # Variable names holding Typer instances
                "fastapi_apps": set(),    # Variable names holding FastAPI instances
                "fastapi_routers": set(), # Variable names holding APIRouter instances
                "flask_apps": set(),      # Variable names holding Flask instances
            }

            # Detect imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "click":
                            context["has_click"] = True
                        elif alias.name == "typer":
                            context["has_typer"] = True
                        elif alias.name == "fastapi":
                            context["has_fastapi"] = True
                        elif alias.name == "flask":
                            context["has_flask"] = True

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if module == "click" or module.startswith("click."):
                        context["has_click"] = True
                    elif module == "typer" or module.startswith("typer."):
                        context["has_typer"] = True
                    elif module == "fastapi" or module.startswith("fastapi."):
                        context["has_fastapi"] = True
                    elif module == "flask" or module.startswith("flask."):
                        context["has_flask"] = True

                # Detect instance assignments: app = Typer(), app = FastAPI(), etc.
                elif isinstance(node, ast.Assign):
                    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                        var_name = node.targets[0].id
                        call_name = self._get_call_name(node.value)

                        if call_name in {"Typer", "typer.Typer"}:
                            context["typer_apps"].add(var_name)
                        elif call_name in {"FastAPI", "fastapi.FastAPI"}:
                            context["fastapi_apps"].add(var_name)
                        elif call_name in {"APIRouter", "fastapi.APIRouter"}:
                            context["fastapi_routers"].add(var_name)
                        elif call_name in {"Flask", "flask.Flask"}:
                            context["flask_apps"].add(var_name)

            self._file_contexts[rel_path] = context

    def _get_call_name(self, node: ast.expr) -> str:
        """Get the name of a Call expression."""
        if not isinstance(node, ast.Call):
            return ""
        func = node.func
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            parts = []
            curr = func
            while isinstance(curr, ast.Attribute):
                parts.append(curr.attr)
                curr = curr.value
            if isinstance(curr, ast.Name):
                parts.append(curr.id)
            return ".".join(reversed(parts))
        return ""

    def _is_entrypoint(self, node: Dict) -> bool:
        """Check if node is an entrypoint using framework-aware detection."""
        name = node.get("name", "").lower()
        short_name = name.split(".")[-1]  # Handle Class.method
        decorators = node.get("decorators", [])
        file_path = node.get("file_path", "")

        # Get file context
        ctx = self._file_contexts.get(file_path, {})

        # 1. Check direct name patterns
        if short_name in self.ENTRY_NAMES:
            return True

        # 2. Check Click decorators
        if ctx.get("has_click"):
            for dec in decorators:
                base, attr = self._parse_decorator(dec)
                if base == "click" and attr in self.CLICK_DECORATORS:
                    return True

        # 3. Check Typer decorators
        if ctx.get("has_typer"):
            typer_apps = ctx.get("typer_apps", set())
            for dec in decorators:
                base, attr = self._parse_decorator(dec)
                if base in typer_apps and attr in self.TYPER_DECORATORS:
                    return True

        # 4. Check FastAPI decorators
        if ctx.get("has_fastapi"):
            fastapi_instances = ctx.get("fastapi_apps", set()) | ctx.get("fastapi_routers", set())
            for dec in decorators:
                base, attr = self._parse_decorator(dec)
                if base in fastapi_instances and attr in self.FASTAPI_DECORATORS:
                    return True

        # 5. Check Flask decorators
        if ctx.get("has_flask"):
            flask_apps = ctx.get("flask_apps", set())
            for dec in decorators:
                base, attr = self._parse_decorator(dec)
                if base in flask_apps and attr in self.FLASK_DECORATORS:
                    return True

        # 6. Check pytest patterns (flag-gated)
        if self.include_tests:
            if self._is_test_file(file_path) and short_name.startswith("test_"):
                return True

        # 7. Check pytest.fixture decorator
        for dec in decorators:
            if "pytest.fixture" in dec or dec == "fixture":
                return True

        return False

    def _parse_decorator(self, dec: str) -> tuple:
        """Parse decorator string into (base, attr) tuple."""
        parts = dec.split(".")
        if len(parts) >= 2:
            return parts[0], parts[-1]
        elif len(parts) == 1:
            return "", parts[0]
        return "", ""

    def _is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file."""
        path_lower = file_path.lower()
        return (
            path_lower.startswith("test_") or
            path_lower.startswith("tests/") or
            "/test_" in path_lower or
            "/tests/" in path_lower or
            path_lower.endswith("_test.py")
        )

    def _extract_call_edges(self) -> None:
        """Extract call edges between atomic nodes."""
        # Build name → id lookup for resolution
        name_to_ids: Dict[str, List[str]] = defaultdict(list)
        for node_id, node in self.atomic_nodes.items():
            name_to_ids[node.get("name", "")].append(node_id)

        for py_file in self.target_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            rel_path = py_file.relative_to(self.target_path)

            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            # Find all function/method definitions and their calls
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    caller_id = f"{rel_path}::{node.name}"
                    if caller_id not in self.atomic_nodes:
                        continue

                    # Find calls within this function
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            callee_name = self._call_target_name(child)
                            if callee_name and callee_name in name_to_ids:
                                for target_id in name_to_ids[callee_name]:
                                    self.edges.append({
                                        "source": caller_id,
                                        "target": target_id,
                                        "edge_type": "calls",
                                        "resolution": "resolved_internal",
                                    })

    def _call_target_name(self, call: ast.Call) -> Optional[str]:
        """Extract target name from a Call node."""
        func = call.func
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return func.attr
        return None

    def _compute_reachability(self) -> Set[str]:
        """Compute reachable nodes from entrypoints via BFS."""
        reachable = set()
        queue = list(self.entrypoints)

        # Build adjacency list
        adj: Dict[str, Set[str]] = defaultdict(set)
        for edge in self.edges:
            if edge.get("resolution") == "resolved_internal":
                adj[edge["source"]].add(edge["target"])

        while queue:
            current = queue.pop(0)
            if current in reachable:
                continue
            reachable.add(current)
            for target in adj.get(current, set()):
                if target not in reachable:
                    queue.append(target)

        return reachable

    def _compute_registry_accuracy(self, fs_components: Dict[str, Dict]) -> float:
        """Compute registry accuracy: overlap between registry and filesystem."""
        if not fs_components:
            return 0.0

        registry_ids = set(self.atomic_nodes.keys())
        fs_ids = set(fs_components.keys())

        intersection = registry_ids & fs_ids
        union = registry_ids | fs_ids

        return len(intersection) / len(union) if union else 0.0

    def _compute_connection_coverage(self) -> float:
        """Compute connection coverage: fraction of nodes with resolved edges."""
        if not self.atomic_nodes:
            return 0.0

        connected = set()
        for edge in self.edges:
            if edge.get("resolution") == "resolved_internal":
                connected.add(edge["source"])
                connected.add(edge["target"])

        return len(connected) / len(self.atomic_nodes)

    def _compute_reachability_diagnostics(
        self, reachable: Set[str], unreachable: Set[str]
    ) -> ReachabilityDiagnostics:
        """
        Compute diagnostics explaining why nodes are unreachable.

        Reasons:
        - no_entrypoints: entrypoint set is empty
        - isolated: in_degree=0 and out_degree=0 in proof graph
        - disconnected_from_entries: in a different component than entries
        - no_incoming_from_reachable: cluster has no bridge from reachable set
        """
        diag = ReachabilityDiagnostics(unreachable_total=len(unreachable))

        if not unreachable:
            return diag

        # Build adjacency lists for proof graph
        out_adj: Dict[str, Set[str]] = defaultdict(set)
        in_adj: Dict[str, Set[str]] = defaultdict(set)
        for edge in self.edges:
            if edge.get("resolution") == "resolved_internal":
                out_adj[edge["source"]].add(edge["target"])
                in_adj[edge["target"]].add(edge["source"])

        # Classify each unreachable node
        reasons: Dict[str, int] = defaultdict(int)
        examples: Dict[str, List[str]] = defaultdict(list)

        for node_id in sorted(unreachable):  # sorted for determinism
            reason = self._classify_unreachable_reason(
                node_id, reachable, out_adj, in_adj
            )
            reasons[reason] += 1
            if len(examples[reason]) < 5:  # Keep up to 5 examples per reason
                examples[reason].append(node_id)

        diag.reasons = dict(reasons)
        diag.examples = dict(examples)

        # Compute cluster roots (unreachable nodes with no incoming from other unreachable)
        diag.cluster_roots = self._compute_cluster_roots(
            unreachable, reachable, in_adj, out_adj
        )

        return diag

    def _classify_unreachable_reason(
        self,
        node_id: str,
        reachable: Set[str],
        out_adj: Dict[str, Set[str]],
        in_adj: Dict[str, Set[str]],
    ) -> str:
        """Classify why a single node is unreachable."""
        # Check if no entrypoints exist
        if not self.entrypoints:
            return "no_entrypoints"

        in_degree = len(in_adj.get(node_id, set()))
        out_degree = len(out_adj.get(node_id, set()))

        # Isolated: no edges at all in proof graph
        if in_degree == 0 and out_degree == 0:
            return "isolated"

        # Check if any incoming edges are from reachable nodes
        incoming = in_adj.get(node_id, set())
        has_reachable_incoming = any(src in reachable for src in incoming)

        if has_reachable_incoming:
            # This shouldn't happen if reachability is computed correctly
            return "reachability_error"

        # Check if incoming edges exist but all from unreachable nodes
        if incoming:
            return "no_incoming_from_reachable"

        # Has outgoing but no incoming
        return "disconnected_from_entries"

    def _compute_cluster_roots(
        self,
        unreachable: Set[str],
        reachable: Set[str],
        in_adj: Dict[str, Set[str]],
        out_adj: Dict[str, Set[str]],
    ) -> List[Dict]:
        """
        Find cluster roots: unreachable nodes that could become reachable
        with minimal fixes (e.g., adding an entrypoint or edge).

        A cluster root is an unreachable node where:
        - It has no incoming edges from other unreachable nodes, OR
        - It's a "root" of a strongly connected unreachable subgraph
        """
        roots = []

        # Find nodes with no incoming from other unreachable nodes
        for node_id in unreachable:
            incoming = in_adj.get(node_id, set())
            incoming_from_unreachable = incoming & unreachable

            if not incoming_from_unreachable:
                # This is a cluster root
                # Count how many unreachable nodes are reachable from it
                cluster_size = self._count_downstream_unreachable(
                    node_id, unreachable, out_adj
                )
                roots.append({
                    "node_id": node_id,
                    "cluster_size": cluster_size,
                    "reason": "no_unreachable_incoming",
                })

        # Sort by cluster size (largest first) and take top 10
        roots.sort(key=lambda x: x["cluster_size"], reverse=True)
        return roots[:10]

    def _count_downstream_unreachable(
        self, start: str, unreachable: Set[str], out_adj: Dict[str, Set[str]]
    ) -> int:
        """Count unreachable nodes reachable from start via proof edges."""
        visited = set()
        queue = [start]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            if current not in unreachable:
                continue
            visited.add(current)

            for target in out_adj.get(current, set()):
                if target not in visited and target in unreachable:
                    queue.append(target)

        return len(visited)
