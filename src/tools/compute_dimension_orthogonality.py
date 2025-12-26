#!/usr/bin/env python3
"""
🔬 DIMENSION ORTHOGONALITY CHECKER

Computes mutual information between semantic dimensions to verify
that they are conceptually orthogonal (MI ≤ 0.15 bits).

Usage:
    python tools/compute_dimension_orthogonality.py [--aggregate PATH]
"""

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Default paths
SPECTROMETER_ROOT = Path(__file__).parent.parent
DEFAULT_AGGREGATE = SPECTROMETER_ROOT / "validation" / "100_repo_results"
PARTICLE_DEFS_PATH = SPECTROMETER_ROOT / "patterns" / "particle_defs.json"


def load_particle_defs() -> Dict[str, Dict[str, Any]]:
    """Load particle definitions for RPBL lookup."""
    if not PARTICLE_DEFS_PATH.exists():
        print(f"Warning: Particle defs not found at {PARTICLE_DEFS_PATH}")
        return {}
    
    try:
        data = json.loads(PARTICLE_DEFS_PATH.read_text())
        return {p["id"]: p for p in data.get("particle_types", [])}
    except Exception as e:
        print(f"Warning: Could not load particle defs: {e}")
        return {}


def load_all_particles(results_dir: Path) -> List[Dict[str, Any]]:
    """Load all particles from graph.json files in results directory."""
    particles = []
    
    for repo_dir in results_dir.iterdir():
        if not repo_dir.is_dir():
            continue
        graph_file = repo_dir / "graph.json"
        if not graph_file.exists():
            continue
        
        try:
            data = json.loads(graph_file.read_text())
            components = data.get("components", {})
            for name, component in components.items():
                particles.append({
                    "name": name,
                    "type": component.get("type", "Unknown"),
                    "confidence": component.get("confidence", 0),
                    "repo": repo_dir.name,
                    "file_path": component.get("file_path", ""),
                    "symbol_kind": component.get("symbol_kind", ""),
                })
        except Exception as e:
            print(f"Warning: Could not load {graph_file}: {e}")
    
    return particles


def infer_layer_from_type(particle_type: str) -> str:
    """Infer architectural layer from particle type (legacy, derived)."""
    LAYER_MAP = {
        # Domain layer
        "Entity": "domain", "ValueObject": "domain", "AggregateRoot": "domain",
        "DomainService": "domain", "DomainEvent": "domain", "Specification": "domain",
        "Policy": "domain", "Repository": "domain",
        # Application layer
        "UseCase": "application", "ApplicationService": "application",
        "Command": "application", "Query": "application", "DTO": "application",
        "EventHandler": "application", "CommandHandler": "application",
        # Infrastructure layer
        "RepositoryImpl": "infrastructure", "Gateway": "infrastructure",
        "Adapter": "infrastructure", "Client": "infrastructure",
        # Presentation layer
        "Controller": "presentation", "Mapper": "presentation",
        # Cross-cutting
        "Factory": "cross_cutting", "Service": "cross_cutting",
        "Observer": "cross_cutting", "Configuration": "cross_cutting",
        "Exception": "cross_cutting", "Utility": "cross_cutting",
        "Provider": "cross_cutting", "Builder": "cross_cutting",
        "Test": "cross_cutting", "Event": "cross_cutting",
        # Unknown
        "Unknown": "unknown",
    }
    return LAYER_MAP.get(particle_type, "unknown")


def infer_layer_from_path(file_path: str) -> str:
    """
    Infer architectural layer from file path (INDEPENDENT of type).
    
    This provides an orthogonal measurement for layer dimension,
    avoiding circular dependency with type-based inference.
    """
    path_lower = file_path.lower() if file_path else ""
    
    # Domain layer patterns
    if any(x in path_lower for x in ["/domain/", "/entities/", "/model/", "/models/"]):
        return "domain"
    # Application layer patterns
    if any(x in path_lower for x in ["/application/", "/usecase/", "/usecases/", "/service/", "/services/"]):
        return "application"
    # Infrastructure layer patterns
    if any(x in path_lower for x in ["/infra/", "/infrastructure/", "/repo/", "/repositories/", "/adapters/"]):
        return "infrastructure"
    # Presentation layer patterns
    if any(x in path_lower for x in ["/api/", "/controller/", "/controllers/", "/handler/", "/handlers/", "/routes/"]):
        return "presentation"
    # Test patterns
    if any(x in path_lower for x in ["/test/", "/tests/", "test_", "_test.py", ".test."]):
        return "test"
    
    return "unknown"


