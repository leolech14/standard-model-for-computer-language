#!/usr/bin/env python3
"""
SMC Column - Token-Driven Blender Visualization

Creates the Standard Model of Code column using the BlenderEngine
for all configuration. Zero hardcoded values.

Run from repo root:
  blender --background --python blender/scripts/smc_column.py

Architecture:
  blender/tokens/appearance.tokens.json → BlenderEngine → this script → Blender API
"""

import math
import os
import sys

# Add blender folder to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLENDER_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BLENDER_ROOT)

import bpy
import bmesh

from engine.blender_engine import BlenderEngine

# ============================================================================
# CONFIGURATION (from engine)
# ============================================================================

OUTPUT_DIR = os.path.join(BLENDER_ROOT, "output")
BLEND_FILE = os.path.join(OUTPUT_DIR, "SMC_Column.blend")
RENDER_FILE = os.path.join(OUTPUT_DIR, "SMC_Column_render.png")

# Initialize engine
engine = BlenderEngine()
CONFIG = engine.to_blender_config()


# ============================================================================
# UTILITIES
# ============================================================================

def clear_scene():
    """Remove all objects and orphan data from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


# ============================================================================
# MATERIALS
# ============================================================================

def create_glow_material(name: str, color: tuple, emission_strength: float):
    """
    Create a glowing glass material.

    Args:
        name: Material name
        color: RGBA color tuple
        emission_strength: Emission intensity from engine

    Returns:
        Blender material
    """
    mat_config = CONFIG["material"]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)

    # Emission shader
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (200, 100)
    emission.inputs['Color'].default_value = color
    emission.inputs['Strength'].default_value = emission_strength

    # Glass shader
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.location = (200, -100)
    glass.inputs['Color'].default_value = color
    glass.inputs['Roughness'].default_value = mat_config["glass"]["roughness"]
    glass.inputs['IOR'].default_value = mat_config["glass"]["ior"]

    # Mix shader (glass vs emission)
    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (500, 0)
    mix.inputs[0].default_value = mat_config["glass"]["transmission"]

    links.new(glass.outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output.inputs['Surface'])

    # Volumetric emission (if enabled)
    if mat_config["volume"]["enabled"]:
        vol_emission = nodes.new('ShaderNodeEmission')
        vol_emission.location = (400, -300)
        vol_emission.inputs['Color'].default_value = color
        vol_emission.inputs['Strength'].default_value = mat_config["volume"]["density"]
        links.new(vol_emission.outputs['Emission'], output.inputs['Volume'])

    return mat


# ============================================================================
# GEOMETRY
# ============================================================================

def create_funnel_segment(idx: int, num_segments: int):
    """
    Create a single funnel segment for level idx.

    Uses engine methods for all geometry calculations.

    Args:
        idx: Zero-based level index
        num_segments: Total number of segments

    Returns:
        Blender object
    """
    geom = CONFIG["geometry"]
    funnel_height = geom["funnel_height"]
    funnel_gap = geom["funnel_gap"]
    segments = geom["mesh"]["segments"]
    profile_res = geom["mesh"]["profile_resolution"]

    # Get radii from engine
    r_bottom, r_top = engine.get_level_radii(idx, num_segments)

    # Vertical position
    z_pos = idx * (funnel_height + funnel_gap)

    # Create mesh
    mesh = bpy.data.meshes.new(f"Funnel_{idx}")
    obj = bpy.data.objects.new(engine.get_level_name(idx), mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Build geometry with bmesh
    bm = bmesh.new()

    # Create profile vertices using engine curve
    profile_verts = []
    for i in range(profile_res + 1):
        t = i / profile_res
        z = t * funnel_height

        # Get radius from engine's curve function
        r = engine.get_curve_radius(t, r_bottom, r_top)

        v = bm.verts.new((r, 0, z))
        profile_verts.append(v)

    bm.verts.ensure_lookup_table()

    # Create edges along profile
    for i in range(len(profile_verts) - 1):
        bm.edges.new((profile_verts[i], profile_verts[i + 1]))

    # Spin around Z axis
    geom_to_spin = bm.verts[:] + bm.edges[:]
    bmesh.ops.spin(
        bm,
        geom=geom_to_spin,
        cent=(0, 0, 0),
        axis=(0, 0, 1),
        angle=math.radians(360),
        steps=segments,
        use_duplicate=True
    )

    # Remove doubles
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

    # Fill caps
    bottom_verts = [v for v in bm.verts if abs(v.co.z) < 0.01]
    if len(bottom_verts) >= 3:
        try:
            bmesh.ops.convex_hull(bm, input=bottom_verts)
        except:
            pass

    top_verts = [v for v in bm.verts if abs(v.co.z - funnel_height) < 0.01]
    if len(top_verts) >= 3:
        try:
            bmesh.ops.convex_hull(bm, input=top_verts)
        except:
            pass

    # Write to mesh
    bm.to_mesh(mesh)
    bm.free()

    # Smooth shading
    for poly in mesh.polygons:
        poly.use_smooth = True

    # Position
    obj.location.z = z_pos

    # Add subdivision for smoothness
    subsurf = obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return obj


def create_column():
    """Create the complete SMC column with all levels."""
    # Create collection
    col_name = "SMC_Column"
    if col_name not in bpy.data.collections:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    else:
        col = bpy.data.collections[col_name]

    num_levels = CONFIG["domain"]["num_levels"]
    segments = []

    for i in range(num_levels):
        # Create geometry
        segment = create_funnel_segment(i, num_levels)

        # Get color and emission from engine
        color = engine.get_level_color(i, num_levels)
        emission = engine.get_level_emission(i)

        # Create and assign material
        level_name = engine.get_level_name(i)
        mat = create_glow_material(f"Glow_{level_name}", color, emission)
        segment.data.materials.append(mat)

        # Move to collection
        if segment.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(segment)
        col.objects.link(segment)

        segments.append(segment)
        print(f"Created {level_name}: color=({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f}), emission={emission:.1f}")

    return segments


# ============================================================================
# SCENE SETUP
# ============================================================================

def setup_world():
    """Configure world background from tokens."""
    world_config = CONFIG["world"]

    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    bg = nodes.new('ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Color'].default_value = world_config["background_color"]
    bg.inputs['Strength'].default_value = world_config["background_strength"]

    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)

    links.new(bg.outputs['Background'], output.inputs['Surface'])


def setup_lighting():
    """Create three-point lighting rig from tokens."""
    for light_cfg in CONFIG["lighting"]:
        bpy.ops.object.light_add(
            type=light_cfg["type"],
            location=light_cfg["location"]
        )
        light = bpy.context.active_object
        light.name = light_cfg["name"]
        light.data.energy = light_cfg["energy"]
        light.data.size = light_cfg["size"]
        light.data.color = light_cfg["color"]

        # Convert degrees to radians for rotation
        rot_deg = light_cfg["rotation_deg"]
        light.rotation_euler = (
            math.radians(rot_deg[0]),
            math.radians(rot_deg[1]),
            math.radians(rot_deg[2])
        )


def setup_camera():
    """Position camera to frame the column, using token config."""
    cam_config = CONFIG["camera"]
    geom = CONFIG["geometry"]
    num_levels = CONFIG["domain"]["num_levels"]

    # Calculate column dimensions
    column_height = num_levels * (geom["funnel_height"] + geom["funnel_gap"])
    center_z = column_height / 2

    # Camera position from polar coordinates
    distance = cam_config["distance"]
    angle = math.radians(cam_config["angle_deg"])

    cam_x = distance * math.cos(angle)
    cam_y = -distance * math.sin(angle)
    cam_z = center_z + cam_config["height_offset"]

    bpy.ops.object.camera_add(
        location=(cam_x, cam_y, cam_z),
        rotation=(math.radians(cam_config["tilt_deg"]), 0, angle)
    )
    cam = bpy.context.active_object
    cam.name = "Camera"
    bpy.context.scene.camera = cam
    cam.data.lens = cam_config["lens"]

    # Create tracking target
    bpy.ops.object.empty_add(location=(0, 0, center_z))
    target = bpy.context.active_object
    target.name = "Target"

    track = cam.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'


def setup_render():
    """Configure render settings and compositor bloom from tokens."""
    render_config = CONFIG["render"]

    scene = bpy.context.scene
    scene.render.engine = render_config["engine"]
    scene.render.resolution_x = render_config["resolution"]["x"]
    scene.render.resolution_y = render_config["resolution"]["y"]
    scene.render.filepath = RENDER_FILE
    scene.render.image_settings.file_format = render_config["output"]["format"]

    # Compositor bloom
    bloom = render_config["bloom"]
    if bloom["enabled"]:
        scene.use_nodes = True
        tree = scene.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        # Render layers input
        rl = nodes.new('CompositorNodeRLayers')
        rl.location = (0, 0)

        # Glare node for bloom
        glare = nodes.new('CompositorNodeGlare')
        glare.location = (300, 0)
        glare.glare_type = bloom["type"]
        glare.quality = bloom["quality"]
        glare.threshold = bloom["threshold"]
        glare.size = bloom["size"]

        # Output
        comp = nodes.new('CompositorNodeComposite')
        comp.location = (600, 0)

        links.new(rl.outputs['Image'], glare.inputs['Image'])
        links.new(glare.outputs['Image'], comp.inputs['Image'])


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution: build column, setup scene, save and render."""
    print("\n" + "=" * 60)
    print("SMC COLUMN - TOKEN-DRIVEN BLENDER VISUALIZATION")
    print("=" * 60)
    print(f"Levels: {CONFIG['domain']['num_levels']}")
    print(f"Engine: {CONFIG['render']['engine']}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60 + "\n")

    clear_scene()
    setup_world()

    print("Creating column...")
    segments = create_column()
    print(f"Created {len(segments)} segments\n")

    setup_lighting()
    setup_camera()
    setup_render()

    print(f"Saving: {BLEND_FILE}")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)

    print(f"Rendering: {RENDER_FILE}")
    bpy.ops.render.render(write_still=True)

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print(f"  Blend: {BLEND_FILE}")
    print(f"  Render: {RENDER_FILE}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
