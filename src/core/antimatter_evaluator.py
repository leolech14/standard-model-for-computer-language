#!/usr/bin/env python3
"""
⚛️ ANTIMATTER EVALUATOR — Machine-Executable Constraint Checker

This module evaluates the 11 canonical antimatter laws against analyzed particles.
Each law is defined in data/LAW_11_CANONICAL.json with executable patterns.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Path to canonical laws
LAWS_PATH = Path(__file__).parent.parent / "data" / "LAW_11_CANONICAL.json"


@dataclass
class Violation:
    """A detected antimatter violation."""
    law_id: str
    law_name: str
    particle_id: str
    particle_name: str
    particle_type: str
    file_path: str
    line: int
    message: str
    severity: str  # error, warning, info
    confidence: float
    evidence: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Result of evaluating all laws against a particle set."""
    total_particles: int
    laws_checked: int
    violations: List[Violation] = field(default_factory=list)
    by_law: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_particles": self.total_particles,
            "laws_checked": self.laws_checked,
            "total_violations": len(self.violations),
            "by_law": self.by_law,
            "by_severity": self.by_severity,
            "violations": [
                {
                    "law_id": v.law_id,
                    "law_name": v.law_name,
                    "particle": v.particle_name,
                    "type": v.particle_type,
                    "file": v.file_path,
                    "line": v.line,
                    "message": v.message,
                    "severity": v.severity,
                    "confidence": v.confidence,
                }
                for v in self.violations
            ],
        }


class AntimatterEvaluator:
    """
    Evaluates particles against the 11 canonical antimatter laws.
    
    Each law is evaluated using pattern matching defined in data/LAW_11_CANONICAL.json.
    """
    
    def __init__(self, laws_path: Path = LAWS_PATH):
        self.laws = self._load_laws(laws_path)
    
    def _load_laws(self, path: Path) -> List[Dict[str, Any]]:
        """Load laws from JSON file."""
        if not path.exists():
            print(f"Warning: Laws file not found: {path}")
            return []
        return json.loads(path.read_text())
    
    def evaluate(
        self,
        particles: List[Dict[str, Any]],
        threshold: float = 0.55,
    ) -> EvaluationResult:
        """
        Evaluate all laws against all particles.
        
        Args:
            particles: List of particle dicts with type, edges, etc.
            threshold: Minimum confidence to report violations
            
        Returns:
            EvaluationResult with all violations
        """
        result = EvaluationResult(
            total_particles=len(particles),
            laws_checked=len(self.laws),
        )
        
        for law in self.laws:
            law_violations = self._evaluate_law(law, particles, threshold)
            result.violations.extend(law_violations)
            result.by_law[law["id"]] = len(law_violations)
        
        # Count by severity
        for v in result.violations:
            result.by_severity[v.severity] = result.by_severity.get(v.severity, 0) + 1
        
        return result
    
    def _evaluate_law(
        self,
        law: Dict[str, Any],
        particles: List[Dict[str, Any]],
        threshold: float,
    ) -> List[Violation]:
        """Evaluate a single law against all particles."""
        violations = []
        pattern = law.get("pattern", {})
        particle_types = pattern.get("particle_types", law.get("scope", []))
        law_threshold = law.get("threshold", threshold)
        
        for particle in particles:
            p_type = particle.get("type", "Unknown")
            p_conf = particle.get("confidence", 0.5)
            
            # Skip if particle type doesn't match law scope
            if p_type not in particle_types:
                continue
            
            # Skip if confidence too low
            if p_conf < law_threshold:
                continue
            
            # Check for violations
            violation = self._check_particle(law, pattern, particle)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_particle(
        self,
        law: Dict[str, Any],
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
    ) -> Optional[Violation]:
        """Check if a particle violates the law."""
        
        evidence = []
        is_violation = False
        
        # Check forbidden edges
        forbidden_edges = pattern.get("forbidden_edges", [])
        if forbidden_edges:
            particle_edges = self._get_edge_types(particle)
            for edge in forbidden_edges:
                if edge in particle_edges:
                    is_violation = True
                    evidence.append(f"Has forbidden edge: {edge}")
        
        # Check forbidden imports
        forbidden_imports = pattern.get("forbidden_imports", [])
        if forbidden_imports:
            particle_imports = self._get_imports(particle)
            for imp in forbidden_imports:
                if any(imp in i for i in particle_imports):
                    is_violation = True
                    evidence.append(f"Has forbidden import: {imp}")
        
        # Check forbidden calls
        forbidden_calls = pattern.get("forbidden_calls", [])
        if forbidden_calls:
            particle_calls = self._get_calls(particle)
            for call in forbidden_calls:
                if any(call in c for c in particle_calls):
                    is_violation = True
                    evidence.append(f"Has forbidden call: {call}")
        
        # Check forbidden methods
        forbidden_methods = pattern.get("forbidden_methods", [])
        if forbidden_methods:
            particle_methods = self._get_methods(particle)
            for method in forbidden_methods:
                if any(method in m for m in particle_methods):
                    is_violation = True
                    evidence.append(f"Has forbidden method pattern: {method}")
        
        # Check forbidden fields
        forbidden_fields = pattern.get("forbidden_fields", [])
        if forbidden_fields:
            particle_fields = self._get_fields(particle)
            for f in forbidden_fields:
                if f in particle_fields:
                    is_violation = True
                    evidence.append(f"Has forbidden field: {f}")
        
        # Check required fields (inverse - violation if MISSING)
        required_fields = pattern.get("required_fields", [])
        if required_fields:
            particle_fields = self._get_fields(particle)
            has_any = any(f in particle_fields for f in required_fields)
            if not has_any:
                is_violation = True
                evidence.append(f"Missing required field (one of: {required_fields})")
        
        # Check required patterns (inverse - violation if MISSING)
        required_patterns = pattern.get("required_patterns", [])
        if required_patterns:
            code = particle.get("code_excerpt", "") or particle.get("evidence", "")
            has_any = any(p in code for p in required_patterns)
            if not has_any and not pattern.get("inversion"):
                is_violation = True
                evidence.append(f"Missing required pattern (one of: {required_patterns})")
        
        # Check inversion (law checks for PRESENCE of required things)
        if pattern.get("inversion"):
            required_edges = pattern.get("required_edges", [])
            if required_edges:
                particle_edges = self._get_edge_types(particle)
                has_any = any(e in particle_edges for e in required_edges)
                if not has_any:
                    is_violation = True
                    evidence.append(pattern.get("inversion_message", "Missing required edges"))
        
        if not is_violation:
            return None
        
        return Violation(
            law_id=law["id"],
            law_name=law["name"],
            particle_id=particle.get("id", "unknown"),
            particle_name=particle.get("name", "unknown"),
            particle_type=particle.get("type", "Unknown"),
            file_path=particle.get("file_path", ""),
            line=particle.get("line", 0),
            message=law["statement"],
            severity=law.get("severity", "warning"),
            confidence=particle.get("confidence", 0.5),
            evidence=evidence,
        )
    
    # ==========================================================================
    # PARTICLE ACCESSORS (extract data from particle dict)
    # ==========================================================================
    
    def _get_edge_types(self, particle: Dict[str, Any]) -> Set[str]:
        """Get edge types from particle."""
        edges = particle.get("edges", []) or particle.get("outgoing_edges", [])
        return {e.get("type", e) if isinstance(e, dict) else str(e) for e in edges}
    
    def _get_imports(self, particle: Dict[str, Any]) -> List[str]:
        """Get imports from particle."""
        return particle.get("imports", []) or []
    
    def _get_calls(self, particle: Dict[str, Any]) -> List[str]:
        """Get function calls from particle."""
        return particle.get("calls", []) or particle.get("called_functions", []) or []
    
    def _get_methods(self, particle: Dict[str, Any]) -> List[str]:
        """Get method names from particle."""
        return particle.get("methods", []) or particle.get("method_names", []) or []
    
    def _get_fields(self, particle: Dict[str, Any]) -> Set[str]:
        """Get field/attribute names from particle."""
        fields = particle.get("fields", []) or particle.get("attributes", []) or []
        return set(fields)


