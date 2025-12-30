"""
Purpose Classifier
==================

Classifies code elements by their atomic and composite purposes.
"""

from typing import Dict, List, Optional
from collections import Counter

from .constants import Layer, ROLE_TO_LAYER, EMERGENCE_RULES, LAYER_NAME_PATTERNS


class PurposeClassifier:
    """
    Classifies nodes by their purpose level.

    Levels:
    - Level 1: Atomic Purpose (individual function/class role)
    - Level 2: Composite Purpose (emergent from children)
    """

    def classify_atomic(self, role: str) -> tuple:
        """
        Classify a single node's atomic purpose.

        Args:
            role: The node's role (e.g., "Controller", "Repository")

        Returns:
            Tuple of (layer, purpose_description)
        """
        layer = ROLE_TO_LAYER.get(role, Layer.UNKNOWN)
        return layer, role

    def classify_composite(self, child_roles: List[str]) -> Optional[str]:
        """
        Determine composite purpose from child purposes.

        Args:
            child_roles: List of roles from child nodes

        Returns:
            Composite purpose string or None
        """
        if not child_roles:
            return None

        purpose_set = frozenset(set(child_roles))

        if purpose_set in EMERGENCE_RULES:
            return EMERGENCE_RULES[purpose_set]

        # Default: use most common child purpose + "Container"
        most_common = Counter(child_roles).most_common(1)[0][0]
        return f"{most_common}Container"

    def infer_layer_from_name(self, name: str) -> Layer:
        """
        Infer layer from name patterns when role is unknown.

        Args:
            name: Node name

        Returns:
            Inferred Layer or UNKNOWN
        """
        name_lower = name.lower()

        for layer, patterns in LAYER_NAME_PATTERNS.items():
            if any(p in name_lower for p in patterns):
                return layer

        return Layer.UNKNOWN

    def get_effective_layer(
        self,
        role: str,
        name: str,
        composite_purpose: Optional[str] = None
    ) -> Layer:
        """
        Get the effective layer considering all classification methods.

        Priority:
        1. Composite purpose (if available)
        2. Atomic purpose (role)
        3. Name pattern inference

        Args:
            role: Node's role
            name: Node's name
            composite_purpose: Composite purpose if this is a parent node

        Returns:
            The determined Layer
        """
        # Try composite purpose first
        if composite_purpose and composite_purpose in ROLE_TO_LAYER:
            return ROLE_TO_LAYER[composite_purpose]

        # Try atomic purpose (role)
        if role in ROLE_TO_LAYER:
            return ROLE_TO_LAYER[role]

        # Fall back to name inference
        return self.infer_layer_from_name(name)
