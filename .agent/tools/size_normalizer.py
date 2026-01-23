#!/usr/bin/env python3
"""
Size Normalizer for File Tree Visualization

Uses cube root scaling because volume scales with r³.
Different file types have different "cognitive mass" formulas.
"""

import math
from pathlib import Path

# Global scale factor (tune this for your visualization)
GLOBAL_SCALE_FACTOR = 0.5

# File type weights
WEIGHTS = {
    'code': 1.0,      # 1 LOC = 1 unit
    'config': 2.0,    # Config is dense, more weight per line
    'docs': 0.1,      # Docs are airy, less weight per word
    'binary': 10.0,   # Log(KB) multiplier for binaries
}

CODE_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.c', '.cpp', '.rb', '.php'}
CONFIG_EXTENSIONS = {'.json', '.yaml', '.yml', '.toml', '.ini', '.xml', '.env'}
DOC_EXTENSIONS = {'.md', '.txt', '.rst', '.html'}


def get_file_type(extension: str) -> str:
    """Categorize file by extension."""
    ext = extension.lower()
    if ext in CODE_EXTENSIONS:
        return 'code'
    elif ext in CONFIG_EXTENSIONS:
        return 'config'
    elif ext in DOC_EXTENSIONS:
        return 'docs'
    else:
        return 'binary'


def get_cognitive_mass(file_type: str, loc: int = 0, words: int = 0, size_kb: float = 0) -> float:
    """Calculate cognitive mass based on file type and metrics."""
    if file_type == 'code':
        return loc * WEIGHTS['code']
    elif file_type == 'config':
        return loc * WEIGHTS['config']
    elif file_type == 'docs':
        return words * WEIGHTS['docs']
    else:  # binary
        return math.log1p(size_kb) * WEIGHTS['binary']


def get_radius(cognitive_mass: float) -> float:
    """Convert cognitive mass to visual radius using cube root."""
    if cognitive_mass <= 0:
        return GLOBAL_SCALE_FACTOR * 0.5  # Minimum size
    return math.pow(cognitive_mass, 1/3) * GLOBAL_SCALE_FACTOR


def normalize_file(extension: str, loc: int = 0, words: int = 0, size_kb: float = 0) -> dict:
    """Full normalization pipeline for a file."""
    file_type = get_file_type(extension)
    mass = get_cognitive_mass(file_type, loc, words, size_kb)
    radius = get_radius(mass)

    return {
        'file_type': file_type,
        'cognitive_mass': mass,
        'radius': radius,
    }


if __name__ == '__main__':
    # Test examples
    examples = [
        ('.py', 100, 0, 0),    # 100 LOC Python
        ('.py', 1000, 0, 0),   # 1000 LOC Python
        ('.json', 50, 0, 0),   # 50 line config
        ('.md', 0, 500, 0),    # 500 word doc
        ('.png', 0, 0, 100),   # 100KB image
        ('.png', 0, 0, 10000), # 10MB image
    ]

    print("Size Normalizer Test:")
    print("-" * 60)
    for ext, loc, words, kb in examples:
        result = normalize_file(ext, loc, words, kb)
        print(f"{ext:6} LOC:{loc:5} Words:{words:5} KB:{kb:6} -> radius: {result['radius']:.3f}")
