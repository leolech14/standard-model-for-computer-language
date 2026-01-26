"""
Shared YAML utilities for .agent/tools.

Provides two modes:
1. Standard (pyyaml): Fast, simple, for read-only or no-comment-preservation
2. Preserve (ruamel.yaml): Round-trip with comment preservation

Consolidates load_yaml/save_yaml that were duplicated across 8+ files.
See: OPP-ARCH-002, TASK-068
"""

from pathlib import Path
from typing import Optional, Any
import yaml

# Try to import ruamel.yaml for comment preservation
try:
    from ruamel.yaml import YAML
    _ruamel_yaml = YAML()
    _ruamel_yaml.preserve_quotes = True
    _ruamel_yaml.width = 4096  # Prevent line wrapping
    HAS_RUAMEL = True
except ImportError:
    HAS_RUAMEL = False
    _ruamel_yaml = None


# =============================================================================
# Standard YAML (pyyaml) - Fast, simple, no comment preservation
# =============================================================================

def load_yaml(path: Path) -> dict:
    """Load YAML file safely using pyyaml.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML content as dict, or empty dict if file doesn't exist or is invalid
    """
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def save_yaml(path: Path, data: dict, sort_keys: bool = False):
    """Save data to YAML file using pyyaml.

    Args:
        path: Path to YAML file
        data: Dictionary to save
        sort_keys: Whether to sort keys alphabetically (default False)

    Creates parent directories if they don't exist.
    Note: Comments are NOT preserved. Use save_yaml_preserve for that.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=sort_keys, allow_unicode=True)


def load_yaml_optional(path: Path) -> Optional[dict]:
    """Load YAML file, returning None if not found.

    Use this when you need to distinguish between missing file and empty content.
    """
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


# =============================================================================
# Preserving YAML (ruamel.yaml) - Round-trip with comments
# =============================================================================

def load_yaml_preserve(path: Path) -> Any:
    """Load YAML file with comment preservation using ruamel.yaml.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML content (CommentedMap), or empty dict if not exists

    Note: Falls back to pyyaml if ruamel.yaml is not available.
    """
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            if HAS_RUAMEL:
                return _ruamel_yaml.load(f) or {}
            else:
                return yaml.safe_load(f) or {}
    except Exception:
        return {}


def save_yaml_preserve(path: Path, data: Any):
    """Save YAML file with comment preservation using ruamel.yaml.

    Args:
        path: Path to YAML file
        data: Data to save (typically CommentedMap from ruamel)

    Creates parent directories if they don't exist.
    Note: Falls back to pyyaml if ruamel.yaml is not available.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        if HAS_RUAMEL:
            _ruamel_yaml.dump(data, f)
        else:
            yaml.dump(dict(data) if hasattr(data, 'items') else data,
                      f, default_flow_style=False, sort_keys=False, allow_unicode=True)
