"""
Purpose Emergence Calculator

Computes emergent purpose (π) at multiple levels:
- π₁ = Atomic Purpose (= Role, the job title)
- π₂ = Molecular Purpose (emergent from composition)
- π₃ = Organelle Purpose (emergent from molecules)
- π₄ = System Purpose (emergent from organelles)

EXPERIMENTAL: Schema is derived from observation, not hardcoded.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
from enum import Enum


class PurposeLevel(Enum):
    """Levels of purpose emergence"""
    PI_1 = 1  # Atomic (= Role)
    PI_2 = 2  # Molecular (function/method)
    PI_3 = 3  # Organelle (class/module)
    PI_4 = 4  # System (package/service)


@dataclass
class EmergentPurpose:
    """Computed purpose at any level"""
    level: PurposeLevel
    purpose: str           # The emergent purpose name
    confidence: float      # How confident (0-1)
    signals: Dict          # The signals that produced this
    children: List[str]    # Child purposes that contributed (for π₂+)


# =============================================================================
# π₁: ATOMIC PURPOSE (= Role)
# =============================================================================

def compute_pi1(node: Dict) -> EmergentPurpose:
    """
    π₁ = Atomic Purpose = Role

    This is the base case - looked up from the role classifier.
    """
    role = node.get('role', 'Unknown')
    confidence = node.get('role_confidence', 0)

    # Normalize confidence to 0-1 if it's 0-100
    if confidence > 1:
        confidence = confidence / 100.0

    return EmergentPurpose(
        level=PurposeLevel.PI_1,
        purpose=role,
        confidence=confidence,
        signals={'role': role, 'role_confidence': confidence},
        children=[]
    )


# =============================================================================
# π₂: MOLECULAR PURPOSE (emergent from atoms)
# =============================================================================

# Purpose emergence rules based on signal combinations
# Format: (effect, boundary, dominant_category) -> purpose
PI2_EMERGENCE_RULES = {
    # Pure computations
    ('Pure', 'internal', 'LOG'): 'Compute',
    ('Pure', 'internal', 'DAT'): 'Compute',
    ('Pure', 'output', 'LOG'): 'Produce',

    # Data retrieval
    ('Read', 'internal', 'DAT'): 'Retrieve',
    ('Read', 'internal', 'LOG'): 'Retrieve',
    ('Read', 'input', 'DAT'): 'Intake',
    ('Read', 'input', 'LOG'): 'Intake',

    # Data mutation
    ('Write', 'internal', 'DAT'): 'Persist',
    ('Write', 'internal', 'LOG'): 'Persist',
    ('Write', 'output', 'DAT'): 'Emit',
    ('Write', 'output', 'LOG'): 'Emit',

    # Transformations
    ('ReadWrite', 'internal', 'LOG'): 'Transform',
    ('ReadWrite', 'internal', 'DAT'): 'Transform',
    ('ReadWrite', 'input', 'LOG'): 'Process',
    ('ReadWrite', 'input', 'DAT'): 'Process',
    ('ReadWrite', 'output', 'LOG'): 'Generate',
    ('ReadWrite', 'output', 'DAT'): 'Generate',

    # IO boundary
    ('ReadWrite', 'io', 'LOG'): 'Gateway',
    ('ReadWrite', 'io', 'DAT'): 'Gateway',
    ('Read', 'io', 'LOG'): 'Receiver',
    ('Write', 'io', 'DAT'): 'Sender',
}

# Topology modifiers - adjust purpose based on graph position
TOPOLOGY_MODIFIERS = {
    'hub': 'Coordinate',      # Hubs coordinate
    'root': 'Initiate',       # Roots initiate
    'leaf': None,             # Leaves keep base purpose
    'bridge': 'Connect',      # Bridges connect
    'orphan': 'Isolate',      # Orphans are isolated
}


def compute_pi2(node: Dict) -> EmergentPurpose:
    """
    π₂ = Molecular Purpose

    Emergent from:
    - Effect (Read/Write/ReadWrite/Pure)
    - Boundary (Input/Output/Internal/IO)
    - Atom family (DAT/LOG/ORG/EXE)
    - Topology (Hub/Leaf/Bridge/Root/Orphan)
    - Flow direction (Source/Sink/Balanced)
    """
    # Extract signals
    effect = node.get('effect', 'Unknown')
    boundary = node.get('boundary', 'internal')
    atom_family = node.get('atom_family', 'LOG')  # Default to Logic
    topology = node.get('topology_role', 'internal')

    # Compute flow direction from degree
    in_deg = node.get('in_degree', 0)
    out_deg = node.get('out_degree', 0)
    if in_deg == 0 and out_deg == 0:
        flow = 'isolated'
    elif out_deg > in_deg * 2:
        flow = 'source'
    elif in_deg > out_deg * 2:
        flow = 'sink'
    else:
        flow = 'balanced'

    # Normalize boundary
    boundary_norm = boundary.lower() if boundary else 'internal'

    # Look up base purpose from rules
    key = (effect, boundary_norm, atom_family)
    base_purpose = PI2_EMERGENCE_RULES.get(key)

    if not base_purpose:
        # Fallback: try with just effect and boundary
        for (e, b, _), purpose in PI2_EMERGENCE_RULES.items():
            if e == effect and b == boundary_norm:
                base_purpose = purpose
                break

    if not base_purpose:
        # Ultimate fallback based on effect alone
        effect_fallback = {
            'Pure': 'Compute',
            'Read': 'Retrieve',
            'Write': 'Persist',
            'ReadWrite': 'Transform',
        }
        base_purpose = effect_fallback.get(effect, 'Unknown')

    # Apply topology modifier
    topo_modifier = TOPOLOGY_MODIFIERS.get(topology)
    if topo_modifier and topology in ('hub', 'root', 'bridge'):
        # Combine: "Coordinate + Transform" -> "Coordinate"
        # The topology role takes precedence for structural nodes
        final_purpose = topo_modifier
    elif topology == 'orphan':
        final_purpose = f'{base_purpose}(Orphan)'
    else:
        final_purpose = base_purpose

    # Confidence based on how many signals matched
    confidence = 0.5  # Base confidence
    if key in PI2_EMERGENCE_RULES:
        confidence += 0.3  # Exact match bonus
    if topology != 'internal':
        confidence += 0.1  # Clear topology bonus
    if flow != 'balanced':
        confidence += 0.1  # Clear flow direction bonus

    confidence = min(confidence, 1.0)

    signals = {
        'effect': effect,
        'boundary': boundary_norm,
        'atom_family': atom_family,
        'topology': topology,
        'flow': flow,
        'in_degree': in_deg,
        'out_degree': out_deg,
    }

    return EmergentPurpose(
        level=PurposeLevel.PI_2,
        purpose=final_purpose,
        confidence=confidence,
        signals=signals,
        children=[node.get('role', 'Unknown')]  # π₁ is the child
    )


# =============================================================================
# π₃: ORGANELLE PURPOSE (emergent from molecules)
# =============================================================================

def compute_pi3(container_node: Dict, child_nodes: List[Dict]) -> EmergentPurpose:
    """
    π₃ = Organelle Purpose (class/module level)

    Emergent from:
    - Distribution of child π₂ purposes
    - Container's own signals
    - Relationship patterns
    """
    if not child_nodes:
        # No children - fall back to π₂
        pi2 = compute_pi2(container_node)
        return EmergentPurpose(
            level=PurposeLevel.PI_3,
            purpose=pi2.purpose,
            confidence=pi2.confidence * 0.8,  # Lower confidence without children
            signals=pi2.signals,
            children=[]
        )

    # Compute π₂ for all children
    child_purposes = []
    for child in child_nodes:
        pi2 = compute_pi2(child)
        child_purposes.append(pi2.purpose)

    # Count purpose distribution
    purpose_counts = Counter(child_purposes)
    total = len(child_purposes)

    # Dominant purpose
    dominant_purpose, dominant_count = purpose_counts.most_common(1)[0]
    dominance_ratio = dominant_count / total

    # Unique purposes
    unique_count = len(purpose_counts)

    # Emergence rules for π₃
    if unique_count == 1:
        # All children same purpose -> Container amplifies it
        final_purpose = f'{dominant_purpose}Container'
        confidence = 0.9
    elif dominance_ratio > 0.7:
        # Strong dominant purpose
        final_purpose = dominant_purpose
        confidence = 0.7
    elif unique_count <= 3:
        # Few purposes -> might be a coherent pattern
        purposes_str = '+'.join(sorted(purpose_counts.keys()))
        # Check for known patterns
        if set(purpose_counts.keys()) <= {'Retrieve', 'Persist'}:
            final_purpose = 'Repository'
            confidence = 0.8
        elif set(purpose_counts.keys()) <= {'Transform', 'Compute'}:
            final_purpose = 'Processor'
            confidence = 0.8
        elif set(purpose_counts.keys()) <= {'Intake', 'Emit'}:
            final_purpose = 'Gateway'
            confidence = 0.8
        else:
            final_purpose = f'Mixed({purposes_str})'
            confidence = 0.5
    else:
        # Many different purposes -> potentially a God class
        final_purpose = 'Scattered'
        confidence = 0.4

    signals = {
        'child_count': total,
        'unique_purposes': unique_count,
        'dominant_purpose': dominant_purpose,
        'dominance_ratio': round(dominance_ratio, 2),
        'purpose_distribution': dict(purpose_counts),
    }

    return EmergentPurpose(
        level=PurposeLevel.PI_3,
        purpose=final_purpose,
        confidence=confidence,
        signals=signals,
        children=child_purposes
    )


# =============================================================================
# π₄: SYSTEM PURPOSE (emergent from organelles)
# =============================================================================

def compute_pi4(file_path: str, file_nodes: List[Dict]) -> EmergentPurpose:
    """
    π₄ = System Purpose (file/package level)

    Emergent from:
    - Distribution of π₃ purposes in the file
    - If no π₃, fall back to π₂ distribution
    - File-level patterns (test files, config files, etc.)
    """
    if not file_nodes:
        return EmergentPurpose(
            level=PurposeLevel.PI_4,
            purpose='Empty',
            confidence=0.0,
            signals={'file': file_path, 'node_count': 0},
            children=[]
        )

    # Check for special file patterns first
    file_lower = file_path.lower() if file_path else ''
    if 'test' in file_lower or file_lower.endswith('_test.py') or file_lower.startswith('test_'):
        return EmergentPurpose(
            level=PurposeLevel.PI_4,
            purpose='TestSuite',
            confidence=0.9,
            signals={'file': file_path, 'pattern': 'test_file'},
            children=[n.get('pi2_purpose', 'Unknown') for n in file_nodes]
        )
    if 'config' in file_lower or file_lower.endswith('config.py'):
        return EmergentPurpose(
            level=PurposeLevel.PI_4,
            purpose='Configuration',
            confidence=0.85,
            signals={'file': file_path, 'pattern': 'config_file'},
            children=[]
        )
    if '__init__' in file_lower:
        return EmergentPurpose(
            level=PurposeLevel.PI_4,
            purpose='ModuleExport',
            confidence=0.8,
            signals={'file': file_path, 'pattern': 'init_file'},
            children=[]
        )

    # Collect π₃ purposes (for containers) or π₂ (for all)
    pi3_purposes = [n.get('pi3_purpose') for n in file_nodes if n.get('pi3_purpose')]
    pi2_purposes = [n.get('pi2_purpose', 'Unknown') for n in file_nodes]

    # Use π₃ if we have containers, else π₂
    purposes = pi3_purposes if pi3_purposes else pi2_purposes

    if not purposes:
        return EmergentPurpose(
            level=PurposeLevel.PI_4,
            purpose='Unknown',
            confidence=0.3,
            signals={'file': file_path, 'node_count': len(file_nodes)},
            children=[]
        )

    purpose_counts = Counter(purposes)
    total = len(purposes)
    unique = len(purpose_counts)
    dominant, dominant_count = purpose_counts.most_common(1)[0]
    dominance = dominant_count / total

    # Determine system purpose
    if unique == 1:
        # Single purpose file
        final_purpose = f'{dominant}System'
        confidence = 0.9
    elif dominance > 0.7:
        # Strong dominant purpose
        final_purpose = dominant
        confidence = 0.75
    elif 'Scattered' in purpose_counts:
        # Contains God classes
        final_purpose = 'MixedResponsibility'
        confidence = 0.5
    elif unique <= 3:
        # Few coherent purposes
        if set(purpose_counts.keys()) <= {'Retrieve', 'Persist', 'Repository'}:
            final_purpose = 'DataAccess'
            confidence = 0.8
        elif set(purpose_counts.keys()) <= {'Transform', 'Process', 'Compute'}:
            final_purpose = 'Processing'
            confidence = 0.8
        elif set(purpose_counts.keys()) <= {'Intake', 'Emit', 'Gateway'}:
            final_purpose = 'IOBoundary'
            confidence = 0.8
        else:
            final_purpose = 'Composite'
            confidence = 0.6
    else:
        # Many purposes - utility/helper file
        final_purpose = 'Utility'
        confidence = 0.5

    signals = {
        'file': file_path,
        'node_count': len(file_nodes),
        'container_count': len(pi3_purposes),
        'unique_purposes': unique,
        'dominant_purpose': dominant,
        'dominance': round(dominance, 2),
        'purpose_distribution': dict(purpose_counts),
    }

    return EmergentPurpose(
        level=PurposeLevel.PI_4,
        purpose=final_purpose,
        confidence=confidence,
        signals=signals,
        children=purposes
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def compute_purpose(node: Dict, level: int = 2, children: List[Dict] = None) -> EmergentPurpose:
    """
    Compute purpose at specified level.

    Args:
        node: Node dictionary with metadata
        level: Purpose level (1=atomic, 2=molecular, 3=organelle)
        children: Child nodes (required for level 3+)

    Returns:
        EmergentPurpose with computed purpose and confidence
    """
    if level == 1:
        return compute_pi1(node)
    elif level == 2:
        return compute_pi2(node)
    elif level == 3:
        return compute_pi3(node, children or [])
    else:
        raise ValueError(f"Level {level} not yet implemented")


def analyze_purpose_distribution(nodes: List[Dict]) -> Dict:
    """
    Analyze the distribution of purposes across a codebase.

    Returns summary statistics for understanding emergent patterns.
    """
    pi1_purposes = []
    pi2_purposes = []

    for node in nodes:
        pi1 = compute_pi1(node)
        pi2 = compute_pi2(node)
        pi1_purposes.append(pi1.purpose)
        pi2_purposes.append(pi2.purpose)

    pi1_dist = Counter(pi1_purposes)
    pi2_dist = Counter(pi2_purposes)

    return {
        'total_nodes': len(nodes),
        'pi1_distribution': dict(pi1_dist.most_common(15)),
        'pi2_distribution': dict(pi2_dist.most_common(15)),
        'pi1_unique': len(pi1_dist),
        'pi2_unique': len(pi2_dist),
        # Emergence ratio: how many π₂ categories vs π₁
        'emergence_ratio': round(len(pi2_dist) / max(len(pi1_dist), 1), 2),
    }


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    import json

    # Test with sample node
    test_node = {
        'name': 'UserService.validate',
        'role': 'Validator',
        'role_confidence': 70,
        'effect': 'ReadWrite',
        'boundary': 'input',
        'atom_family': 'LOG',
        'topology_role': 'internal',
        'in_degree': 3,
        'out_degree': 2,
    }

    print("=== PURPOSE EMERGENCE TEST ===\n")

    pi1 = compute_pi1(test_node)
    print(f"π₁ (Atomic):    {pi1.purpose} ({pi1.confidence:.0%})")

    pi2 = compute_pi2(test_node)
    print(f"π₂ (Molecular): {pi2.purpose} ({pi2.confidence:.0%})")
    print(f"   Signals: {pi2.signals}")

    # Test π₃ with children
    test_children = [
        {'effect': 'Read', 'boundary': 'internal', 'atom_family': 'DAT', 'role': 'Query'},
        {'effect': 'Write', 'boundary': 'internal', 'atom_family': 'DAT', 'role': 'Command'},
        {'effect': 'Read', 'boundary': 'internal', 'atom_family': 'DAT', 'role': 'Query'},
    ]

    pi3 = compute_pi3(test_node, test_children)
    print(f"\nπ₃ (Organelle): {pi3.purpose} ({pi3.confidence:.0%})")
    print(f"   Children: {pi3.children}")
    print(f"   Signals: {pi3.signals}")
