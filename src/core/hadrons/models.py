"""
Hadron Models
=============

Data structures for the 96 Hadrons taxonomy.

Hierarchy:
  ATOMS (syntax primitives) -> MOLECULES (program structure) -> ORGANELLES (architecture roles)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List


class HadronLevel(Enum):
    """The three-level hierarchy from STANDARD_MODEL_STRUCTURE.md"""
    ATOM = "atom"           # Syntax primitives (tree-sitter leaf nodes)
    MOLECULE = "molecule"   # Program structure (tree-sitter compound nodes)
    ORGANELLE = "organelle" # Architecture roles (inferred from patterns)


@dataclass
class Hadron:
    """A detected code element mapped to the 96 Hadrons taxonomy."""
    id: int                          # 1-96 from HADRONS_96_FULL.md
    name: str                        # e.g., "PureFunction", "Entity"
    level: HadronLevel               # atom/molecule/organelle
    continent: str                   # Data Foundations, Logic & Flow, Organization, Execution
    fundamental: str                 # e.g., Bits, Functions, Aggregates

    # Source location
    file_path: str = ""
    start_line: int = 0
    end_line: int = 0
    text_snippet: str = ""

    # Detection evidence
    detection_rule: str = ""         # What matched
    confidence: float = 1.0          # 0.0-1.0

    # Composition (for molecules/organelles)
    composed_of: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level.value,
            "continent": self.continent,
            "fundamental": self.fundamental,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "text_snippet": self.text_snippet,
            "detection_rule": self.detection_rule,
            "confidence": self.confidence,
        }