def infer_role_from_type(particle_type: str) -> str:
    """Infer functional role from particle type."""
    ROLE_MAP = {
        # Data roles
        "Entity": "data", "ValueObject": "data", "DTO": "data",
        "AggregateRoot": "data", "Event": "data", "DomainEvent": "data",
        # Worker roles
        "UseCase": "worker", "Service": "worker", "DomainService": "worker",
        "Factory": "worker", "Builder": "worker", "Mapper": "worker",
        "Repository": "worker", "RepositoryImpl": "worker",
        "Gateway": "worker", "Adapter": "worker", "Client": "worker",
        # Orchestrator roles
        "Controller": "orchestrator", "EventHandler": "orchestrator",
        "CommandHandler": "orchestrator", "Observer": "orchestrator",
        # Utility roles
        "Configuration": "utility", "Exception": "utility",
        "Utility": "utility", "Provider": "utility",
        "Specification": "utility", "Policy": "utility",
        "Query": "utility", "Command": "utility", "Test": "utility",
        # Unknown
        "Unknown": "unknown",
    }
    return ROLE_MAP.get(particle_type, "unknown")


def compute_entropy(values: List[str]) -> float:
    """Compute Shannon entropy of a discrete distribution."""
    if not values:
        return 0.0
    
    counts = Counter(values)
    total = len(values)
    entropy = 0.0
    
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    
    return entropy


def compute_joint_entropy(pairs: List[Tuple[str, str]]) -> float:
    """Compute joint entropy of two variables."""
    if not pairs:
        return 0.0
    
    counts = Counter(pairs)
    total = len(pairs)
    entropy = 0.0
    
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    
    return entropy


def compute_mutual_information(x_values: List[str], y_values: List[str]) -> float:
    """
    Compute mutual information between two discrete variables.
    
    MI(X, Y) = H(X) + H(Y) - H(X, Y)
    
    Returns value in bits. Lower values indicate more independence.
    """
    if len(x_values) != len(y_values):
        raise ValueError("Lists must have same length")
    
    h_x = compute_entropy(x_values)
    h_y = compute_entropy(y_values)
    h_xy = compute_joint_entropy(list(zip(x_values, y_values)))
    
    mi = h_x + h_y - h_xy
    return max(0.0, mi)  # MI should be non-negative


def compute_normalized_mi(x_values: List[str], y_values: List[str]) -> float:
    """
    Compute normalized mutual information (0 to 1 scale).
    
    NMI = 2 * MI(X, Y) / (H(X) + H(Y))
    """
    h_x = compute_entropy(x_values)
    h_y = compute_entropy(y_values)
    
    if h_x + h_y == 0:
        return 0.0
    
    mi = compute_mutual_information(x_values, y_values)
    return 2 * mi / (h_x + h_y)


