#!/usr/bin/env python3
"""
🔬 ATOM CLASSIFIER
Uses the 167-atom taxonomy to classify code entities with more granularity.
"""

import json
import re
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
from .registry.pattern_repository import get_pattern_repository


@dataclass
class AtomClassification:
    """Result of classifying a code entity."""
    phase: str          # DATA, LOGIC, ORGANIZATION, EXECUTION
    family: str         # e.g., Functions, Aggregates
    atom_id: str        # e.g., LOG.FNC.M
    subtype: str        # e.g., Validator, Factory
    confidence: float   # 0.0 - 1.0


class AtomClassifier:
    """Classifies code entities using the 167-atom taxonomy."""
    
    def __init__(self, atoms_path: str = None):
        """Load atom definitions from JSON."""
        if atoms_path is None:
            atoms_path = Path(__file__).parent.parent / "patterns" / "atoms.json"
        
        with open(atoms_path, "r", encoding="utf-8") as f:
            self.taxonomy = json.load(f)
        
        
        # Build lookup structures
        self._build_lookups()
        
        # Load pattern repository (Learned Patterns)
        self.repo = get_pattern_repository()
    
    def _build_lookups(self):
        """Build fast lookup structures from taxonomy."""
        # atom_id -> (phase, family, atom_info)
        self.atoms_by_id = {}
        
        # subtype name -> atom_id
        self.atoms_by_subtype = {}
        
        for phase_name, phase in self.taxonomy.get("phases", {}).items():
            for family_name, family in phase.get("families", {}).items():
                for atom in family.get("atoms", []):
                    atom_id = atom["id"]
                    subtype = atom["name"]
                    
                    if atom_id not in self.atoms_by_id:
                        self.atoms_by_id[atom_id] = (phase_name, family_name, atom)
                    
                    self.atoms_by_subtype[subtype.lower()] = atom_id
        
        # Add common aliases
        self.atoms_by_subtype['configuration'] = self.atoms_by_subtype.get('configvalue', 'ORG.CFG.O')
        self.atoms_by_subtype['adapter'] = self.atoms_by_subtype.get('adapter', 'ORG.SVC.M')
        self.atoms_by_subtype['observer'] = self.atoms_by_subtype.get('eventhandler', 'EXE.HDL.O')
        self.atoms_by_subtype['specification']
        self.atoms_by_subtype['query'] = self.atoms_by_subtype.get('query', 'LOG.FNC.M')  # LEARNED = self.atoms_by_subtype.get('policy', 'LOG.FNC.M')
        
        # Compile semantic patterns
        self.semantic_patterns = []
        for pattern in self.taxonomy.get("semantic_patterns", {}).get("patterns", []):
            try:
                regex = re.compile(pattern["pattern"])
                self.semantic_patterns.append((regex, pattern["atom"], pattern["subtype"]))
            except re.error:
                pass
        
        # Tree-sitter mappings
        self.ts_mappings = self.taxonomy.get("tree_sitter_mappings", {})
    
    def classify_by_name(self, name: str, ast_node_type: str = None, language: str = None, file_path: str = None) -> AtomClassification:
        """
        Classify a code entity by its name and optionally AST info.
        
        Args:
            name: Function/class/variable name
            ast_node_type: Tree-sitter AST node type (e.g., "function_declaration")
            language: Language (e.g., "javascript", "python")
            file_path: Optional file path for context-aware classification
        """
        confidence = 0.5  # Default confidence
        
        # 0. Context Awareness (Path Patterns) - HIGHEST PRIORITY
        # Learned from feedback loop: File path is strongest signal for tests/services
        if language and language == "python" and self.repo and file_path:
             path_patterns = self.repo.get_path_patterns()
             for pattern, (role, confidence) in path_patterns.items():
                 # Check if path contains the pattern (e.g. "tests/")
                 if pattern in file_path:
                     # Map role to Atom ID (with alias for Test -> testdouble)
                     key = role.lower()
                     if key == 'test': 
                         key = 'testdouble'  # Alias: generic Test -> TestDouble atom
                     atom_id = self.atoms_by_subtype.get(key)
                     if atom_id:
                         return AtomClassification(
                             phase=self.atoms_by_id[atom_id][0],
                             family=self.atoms_by_id[atom_id][1],
                             atom_id=atom_id, 
                             subtype=role,
                             confidence=confidence / 100.0
                         )

        # 1. Try Tree-sitter mapping first (highest confidence for structure)
        atom_id = None
        if language and ast_node_type:
            lang_mappings = self.ts_mappings.get(language, {})
            if ast_node_type in lang_mappings:
                atom_id = lang_mappings[ast_node_type]
                confidence = 0.8
        
        # 2. Try semantic patterns on name (can override or refine)
        subtype = None
        for regex, pattern_atom, pattern_subtype in self.semantic_patterns:
            if regex.match(name):
                atom_id = pattern_atom
                subtype = pattern_subtype
                confidence = max(confidence, 0.75)
                break
        
        # 2.5. Try PREFIX patterns from pattern repository (CRITICAL FIX)
        if self.repo:
            prefix_patterns = self.repo.get_prefix_patterns()
            for pattern, (role, conf) in prefix_patterns.items():
                if name.startswith(pattern) or name.lower().startswith(pattern.lower()):
                    role_key = role.lower()
                    if role_key == 'test':
                        role_key = 'testdouble'
                    atom_id = self.atoms_by_subtype.get(role_key)
                    if atom_id:
                        return AtomClassification(
                            phase=self.atoms_by_id[atom_id][0],
                            family=self.atoms_by_id[atom_id][1],
                            atom_id=atom_id,
                            subtype=role,
                            confidence=conf / 100.0
                        )
        
        # 2.6. Try SUFFIX patterns from pattern repository
        if self.repo:
            suffix_patterns = self.repo.get_suffix_patterns()
            for pattern, (role, conf) in suffix_patterns.items():
                if name.endswith(pattern):
                    role_key = role.lower()
                    atom_id = self.atoms_by_subtype.get(role_key)
                    if atom_id:
                        return AtomClassification(
                            phase=self.atoms_by_id[atom_id][0],
                            family=self.atoms_by_id[atom_id][1],
                            atom_id=atom_id,
                            subtype=role,
                            confidence=conf / 100.0
                        )

        
        # 3. Fall back to generic classification
        if atom_id is None:
            # Infer from name patterns
            name_lower = name.lower()
            
            if any(x in name_lower for x in ["handler", "controller", "endpoint", "route"]):
                atom_id = "EXE.HDL.O"
                subtype = "APIHandler"
            elif any(x in name_lower for x in ["service", "manager"]):
                atom_id = "ORG.SVC.M"
                subtype = "ApplicationService"
            elif any(x in name_lower for x in ["repository", "repo", "store"]):
                atom_id = "ORG.SVC.M"
                subtype = "Repository"
            elif any(x in name_lower for x in ["entity", "model", "aggregate"]):
                atom_id = "ORG.AGG.M"
                subtype = "Entity"
            elif any(x in name_lower for x in ["dto", "request", "response"]):
                atom_id = "ORG.AGG.M"
                subtype = "DTO"
            elif any(x in name_lower for x in ["factory", "create", "build"]):
                atom_id = "LOG.FNC.M"
                subtype = "Factory"
            elif any(x in name_lower for x in ["validate", "check", "verify"]):
                atom_id = "LOG.FNC.M"
                subtype = "Validator"
            elif any(x in name_lower for x in ["map", "transform", "convert"]):
                atom_id = "LOG.FNC.M"
                subtype = "Mapper"
            elif any(x in name_lower for x in ["test", "spec", "should"]):
                atom_id = "EXE.PRB.O"
                subtype = "TestDouble"
            else:
                # Default to generic function
                atom_id = "LOG.FNC.M"
                subtype = "ImpureFunction"
                confidence = 0.4
        
        # Look up phase and family
        if atom_id in self.atoms_by_id:
            phase, family, _ = self.atoms_by_id[atom_id]
        else:
            phase = atom_id.split(".")[0] if "." in atom_id else "LOGIC"
            family = "Functions"
        
        return AtomClassification(
            phase=phase,
            family=family,
            atom_id=atom_id,
            subtype=subtype or atom_id.split(".")[-1],
            confidence=confidence
        )
    
    def classify_semantic_id(self, semantic_id: str) -> AtomClassification:
        """
        Reclassify an existing semantic ID with more granularity.
        
        Args:
            semantic_id: Existing ID like "LOG.FNC.M|file.js|functionName|..."
        
        Returns:
            AtomClassification with refined subtype
        """
        parts = semantic_id.split("|")
        if len(parts) < 3:
            return self.classify_by_name(semantic_id)
        
        base_atom = parts[0]
        file_path = parts[1]
        name = parts[2]
        
        # Infer language from file extension
        language = None
        if file_path.endswith(".js"):
            language = "javascript"
        elif file_path.endswith(".ts") or file_path.endswith(".tsx"):
            language = "typescript"
        elif file_path.endswith(".py"):
            language = "python"
        
        # Classify with name
        result = self.classify_by_name(name, language=language)
        
        # Preserve original atom_id if higher confidence
        if base_atom in self.atoms_by_id:
            result.atom_id = base_atom
        
        return result
    
    def get_atom_info(self, atom_id: str) -> Optional[dict]:
        """Get full info for an atom type."""
        if atom_id in self.atoms_by_id:
            phase, family, atom = self.atoms_by_id[atom_id]
            return {
                "phase": phase,
                "family": family,
                **atom
            }
        return None
    
    def list_all_atoms(self) -> list:
        """List all 167 atoms with their info."""
        atoms = []
        for phase_name, phase in self.taxonomy.get("phases", {}).items():
            for family_name, family in phase.get("families", {}).items():
                for atom in family.get("atoms", []):
                    atoms.append({
                        "phase": phase_name,
                        "family": family_name,
                        **atom
                    })
        return atoms


