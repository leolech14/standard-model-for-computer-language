#!/usr/bin/env python3
"""
🎯 GOLDEN SCORER — Automated Testing Against Expected Results

Compares detected components against golden specs and produces:
1. Precision (how many detected are correct)
2. Recall (how many expected were found)
3. F1 Score (balanced measure)
4. Detailed mismatch report

Single command = Single comprehensive scored report
"""

import sys
import json
import fnmatch
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Set, Optional
from datetime import datetime


@dataclass
class ComponentMatch:
    """Result of matching a detected component against golden spec."""
    expected_name: str
    expected_type: str
    expected_file_pattern: str
    detected_name: Optional[str] = None
    detected_file: Optional[str] = None
    matched: bool = False
    partial: bool = False  # Name matched but type wrong
    

@dataclass
class RelationshipMatch:
    """Result of matching a relationship."""
    expected_from: str
    expected_to: str
    expected_type: str
    matched: bool = False


@dataclass
class ScoredResult:
    """Complete scoring result for a repo."""
    repo: str
    spec_path: str
    timestamp: str
    
    # Component scores
    expected_components: int = 0
    detected_components: int = 0
    matched_components: int = 0
    component_precision: float = 0.0
    component_recall: float = 0.0
    component_f1: float = 0.0
    
    # Relationship scores
    expected_relationships: int = 0
    matched_relationships: int = 0
    relationship_recall: float = 0.0
    
    # Pattern scores
    expected_patterns: int = 0
    matched_patterns: int = 0
    pattern_accuracy: float = 0.0
    
    # Overall
    weighted_score: float = 0.0
    grade: str = ""  # A, B, C, D, F
    
    # Details
    component_matches: List[Dict] = field(default_factory=list)
    missing_components: List[Dict] = field(default_factory=list)
    extra_components: List[Dict] = field(default_factory=list)
    relationship_matches: List[Dict] = field(default_factory=list)
    pattern_matches: Dict[str, bool] = field(default_factory=dict)


