"""
Token resolver for Blender visualization tokens.

Standalone resolver that loads tokens from the local blender/tokens/ folder.
"""

import json
from pathlib import Path
from typing import Any, Optional

# Singleton instance
_resolver_instance = None


class TokenResolver:
    """Resolves design tokens from JSON files."""

    def __init__(self, tokens_dir: Optional[Path] = None):
        """
        Initialize the token resolver.

        Args:
            tokens_dir: Path to tokens directory. Defaults to ../tokens/
        """
        if tokens_dir is None:
            current = Path(__file__).resolve()
            tokens_dir = current.parent.parent / "tokens"

        self.tokens_dir = Path(tokens_dir)
        self._tokens = self._load_tokens("appearance.tokens.json")

    def _load_tokens(self, filename: str) -> dict:
        """Load tokens from a JSON file."""
        filepath = self.tokens_dir / filename
        if filepath.exists():
            try:
                with open(filepath, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _resolve_path(self, tokens: dict, path: str) -> Any:
        """
        Resolve a dot-notation path in the tokens dict.

        Handles both direct values and $value wrapped values.
        """
        parts = path.split(".")
        current = tokens

        for part in parts:
            if not isinstance(current, dict):
                return None
            if part not in current:
                return None
            current = current[part]

        if isinstance(current, dict) and "$value" in current:
            return current["$value"]

        return current

    def blender(self, path: str, default: Any = None) -> Any:
        """
        Get a Blender token value.

        Args:
            path: Dot-notation path like "smc.geometry.funnel_height"
            default: Default value if path not found

        Returns:
            The token value or default
        """
        result = self._resolve_path(self._tokens, path)
        return result if result is not None else default


def get_resolver() -> TokenResolver:
    """Get the singleton token resolver instance."""
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = TokenResolver()
    return _resolver_instance
