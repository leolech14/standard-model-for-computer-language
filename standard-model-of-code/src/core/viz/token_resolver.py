"""
Token resolver for design tokens.

Resolves design tokens from JSON files in schema/viz/tokens/.
Provides lookup with dot-notation paths and default fallbacks.
Generates CSS custom properties from tokens for injection into HTML.

Token Files:
    - appearance.tokens.json: Graph visuals (node/edge colors, sizes)
    - controls.tokens.json: UI controls (panels, buttons, layouts)
    - theme.tokens.json: UI chrome (backgrounds, text, typography, shadows)
    - layout.tokens.json: Spacing, z-index, transitions, radius

Theme Support:
    - theme.tokens.json can contain a "themes" object with theme variants
    - Default theme is "dark" (the root tokens)
    - Variants (light, high-contrast) are stored in themes.{name}
    - CSS is generated with [data-theme="X"] attribute selectors
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Singleton instance
_resolver_instance = None


class TokenResolver:
    """Resolves design tokens from JSON schema files."""

    def __init__(self, tokens_dir: Optional[Path] = None):
        """
        Initialize the token resolver.

        Args:
            tokens_dir: Path to tokens directory. Defaults to schema/viz/tokens/.
        """
        if tokens_dir is None:
            # Find the project root by going up from this file
            current = Path(__file__).resolve()
            project_root = current.parent.parent.parent.parent
            tokens_dir = project_root / "schema" / "viz" / "tokens"

        self.tokens_dir = Path(tokens_dir)
        self._appearance_tokens = self._load_tokens("appearance.tokens.json")
        self._controls_tokens = self._load_tokens("controls.tokens.json")
        self._theme_tokens = self._load_tokens("theme.tokens.json")
        self._layout_tokens = self._load_tokens("layout.tokens.json")

        # Extract theme variants
        self._theme_variants = self._theme_tokens.get("themes", {})
        self._default_theme = self._theme_tokens.get("$default-theme", "dark")

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

        Args:
            tokens: Token dictionary to search
            path: Dot-notation path like "color.edge.default"

        Returns:
            The resolved value or None if not found
        """
        parts = path.split(".")
        current = tokens

        for part in parts:
            if not isinstance(current, dict):
                return None
            if part not in current:
                return None
            current = current[part]

        # If we found a dict with $value, extract it
        if isinstance(current, dict) and "$value" in current:
            return current["$value"]

        return current

    def appearance(self, path: str, default: Any = None) -> Any:
        """
        Get an appearance token value.

        Args:
            path: Dot-notation path like "color.edge.default"
            default: Default value if path not found

        Returns:
            The token value or default
        """
        result = self._resolve_path(self._appearance_tokens, path)
        return result if result is not None else default

    def controls(self, path: str, default: Any = None) -> Any:
        """
        Get a controls token value.

        Args:
            path: Dot-notation path like "panels.metrics.visible"
            default: Default value if path not found

        Returns:
            The token value or default
        """
        result = self._resolve_path(self._controls_tokens, path)
        return result if result is not None else default

    def theme(self, path: str, default: Any = None) -> Any:
        """
        Get a theme token value.

        Args:
            path: Dot-notation path like "color.bg.surface"
            default: Default value if path not found

        Returns:
            The token value or default
        """
        result = self._resolve_path(self._theme_tokens, path)
        return result if result is not None else default

    def layout(self, path: str, default: Any = None) -> Any:
        """
        Get a layout token value.

        Args:
            path: Dot-notation path like "spacing.3"
            default: Default value if path not found

        Returns:
            The token value or default
        """
        result = self._resolve_path(self._layout_tokens, path)
        return result if result is not None else default

    def _flatten_tokens(self, tokens: dict, prefix: str = "") -> List[Tuple[str, str]]:
        """
        Flatten nested token dict to list of (css-var-name, value) tuples.

        Skips keys starting with $ (metadata).
        Converts dots to dashes for CSS variable names.

        Args:
            tokens: Token dictionary
            prefix: Current path prefix

        Returns:
            List of (name, value) tuples
        """
        result = []
        for key, value in tokens.items():
            # Skip metadata keys
            if key.startswith("$"):
                continue

            var_name = f"{prefix}-{key}" if prefix else key

            if isinstance(value, dict):
                if "$value" in value:
                    # Terminal value node
                    result.append((var_name, str(value["$value"])))
                else:
                    # Nested object, recurse
                    result.extend(self._flatten_tokens(value, var_name))
            else:
                # Direct value (shouldn't happen in well-formed tokens)
                result.append((var_name, str(value)))

        return result

    def generate_css_variables(self, include: Optional[List[str]] = None) -> str:
        """
        Generate CSS custom properties from tokens.

        Args:
            include: List of token sets to include. Options: "theme", "layout", "appearance".
                     Defaults to ["theme", "layout"] (UI-focused tokens).

        Returns:
            CSS string with :root block containing custom properties.

        Example output:
            :root {
              --color-bg-base: oklch(8% 0.02 250);
              --spacing-3: 8px;
              ...
            }
        """
        if include is None:
            include = ["theme", "layout"]

        variables = []

        if "theme" in include:
            variables.extend(self._flatten_tokens(self._theme_tokens))
        if "layout" in include:
            variables.extend(self._flatten_tokens(self._layout_tokens))
        if "appearance" in include:
            variables.extend(self._flatten_tokens(self._appearance_tokens))

        if not variables:
            return ""

        # Build CSS
        lines = [":root {"]
        for name, value in sorted(variables):
            css_name = name.replace(".", "-").replace("_", "-").lower()
            lines.append(f"  --{css_name}: {value};")
        lines.append("}")

        return "\n".join(lines)

    def get_css_variable(self, token_type: str, path: str) -> str:
        """
        Get the CSS variable name for a token path.

        Args:
            token_type: "theme", "layout", "appearance"
            path: Token path like "color.bg.surface"

        Returns:
            CSS variable reference like "var(--color-bg-surface)"
        """
        css_name = path.replace(".", "-").replace("_", "-").lower()
        return f"var(--{css_name})"

    def get_theme_names(self) -> List[str]:
        """
        Get list of available theme names.

        Returns:
            List of theme names including the default theme.
        """
        themes = [self._default_theme]  # Default theme first
        for name in self._theme_variants.keys():
            if not name.startswith("$") and name != self._default_theme:
                themes.append(name)
        return themes

    def get_default_theme(self) -> str:
        """
        Get the default theme name.

        Returns:
            The default theme name (usually "dark").
        """
        return self._default_theme

    def _flatten_theme_tokens(self, tokens: dict, prefix: str = "") -> List[Tuple[str, str]]:
        """
        Flatten nested theme token dict to list of (css-var-name, value) tuples.
        Only extracts color-related tokens that vary between themes.

        Args:
            tokens: Theme variant token dictionary
            prefix: Current path prefix

        Returns:
            List of (name, value) tuples
        """
        result = []
        for key, value in tokens.items():
            # Skip metadata keys
            if key.startswith("$"):
                continue

            var_name = f"{prefix}-{key}" if prefix else key

            if isinstance(value, dict):
                if "$value" in value:
                    # Terminal value node
                    result.append((var_name, str(value["$value"])))
                else:
                    # Nested object, recurse
                    result.extend(self._flatten_theme_tokens(value, var_name))
            else:
                # Direct value (shouldn't happen in well-formed tokens)
                result.append((var_name, str(value)))

        return result

    def generate_theme_css(self, theme_name: str) -> str:
        """
        Generate CSS custom properties for a specific theme.

        Args:
            theme_name: Name of the theme ("dark", "light", "high-contrast")

        Returns:
            CSS string with theme-specific custom properties.
        """
        if theme_name == self._default_theme:
            # Default theme uses root tokens (already generated)
            return ""

        if theme_name not in self._theme_variants:
            return ""

        theme_tokens = self._theme_variants[theme_name]
        if not isinstance(theme_tokens, dict):
            return ""

        variables = self._flatten_theme_tokens(theme_tokens)
        if not variables:
            return ""

        # Build CSS with attribute selector
        lines = [f'[data-theme="{theme_name}"] {{']
        for name, value in sorted(variables):
            css_name = name.replace(".", "-").replace("_", "-").lower()
            lines.append(f"  --{css_name}: {value};")
        lines.append("}")

        return "\n".join(lines)

    def generate_all_themes_css(self, include: Optional[List[str]] = None) -> str:
        """
        Generate CSS for all themes including base variables and theme variants.

        This generates:
        1. :root block with default (dark) theme variables
        2. [data-theme="light"] block with light theme overrides
        3. [data-theme="high-contrast"] block with high-contrast overrides

        Args:
            include: List of token sets to include. Options: "theme", "layout", "appearance".
                     Defaults to ["theme", "layout"] (UI-focused tokens).

        Returns:
            Complete CSS string with all theme variables.
        """
        css_parts = []

        # Generate base variables (default/dark theme)
        base_css = self.generate_css_variables(include=include)
        if base_css:
            css_parts.append(base_css)

        # Generate theme variant CSS
        for theme_name in self.get_theme_names():
            if theme_name != self._default_theme:
                theme_css = self.generate_theme_css(theme_name)
                if theme_css:
                    css_parts.append(f"\n/* Theme: {theme_name} */\n{theme_css}")

        return "\n".join(css_parts)

    def get_js_theme_config(self) -> Dict[str, Any]:
        """
        Get theme configuration for injection into JavaScript.

        Returns a dict containing:
        - available: List of theme names
        - default: Default theme name
        - colors: Commonly needed colors for JS (edge colors, canvas bg, etc.)

        Returns:
            Dict with theme configuration for JS.
        """
        # Extract commonly needed colors from theme tokens
        colors = {}

        # Edge colors
        edge_colors = self._resolve_path(self._theme_tokens, "color.edge")
        if isinstance(edge_colors, dict):
            colors["edge"] = {}
            for key, val in edge_colors.items():
                if not key.startswith("$"):
                    if isinstance(val, dict) and "$value" in val:
                        colors["edge"][key] = val["$value"]
                    elif isinstance(val, str):
                        colors["edge"][key] = val

        # Viz colors
        viz_colors = self._resolve_path(self._theme_tokens, "color.viz")
        if isinstance(viz_colors, dict):
            colors["viz"] = {}
            for key, val in viz_colors.items():
                if not key.startswith("$"):
                    if isinstance(val, dict) and "$value" in val:
                        colors["viz"][key] = val["$value"]
                    elif isinstance(val, str):
                        colors["viz"][key] = val

        # Console colors
        console_colors = self._resolve_path(self._theme_tokens, "color.console")
        if isinstance(console_colors, dict):
            colors["console"] = {}
            for key, val in console_colors.items():
                if not key.startswith("$"):
                    if isinstance(val, dict) and "$value" in val:
                        colors["console"][key] = val["$value"]
                    elif isinstance(val, str):
                        colors["console"][key] = val

        # Color schemes
        schemes = self._resolve_path(self._theme_tokens, "color.schemes")
        if isinstance(schemes, dict):
            colors["schemes"] = {}
            for scheme_name, scheme_val in schemes.items():
                if not scheme_name.startswith("$") and isinstance(scheme_val, dict):
                    colors["schemes"][scheme_name] = {}
                    for key, val in scheme_val.items():
                        if not key.startswith("$"):
                            if isinstance(val, dict) and "$value" in val:
                                colors["schemes"][scheme_name][key] = val["$value"]
                            elif isinstance(val, str):
                                colors["schemes"][scheme_name][key] = val

        return {
            "available": self.get_theme_names(),
            "default": self._default_theme,
            "colors": colors
        }


def get_resolver() -> TokenResolver:
    """
    Get the singleton token resolver instance.

    Returns:
        TokenResolver instance
    """
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = TokenResolver()
    return _resolver_instance
