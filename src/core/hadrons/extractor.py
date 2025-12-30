"""
Atom Extractor
==============

Main facade for extracting hadrons from source code using tree-sitter.
"""

import json
from typing import List, Dict, Any

from .models import Hadron, HadronLevel
from .taxonomy import ATOM_MAP
from .classifiers import ClassClassifier, FunctionClassifier, OrganelleInferrer


class AtomExtractor:
    """
    Extracts atoms, molecules, and organelles from source code using tree-sitter.

    Usage:
        extractor = AtomExtractor()
        hadrons = extractor.extract(code, language="python", file_path="user.py")
    """

    def __init__(self):
        self.parsers: Dict[str, Any] = {}
        self._class_classifier = ClassClassifier()
        self._function_classifier = FunctionClassifier()
        self._organelle_inferrer = OrganelleInferrer()
        self._init_parsers()

    def _init_parsers(self):
        """Initialize tree-sitter parsers for supported languages."""
        try:
            from tree_sitter import Language, Parser

            # Python
            try:
                import tree_sitter_python as tspython
                parser = Parser(Language(tspython.language()))
                self.parsers["python"] = parser
            except ImportError:
                pass

            # TypeScript
            try:
                import tree_sitter_typescript as tstypescript
                parser = Parser(Language(tstypescript.language_typescript()))
                self.parsers["typescript"] = parser
            except ImportError:
                pass

            # JavaScript
            try:
                import tree_sitter_javascript as tsjavascript
                parser = Parser(Language(tsjavascript.language()))
                self.parsers["javascript"] = parser
            except ImportError:
                pass

            # Go
            try:
                import tree_sitter_go as tsgo
                parser = Parser(Language(tsgo.language()))
                self.parsers["go"] = parser
            except ImportError:
                pass

            # Java
            try:
                import tree_sitter_java as tsjava
                parser = Parser(Language(tsjava.language()))
                self.parsers["java"] = parser
            except ImportError:
                pass

        except ImportError:
            print("Warning: tree-sitter not installed. Run: pip install tree-sitter")

    def extract(self, code: bytes, language: str = "python", file_path: str = "") -> List[Hadron]:
        """
        Extract all hadrons (atoms, molecules, organelles) from source code.

        Args:
            code: Source code as bytes
            language: Programming language (python, typescript, go, java)
            file_path: Path to source file (for reporting)

        Returns:
            List of detected Hadron objects
        """
        if language not in self.parsers:
            raise ValueError(f"Unsupported language: {language}. Available: {list(self.parsers.keys())}")

        parser = self.parsers[language]
        tree = parser.parse(code)

        hadrons: List[Hadron] = []

        # Phase 1: Extract ATOMS (leaf nodes)
        atoms = self._extract_atoms(tree.root_node, file_path)
        hadrons.extend(atoms)

        # Phase 2: Compose MOLECULES (compound patterns)
        molecules = self._extract_molecules(tree.root_node, file_path, atoms)
        hadrons.extend(molecules)

        # Phase 3: Infer ORGANELLES (architecture roles)
        organelles = self._organelle_inferrer.infer(tree.root_node, file_path)
        hadrons.extend(organelles)

        return hadrons

    def _extract_atoms(self, root_node, file_path: str) -> List[Hadron]:
        """Extract atomic syntax elements from AST."""
        atoms = []

        def visit(node):
            if node.type in ATOM_MAP:
                mapping = ATOM_MAP[node.type]
                hadron = Hadron(
                    id=mapping["id"],
                    name=mapping["name"],
                    level=HadronLevel.ATOM,
                    continent=mapping["continent"],
                    fundamental=mapping["fundamental"],
                    file_path=file_path,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    text_snippet=node.text.decode()[:100] if node.text else "",
                    detection_rule=f"node_type={node.type}",
                )
                atoms.append(hadron)

            for child in node.children:
                visit(child)

        visit(root_node)
        return atoms

    def _extract_molecules(self, root_node, file_path: str, atoms: List[Hadron]) -> List[Hadron]:
        """Extract molecular patterns (classes, functions with context)."""
        molecules = []

        def visit(node):
            # Detect classes
            if node.type == "class_definition":
                molecule = self._class_classifier.classify(node, file_path)
                if molecule:
                    molecules.append(molecule)

            # Detect functions with semantic analysis
            if node.type == "function_definition":
                molecule = self._function_classifier.classify(node, file_path)
                if molecule:
                    molecules.append(molecule)

            for child in node.children:
                visit(child)

        visit(root_node)
        return molecules

    def to_json(self, hadrons: List[Hadron]) -> str:
        """Convert hadrons to JSON for output."""
        return json.dumps([h.to_dict() for h in hadrons], indent=2)

    def summary(self, hadrons: List[Hadron]) -> Dict:
        """Generate summary statistics."""
        by_level = {"atom": 0, "molecule": 0, "organelle": 0}
        by_continent = {}
        by_fundamental = {}
        by_name = {}

        for h in hadrons:
            by_level[h.level.value] += 1
            by_continent[h.continent] = by_continent.get(h.continent, 0) + 1
            by_fundamental[h.fundamental] = by_fundamental.get(h.fundamental, 0) + 1
            by_name[h.name] = by_name.get(h.name, 0) + 1

        return {
            "total": len(hadrons),
            "by_level": by_level,
            "by_continent": by_continent,
            "by_fundamental": by_fundamental,
            "top_10_hadrons": sorted(by_name.items(), key=lambda x: -x[1])[:10],
        }