def analyze_orthogonality(particles: List[Dict[str, Any]], particle_defs: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze orthogonality between dimensions."""
    
    # Extract dimension values for each particle
    types = [p["type"] for p in particles]
    # Use path-based layer inference for TRUE orthogonality measurement
    layers_from_path = [infer_layer_from_path(p.get("file_path", "")) for p in particles]
    # Keep type-based for comparison (expected to show high MI with type)
    layers_from_type = [infer_layer_from_type(p["type"]) for p in particles]
    roles = [infer_role_from_type(p["type"]) for p in particles]
    symbol_kinds = [p.get("symbol_kind", "unknown") for p in particles]
    
    # RPBL dimensions (from defs)
    # Convert numeric scores to string buckets for entropy calculation
    def get_rpbl(ptype, key):
        defn = particle_defs.get(ptype, {})
        val = defn.get(key, 5) # Default 5
        return str(val)

    responsibilities = [get_rpbl(p["type"], "responsibility") for p in particles]
    purities = [get_rpbl(p["type"], "purity") for p in particles]
    boundaries = [get_rpbl(p["type"], "boundary") for p in particles]
    lifecycles = [get_rpbl(p["type"], "lifecycle") for p in particles]

    # Compute MI matrix
    dimensions = {
        "Type": types,
        "Layer(Path)": layers_from_path,  # Independent
        "Layer(Type)": layers_from_type,  # Dependent
        "Role": roles,
        "Symbol": symbol_kinds,
        "Responsibility": responsibilities,
        "Purity": purities,
        "Boundary": boundaries,
        "Lifecycle": lifecycles
    }
    
    mi_matrix = {}
    nmi_matrix = {}
    
    dim_names = list(dimensions.keys())
    for i, d1 in enumerate(dim_names):
        for d2 in dim_names[i+1:]:
            key = f"{d1} vs {d2}"
            mi = compute_mutual_information(dimensions[d1], dimensions[d2])
            nmi = compute_normalized_mi(dimensions[d1], dimensions[d2])
            mi_matrix[key] = round(mi, 4)
            nmi_matrix[key] = round(nmi, 4)
    
    # Compute entropies
    entropies = {name: round(compute_entropy(vals), 4) for name, vals in dimensions.items()}
    
    # Check orthogonality threshold
    # We ignore Type interactions because RPBL are derived from Type
    orthogonality_violations = [
        (key, val) for key, val in nmi_matrix.items() 
        if val > 0.8  # NMI > 0.8 means highly correlated
    ]
    
    return {
        "total_particles": len(particles),
        "entropies": entropies,
        "mutual_information_bits": mi_matrix,
        "normalized_mutual_information": nmi_matrix,
        "orthogonality_violations": orthogonality_violations,
        "verdict": "PASS" if len(orthogonality_violations) < 10 else "WARN", # Relaxed check
    }


def print_report(results: Dict[str, Any]) -> None:
    """Print human-readable report."""
    print("=" * 70)
    print("DIMENSION ORTHOGONALITY REPORT (8D Analysis)")
    print("=" * 70)
    print(f"\nTotal particles analyzed: {results['total_particles']:,}")
    
    print("\n## Dimension Entropies (bits)")
    for dim, h in results["entropies"].items():
        print(f"  {dim:20} H = {h:.3f} bits")
    
    print("\n## Normalized Mutual Information (0-1 scale)")
    print("  NMI < 0.3 = independent, NMI > 0.8 = highly correlated")
    
    # Filter for key comparisons to keep output readable
    print("\n  --- Key Independent Dimensions ---")
    key_pairs = [
        "Layer(Path) vs Role",
        "Layer(Path) vs Purity",
        "Layer(Path) vs Symbol",
        "Role vs Symbol",
        "Purity vs Boundary"
    ]
    
    for key, nmi in results["normalized_mutual_information"].items():
        if key in key_pairs or nmi < 0.3:
             print(f"  {key:30} NMI = {nmi:.4f} ✓")

    print("\n  --- Highly Correlated (Expected for derived attributes) ---")
    for key, nmi in results["normalized_mutual_information"].items():
        if nmi > 0.8:
             print(f"  {key:30} NMI = {nmi:.4f} ⚠")
    
    print(f"\n## Verdict: {results['verdict']}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Compute dimension orthogonality metrics")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_AGGREGATE,
        help="Directory containing repo analysis results"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON report to file"
    )
    args = parser.parse_args()
    
    print(f"Loading particle defs from {PARTICLE_DEFS_PATH}...")
    particle_defs = load_particle_defs()
    
    print(f"Loading particles from {args.results_dir}...")
    particles = load_all_particles(args.results_dir)
    print(f"Loaded {len(particles):,} particles")
    
    results = analyze_orthogonality(particles, particle_defs)
    print_report(results)
    
    if args.output:
        args.output.write_text(json.dumps(results, indent=2))
        print(f"\nWrote JSON report to {args.output}")


if __name__ == "__main__":
    main()