def reclassify_semantic_ids(input_path: str, output_path: str = None):
    """
    Reclassify all semantic IDs in a file with more granular subtypes.
    """
    classifier = AtomClassifier()
    
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    ids = data.get("ids", [])
    classified = []
    subtype_counts = {}
    
    for sid in ids:
        result = classifier.classify_semantic_id(sid)
        
        # Track subtypes
        subtype_counts[result.subtype] = subtype_counts.get(result.subtype, 0) + 1
        
        classified.append({
            "original_id": sid,
            "atom_id": result.atom_id,
            "subtype": result.subtype,
            "phase": result.phase,
            "confidence": result.confidence
        })
    
    output = {
        "total": len(classified),
        "by_subtype": subtype_counts,
        "classified": classified
    }
    
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        print(f"📝 Saved to {output_path}")
    
    return output


# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # Demo mode
        classifier = AtomClassifier()
        
        print("=== 167 ATOM TAXONOMY ===")
        print(f"Total atoms: {len(classifier.list_all_atoms())}")
        print()
        
        # Test classification
        test_names = [
            "handleApiRequest",
            "UserRepository",
            "validateEmail",
            "CreateUserCommand",
            "buildSankeyModel",
            "syncItemConnectionById",
            "transformData"
        ]
        
        print("=== CLASSIFICATION EXAMPLES ===")
        for name in test_names:
            result = classifier.classify_by_name(name)
            print(f"  {name}")
            print(f"    → {result.phase}/{result.family}/{result.subtype} ({result.confidence:.0%})")
            print()
    else:
        # Reclassify mode
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = reclassify_semantic_ids(input_path, output_path)
        
        print(f"Reclassified {result['total']} IDs")
        print("Top subtypes:")
        for subtype, count in sorted(result["by_subtype"].items(), key=lambda x: -x[1])[:15]:
            print(f"  {subtype}: {count}")
