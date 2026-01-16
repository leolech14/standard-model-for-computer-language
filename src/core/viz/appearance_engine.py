"""
Appearance Engine - Applies visual tokens to graph data.

PURPOSE: Transform raw graph data into visually-encoded data.
CONCERN: Colors, sizes, shapes - WHAT THINGS LOOK LIKE.

DUAL SYSTEM:
    TOKENS (appearance.tokens.json)  →  ENGINE (this)  →  RENDERED OUTPUT
"""

import colorsys
import math
import re
from typing import Any, Dict, List, Optional, Tuple

from .token_resolver import get_resolver


class AppearanceEngine:
    """
    Applies appearance tokens to graph nodes and edges.

    Transforms raw data:
        {"name": "foo", "atom": "CORE.019", ...}
    Into visually-encoded data:
        {"name": "foo", "atom": "CORE.019", "color": "#00f3ff", "size": 2.4, ...}
    """

    def __init__(self):
        self.resolver = get_resolver()
        self._file_color_cache: Dict[int, str] = {}
        self._oklch_pattern = re.compile(r"^oklch\((.+)\)$", re.IGNORECASE)

    def apply_to_nodes(
        self,
        nodes: List[Dict[str, Any]],
        file_boundaries: List[Dict[str, Any]],
        color_mode: str = "tier"
    ) -> List[Dict[str, Any]]:
        """
        Apply appearance tokens to all nodes.

        Args:
            nodes: Raw node data from analysis
            file_boundaries: File boundary data for file-based coloring
            color_mode: "tier" | "ring" | "file"

        Returns:
            Nodes with added visual properties (color, size, etc.)
        """
        total_files = len(file_boundaries)

        for node in nodes:
            # Apply color
            if color_mode == "file":
                node["color"] = self._file_color(node.get("fileIdx", -1), total_files)
            elif color_mode == "ring":
                node["color"] = self._ring_color(node)
            else:  # tier
                node["color"] = self._tier_color(node.get("atom", ""))

            # Apply size
            node["size"] = self._compute_size(node)

        return nodes

    def apply_to_edges(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply appearance tokens to all edges."""
        default_color = self._normalize_color(
            self.resolver.appearance("color.edge.default", "#333333")
        )
        default_opacity = self.resolver.appearance(
            "color.edge-modes.opacity",
            self.resolver.appearance("opacity.edge", 0.2)
        )

        for edge in edges:
            edge_type = edge.get("edge_type", "default")
            edge["color"] = self._normalize_color(
                self.resolver.appearance(f"color.edge.{edge_type}", default_color)
            )
            edge["opacity"] = default_opacity

        return edges

    def _tier_color(self, atom_id: str) -> str:
        """Get color based on atom tier (T0/T1/T2/T3)."""
        if not atom_id:
            return self._normalize_color(
                self.resolver.appearance("color.atom.unknown", "#666666")
            )

        if atom_id.startswith("CORE."):
            return self._normalize_color(
                self.resolver.appearance("color.atom.t0-core", "hsl(200, 80%, 55%)")
            )
        elif atom_id.startswith("ARCH."):
            return self._normalize_color(
                self.resolver.appearance("color.atom.t1-arch", "hsl(45, 75%, 50%)")
            )
        elif atom_id.startswith("EXT.DISCOVERED"):
            return self._normalize_color(
                self.resolver.appearance("color.atom.t3-discovered", "hsl(15, 60%, 45%)")
            )
        elif atom_id.startswith("EXT."):
            return self._normalize_color(
                self.resolver.appearance("color.atom.t2-eco", "hsl(280, 70%, 50%)")
            )
        else:
            return self._normalize_color(
                self.resolver.appearance("color.atom.unknown", "#666666")
            )

    def _atom_family_color(self, atom_family: str, atom_id: str = "") -> str:
        """Get color based on atom_family (LOG/DAT/ORG/EXE/EXT)."""
        family = (atom_family or "").upper()
        if not family and atom_id:
            family = atom_id.split(".")[0].upper()

        family_colors = {
            "LOG": self._normalize_color(self.resolver.appearance("color.atom-family.LOG", "#00f3ff")),
            "DAT": self._normalize_color(self.resolver.appearance("color.atom-family.DAT", "#00ff9d")),
            "ORG": self._normalize_color(self.resolver.appearance("color.atom-family.ORG", "#ffb800")),
            "EXE": self._normalize_color(self.resolver.appearance("color.atom-family.EXE", "#ff0055")),
            "EXT": self._normalize_color(self.resolver.appearance("color.atom-family.EXT", "#8a2be2")),
            "UNKNOWN": self._normalize_color(
                self.resolver.appearance("color.atom-family.UNKNOWN", "#666666")
            ),
        }

        return family_colors.get(family, family_colors["UNKNOWN"])

    def _ring_color(self, node: Dict[str, Any]) -> str:
        """Get color based on node ring (domain/application/etc)."""
        ring = node.get("ring")
        ring_key = str(ring).upper() if ring else "UNKNOWN"

        ring_colors = {
            "DOMAIN": self._normalize_color(
                self.resolver.appearance("color.ring.DOMAIN", "#ffb800")
            ),
            "APPLICATION": self._normalize_color(
                self.resolver.appearance("color.ring.APPLICATION", "#00f3ff")
            ),
            "PRESENTATION": self._normalize_color(
                self.resolver.appearance("color.ring.PRESENTATION", "#00ff9d")
            ),
            "INTERFACE": self._normalize_color(
                self.resolver.appearance("color.ring.INTERFACE", "#4b7bec")
            ),
            "INFRASTRUCTURE": self._normalize_color(
                self.resolver.appearance("color.ring.INFRASTRUCTURE", "#ff0055")
            ),
            "CROSS_CUTTING": self._normalize_color(
                self.resolver.appearance("color.ring.CROSS_CUTTING", "#8a2be2")
            ),
            "TEST": self._normalize_color(
                self.resolver.appearance("color.ring.TEST", "#cc4abf")
            ),
            "UNKNOWN": self._normalize_color(
                self.resolver.appearance("color.ring.UNKNOWN", "#666666")
            ),
        }

        if ring_key in ring_colors:
            return ring_colors[ring_key]
        return self._atom_family_color(node.get("atom_family"), node.get("atom", ""))

    def _file_color(self, file_idx: int, total_files: int) -> str:
        """Get color based on file index using golden angle."""
        if file_idx < 0:
            return "#666666"

        if file_idx in self._file_color_cache:
            return self._file_color_cache[file_idx]

        angle = self.resolver.appearance("file-color.angle", 137.5)
        saturation = self.resolver.appearance("file-color.saturation", 70)
        lightness = self.resolver.appearance("file-color.lightness", 50)

        hue = (file_idx * angle) % 360
        color = f"hsl({hue}, {saturation}%, {lightness}%)"

        self._file_color_cache[file_idx] = color
        return color

    def _compute_size(self, node: Dict[str, Any]) -> float:
        """Compute node size based on importance (fanout)."""
        base = self.resolver.appearance("size.atom.base", 1.0)
        scale = self.resolver.appearance("size.atom.scale", 0.2)
        max_size = self.resolver.appearance("size.atom.max", 10.0)
        min_size = self.resolver.appearance("size.atom.min", 0.5)

        fanout = node.get("fan_out", node.get("out_degree", 0))
        size = base + (fanout * scale)

        return max(min_size, min(max_size, size))

    def get_render_config(self) -> Dict[str, Any]:
        """Get core rendering parameters."""
        return {
            "dimensions": self.resolver.appearance("render.dimensions", 3),
            "nodeResolution": self.resolver.appearance("render.node-resolution", 8),
            "antiAlias": self.resolver.appearance("render.anti-alias", True)
        }

    def get_background_config(self) -> Dict[str, Any]:
        """Get background and bloom configuration."""
        return {
            "color": self._normalize_color(
                self.resolver.appearance("color.background", "#000000")
            ),
            "stars": {
                "enabled": self.resolver.appearance("stars.enabled", True),
                "count": self.resolver.appearance("stars.count", 1500),
                "spread": self.resolver.appearance("stars.spread", 4000),
                "size": self.resolver.appearance("stars.size", 1.5),
                "opacity": self.resolver.appearance("opacity.stars", 0.6)
            },
            "bloom": {
                "enabled": self.resolver.appearance("bloom.enabled", False),
                "strength": self.resolver.appearance("bloom.strength", 1.2),
                "radius": self.resolver.appearance("bloom.radius", 0.4),
                "threshold": self.resolver.appearance("bloom.threshold", 0.2)
            }
        }

    def get_highlight_config(self) -> Dict[str, Any]:
        """Get selection and hover highlight colors."""
        return {
            "selected": self._normalize_color(
                self.resolver.appearance("color.highlight.selected", "#ffcc00")
            ),
            "hover": self._normalize_color(
                self.resolver.appearance("color.highlight.hover", "#00ccff")
            ),
            "connected": self._normalize_color(
                self.resolver.appearance("color.highlight.connected", "#44aa88")
            )
        }

    def get_flow_mode_config(self) -> Dict[str, Any]:
        """Get flow mode (Markov chain) visualization settings."""
        return {
            "highlightColor": self._normalize_color(
                self.resolver.appearance("flow-mode.highlight-color", "#ff8c00")
            ),
            "sizeMultiplier": self.resolver.appearance("flow-mode.size-multiplier", 1.8),
            "edgeWidthScale": self.resolver.appearance("flow-mode.edge-width-scale", 2.0),
            "particles": {
                "enabled": self.resolver.appearance("flow-mode.particles.enabled", True),
                "count": self.resolver.appearance("flow-mode.particles.count", 2),
                "speed": self.resolver.appearance("flow-mode.particles.speed", 0.005),
                "width": self.resolver.appearance("flow-mode.particles.width", 2)
            }
        }

    def get_boundary_config(self) -> Dict[str, Any]:
        """Get file boundary appearance configuration."""
        return {
            "fill_opacity": self.resolver.appearance("opacity.boundary-fill", 0.08),
            "wire_opacity": self.resolver.appearance("opacity.boundary-wire", 0.3),
            "padding": self.resolver.appearance("size.boundary.padding", 1.2),
            "min_extent": self.resolver.appearance("size.boundary.min_extent", 6),
            "quantile": self.resolver.appearance("size.boundary.quantile", 0.9)
        }

    def get_edge_modes_config(self) -> Dict[str, Any]:
        """Get edge visualization mode configuration."""
        base_width = self.resolver.appearance("color.edge-modes.width.base", None)
        if base_width is None:
            base_width = self.resolver.appearance("size.edge.width", 1)

        return {
            "resolution": {
                "internal": self._normalize_color(self.resolver.appearance(
                    "color.edge-modes.resolution.internal", "#4dd4ff"
                )),
                "external": self._normalize_color(self.resolver.appearance(
                    "color.edge-modes.resolution.external", "#ff6b6b"
                )),
                "unresolved": self._normalize_color(self.resolver.appearance(
                    "color.edge-modes.resolution.unresolved", "#9aa0a6"
                )),
                "unknown": self._normalize_color(self.resolver.appearance(
                    "color.edge-modes.resolution.unknown", "#666666"
                ))
            },
            "weight": {
                "hue_min": self.resolver.appearance("color.edge-modes.weight.hue-min", 210),
                "hue_max": self.resolver.appearance("color.edge-modes.weight.hue-max", 50),
                "chroma": self.resolver.appearance("color.edge-modes.weight.chroma", None),
                "saturation": self.resolver.appearance("color.edge-modes.weight.saturation", 45),
                "lightness": self.resolver.appearance("color.edge-modes.weight.lightness", 42)
            },
            "confidence": {
                "hue_min": self.resolver.appearance("color.edge-modes.confidence.hue-min", 20),
                "hue_max": self.resolver.appearance("color.edge-modes.confidence.hue-max", 120),
                "chroma": self.resolver.appearance("color.edge-modes.confidence.chroma", None),
                "saturation": self.resolver.appearance(
                    "color.edge-modes.confidence.saturation", 45
                ),
                "lightness": self.resolver.appearance(
                    "color.edge-modes.confidence.lightness", 44
                )
            },
            "width": {
                "base": base_width,
                "weight_scale": self.resolver.appearance(
                    "color.edge-modes.width.weight-scale", 2.5
                ),
                "confidence_scale": self.resolver.appearance(
                    "color.edge-modes.width.confidence-scale", 1.5
                )
            },
            "dim": {
                "interfile_factor": self.resolver.appearance(
                    "color.edge-modes.dim.interfile-factor", 0.25
                )
            },
            "opacity": self.resolver.appearance(
                "color.edge-modes.opacity",
                self.resolver.appearance("opacity.edge", 0.2)
            )
        }

    def get_edge_color_config(self) -> Dict[str, Any]:
        """Get edge type color configuration."""
        return {
            "default": self.resolver.appearance("color.edge.default", "#333333"),
            "calls": self.resolver.appearance("color.edge.calls", "#4dd4ff"),
            "contains": self.resolver.appearance("color.edge.contains", "#00ff9d"),
            "uses": self.resolver.appearance("color.edge.uses", "#ffb800"),
            "imports": self.resolver.appearance("color.edge.imports", "#9aa0a6"),
            "inherits": self.resolver.appearance("color.edge.inherits", "#ff6b6b")
        }

    def get_node_color_config(self) -> Dict[str, Any]:
        """Get node color configuration for tier and ring mappings."""
        return {
            "tier": {
                "CORE": self.resolver.appearance("color.atom.t0-core", "hsl(200, 80%, 55%)"),
                "ARCH": self.resolver.appearance("color.atom.t1-arch", "hsl(45, 75%, 50%)"),
                "EXT": self.resolver.appearance("color.atom.t2-eco", "hsl(280, 70%, 50%)"),
                "DISCOVERED": self.resolver.appearance(
                    "color.atom.t3-discovered", "hsl(15, 60%, 45%)"
                ),
                "UNKNOWN": self.resolver.appearance("color.atom.unknown", "#666666")
            },
            "ring": {
                "DOMAIN": self.resolver.appearance("color.ring.DOMAIN", "#ffb800"),
                "APPLICATION": self.resolver.appearance("color.ring.APPLICATION", "#00f3ff"),
                "PRESENTATION": self.resolver.appearance("color.ring.PRESENTATION", "#00ff9d"),
                "INTERFACE": self.resolver.appearance("color.ring.INTERFACE", "#4b7bec"),
                "INFRASTRUCTURE": self.resolver.appearance("color.ring.INFRASTRUCTURE", "#ff0055"),
                "CROSS_CUTTING": self.resolver.appearance("color.ring.CROSS_CUTTING", "#8a2be2"),
                "TEST": self.resolver.appearance("color.ring.TEST", "#cc4abf"),
                "UNKNOWN": self.resolver.appearance("color.ring.UNKNOWN", "#666666")
            },
            "unknown": self.resolver.appearance("color.atom.unknown", "#666666")
        }

    def get_file_color_config(self) -> Dict[str, Any]:
        """Get file color configuration."""
        return {
            "strategy": self.resolver.appearance("file-color.strategy", "golden-angle"),
            "angle": self.resolver.appearance("file-color.angle", 137.5),
            "chroma": self.resolver.appearance("file-color.chroma", None),
            "saturation": self.resolver.appearance("file-color.saturation", 70),
            "lightness": self.resolver.appearance("file-color.lightness", 50)
        }

    def _normalize_color(self, value: Any) -> Any:
        """Convert okLCH colors to sRGB CSS strings for renderer compatibility."""
        if not isinstance(value, str):
            return value

        match = self._oklch_pattern.match(value.strip())
        if not match:
            return value

        parsed = self._parse_oklch(match.group(1))
        if not parsed:
            return value

        r, g, b, alpha = parsed
        r_byte = int(round(max(0, min(1, r)) * 255))
        g_byte = int(round(max(0, min(1, g)) * 255))
        b_byte = int(round(max(0, min(1, b)) * 255))

        if alpha < 1:
            return f"rgba({r_byte}, {g_byte}, {b_byte}, {alpha:.3f})"
        return f"rgb({r_byte}, {g_byte}, {b_byte})"

    def _parse_oklch(self, content: str) -> Optional[Tuple[float, float, float, float]]:
        """Parse okLCH content and return sRGB channels plus alpha."""
        if not content:
            return None

        if "/" in content:
            parts, alpha_part = content.split("/", 1)
            alpha = alpha_part.strip()
        else:
            parts = content
            alpha = None

        tokens = re.split(r"[ ,]+", parts.strip())
        if len(tokens) < 3:
            return None

        l_token, c_token, h_token = tokens[0], tokens[1], tokens[2]
        L = self._parse_percent_or_number(l_token)
        C = self._parse_number(c_token)
        H = self._parse_angle(h_token)

        if L is None or C is None or H is None:
            return None

        alpha_value = 1.0
        if alpha is not None:
            alpha_value = self._parse_percent_or_number(alpha)
            if alpha_value is None:
                alpha_value = 1.0

        r, g, b = self._oklch_to_srgb(L, C, H)
        return r, g, b, max(0.0, min(1.0, alpha_value))

    @staticmethod
    def _parse_percent_or_number(token: str) -> Optional[float]:
        token = token.strip().lower()
        if not token:
            return None
        if token.endswith("%"):
            try:
                return float(token[:-1]) / 100.0
            except ValueError:
                return None
        try:
            value = float(token)
        except ValueError:
            return None
        return value / 100.0 if value > 1.0 else value

    @staticmethod
    def _parse_number(token: str) -> Optional[float]:
        token = token.strip().lower()
        if not token:
            return None
        if token.endswith("%"):
            try:
                return float(token[:-1]) / 100.0
            except ValueError:
                return None
        try:
            return float(token)
        except ValueError:
            return None

    @staticmethod
    def _parse_angle(token: str) -> Optional[float]:
        token = token.strip().lower()
        if not token:
            return None
        token = token.replace("deg", "")
        try:
            return float(token) % 360.0
        except ValueError:
            return None

    @staticmethod
    def _oklch_to_srgb(L: float, C: float, H: float) -> Tuple[float, float, float]:
        """Convert okLCH values to sRGB (0-1)."""
        h_rad = math.radians(H)
        a = C * math.cos(h_rad)
        b = C * math.sin(h_rad)

        l_ = L + 0.3963377774 * a + 0.2158037573 * b
        m_ = L - 0.1055613458 * a - 0.0638541728 * b
        s_ = L - 0.0894841775 * a - 1.2914855480 * b

        l = l_ ** 3
        m = m_ ** 3
        s = s_ ** 3

        r_lin = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
        g_lin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
        b_lin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

        r = AppearanceEngine._linear_to_srgb(r_lin)
        g = AppearanceEngine._linear_to_srgb(g_lin)
        b = AppearanceEngine._linear_to_srgb(b_lin)

        return (
            max(0.0, min(1.0, r)),
            max(0.0, min(1.0, g)),
            max(0.0, min(1.0, b))
        )

    @staticmethod
    def _linear_to_srgb(channel: float) -> float:
        if channel <= 0.0031308:
            return 12.92 * channel
        return 1.055 * (channel ** (1 / 2.4)) - 0.055
