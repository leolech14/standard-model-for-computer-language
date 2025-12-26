#!/usr/bin/env python3
"""
🧪 TOTALITY TESTS — Verifying τ covers all AST node types

Property 1 (Totality): Every Tree-Sitter AST node of interest maps to at least one atom in A.

This test suite verifies that the particle classifier handles all observed AST node types
without leaving any as "unmapped" or producing errors.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Any

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from tree_sitter_engine import TreeSitterUniversalEngine


@dataclass
class TotalityReport:
    """Report on τ totality coverage."""
    total_node_types: int = 0
    mapped_types: int = 0
    unmapped_types: List[str] = field(default_factory=list)
    fallback_types: List[str] = field(default_factory=list)  # Mapped but low confidence
    coverage_rate: float = 0.0
    is_total: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_node_types": self.total_node_types,
            "mapped_types": self.mapped_types,
            "unmapped_types": self.unmapped_types,
            "fallback_types": self.fallback_types,
            "coverage_rate": round(self.coverage_rate, 4),
            "is_total": self.is_total,
        }


def collect_ast_node_types(repo_path: Path) -> Set[str]:
    """
    Scan a repository and collect all unique AST node types encountered.
    Uses Tree-Sitter to parse files and extract node kinds.
    """
    from tree_sitter_engine import TreeSitterUniversalEngine
    
    engine = TreeSitterUniversalEngine()
    node_types: Set[str] = set()
    
    # Analyze the repo
    results = engine.analyze_directory(str(repo_path))
    
    for file_result in results:
        for particle in file_result.get("particles", []):
            node_kind = particle.get("node_kind") or particle.get("kind") or particle.get("symbol_kind")
            if node_kind:
                node_types.add(node_kind)
    
    return node_types


def test_totality(
    classifier: ParticleClassifier,
    node_types: Set[str],
    fallback_threshold: float = 0.4,
) -> TotalityReport:
    """
    Test that τ maps every node type to an atom.
    
    A node type is considered:
    - Mapped: classifier returns a type != "Unknown" with confidence >= fallback_threshold
    - Fallback: classifier returns a type but with confidence < fallback_threshold
    - Unmapped: classifier returns "Unknown"
    
    Args:
        classifier: The particle classifier to test
        node_types: Set of AST node types to test
        fallback_threshold: Confidence below which a mapping is considered "fallback"
        
    Returns:
        TotalityReport with coverage statistics
    """
    report = TotalityReport(total_node_types=len(node_types))
    
    for node_type in node_types:
        # Create a minimal particle for classification
        test_particle = {
            "name": f"test_{node_type}",
            "kind": node_type,
            "symbol_kind": node_type,
            "line": 1,
            "file_path": "test.py",
        }
        
        # Classify
        classified = classifier.classify_particle(test_particle)
        result_type = classified.get("type", "Unknown")
        confidence = classified.get("confidence", 0.0)
        
        if result_type == "Unknown":
            report.unmapped_types.append(node_type)
        elif confidence < fallback_threshold:
            report.fallback_types.append(f"{node_type} -> {result_type} ({confidence:.2f})")
            report.mapped_types += 1
        else:
            report.mapped_types += 1
    
    # Calculate coverage
    if report.total_node_types > 0:
        report.coverage_rate = report.mapped_types / report.total_node_types
    
    # Totality check: must map ALL types (fallback is ok, unmapped is not)
    report.is_total = len(report.unmapped_types) == 0
    
    return report


def test_determinism(
    classifier: ParticleClassifier,
    test_particles: List[Dict[str, Any]],
    iterations: int = 3,
) -> Dict[str, Any]:
    """
    Test that τ is deterministic: same input always produces same output.
    
    This is critical for reproducibility and caching.
    """
    results: Dict[str, List[str]] = {}  # particle_name -> [result_type, ...]
    
    for _ in range(iterations):
        for particle in test_particles:
            name = particle.get("name", "unknown")
            classified = classifier.classify_particle(particle)
            result_type = classified.get("type", "Unknown")
            
            if name not in results:
                results[name] = []
            results[name].append(result_type)
    
    # Check for consistency
    inconsistent = []
    for name, types in results.items():
        if len(set(types)) > 1:
            inconsistent.append({"name": name, "types": types})
    
    return {
        "particles_tested": len(test_particles),
        "iterations": iterations,
        "is_deterministic": len(inconsistent) == 0,
        "inconsistent": inconsistent,
    }


# =============================================================================
# STANDARD TEST SUITE
# =============================================================================

# These particles are realistic samples that τ MUST classify
STANDARD_TEST_PARTICLES = [
    # Domain Layer
    {"name": "UserEntity", "kind": "class", "symbol_kind": "class", "file_path": "domain/user.py"},
    {"name": "Money", "kind": "class", "symbol_kind": "class", "file_path": "domain/value_objects.py"},
    {"name": "OrderAggregate", "kind": "class", "symbol_kind": "class", "file_path": "domain/order.py"},
    
    # Application Layer
    {"name": "CreateUserUseCase", "kind": "class", "symbol_kind": "class", "file_path": "application/usecases.py"},
    {"name": "CreateOrderCommand", "kind": "class", "symbol_kind": "class", "file_path": "application/commands.py"},
    {"name": "GetOrderQuery", "kind": "class", "symbol_kind": "class", "file_path": "application/queries.py"},
    {"name": "handle_order_created", "kind": "function", "symbol_kind": "function", "file_path": "application/handlers.py"},
    
    # Infrastructure
    {"name": "UserRepository", "kind": "class", "symbol_kind": "class", "file_path": "infrastructure/repositories.py"},
    {"name": "PostgresUserRepository", "kind": "class", "symbol_kind": "class", "file_path": "infrastructure/postgres_repo.py"},
    {"name": "PaymentGateway", "kind": "class", "symbol_kind": "class", "file_path": "infrastructure/gateways.py"},
    {"name": "EmailAdapter", "kind": "class", "symbol_kind": "class", "file_path": "infrastructure/adapters.py"},
    
    # Presentation
    {"name": "UserController", "kind": "class", "symbol_kind": "class", "file_path": "presentation/controllers.py"},
    {"name": "get_user", "kind": "function", "symbol_kind": "function", "file_path": "api/endpoints.py"},
    
    # Utilities
    {"name": "validate_email", "kind": "function", "symbol_kind": "function", "file_path": "utils/validators.py"},
    {"name": "UserFactory", "kind": "class", "symbol_kind": "class", "file_path": "factories.py"},
    {"name": "DatabaseConfig", "kind": "class", "symbol_kind": "class", "file_path": "config/database.py"},
    
    # Basic constructs (should classify as basic types)
    {"name": "main", "kind": "function", "symbol_kind": "function", "file_path": "main.py"},
    {"name": "test_user_creation", "kind": "function", "symbol_kind": "function", "file_path": "tests/test_user.py"},
]


def run_standard_tests() -> Dict[str, Any]:
    """Run the standard totality test suite."""
    print("=" * 70)
    print("🧪 TOTALITY TEST SUITE")
    print("=" * 70)
    
    engine = TreeSitterUniversalEngine()
    
    # Test 1: Standard DDD Particles
    print("\n📋 Test 1: Standard DDD Particles")
    print("-" * 40)
    
    mapped = 0
    unmapped = []
    results_detail = []
    
    for particle in STANDARD_TEST_PARTICLES:
        # Use the actual τ function (type assignment)
        classified = engine._classify_extracted_symbol(
            name=particle["name"],
            symbol_kind=particle.get("symbol_kind", particle.get("kind", "class")),
            file_path=particle["file_path"],
            line_num=1,
            evidence="",
            parent="",
            base_classes=[],
            decorators=[],
        )
        result_type = classified.get("type", "Unknown")
        confidence = classified.get("confidence", 0.0)
        
        if result_type == "Unknown":
            unmapped.append(particle["name"])
        else:
            mapped += 1
        
        results_detail.append({
            "name": particle["name"],
            "type": result_type,
            "confidence": confidence,
        })
    
    total = len(STANDARD_TEST_PARTICLES)
    coverage = mapped / total if total > 0 else 0.0
    
    print(f"   Total particles: {total}")
    print(f"   Mapped: {mapped}")
    print(f"   Coverage: {coverage:.1%}")
    print(f"   Totality: {'✅ PASS' if not unmapped else '❌ FAIL'}")
    
    if unmapped:
        print(f"   Unmapped: {unmapped}")
    else:
        print("   All particles classified!")
    
    # Show sample classifications
    print("\n   Sample classifications:")
    for r in results_detail[:5]:
        print(f"     {r['name']} -> {r['type']} ({r['confidence']:.0%})")
    
    # Test 2: Determinism
    print("\n📋 Test 2: Determinism")
    print("-" * 40)
    
    # Run classification 3 times and check for consistency
    iterations = 3
    results_by_name: Dict[str, List[str]] = {}
    
    for _ in range(iterations):
        for particle in STANDARD_TEST_PARTICLES:
            classified = engine._classify_extracted_symbol(
                name=particle["name"],
                symbol_kind=particle.get("symbol_kind", particle.get("kind", "class")),
                file_path=particle["file_path"],
                line_num=1,
                evidence="",
                parent="",
                base_classes=[],
                decorators=[],
            )
            result_type = classified.get("type", "Unknown")
            
            name = particle["name"]
            if name not in results_by_name:
                results_by_name[name] = []
            results_by_name[name].append(result_type)
    
    # Check for consistency
    inconsistent = []
    for name, types in results_by_name.items():
        if len(set(types)) > 1:
            inconsistent.append({"name": name, "types": types})
    
    is_deterministic = len(inconsistent) == 0
    
    print(f"   Particles tested: {total}")
    print(f"   Iterations: {iterations}")
    print(f"   Deterministic: {'✅ PASS' if is_deterministic else '❌ FAIL'}")
    
    if inconsistent:
        print(f"   Inconsistent: {inconsistent}")
    
    # Summary
    print("\n" + "=" * 70)
    is_total = len(unmapped) == 0
    all_passed = is_total and is_deterministic
    print(f"{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("=" * 70)
    
    return {
        "totality": {
            "total_particles": total,
            "mapped": mapped,
            "unmapped": unmapped,
            "coverage_rate": round(coverage, 4),
            "is_total": is_total,
            "classifications": results_detail,
        },
        "determinism": {
            "particles_tested": total,
            "iterations": iterations,
            "is_deterministic": is_deterministic,
            "inconsistent": inconsistent,
        },
        "all_passed": all_passed,
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run τ totality tests")
    parser.add_argument("--repo", help="Test against a specific repository")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if args.repo:
        # Test against a real repo
        repo_path = Path(args.repo)
        if not repo_path.exists():
            print(f"Error: Repository not found: {repo_path}")
            sys.exit(1)
        
        print(f"Collecting AST node types from: {repo_path}")
        node_types = collect_ast_node_types(repo_path)
        print(f"Found {len(node_types)} unique node types")
        
        classifier = ParticleClassifier()
        report = test_totality(classifier, node_types)
        
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(f"\nTotality Report:")
            print(f"  Coverage: {report.coverage_rate:.1%}")
            print(f"  Unmapped: {report.unmapped_types}" if report.unmapped_types else "  All types mapped!")
    else:
        # Run standard tests
        results = run_standard_tests()
        
        if args.json:
            print(json.dumps(results, indent=2))
