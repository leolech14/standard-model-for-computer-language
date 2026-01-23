"""
OKLCH Color Mapper for File Tree Visualization

Transforms file metadata (extension, recency, importance) into perceptually-uniform
OKLCH colors for rendering file tree nodes. OKLCH is a perceptually uniform color
space that makes visual encoding more intuitive:

- Hue (0-360°): Semantic meaning (file type)
- Lightness (0-1): Recency (newer = brighter)
- Chroma (0-1): Importance (more important = more saturated)

The module loads semantic hue mappings from .agent/config/hue_wheel.yaml
and implements OKLCH→RGB conversion for web rendering.
"""

import math
from pathlib import Path
from typing import Optional, Tuple, Union
import yaml


class OKLCHColorMapper:
    """Maps file metadata to OKLCH color space with semantic hue wheel."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize color mapper with hue wheel configuration.

        Args:
            config_path: Path to hue_wheel.yaml. If None, looks in .agent/config/
        """
        if config_path is None:
            # Auto-locate relative to this file
            base = Path(__file__).parent.parent
            resolved_path = base / "config" / "hue_wheel.yaml"
        else:
            resolved_path = Path(config_path)

        self.config_path = resolved_path
        self.hue_map = self._load_hue_wheel()

    def _load_hue_wheel(self) -> dict:
        """Load and flatten hue mappings from YAML config."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Hue wheel config not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)

        # Flatten nested extension mappings
        hue_map = {}
        default_hue = 0

        # Handle both flat and nested (families) structures
        families = config.get("families", config)

        for family, data in families.items():
            if family == "default" and isinstance(data, dict):
                default_hue = data.get("hue", 0)
            elif isinstance(data, dict) and "extensions" in data:
                for ext, hue in data["extensions"].items():
                    hue_map[ext] = hue

        hue_map["_default"] = default_hue
        return hue_map

    def get_oklch_color(
        self, extension: str, recency_days: float, importance: float
    ) -> Tuple[float, float, float]:
        """
        Map file metadata to OKLCH color.

        Args:
            extension: File extension (e.g., '.py', '.js'). Must include dot.
            recency_days: Days since file was modified. 0 = today, 7+ = older.
            importance: Importance weight 0.0-1.0. Affects color saturation (chroma).

        Returns:
            Tuple of (H, L, C) in OKLCH space:
            - H (hue): 0-360° from hue wheel
            - L (lightness): 0.3-0.9 from recency
            - C (chroma): 0.1-0.4 from importance
        """
        # Map extension to hue
        hue = self.hue_map.get(extension.lower(), self.hue_map.get("_default", 0))

        # Map recency to lightness (0 days = 0.9, 90+ days = 0.3)
        lightness = self._map_recency_to_lightness(recency_days)

        # Map importance to chroma (0.0 = 0.1, 1.0 = 0.4)
        chroma = self._map_importance_to_chroma(importance)

        return (hue, lightness, chroma)

    @staticmethod
    def _map_recency_to_lightness(recency_days: float) -> float:
        """
        Map recency (days since modification) to lightness (0.3-0.9).

        Mapping:
        - 0 days (today): L = 0.9 (brightest)
        - 7 days: L = 0.7
        - 30 days: L = 0.5
        - 90+ days: L = 0.3 (darkest)
        """
        # Clamp to reasonable range
        days = min(max(recency_days, 0), 90)

        # Piecewise linear interpolation
        if days <= 7:
            # 0-7 days: 0.9 → 0.7
            return 0.9 - (0.2 * days / 7)
        elif days <= 30:
            # 7-30 days: 0.7 → 0.5
            return 0.7 - (0.2 * (days - 7) / 23)
        else:
            # 30-90+ days: 0.5 → 0.3
            return max(0.3, 0.5 - (0.2 * (days - 30) / 60))

    @staticmethod
    def _map_importance_to_chroma(importance: float) -> float:
        """
        Map importance weight (0.0-1.0) to chroma (0.1-0.4).

        More important = more saturated (higher chroma).
        """
        importance = max(0.0, min(1.0, importance))
        return 0.1 + (0.3 * importance)

    @staticmethod
    def oklch_to_rgb(l: float, c: float, h: float) -> Tuple[int, int, int]:
        """
        Convert OKLCH to sRGB color space.

        Uses the OKLab→Linear RGB conversion chain.

        Args:
            l: Lightness (0-1)
            c: Chroma (0-1)
            h: Hue (0-360 degrees)

        Returns:
            Tuple of (R, G, B) in 8-bit range (0-255)
        """
        # Convert hue from degrees to radians
        h_rad = math.radians(h)

        # OKLCH → OKLab
        a = c * math.cos(h_rad)
        b = c * math.sin(h_rad)

        # OKLab → Linear RGB (using standard conversion matrix)
        l_ = l + 0.3963377774 * a + 0.2158037573 * b
        m_ = l - 0.1055613458 * a - 0.0638541728 * b
        s_ = l - 0.0894841775 * a - 1.2914855480 * b

        l = l_ * l_ * l_
        m = m_ * m_ * m_
        s = s_ * s_ * s_

        r = (
            +4.0767416621 * l
            - 3.3077363322 * m
            + 0.2309101289 * s
        )
        g = (
            -1.2684380046 * l
            + 2.6097574011 * m
            - 0.3413193761 * s
        )
        b_out = (
            -0.0041960863 * l
            - 0.7034186147 * m
            + 1.7076147010 * s
        )

        # Linear RGB → sRGB (gamma correction)
        def srgb_compand(x):
            if x <= 0.0031308:
                return 12.92 * x
            else:
                return (1 + 0.055) * (x ** (1 / 2.4)) - 0.055

        r = srgb_compand(r)
        g = srgb_compand(g)
        b_out = srgb_compand(b_out)

        # Clamp to 0-1 and convert to 8-bit
        r = max(0, min(255, round(r * 255)))
        g = max(0, min(255, round(g * 255)))
        b = max(0, min(255, round(b_out * 255)))

        return (int(r), int(g), int(b))

    def get_rgb_hex(
        self, extension: str, recency_days: float, importance: float
    ) -> str:
        """
        Get OKLCH color as hex string for CSS/SVG.

        Args:
            extension: File extension (e.g., '.py')
            recency_days: Days since modification
            importance: Importance weight (0.0-1.0)

        Returns:
            Hex color string (e.g., '#A1B2C3')
        """
        h, l, c = self.get_oklch_color(extension, recency_days, importance)
        r, g, b = self.oklch_to_rgb(l, c, h)
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_oklch_css(
        self, extension: str, recency_days: float, importance: float
    ) -> str:
        """
        Get OKLCH color as CSS oklch() function string.

        Args:
            extension: File extension
            recency_days: Days since modification
            importance: Importance weight (0.0-1.0)

        Returns:
            CSS string like "oklch(0.5 0.3 220)"
        """
        h, l, c = self.get_oklch_color(extension, recency_days, importance)
        return f"oklch({l:.2f} {c:.2f} {h:.0f})"


# ============================================================================
# Test Examples
# ============================================================================

if __name__ == "__main__":
    # Initialize mapper
    mapper = OKLCHColorMapper()

    print("=" * 70)
    print("OKLCH Color Mapping Examples")
    print("=" * 70)

    # Test cases: (extension, recency_days, importance, description)
    test_cases = [
        (".py", 0, 1.0, "Python file, just modified, high importance"),
        (".py", 7, 0.5, "Python file, 1 week old, medium importance"),
        (".py", 90, 0.1, "Python file, 3 months old, low importance"),
        (".json", 0, 0.8, "Config file, fresh, important"),
        (".md", 30, 0.3, "Docs, month old, low importance"),
        (".js", 2, 0.9, "JavaScript, 2 days old, very important"),
        (".yaml", 15, 0.6, "Config, 2 weeks old, medium importance"),
        (".unknown", 5, 0.5, "Unknown extension, should use default hue"),
    ]

    print("\n{:<35} {:<45} {:<20}".format("Description", "OKLCH", "Hex RGB"))
    print("-" * 100)

    for ext, days, imp, desc in test_cases:
        h, l, c = mapper.get_oklch_color(ext, days, imp)
        hex_color = mapper.get_rgb_hex(ext, days, imp)
        oklch_css = mapper.get_oklch_css(ext, days, imp)

        print(
            f"{desc:<35} {oklch_css:<45} {hex_color:<20}"
        )

    print("\n" + "=" * 70)
    print("Recency Mapping Test (L value for different day ranges)")
    print("=" * 70)
    days_to_test = [0, 1, 7, 14, 30, 60, 90]
    for days in days_to_test:
        l = mapper._map_recency_to_lightness(days)
        print(f"  {days:3d} days → Lightness: {l:.2f}")

    print("\n" + "=" * 70)
    print("Importance Mapping Test (C value for 0.0-1.0 range)")
    print("=" * 70)
    importances = [0.0, 0.25, 0.5, 0.75, 1.0]
    for imp in importances:
        c = mapper._map_importance_to_chroma(imp)
        print(f"  Importance {imp:.2f} → Chroma: {c:.2f}")

    print("\n" + "=" * 70)
    print("Hue Wheel Coverage (loaded from config)")
    print("=" * 70)
    extensions_by_hue = sorted(
        [(ext, hue) for ext, hue in mapper.hue_map.items() if ext != "_default"],
        key=lambda x: x[1],
    )
    for ext, hue in extensions_by_hue[:10]:
        print(f"  {ext:<10} → Hue: {hue:3.0f}°")
    print(f"  ... and {len(extensions_by_hue) - 10} more")
    print(f"  Default hue: {mapper.hue_map.get('_default', 'not set')}°")