# =============================================================================
# INDIVIDUAL LAW CHECKERS (for use as detector functions)
# =============================================================================

def check_purity_violation(particle: Dict[str, Any], law: Dict[str, Any]) -> Optional[Violation]:
    """L3: Check if a pure function has side effects."""
    evaluator = AntimatterEvaluator.__new__(AntimatterEvaluator)
    evaluator.laws = []
    return evaluator._check_particle(law, law.get("pattern", {}), particle)


def check_command_returns(particle: Dict[str, Any], law: Dict[str, Any]) -> Optional[Violation]:
    """L1: Check if CommandHandler returns domain data."""
    evaluator = AntimatterEvaluator.__new__(AntimatterEvaluator)
    evaluator.laws = []
    return evaluator._check_particle(law, law.get("pattern", {}), particle)


def check_query_mutation(particle: Dict[str, Any], law: Dict[str, Any]) -> Optional[Violation]:
    """L2: Check if QueryHandler mutates state."""
    evaluator = AntimatterEvaluator.__new__(AntimatterEvaluator)
    evaluator.laws = []
    return evaluator._check_particle(law, law.get("pattern", {}), particle)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("⚛️ ANTIMATTER EVALUATOR — Constraint Checker")
    print("=" * 70)
    
    evaluator = AntimatterEvaluator()
    print(f"Loaded {len(evaluator.laws)} laws")
    
    # Demo with sample particles
    sample_particles = [
        {
            "id": "p1",
            "name": "get_user",
            "type": "PureFunction",
            "confidence": 0.8,
            "imports": ["requests"],
            "file_path": "utils.py",
            "line": 10,
        },
        {
            "id": "p2", 
            "name": "UserEntity",
            "type": "Entity",
            "confidence": 0.9,
            "fields": ["name", "email"],  # Missing id!
            "file_path": "domain/user.py",
            "line": 5,
        },
        {
            "id": "p3",
            "name": "CreateUserCommand",
            "type": "Command",
            "confidence": 0.85,
            "file_path": "commands/user.py",
            "line": 1,
        },
    ]
    
    print(f"\nEvaluating {len(sample_particles)} sample particles...")
    result = evaluator.evaluate(sample_particles)
    
    print(f"\n📊 Results:")
    print(f"   Violations: {len(result.violations)}")
    print(f"   By severity: {result.by_severity}")
    print(f"   By law: {result.by_law}")
    
    if result.violations:
        print("\n⚠️ Violations found:")
        for v in result.violations:
            print(f"   [{v.severity.upper()}] {v.law_id}: {v.particle_name} ({v.particle_type})")
            for e in v.evidence:
                print(f"      - {e}")
