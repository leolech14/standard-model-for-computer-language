"""
Hadrons Package
===============

Maps tree-sitter AST nodes to the 96 Hadrons taxonomy.

Hierarchy:
  ATOMS (syntax primitives) -> MOLECULES (program structure) -> ORGANELLES (architecture roles)

Tree-sitter provides the universal atomic layer. This package:
1. Extracts atoms from source code using tree-sitter
2. Composes atoms into molecules
3. Infers organelles (architecture roles) from patterns

Usage:
    from hadrons import AtomExtractor

    extractor = AtomExtractor()
    hadrons = extractor.extract(code, language="python", file_path="user.py")
"""

from .models import Hadron, HadronLevel
from .taxonomy import (
    ATOM_MAP,
    MOLECULE_PATTERNS,
    ORGANELLE_PATTERNS,
    IO_INDICATORS,
    PURE_INDICATORS,
)
from .classifiers import ClassClassifier, FunctionClassifier, OrganelleInferrer
from .extractor import AtomExtractor


__all__ = [
    # Main entry point
    'AtomExtractor',

    # Models
    'Hadron',
    'HadronLevel',

    # Classifiers
    'ClassClassifier',
    'FunctionClassifier',
    'OrganelleInferrer',

    # Taxonomy mappings
    'ATOM_MAP',
    'MOLECULE_PATTERNS',
    'ORGANELLE_PATTERNS',
    'IO_INDICATORS',
    'PURE_INDICATORS',
]
