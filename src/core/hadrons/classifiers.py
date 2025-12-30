"""
Hadron Classifiers
==================

Classification logic for classes, functions, and I/O detection.
"""

from typing import Optional, List

from .models import Hadron, HadronLevel
from .taxonomy import IO_INDICATORS


class ClassClassifier:
    """Classifies class nodes into molecules/organelles."""

    def classify(self, node, file_path: str) -> Optional[Hadron]:
        """Classify a class node into the appropriate molecule/organelle."""
        class_name = ""
        has_id_field = False
        has_save_method = False
        has_find_method = False
        is_immutable = True  # Assume immutable until proven otherwise

        for child in node.children:
            if child.type == "identifier":
                class_name = child.text.decode() if child.text else ""
            elif child.type == "block":
                for stmt in child.children:
                    # Check for id field
                    if "id" in (stmt.text.decode() if stmt.text else "").lower():
                        if "self.id" in (stmt.text.decode() if stmt.text else "") or "this.id" in (stmt.text.decode() if stmt.text else ""):
                            has_id_field = True
                    # Check for mutation (setters)
                    if stmt.type == "function_definition":
                        func_name = ""
                        for c in stmt.children:
                            if c.type == "identifier":
                                func_name = c.text.decode() if c.text else ""
                                break
                        if func_name.startswith("set") or func_name.startswith("update"):
                            is_immutable = False
                        if func_name in ("save", "persist", "store"):
                            has_save_method = True
                        if func_name in ("find", "get", "load", "fetch"):
                            has_find_method = True

        # Classification logic
        if has_save_method and has_find_method:
            return Hadron(
                id=52, name="Repository", level=HadronLevel.ORGANELLE,
                continent="Organization", fundamental="Modules",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=class_name,
                detection_rule="class with save+find methods",
            )
        elif has_id_field and not is_immutable:
            return Hadron(
                id=44, name="Entity", level=HadronLevel.MOLECULE,
                continent="Organization", fundamental="Aggregates",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=class_name,
                detection_rule="class with id field + mutable",
            )
        elif is_immutable and not has_id_field:
            return Hadron(
                id=43, name="ValueObject", level=HadronLevel.MOLECULE,
                continent="Organization", fundamental="Aggregates",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=class_name,
                detection_rule="class immutable + no id",
            )

        return None


class FunctionClassifier:
    """Classifies function nodes into pure/impure/async/handler."""

    def classify(self, node, file_path: str) -> Optional[Hadron]:
        """Classify a function into pure/impure/async/handler."""
        func_name = ""
        is_async = False
        has_io = False

        for child in node.children:
            if child.type == "identifier":
                func_name = child.text.decode() if child.text else ""
            elif child.type == "async":
                is_async = True
            elif child.type == "block":
                # Scan for I/O calls
                has_io = self._has_io_calls(child)

        # Classification
        if is_async:
            return Hadron(
                id=32, name="AsyncFunction", level=HadronLevel.MOLECULE,
                continent="Logic & Flow", fundamental="Functions",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=func_name,
                detection_rule="async keyword",
            )
        elif not has_io:
            return Hadron(
                id=30, name="PureFunction", level=HadronLevel.MOLECULE,
                continent="Logic & Flow", fundamental="Functions",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=func_name,
                detection_rule="no I/O calls detected",
                confidence=0.8,  # Not 100% sure without deeper analysis
            )
        else:
            return Hadron(
                id=31, name="ImpureFunction", level=HadronLevel.MOLECULE,
                continent="Logic & Flow", fundamental="Functions",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=func_name,
                detection_rule="has I/O calls",
            )

    def _has_io_calls(self, node) -> bool:
        """Check if a node contains any I/O-related function calls."""
        if node.type == "call":
            call_text = node.text.decode() if node.text else ""
            for io_func in IO_INDICATORS:
                if io_func in call_text.lower():
                    return True

        for child in node.children:
            if self._has_io_calls(child):
                return True

        return False


class OrganelleInferrer:
    """Infers architecture-level organelles from patterns."""

    def infer(self, root_node, file_path: str) -> List[Hadron]:
        """Infer architecture-level organelles from patterns."""
        organelles = []

        def visit(node):
            if node.type == "function_definition":
                func_name = ""
                for child in node.children:
                    if child.type == "identifier":
                        func_name = child.text.decode() if child.text else ""
                        break

                # Command handler detection
                if "command" in func_name.lower() and "handle" in func_name.lower():
                    organelles.append(Hadron(
                        id=35, name="CommandHandler", level=HadronLevel.ORGANELLE,
                        continent="Logic & Flow", fundamental="Functions",
                        file_path=file_path,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        text_snippet=func_name,
                        detection_rule="name contains command+handle",
                    ))

                # Query handler detection
                elif "query" in func_name.lower() and "handle" in func_name.lower():
                    organelles.append(Hadron(
                        id=36, name="QueryHandler", level=HadronLevel.ORGANELLE,
                        continent="Logic & Flow", fundamental="Functions",
                        file_path=file_path,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        text_snippet=func_name,
                        detection_rule="name contains query+handle",
                    ))

                # Validator detection
                elif func_name.lower().startswith("validate"):
                    organelles.append(Hadron(
                        id=40, name="Validator", level=HadronLevel.ORGANELLE,
                        continent="Logic & Flow", fundamental="Functions",
                        file_path=file_path,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        text_snippet=func_name,
                        detection_rule="name starts with validate",
                    ))

            for child in node.children:
                visit(child)

        visit(root_node)
        return organelles