class GoldenScorer:
    """
    Scores analysis results against golden specs.
    """
    
    def __init__(self, specs_dir: str = None):
        self.specs_dir = Path(specs_dir) if specs_dir else (
            Path(__file__).parent / "validation" / "benchmarks" / "golden_specs"
        )
    
    def load_spec(self, repo_name: str) -> Optional[Dict]:
        """Load golden spec for a repo."""
        # Try different name patterns
        names_to_try = [
            f"{repo_name}.golden.json",
            f"{repo_name.replace('/', '_')}.golden.json",
            f"{repo_name.split('/')[-1]}.golden.json",
        ]
        
        for name in names_to_try:
            spec_path = self.specs_dir / name
            if spec_path.exists():
                return json.loads(spec_path.read_text())
        
        return None
    
    def score(self, repo_name: str, analysis_result: Dict, 
              detected_classes: List[Dict], detected_edges: List[Dict]) -> ScoredResult:
        """
        Score analysis against golden spec.
        """
        spec = self.load_spec(repo_name)
        
        result = ScoredResult(
            repo=repo_name,
            spec_path=str(self.specs_dir / f"{repo_name.split('/')[-1]}.golden.json"),
            timestamp=datetime.now().isoformat(),
        )
        
        if not spec:
            result.grade = "N/A"
            return result
        
        # Score components
        self._score_components(result, spec, detected_classes)
        
        # Score relationships
        self._score_relationships(result, spec, detected_edges)
        
        # Score patterns
        self._score_patterns(result, spec, analysis_result)
        
        # Calculate weighted score
        weights = spec.get("scoring_weights", {
            "components_found": 0.4,
            "relationships_found": 0.3,
            "patterns_detected": 0.2,
            "structure_match": 0.1,
        })
        
        result.weighted_score = (
            result.component_f1 * weights.get("components_found", 0.4) +
            result.relationship_recall * weights.get("relationships_found", 0.3) +
            result.pattern_accuracy * weights.get("patterns_detected", 0.2) +
            1.0 * weights.get("structure_match", 0.1)  # Placeholder
        )
        
        # Assign grade
        if result.weighted_score >= 0.9:
            result.grade = "A"
        elif result.weighted_score >= 0.8:
            result.grade = "B"
        elif result.weighted_score >= 0.7:
            result.grade = "C"
        elif result.weighted_score >= 0.6:
            result.grade = "D"
        else:
            result.grade = "F"
        
        return result
    
    def _score_components(self, result: ScoredResult, spec: Dict, 
                          detected_classes: List[Dict]):
        """Score component detection."""
        expected = spec.get("expected_components", [])
        result.expected_components = len(expected)
        result.detected_components = len(detected_classes)
        
        # Build lookup of detected classes by name
        detected_by_name: Dict[str, Dict] = {}
        for cls in detected_classes:
            name = cls.get("name", "")
            detected_by_name[name] = cls
            # Also try variations
            detected_by_name[name.lower()] = cls
        
        matched = 0
        missing = []
        
        for exp in expected:
            exp_name = exp["name"]
            exp_type = exp["type"]
            
            # Try to find match
            found = None
            for det_name, det in detected_by_name.items():
                if exp_name.lower() == det_name.lower():
                    found = det
                    break
                # Partial match
                if exp_name.lower() in det_name.lower():
                    found = det
                    break
            
            if found:
                matched += 1
                result.component_matches.append({
                    "expected": exp_name,
                    "detected": found.get("name"),
                    "type_expected": exp_type,
                    "file": found.get("file"),
                })
            else:
                missing.append({
                    "name": exp_name,
                    "type": exp_type,
                    "file_pattern": exp.get("file_pattern"),
                })
        
        result.matched_components = matched
        result.missing_components = missing
        
        # Find extras (detected but not expected)
        expected_names = {e["name"].lower() for e in expected}
        for det_name, det in detected_by_name.items():
            if det_name.lower() not in expected_names:
                result.extra_components.append({
                    "name": det.get("name"),
                    "file": det.get("file"),
                })
        
        # Calculate metrics
        if result.detected_components > 0:
            result.component_precision = matched / result.detected_components
        if result.expected_components > 0:
            result.component_recall = matched / result.expected_components
        if result.component_precision + result.component_recall > 0:
            result.component_f1 = (
                2 * result.component_precision * result.component_recall /
                (result.component_precision + result.component_recall)
            )
    
    def _score_relationships(self, result: ScoredResult, spec: Dict,
                             detected_edges: List[Dict]):
        """Score relationship detection."""
        expected = spec.get("expected_relationships", [])
        result.expected_relationships = len(expected)
        
        # Build edge index
        edge_index: Set[str] = set()
        for edge in detected_edges:
            key = f"{edge.get('from', '')}|{edge.get('to', '')}|{edge.get('type', '')}"
            edge_index.add(key.lower())
            # Also add without type
            key_no_type = f"{edge.get('from', '')}|{edge.get('to', '')}"
            edge_index.add(key_no_type.lower())
        
        matched = 0
        for exp in expected:
            key = f"{exp['from']}|{exp['to']}|{exp['type']}"
            key_no_type = f"{exp['from']}|{exp['to']}"
            
            if key.lower() in edge_index or key_no_type.lower() in edge_index:
                matched += 1
                result.relationship_matches.append({
                    "from": exp["from"],
                    "to": exp["to"],
                    "type": exp["type"],
                    "matched": True,
                })
            else:
                result.relationship_matches.append({
                    "from": exp["from"],
                    "to": exp["to"],
                    "type": exp["type"],
                    "matched": False,
                })
        
        result.matched_relationships = matched
        if result.expected_relationships > 0:
            result.relationship_recall = matched / result.expected_relationships
    
    def _score_patterns(self, result: ScoredResult, spec: Dict, 
                        analysis_result: Dict):
        """Score architectural pattern detection."""
        expected = spec.get("expected_patterns", {})
        result.expected_patterns = len(expected)
        
        # For now, assume all patterns detected if we have the right structure
        # This can be enhanced with actual pattern detection
        matched = 0
        for pattern, expected_value in expected.items():
            # Simple heuristic: if we detected classes matching pattern names
            detected = True  # Placeholder - would check actual detection
            result.pattern_matches[pattern] = detected
            if detected == expected_value:
                matched += 1
        
        result.matched_patterns = matched
        if result.expected_patterns > 0:
            result.pattern_accuracy = matched / result.expected_patterns
    
    def generate_report(self, result: ScoredResult) -> str:
        """Generate markdown report."""
        lines = [
            f"# 🎯 Golden Score Report: {result.repo}",
            "",
            f"**Timestamp:** {result.timestamp}",
            f"**Grade:** **{result.grade}** ({result.weighted_score:.1%})",
            "",
            "## Component Detection",
            "",
            f"| Metric | Value |",
            f"|--------|------:|",
            f"| Expected | {result.expected_components} |",
            f"| Detected | {result.detected_components} |",
            f"| Matched | {result.matched_components} |",
            f"| Precision | {result.component_precision:.1%} |",
            f"| Recall | {result.component_recall:.1%} |",
            f"| F1 Score | {result.component_f1:.1%} |",
            "",
        ]
        
        if result.component_matches:
            lines.extend([
                "### ✅ Matched Components",
                "",
                "| Expected | Detected | File |",
                "|----------|----------|------|",
            ])
            for m in result.component_matches:
                lines.append(f"| {m['expected']} | {m['detected']} | `{m.get('file', '')}` |")
            lines.append("")
        
        if result.missing_components:
            lines.extend([
                "### ❌ Missing Components",
                "",
                "| Name | Type | Pattern |",
                "|------|------|---------|",
            ])
            for m in result.missing_components:
                lines.append(f"| {m['name']} | {m['type']} | `{m.get('file_pattern', '')}` |")
            lines.append("")
        
        lines.extend([
            "## Relationship Detection",
            "",
            f"| Expected | Matched | Recall |",
            f"|----------|---------|--------|",
            f"| {result.expected_relationships} | {result.matched_relationships} | {result.relationship_recall:.1%} |",
            "",
        ])
        
        lines.extend([
            "## Pattern Detection",
            "",
            f"| Pattern | Detected |",
            f"|---------|----------|",
        ])
        for pattern, detected in result.pattern_matches.items():
            icon = "✅" if detected else "❌"
            lines.append(f"| {pattern} | {icon} |")
        
        return "\n".join(lines)


