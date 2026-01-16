"""
Controls Engine - Applies UI control tokens to visualization.

PURPOSE: Configure UI panels, buttons, sliders, and interactions.
CONCERN: User interface bindings - WHAT THE USER CAN TOUCH.

DUAL SYSTEM:
    TOKENS (controls.tokens.json)  →  ENGINE (this)  →  UI CONFIG
"""

from typing import Any, Dict, List

from .token_resolver import get_resolver


class ControlsEngine:
    """
    Applies control tokens to generate UI configuration.

    Transforms token definitions into UI-ready config
    that can be injected into the HTML visualization.
    """

    def __init__(self):
        self.resolver = get_resolver()

    def get_panels_config(self) -> Dict[str, Any]:
        """Get panel visibility and position configuration."""
        return {
            "metrics": {
                "visible": self.resolver.controls("panels.metrics.visible", True),
                "position": self.resolver.controls("panels.metrics.position", "top-right"),
                "fields": self.resolver.controls("panels.metrics.fields", [
                    "edge-resolution", "call-ratio", "reachability",
                    "dead-code", "knot-score", "topology"
                ])
            },
            "fileInfo": {
                "visible": self.resolver.controls("panels.file-info.visible", False),
                "position": self.resolver.controls("panels.file-info.position", "bottom-left"),
                "showOn": self.resolver.controls("panels.file-info.show-on", "hover"),
                "fields": self.resolver.controls("panels.file-info.fields", [
                    "file-name", "cohesion", "purpose", "atom-count"
                ])
            },
            "report": {
                "visible": self.resolver.controls("panels.report.visible", False),
                "position": self.resolver.controls("panels.report.position", "top-right"),
                "width": self.resolver.controls("panels.report.width", 420)
            }
        }

    def get_buttons_config(self) -> Dict[str, Any]:
        """Get button configuration for datamaps and modes."""
        return {
            "datamaps": {
                "ALL": {
                    "enabled": self.resolver.controls("buttons.datamaps.ALL.$value", True),
                    "filter": None
                },
                "LOGIC": {
                    "enabled": self.resolver.controls("buttons.datamaps.LOGIC.$value", True),
                    "filter": "LOG"
                },
                "DATA": {
                    "enabled": self.resolver.controls("buttons.datamaps.DATA.$value", True),
                    "filter": "DAT"
                },
                "EXTERNAL": {
                    "enabled": self.resolver.controls("buttons.datamaps.EXTERNAL.$value", True),
                    "filter": "EXT"
                }
            },
            "modes": {
                "FILES": {
                    "enabled": self.resolver.controls("buttons.modes.FILES.$value", True),
                    "description": "Toggle file visualization"
                },
                "REPORT": {
                    "enabled": self.resolver.controls("buttons.modes.REPORT.$value", True),
                    "description": "Toggle report panel"
                }
            },
            "fileSubModes": {
                "COLOR": {
                    "enabled": self.resolver.controls("buttons.file-sub-modes.COLOR.$value", True),
                    "mode": "color"
                },
                "HULLS": {
                    "enabled": self.resolver.controls("buttons.file-sub-modes.HULLS.$value", True),
                    "mode": "hulls"
                },
                "CLUSTER": {
                    "enabled": self.resolver.controls("buttons.file-sub-modes.CLUSTER.$value", True),
                    "mode": "cluster"
                },
                "MAP": {
                    "enabled": self.resolver.controls("buttons.file-sub-modes.MAP.$value", True),
                    "mode": "map"
                }
            }
        }

    def get_sliders_config(self) -> Dict[str, Any]:
        """Get slider configuration for density, forces, and appearance."""
        return {
            "density": {
                "label": self.resolver.controls("sliders.density.label", "DETAIL"),
                "min": self.resolver.controls("sliders.density.min", 1),
                "max": self.resolver.controls("sliders.density.max", 10),
                "step": self.resolver.controls("sliders.density.step", 0.5),
                "default": self.resolver.controls("sliders.density.default", 1)
            },
            "clusterStrength": {
                "label": self.resolver.controls("sliders.cluster-strength.label", "CLUSTER FORCE"),
                "min": self.resolver.controls("sliders.cluster-strength.min", 0),
                "max": self.resolver.controls("sliders.cluster-strength.max", 1),
                "step": self.resolver.controls("sliders.cluster-strength.step", 0.1),
                "default": self.resolver.controls("sliders.cluster-strength.default", 0.45)
            },
            "boundaryOpacity": {
                "label": self.resolver.controls("sliders.boundary-opacity.label", "HULL OPACITY"),
                "min": self.resolver.controls("sliders.boundary-opacity.min", 0),
                "max": self.resolver.controls("sliders.boundary-opacity.max", 0.5),
                "step": self.resolver.controls("sliders.boundary-opacity.step", 0.02),
                "default": self.resolver.controls("sliders.boundary-opacity.default", 0.1)
            },
            "hullWireOpacity": {
                "label": self.resolver.controls("sliders.hull-wire-opacity.label", "HULL WIRE"),
                "min": self.resolver.controls("sliders.hull-wire-opacity.min", 0.05),
                "max": self.resolver.controls("sliders.hull-wire-opacity.max", 0.6),
                "step": self.resolver.controls("sliders.hull-wire-opacity.step", 0.02),
                "default": self.resolver.controls("sliders.hull-wire-opacity.default", 0.35)
            },
            "edgeOpacity": {
                "label": self.resolver.controls("sliders.edge-opacity.label", "EDGE OPACITY"),
                "min": self.resolver.controls("sliders.edge-opacity.min", 0),
                "max": self.resolver.controls("sliders.edge-opacity.max", 1),
                "step": self.resolver.controls("sliders.edge-opacity.step", 0.05),
                "default": self.resolver.controls("sliders.edge-opacity.default", 0.2)
            },
            "nodeScale": {
                "label": self.resolver.controls("sliders.node-scale.label", "NODE SCALE"),
                "min": self.resolver.controls("sliders.node-scale.min", 0.5),
                "max": self.resolver.controls("sliders.node-scale.max", 3),
                "step": self.resolver.controls("sliders.node-scale.step", 0.1),
                "default": self.resolver.controls("sliders.node-scale.default", 1)
            },
            "backgroundBrightness": {
                "label": self.resolver.controls("sliders.background-brightness.label", "BACKGROUND"),
                "min": self.resolver.controls("sliders.background-brightness.min", 0),
                "max": self.resolver.controls("sliders.background-brightness.max", 1),
                "step": self.resolver.controls("sliders.background-brightness.step", 0.05),
                "default": self.resolver.controls("sliders.background-brightness.default", 1)
            },
            "fileLightness": {
                "label": self.resolver.controls("sliders.file-lightness.label", "FILE LIGHT"),
                "min": self.resolver.controls("sliders.file-lightness.min", 20),
                "max": self.resolver.controls("sliders.file-lightness.max", 80),
                "step": self.resolver.controls("sliders.file-lightness.step", 1),
                "default": self.resolver.controls("sliders.file-lightness.default", 50)
            },
            "hullWireOpacity": {
                "label": self.resolver.controls("sliders.hull-wire-opacity.label", "HULL WIRE"),
                "min": self.resolver.controls("sliders.hull-wire-opacity.min", 0.05),
                "max": self.resolver.controls("sliders.hull-wire-opacity.max", 0.6),
                "step": self.resolver.controls("sliders.hull-wire-opacity.step", 0.02),
                "default": self.resolver.controls("sliders.hull-wire-opacity.default", 0.3)
            },
            "hueShift": {
                "label": self.resolver.controls("sliders.hue-shift.label", "HUE SHIFT"),
                "min": self.resolver.controls("sliders.hue-shift.min", -180),
                "max": self.resolver.controls("sliders.hue-shift.max", 180),
                "step": self.resolver.controls("sliders.hue-shift.step", 1),
                "default": self.resolver.controls("sliders.hue-shift.default", 0)
            },
            "chromaScale": {
                "label": self.resolver.controls("sliders.chroma-scale.label", "CHROMA SCALE"),
                "min": self.resolver.controls("sliders.chroma-scale.min", 0),
                "max": self.resolver.controls("sliders.chroma-scale.max", 2),
                "step": self.resolver.controls("sliders.chroma-scale.step", 0.05),
                "default": self.resolver.controls("sliders.chroma-scale.default", 1)
            },
            "lightnessShift": {
                "label": self.resolver.controls("sliders.lightness-shift.label", "LIGHT SHIFT"),
                "min": self.resolver.controls("sliders.lightness-shift.min", -20),
                "max": self.resolver.controls("sliders.lightness-shift.max", 20),
                "step": self.resolver.controls("sliders.lightness-shift.step", 1),
                "default": self.resolver.controls("sliders.lightness-shift.default", 0)
            }
        }

    def get_interactions_config(self) -> Dict[str, Any]:
        """Get interaction behavior configuration."""
        return {
            "hover": {
                "showLabel": self.resolver.controls("interactions.hover.show-label", True),
                "showPanel": self.resolver.controls("interactions.hover.show-panel", True),
                "highlight": self.resolver.controls("interactions.hover.highlight", True),
                "delayHideMs": self.resolver.controls("interactions.hover.delay-hide-ms", 300)
            },
            "click": {
                "select": self.resolver.controls("interactions.click.select", True),
                "zoomTo": self.resolver.controls("interactions.click.zoom-to", False),
                "showDetails": self.resolver.controls("interactions.click.show-details", True)
            },
            "navigation": {
                "rotate": self.resolver.controls("interactions.navigation.rotate", "left-click"),
                "pan": self.resolver.controls("interactions.navigation.pan", "right-click"),
                "zoom": self.resolver.controls("interactions.navigation.zoom", "scroll")
            }
        }

    def get_sidebar_config(self) -> Dict[str, Any]:
        """Get sidebar visibility and sizing configuration."""
        return {
            "visible": self.resolver.controls("sidebar.visible", True),
            "collapsed": self.resolver.controls("sidebar.collapsed", True),
            "width": self.resolver.controls("sidebar.width", 240)
        }

    def get_datamaps_config(self) -> List[Dict[str, Any]]:
        """Get datamap overlay definitions for visualization."""
        datamaps = self.resolver.controls("datamaps", [])
        if not isinstance(datamaps, list):
            return []

        normalized: List[Dict[str, Any]] = []
        for item in datamaps:
            if not isinstance(item, dict):
                continue
            match = dict(item.get("match") or {})
            atom_families = match.pop("atom_families", None)
            if atom_families and "atom_prefixes" not in match:
                match["atom_prefixes"] = atom_families
            normalized.append({**item, "match": match})

        return normalized

    def get_filters_config(self) -> Dict[str, Any]:
        """Get default filter configuration for sidebar controls."""
        return {
            "tiers": self.resolver.controls("filters.tiers", []),
            "rings": self.resolver.controls("filters.rings", []),
            "edges": self.resolver.controls("filters.edges", []),
            "metadata": {
                "showLabels": self.resolver.controls("filters.metadata.show-labels", True),
                "showFilePanel": self.resolver.controls("filters.metadata.show-file-panel", True),
                "showReportPanel": self.resolver.controls("filters.metadata.show-report-panel", True),
                "showEdges": self.resolver.controls("filters.metadata.show-edges", True)
            }
        }

    def to_js_config(self) -> Dict[str, Any]:
        """
        Export complete controls config for JavaScript consumption.

        This is injected into the HTML template.
        """
        return {
            "panels": self.get_panels_config(),
            "buttons": self.get_buttons_config(),
            "sliders": self.get_sliders_config(),
            "interactions": self.get_interactions_config(),
            "sidebar": self.get_sidebar_config(),
            "filters": self.get_filters_config(),
            "datamaps": self.get_datamaps_config()
        }

    def get_enabled_datamaps(self) -> List[str]:
        """Get list of enabled datamap button names."""
        buttons = self.get_buttons_config()
        return [
            name for name, config in buttons.get("datamaps", {}).items()
            if config.get("enabled", True)
        ]

    def get_enabled_modes(self) -> List[str]:
        """Get list of enabled mode button names."""
        buttons = self.get_buttons_config()
        return [
            name for name, config in buttons["modes"].items()
            if config.get("enabled", True)
        ]
