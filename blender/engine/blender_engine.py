"""
Blender engine for SMC column visualization.

Provides configuration and calculation methods for Blender 3D rendering
of the Standard Model of Code column. Follows the same engine pattern
as AppearanceEngine and PhysicsEngine.
"""

from typing import Any, Dict, List, Tuple

from .token_resolver import get_resolver


class BlenderEngine:
    """Provides configuration for Blender SMC column visualization."""

    def __init__(self):
        """Initialize the Blender engine with token resolver."""
        self.resolver = get_resolver()

    # =========================================================================
    # DOMAIN METHODS
    # =========================================================================

    def get_num_levels(self) -> int:
        """Get the total number of levels in the SMC column."""
        return self.resolver.blender("smc.domain.num_levels", 16)

    def get_level_offset(self) -> int:
        """Get the offset to convert index to level name."""
        return self.resolver.blender("smc.domain.level_offset", -3)

    def get_level_name(self, idx: int) -> str:
        """
        Get the display name for a level index.

        Args:
            idx: Zero-based level index (0-15)

        Returns:
            Level name like "L-3", "L0", "L5", "L12"
        """
        offset = self.get_level_offset()
        return f"L{idx + offset}"

    def get_plane_for_level(self, idx: int) -> str:
        """
        Determine which plane a level belongs to.

        Args:
            idx: Zero-based level index

        Returns:
            One of: "physical", "virtual", "semantic"
        """
        physical_end = self.resolver.blender("smc.domain.planes.physical.end", 2)
        virtual_end = self.resolver.blender("smc.domain.planes.virtual.end", 7)

        if idx <= physical_end:
            return "physical"
        elif idx <= virtual_end:
            return "virtual"
        else:
            return "semantic"

    # =========================================================================
    # COLOR METHODS
    # =========================================================================

    def get_level_color(self, idx: int, total: int) -> Tuple[float, float, float, float]:
        """
        Get the RGBA color for a level using gradient interpolation.

        Uses the 7-stop gradient defined in tokens, with fallback to
        pre-computed sRGB values for Blender compatibility.

        Args:
            idx: Zero-based level index
            total: Total number of levels

        Returns:
            RGBA tuple (0-1 range) for Blender materials
        """
        t = idx / (total - 1) if total > 1 else 0

        # Fallback sRGB colors from tokens
        colors = {
            'cyan': self.resolver.blender("color.fallback_srgb.cyan", [0.1, 0.6, 0.85, 1.0]),
            'teal': self.resolver.blender("color.fallback_srgb.teal", [0.15, 0.75, 0.65, 1.0]),
            'amber': self.resolver.blender("color.fallback_srgb.amber", [0.95, 0.7, 0.2, 1.0]),
            'violet': self.resolver.blender("color.fallback_srgb.violet", [0.55, 0.3, 0.9, 1.0]),
            'magenta': self.resolver.blender("color.fallback_srgb.magenta", [0.8, 0.25, 0.75, 1.0]),
        }

        # Gradient stops (matching token positions)
        if t < 0.2:
            return self._lerp_color(colors['cyan'], colors['teal'], t / 0.2)
        elif t < 0.35:
            return self._lerp_color(colors['teal'], colors['amber'], (t - 0.2) / 0.15)
        elif t < 0.5:
            a = colors['amber']
            return (a[0], a[1], a[2], a[3])
        elif t < 0.65:
            return self._lerp_color(colors['amber'], colors['violet'], (t - 0.5) / 0.15)
        elif t < 0.8:
            return self._lerp_color(colors['violet'], colors['magenta'], (t - 0.65) / 0.15)
        else:
            m = colors['magenta']
            return (m[0], m[1], m[2], m[3])

    def _lerp_color(
        self, c1: List[float], c2: List[float], t: float
    ) -> Tuple[float, float, float, float]:
        """Linear interpolation between two RGBA colors."""
        r = c1[0] + (c2[0] - c1[0]) * t
        g = c1[1] + (c2[1] - c1[1]) * t
        b = c1[2] + (c2[2] - c1[2]) * t
        a = c1[3] + (c2[3] - c1[3]) * t
        return (r, g, b, a)

    # =========================================================================
    # EMISSION METHODS
    # =========================================================================

    def get_level_emission(self, idx: int) -> float:
        """
        Get emission strength for a level based on its plane.

        Semantic core (L5-L8) gets highest emission for visual emphasis.

        Args:
            idx: Zero-based level index

        Returns:
            Emission strength value for Blender shader
        """
        plane = self.get_plane_for_level(idx)

        if plane == "physical":
            return self.resolver.blender("material.emission.physical_strength", 2.0)
        elif plane == "virtual":
            return self.resolver.blender("material.emission.virtual_strength", 3.0)
        else:
            # Semantic plane - check if in core (L5-L8 = idx 8-11)
            if 8 <= idx <= 11:
                return self.resolver.blender("material.emission.semantic_strength", 4.0)
            else:
                return self.resolver.blender("material.emission.cosmological_strength", 3.5)

    # =========================================================================
    # GEOMETRY METHODS
    # =========================================================================

    def get_geometry_config(self) -> Dict[str, Any]:
        """
        Get all geometry parameters for funnel construction.

        Returns:
            Dictionary with funnel dimensions and mesh settings
        """
        return {
            "funnel_height": self.resolver.blender("smc.geometry.funnel_height", 1.8),
            "funnel_gap": self.resolver.blender("smc.geometry.funnel_gap", 0.2),
            "radii": {
                "base_bottom": self.resolver.blender("smc.geometry.radii.base_bottom", 1.8),
                "base_top": self.resolver.blender("smc.geometry.radii.base_top", 0.6),
                "top_bottom": self.resolver.blender("smc.geometry.radii.top_bottom", 0.9),
                "top_top": self.resolver.blender("smc.geometry.radii.top_top", 0.35),
            },
            "mesh": {
                "segments": self.resolver.blender("smc.geometry.mesh.segments", 64),
                "profile_resolution": self.resolver.blender(
                    "smc.geometry.mesh.profile_resolution", 16
                ),
            },
        }

    def get_curve_radius(self, t: float, r_bottom: float, r_top: float) -> float:
        """
        Calculate radius at vertical position t using vase curve profile.

        Creates an elegant pinched vase shape by narrowing in the middle
        and flaring slightly at the top.

        Args:
            t: Vertical position (0 = bottom, 1 = top)
            r_bottom: Radius at bottom of funnel
            r_top: Radius at top of funnel

        Returns:
            Interpolated radius at position t
        """
        pinch_pos = self.resolver.blender("smc.curve.pinch_position", 0.5)
        pinch_factor = self.resolver.blender("smc.curve.pinch_factor", 0.85)
        flare_power = self.resolver.blender("smc.curve.top_flare_power", 0.7)

        min_r = min(r_bottom, r_top) * pinch_factor

        if t < pinch_pos:
            # Bottom half - curves inward toward pinch
            local_t = t / pinch_pos
            return self._lerp(r_bottom, min_r, local_t)
        else:
            # Top half - curves outward with flare
            local_t = (t - pinch_pos) / (1.0 - pinch_pos)
            return self._lerp(min_r, r_top, local_t ** flare_power)

    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation between two values."""
        return a + (b - a) * t

    def get_level_radii(self, idx: int, total: int) -> Tuple[float, float]:
        """
        Get bottom and top radii for a specific level.

        Radii interpolate from base (large) to top (small) across levels.

        Args:
            idx: Zero-based level index
            total: Total number of levels

        Returns:
            Tuple of (bottom_radius, top_radius)
        """
        geom = self.get_geometry_config()
        radii = geom["radii"]

        t = idx / (total - 1) if total > 1 else 0

        r_bottom = self._lerp(radii["base_bottom"], radii["top_bottom"], t)
        r_top = self._lerp(radii["base_top"], radii["top_top"], t)

        return (r_bottom, r_top)

    # =========================================================================
    # MATERIAL METHODS
    # =========================================================================

    def get_material_config(self) -> Dict[str, Any]:
        """
        Get material parameters for glass+emission shader.

        Returns:
            Dictionary with glass and volume settings
        """
        return {
            "glass": {
                "ior": self.resolver.blender("material.glass.ior", 1.2),
                "roughness": self.resolver.blender("material.glass.roughness", 0.05),
                "transmission": self.resolver.blender("material.glass.transmission", 0.3),
            },
            "volume": {
                "enabled": self.resolver.blender("material.volume.enabled", True),
                "density": self.resolver.blender("material.volume.density", 0.3),
            },
        }

    # =========================================================================
    # SCENE METHODS
    # =========================================================================

    def get_world_config(self) -> Dict[str, Any]:
        """Get world/background settings."""
        return {
            "background_color": self.resolver.blender(
                "scene.world.background_color", [0.012, 0.012, 0.018, 1.0]
            ),
            "background_strength": self.resolver.blender(
                "scene.world.background_strength", 1.0
            ),
        }

    def get_lighting_config(self) -> List[Dict[str, Any]]:
        """
        Get three-point lighting rig configuration.

        Returns:
            List of light definitions with type, energy, size, color,
            location, and rotation.
        """
        lights = []

        for light_name in ["key", "fill", "rim"]:
            prefix = f"scene.lighting.{light_name}"
            lights.append({
                "name": light_name.capitalize(),
                "type": self.resolver.blender(f"{prefix}.type", "AREA"),
                "energy": self.resolver.blender(f"{prefix}.energy", 500),
                "size": self.resolver.blender(f"{prefix}.size", 8),
                "color": self.resolver.blender(f"{prefix}.color", [1.0, 1.0, 1.0]),
                "location": self.resolver.blender(f"{prefix}.location", [0, 0, 10]),
                "rotation_deg": self.resolver.blender(f"{prefix}.rotation_deg", [0, 0, 0]),
            })

        return lights

    def get_camera_config(self) -> Dict[str, Any]:
        """Get camera setup configuration."""
        return {
            "lens": self.resolver.blender("scene.camera.lens", 50),
            "distance": self.resolver.blender("scene.camera.distance", 14.14),
            "height_offset": self.resolver.blender("scene.camera.height_offset", 3),
            "angle_deg": self.resolver.blender("scene.camera.angle_deg", 45),
            "tilt_deg": self.resolver.blender("scene.camera.tilt_deg", 65),
        }

    # =========================================================================
    # RENDER METHODS
    # =========================================================================

    def get_render_config(self) -> Dict[str, Any]:
        """Get render engine and output settings."""
        return {
            "engine": self.resolver.blender("render.engine", "BLENDER_EEVEE_NEXT"),
            "resolution": {
                "x": self.resolver.blender("render.resolution.x", 1920),
                "y": self.resolver.blender("render.resolution.y", 1080),
            },
            "output": {
                "format": self.resolver.blender("render.output.format", "PNG"),
                "color_depth": self.resolver.blender("render.output.color_depth", 16),
            },
            "bloom": {
                "enabled": self.resolver.blender("render.bloom.enabled", True),
                "type": self.resolver.blender("render.bloom.type", "FOG_GLOW"),
                "quality": self.resolver.blender("render.bloom.quality", "HIGH"),
                "threshold": self.resolver.blender("render.bloom.threshold", 0.2),
                "size": self.resolver.blender("render.bloom.size", 9),
            },
        }

    # =========================================================================
    # AGGREGATE CONFIG
    # =========================================================================

    def to_blender_config(self) -> Dict[str, Any]:
        """
        Generate complete Blender configuration dictionary.

        Aggregates all config sections for easy consumption by
        the Blender script.

        Returns:
            Complete configuration dictionary
        """
        return {
            "domain": {
                "num_levels": self.get_num_levels(),
                "level_offset": self.get_level_offset(),
            },
            "geometry": self.get_geometry_config(),
            "material": self.get_material_config(),
            "world": self.get_world_config(),
            "lighting": self.get_lighting_config(),
            "camera": self.get_camera_config(),
            "render": self.get_render_config(),
        }