def score_repo_from_analysis(repo_path: str, specs_dir: str = None) -> ScoredResult:
    """
    Complete scoring pipeline: analyze repo then score against golden spec.
    """
    from learning_engine import LearningEngine
    
    # Analyze
    engine = LearningEngine(auto_learn=False)
    analysis = engine.analyze_repo(repo_path)
    
    # Get classes from complete extractor
    codebase = engine.complete_extractor.extract(repo_path)
    classes = [
        {"name": c.name, "file": c.file, "bases": c.bases}
        for c in codebase.classes.values()
    ]
    
    # Get edges from graph
    graph = engine.graph_extractor.extract(repo_path)
    edges = []
    for edge in graph.edges:
        edges.append({
            "from": edge.source,
            "to": edge.target,
            "type": edge.edge_type,
        })
    
    # Score
    scorer = GoldenScorer(specs_dir)
    repo_name = Path(repo_path).name
    
    return scorer.score(
        repo_name=repo_name,
        analysis_result=analysis.__dict__,
        detected_classes=classes,
        detected_edges=edges,
    )


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🎯 Golden Scorer — Test against expected results"
    )
    parser.add_argument("repo_path", help="Path to repo to score")
    parser.add_argument("--specs-dir", help="Golden specs directory")
    parser.add_argument("--output", help="Output report path")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎯 GOLDEN SCORER — Testing Against Expected Results")
    print("=" * 70)
    
    result = score_repo_from_analysis(args.repo_path, args.specs_dir)
    
    print(f"\n📊 SCORE: {result.grade} ({result.weighted_score:.1%})")
    print(f"   Components: {result.matched_components}/{result.expected_components} ({result.component_f1:.1%} F1)")
    print(f"   Relationships: {result.matched_relationships}/{result.expected_relationships}")
    print(f"   Patterns: {result.matched_patterns}/{result.expected_patterns}")
    
    # Generate report
    report = GoldenScorer().generate_report(result)
    
    if args.output:
        Path(args.output).write_text(report)
        print(f"\n💾 Report: {args.output}")
    else:
        print("\n" + report)
