#!/usr/bin/env python3
"""
🔍 REDUNDANCY DETECTOR
Find duplicate-purpose code and over-engineering patterns.

Detects:
1. Semantic Duplicates - Functions with similar names doing likely same thing
2. Structural Duplicates - Functions with identical call patterns
3. Over-Engineering - Wrappers that just pass-through, unnecessary abstractions
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher

try:
    import networkx as nx
except ImportError:
    nx = None


@dataclass
class DuplicateGroup:
    """A group of potentially duplicate functions."""
    reason: str
    confidence: float
    members: list = field(default_factory=list)
    recommendation: str = ""


@dataclass
class OverEngineeringSignal:
    """A signal of potential over-engineering."""
    node_id: str
    name: str
    file: str
    signal_type: str
    evidence: str
    severity: str  # low, medium, high


def load_semantic_ids(path: str | Path) -> list[dict]:
    """Load semantic IDs from JSON file."""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Handle both list and dict formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # If it's a dict with 'ids' key
        if "ids" in data:
            return data["ids"]
        # If it's a dict of id -> info
        return [{"id": k, **v} for k, v in data.items()]
    return []


def extract_name_from_id(semantic_id: str) -> str:
    """Extract the function/class name from a semantic ID."""
    # Format: LOG.FNC.M|server.js|functionName|calls:4|...
    parts = semantic_id.split("|")
    if len(parts) >= 3:
        return parts[2]
    return semantic_id


def normalize_name(name: str) -> str:
    """Normalize a function name for comparison."""
    # Remove common prefixes/suffixes
    name = re.sub(r"^(get|set|is|has|can|do|on|handle|process)", "", name, flags=re.I)
    name = re.sub(r"(Handler|Callback|Listener|Wrapper|Helper|Util|Utils)$", "", name, flags=re.I)
    # Convert to lowercase for comparison
    return name.lower()


def find_semantic_duplicates(semantic_ids: list[dict], threshold: float = 0.8) -> list[DuplicateGroup]:
    """
    Find functions with very similar names that might be duplicates.
    
    Uses fuzzy string matching on normalized function names.
    """
    groups = []
    seen = set()
    
    # Extract all function names with their IDs
    functions = []
    for item in semantic_ids:
        sid = item.get("id", item) if isinstance(item, dict) else item
        if "|" in sid:
            name = extract_name_from_id(sid)
            file = sid.split("|")[1] if len(sid.split("|")) > 1 else ""
            functions.append({"id": sid, "name": name, "file": file, "normalized": normalize_name(name)})
    
    # Group by similarity
    for i, func1 in enumerate(functions):
        if func1["id"] in seen:
            continue
            
        similar = [func1]
        for j, func2 in enumerate(functions[i+1:], i+1):
            if func2["id"] in seen:
                continue
            
            # Check name similarity
            ratio = SequenceMatcher(None, func1["normalized"], func2["normalized"]).ratio()
            
            # Also check if names are substrings of each other
            if len(func1["normalized"]) > 3 and len(func2["normalized"]) > 3:
                if func1["normalized"] in func2["normalized"] or func2["normalized"] in func1["normalized"]:
                    ratio = max(ratio, 0.85)
            
            if ratio >= threshold:
                similar.append(func2)
                seen.add(func2["id"])
        
        if len(similar) > 1:
            seen.add(func1["id"])
            group = DuplicateGroup(
                reason="Similar function names",
                confidence=threshold,
                members=[{"id": f["id"], "name": f["name"], "file": f["file"]} for f in similar],
                recommendation=f"Review these {len(similar)} functions for consolidation"
            )
            groups.append(group)
    
    return groups


def find_structural_duplicates(G: "nx.DiGraph", min_degree: int = 2) -> list[DuplicateGroup]:
    """
    Find functions with identical call signatures (same in/out edges).
    
    If two functions call the exact same set of other functions,
    they might be doing the same thing.
    """
    if nx is None:
        return []
    
    groups = []
    
    # Build call signature for each node
    signatures = {}
    for node in G.nodes():
        if G.out_degree(node) >= min_degree:
            # Signature = sorted tuple of callees
            callees = tuple(sorted(G.successors(node)))
            if callees:
                if callees not in signatures:
                    signatures[callees] = []
                signatures[callees].append(node)
    
    # Find duplicate signatures
    for callees, nodes in signatures.items():
        if len(nodes) > 1:
            members = []
            for node_id in nodes:
                name = node_id.split("|")[-2] if "|" in node_id else node_id
                file = node_id.split("|")[1] if "|" in node_id and len(node_id.split("|")) > 1 else ""
                members.append({"id": node_id, "name": name, "file": file})
            
            group = DuplicateGroup(
                reason=f"Identical call pattern ({len(callees)} shared callees)",
                confidence=0.9,
                members=members,
                recommendation="These functions call the exact same dependencies—likely duplicates"
            )
            groups.append(group)
    
    return groups


def find_over_engineering(G: "nx.DiGraph", semantic_ids: list[dict]) -> list[OverEngineeringSignal]:
    """
    Detect over-engineering patterns:
    
    1. Pass-through wrappers: Functions that call exactly 1 thing
    2. Unnecessary abstractions: Many tiny functions with few calls
    3. God class indicators: Functions with huge fan-out
    """
    signals = []
    
    if nx is None:
        return signals
    
    for node in G.nodes():
        in_deg = G.in_degree(node)
        out_deg = G.out_degree(node)
        name = node.split("|")[-2] if "|" in node else node
        file = node.split("|")[1] if "|" in node and len(node.split("|")) > 1 else ""
        
        # Skip builtins and very short names (likely minified)
        if len(name) <= 2 or name in ("n", "e", "t", "r"):
            continue
        
        # 1. Pass-through wrapper: calls exactly 1 thing, used by many
        if out_deg == 1 and in_deg >= 3:
            callee = list(G.successors(node))[0]
            callee_name = callee.split("|")[-2] if "|" in callee else callee
            signals.append(OverEngineeringSignal(
                node_id=node,
                name=name,
                file=file,
                signal_type="pass_through_wrapper",
                evidence=f"Only calls `{callee_name}`, used {in_deg} times",
                severity="low"
            ))
        
        # 2. Tiny function used once: possibly unnecessary abstraction
        if in_deg == 1 and out_deg <= 1:
            # Check if name suggests it's a helper
            if any(x in name.lower() for x in ["helper", "util", "wrapper", "do", "internal"]):
                signals.append(OverEngineeringSignal(
                    node_id=node,
                    name=name,
                    file=file,
                    signal_type="single_use_helper",
                    evidence=f"Used only once, calls {out_deg} functions",
                    severity="low"
                ))
        
        # 3. God function: extremely high fan-out
        if out_deg > 50:
            signals.append(OverEngineeringSignal(
                node_id=node,
                name=name,
                file=file,
                signal_type="god_function",
                evidence=f"Calls {out_deg} other functions—too many responsibilities",
                severity="high"
            ))
    
    return signals


def generate_redundancy_report(
    semantic_duplicates: list[DuplicateGroup],
    structural_duplicates: list[DuplicateGroup],
    over_engineering: list[OverEngineeringSignal],
    output_path: str | Path = None
) -> str:
    """Generate a markdown report of findings."""
    
    lines = [
        "# 🔍 Redundancy & Over-Engineering Report",
        "",
        f"| Category | Count |",
        f"|----------|------:|",
        f"| Semantic Duplicate Groups | {len(semantic_duplicates)} |",
        f"| Structural Duplicate Groups | {len(structural_duplicates)} |",
        f"| Over-Engineering Signals | {len(over_engineering)} |",
        "",
    ]
    
    # Semantic duplicates
    if semantic_duplicates:
        lines.extend([
            "---",
            "",
            "## 🔤 Semantic Duplicates (Similar Names)",
            "",
            "Functions with very similar names that might be doing the same thing.",
            "",
        ])
        for i, group in enumerate(semantic_duplicates[:15], 1):
            names = [m["name"] for m in group.members]
            files = set(m["file"] for m in group.members)
            lines.append(f"**{i}. {', '.join(names[:3])}{'...' if len(names) > 3 else ''}**")
            lines.append(f"   - Files: {', '.join(list(files)[:3])}")
            lines.append(f"   - Count: {len(group.members)}")
            lines.append("")
    
    # Structural duplicates
    if structural_duplicates:
        lines.extend([
            "---",
            "",
            "## 🔗 Structural Duplicates (Same Call Pattern)",
            "",
            "Functions that call the exact same set of dependencies.",
            "",
        ])
        for i, group in enumerate(structural_duplicates[:10], 1):
            names = [m["name"] for m in group.members]
            lines.append(f"**{i}. {', '.join(names[:4])}**")
            lines.append(f"   - {group.reason}")
            lines.append("")
    
    # Over-engineering
    if over_engineering:
        high = [s for s in over_engineering if s.severity == "high"]
        lines.extend([
            "---",
            "",
            "## ⚠️ Over-Engineering Signals",
            "",
        ])
        
        if high:
            lines.append("### 🚨 High Severity (God Functions)")
            lines.append("")
            lines.append("| Function | File | Evidence |")
            lines.append("|----------|------|----------|")
            for sig in high[:15]:
                lines.append(f"| `{sig.name}` | {sig.file} | {sig.evidence} |")
            lines.append("")
        
        wrappers = [s for s in over_engineering if s.signal_type == "pass_through_wrapper"]
        if wrappers:
            lines.append(f"### 📦 Pass-Through Wrappers ({len(wrappers)} found)")
            lines.append("")
            lines.append("These functions just forward to one other function—consider inlining.")
            lines.append("")
            for sig in wrappers[:10]:
                lines.append(f"- `{sig.name}` ({sig.file}): {sig.evidence}")
            lines.append("")
    
    report = "\n".join(lines)
    
    if output_path:
        Path(output_path).write_text(report, encoding="utf-8")
        print(f"📝 Report saved to: {output_path}")
    
    return report


def analyze_redundancy(graph_path: str | Path, semantic_ids_path: str | Path = None):
    """Run full redundancy analysis."""
    import sys
    from pathlib import Path as P
    # Add parent directory to path for imports
    sys.path.insert(0, str(P(__file__).parent.parent))
    from core.graph_analyzer import load_graph
    
    print("🔍 Running Redundancy Analysis...")
    
    G = load_graph(graph_path)
    
    # Try to find semantic IDs
    semantic_ids = []
    if semantic_ids_path:
        semantic_ids = load_semantic_ids(semantic_ids_path)
    else:
        # Try to find it in the same directory
        graph_dir = Path(graph_path).parent
        candidates = ["semantic_ids.json", "learning_report.json"]
        for candidate in candidates:
            candidate_path = graph_dir / candidate
            if candidate_path.exists():
                semantic_ids = load_semantic_ids(candidate_path)
                if semantic_ids:
                    print(f"   Found semantic IDs in: {candidate}")
                    break
    
    print(f"   Loaded {len(semantic_ids)} semantic IDs")
    
    print("🔤 Finding semantic duplicates...")
    semantic_dups = find_semantic_duplicates(semantic_ids)
    print(f"   Found {len(semantic_dups)} groups")
    
    print("🔗 Finding structural duplicates...")
    structural_dups = find_structural_duplicates(G)
    print(f"   Found {len(structural_dups)} groups")
    
    print("⚠️  Detecting over-engineering...")
    over_eng = find_over_engineering(G, semantic_ids)
    print(f"   Found {len(over_eng)} signals")
    
    return semantic_dups, structural_dups, over_eng


# CLI entry point
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python redundancy_detector.py <graph.json> [--report output.md]")
        sys.exit(1)
    
    graph_path = sys.argv[1]
    output_path = None
    
    if "--report" in sys.argv:
        idx = sys.argv.index("--report")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    
    sem_dups, struct_dups, over_eng = analyze_redundancy(graph_path)
    report = generate_redundancy_report(sem_dups, struct_dups, over_eng, output_path)
    
    if not output_path:
        print(report)
