"""Output validation against JSON schemas."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    logging.warning("jsonschema not installed. Validation disabled.")


SCHEMA_DIR = Path(__file__).parent.parent.parent / "schema"


class ValidationError(Exception):
    """Raised when output validation fails."""
    pass


def load_schema(schema_name: str) -> Optional[Dict]:
    """Load a JSON schema by name.

    Args:
        schema_name: Name of schema file (without .json extension)

    Returns:
        Schema dict or None if not found
    """
    schema_path = SCHEMA_DIR / f"{schema_name}.schema.json"

    if not schema_path.exists():
        # Try without .schema suffix
        schema_path = SCHEMA_DIR / f"{schema_name}.json"

    if not schema_path.exists():
        logging.warning(f"Schema not found: {schema_name}")
        return None

    try:
        return json.loads(schema_path.read_text())
    except Exception as e:
        logging.error(f"Failed to load schema {schema_name}: {e}")
        return None


def validate_output(data: Dict, schema_name: str = "unified_output") -> List[str]:
    """Validate output data against schema.

    Args:
        data: Output data to validate
        schema_name: Name of schema to validate against

    Returns:
        List of validation error messages (empty if valid)
    """
    if not HAS_JSONSCHEMA:
        return ["jsonschema not installed - validation skipped"]

    schema = load_schema(schema_name)
    if schema is None:
        return [f"Schema '{schema_name}' not found"]

    errors = []
    validator = jsonschema.Draft7Validator(schema)

    for error in validator.iter_errors(data):
        path = ".".join(str(p) for p in error.absolute_path)
        errors.append(f"{path}: {error.message}" if path else error.message)

    return errors


def validate_node(node: Dict) -> List[str]:
    """Validate a single node has required fields.

    Args:
        node: Node dictionary

    Returns:
        List of validation warnings
    """
    warnings = []
    required_fields = ["id", "name", "role", "file", "line"]

    for field in required_fields:
        if field not in node:
            warnings.append(f"Missing required field: {field}")
        elif node[field] is None:
            warnings.append(f"Null value for field: {field}")

    return warnings


def validate_edge(edge: Dict) -> List[str]:
    """Validate a single edge has required fields.

    Args:
        edge: Edge dictionary

    Returns:
        List of validation warnings
    """
    warnings = []
    required_fields = ["source", "target", "type"]

    for field in required_fields:
        if field not in edge:
            warnings.append(f"Missing required field: {field}")

    return warnings
