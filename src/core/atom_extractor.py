"""
Atom Extractor (Backward Compatibility Module)
==============================================

This module re-exports from the refactored hadrons package.
New code should import from src.core.hadrons directly.

Old:
    from atom_extractor import AtomExtractor, Hadron

New:
    from hadrons import AtomExtractor, Hadron
"""

# Re-export everything from the new package for backward compatibility
from hadrons import (
    AtomExtractor,
    Hadron,
    HadronLevel,
    ClassClassifier,
    FunctionClassifier,
    OrganelleInferrer,
    ATOM_MAP,
    MOLECULE_PATTERNS,
    ORGANELLE_PATTERNS,
    IO_INDICATORS,
    PURE_INDICATORS,
)

__all__ = [
    'AtomExtractor',
    'Hadron',
    'HadronLevel',
    'ClassClassifier',
    'FunctionClassifier',
    'OrganelleInferrer',
    'ATOM_MAP',
    'MOLECULE_PATTERNS',
    'ORGANELLE_PATTERNS',
    'IO_INDICATORS',
    'PURE_INDICATORS',
]


# CLI for backward compatibility
if __name__ == "__main__":
    # Demo usage
    demo_code = b'''
class UserRepository:
    def __init__(self, db):
        self.db = db

    def save(self, user):
        self.db.insert(user)

    def find(self, user_id):
        return self.db.query(user_id)

class Email:
    """Value object for email addresses."""
    def __init__(self, value: str):
        self._value = value

    @property
    def value(self) -> str:
        return self._value

def validate_email(email: str) -> bool:
    if "@" not in email:
        raise ValueError("Invalid email")
    return True

async def fetch_user(user_id: str):
    response = await request(f"/users/{user_id}")
    return response.json()

def calculate_total(items: list) -> float:
    return sum(item.price for item in items)
'''

    print("=" * 60)
    print("ATOM EXTRACTOR - Tree-sitter -> 96 Hadrons Mapping")
    print("=" * 60)

    extractor = AtomExtractor()

    if "python" in extractor.parsers:
        hadrons = extractor.extract(demo_code, language="python", file_path="demo.py")

        print(f"\nExtracted {len(hadrons)} hadrons:\n")

        # Group by level
        for level in [HadronLevel.ORGANELLE, HadronLevel.MOLECULE, HadronLevel.ATOM]:
            level_hadrons = [h for h in hadrons if h.level == level]
            if level_hadrons:
                print(f"--- {level.value.upper()}S ({len(level_hadrons)}) ---")
                for h in level_hadrons[:10]:  # Show first 10
                    print(f"  [{h.id:2}] {h.name:20} | {h.fundamental:15} | L{h.start_line}")
                if len(level_hadrons) > 10:
                    print(f"  ... and {len(level_hadrons) - 10} more")
                print()

        print("\n--- SUMMARY ---")
        summary = extractor.summary(hadrons)
        print(f"Total: {summary['total']}")
        print(f"By level: {summary['by_level']}")
        print(f"Top hadrons: {summary['top_10_hadrons']}")
    else:
        print("\nError: tree-sitter-python not installed.")
        print("Run: pip install tree-sitter tree-sitter-python")
