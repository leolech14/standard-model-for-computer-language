#!/usr/bin/env python3
"""
SMC Column V3 - Tall Elegant Funnel Shapes
Creates curved vase-like forms matching reference images

Run with: blender --background --python smc_column_v3.py
"""

import bpy
import bmesh
import math
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = "/Users/lech/PROJECTS_all/PROJECT_elements"
BLEND_FILE = os.path.join(OUTPUT_DIR, "SMC_Column_v3.blend")
RENDER_FILE = os.path.join(OUTPUT_DIR, "SMC_Column_v3_render.png")

NUM_LEVELS = 16
FUNNEL_HEIGHT = 1.8  # Height of each funnel
FUNNEL_GAP = 0.2
BASE_RADIUS_BOTTOM = 1.8
BASE_RADIUS_TOP = 0.6
TOP_RADIUS_BOTTOM = 0.9
TOP_RADIUS_TOP = 0.35

# Colors
COLORS = {
    'cyan': (0.1, 0.6, 0.85, 1.0),
    'teal': (0.15, 0.75, 0.65, 1.0),
    'amber': (0.95, 0.7, 0.2, 1.0),
    'violet': (0.55, 0.3, 0.9, 1.0),
    'magenta': (0.8, 0.25, 0.75, 1.0),
}


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def get_level_color(idx, total):
    t = idx / (total - 1)
    if t < 0.2:
        return lerp_color(COLORS['cyan'], COLORS['teal'], t / 0.2)
    elif t < 0.35:
        return lerp_color(COLORS['teal'], COLORS['amber'], (t - 0.2) / 0.15)
    elif t < 0.5:
        return COLORS['amber']
    elif t < 0.75:
        return lerp_color(COLORS['amber'], COLORS['violet'], (t - 0.5) / 0.25)
    else:
        return lerp_color(COLORS['violet'], COLORS['magenta'], (t - 0.75) / 0.25)


# ============================================================================
# MATERIAL
# ============================================================================

def create_glow_material(name, color, emission=2.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)

    # Emission-heavy material for glow
    emission_node = nodes.new('ShaderNodeEmission')
    emission_node.location = (200, 100)
    emission_node.inputs['Color'].default_value = color
    emission_node.inputs['Strength'].default_value = emission

    # Glass for some transparency
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.location = (200, -100)
    glass.inputs['Color'].default_value = color
    glass.inputs['Roughness'].default_value = 0.05
    glass.inputs['IOR'].default_value = 1.2

    # Mix - more emission than glass
    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (500, 0)
    mix.inputs[0].default_value = 0.3  # 30% glass, 70% emission

    links.new(glass.outputs['BSDF'], mix.inputs[1])
    links.new(emission_node.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output.inputs['Surface'])

    # Subtle volume
    vol_emission = nodes.new('ShaderNodeEmission')
    vol_emission.location = (400, -300)
    vol_emission.inputs['Color'].default_value = color
    vol_emission.inputs['Strength'].default_value = 0.3

    links.new(vol_emission.outputs['Emission'], output.inputs['Volume'])

    return mat


# ============================================================================
# GEOMETRY - Curved Funnel using Spin
# ============================================================================

def create_funnel_mesh(radius_bottom, radius_top, height, segments=64):
    """
    Create a smooth funnel/vase shape using curve profile
    """
    # Create mesh
    mesh = bpy.data.meshes.new("Funnel")
    obj = bpy.data.objects.new("Funnel", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Use bmesh for construction
    bm = bmesh.new()

    # Create profile vertices (curved inward like a vase)
    profile_verts = []
    num_profile = 16

    for i in range(num_profile + 1):
        t = i / num_profile
        z = t * height

        # Curved radius interpolation (pinch in the middle for vase shape)
        if t < 0.5:
            # Bottom half - curves inward
            r = lerp(radius_bottom, min(radius_bottom, radius_top) * 0.85, t * 2)
        else:
            # Top half - curves outward slightly then tapers
            t2 = (t - 0.5) * 2
            mid_r = min(radius_bottom, radius_top) * 0.85
            r = lerp(mid_r, radius_top, t2 ** 0.7)

        v = bm.verts.new((r, 0, z))
        profile_verts.append(v)

    bm.verts.ensure_lookup_table()

    # Create edges along profile
    for i in range(len(profile_verts) - 1):
        bm.edges.new((profile_verts[i], profile_verts[i + 1]))

    # Spin around Z axis
    geom = bm.verts[:] + bm.edges[:]
    bmesh.ops.spin(
        bm,
        geom=geom,
        cent=(0, 0, 0),
        axis=(0, 0, 1),
        angle=math.radians(360),
        steps=segments,
        use_duplicate=True
    )

    # Remove doubles
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

    # Fill bottom cap
    bottom_verts = [v for v in bm.verts if abs(v.co.z) < 0.01]
    if len(bottom_verts) >= 3:
        try:
            bmesh.ops.convex_hull(bm, input=bottom_verts)
        except:
            pass

    # Fill top cap
    top_verts = [v for v in bm.verts if abs(v.co.z - height) < 0.01]
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

    return obj


def create_funnel_segment_simple(idx, num_segments):
    """Create a funnel segment using simple cone + modifiers"""
    z_pos = idx * (FUNNEL_HEIGHT + FUNNEL_GAP)

    # Interpolate radii
    t = idx / (num_segments - 1) if num_segments > 1 else 0
    r_bottom = lerp(BASE_RADIUS_BOTTOM, TOP_RADIUS_BOTTOM, t)
    r_top = lerp(BASE_RADIUS_TOP, TOP_RADIUS_TOP, t)

    # Create cone
    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=r_bottom,
        radius2=r_top * 0.9,
        depth=FUNNEL_HEIGHT,
        location=(0, 0, z_pos + FUNNEL_HEIGHT / 2),
        end_fill_type='NGON'
    )

    obj = bpy.context.active_object
    obj.name = f"Level_L{idx-3}"

    # Smooth shading
    bpy.ops.object.shade_smooth()

    # Add modifiers for curve
    subsurf = obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    # Lattice deform for curve could be added here

    return obj


def create_column():
    """Create the SMC column"""
    if "SMC_Column" not in bpy.data.collections:
        col = bpy.data.collections.new("SMC_Column")
        bpy.context.scene.collection.children.link(col)
    else:
        col = bpy.data.collections["SMC_Column"]

    segments = []

    for i in range(NUM_LEVELS):
        segment = create_funnel_segment_simple(i, NUM_LEVELS)
        color = get_level_color(i, NUM_LEVELS)

        # Emission strength varies
        if 5 <= i <= 8:  # Semantic core
            emission = 4.0
        elif i < 3:  # Physical
            emission = 2.0
        else:
            emission = 3.0

        mat = create_glow_material(f"Glow_L{i-3}", color, emission)
        segment.data.materials.append(mat)

        # Move to collection
        if segment.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(segment)
        col.objects.link(segment)

        segments.append(segment)
        print(f"Created L{i-3}: color=({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f})")

    return segments


# ============================================================================
# SCENE SETUP
# ============================================================================

def setup_world():
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
    bg.inputs['Color'].default_value = (0.012, 0.012, 0.018, 1)  # Very dark blue-gray
    bg.inputs['Strength'].default_value = 1.0

    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)

    links.new(bg.outputs['Background'], output.inputs['Surface'])


def setup_lighting():
    # Key light
    bpy.ops.object.light_add(type='AREA', location=(6, -6, 20))
    key = bpy.context.active_object
    key.name = "Key"
    key.data.energy = 1000
    key.data.size = 10
    key.data.color = (1, 0.95, 0.9)
    key.rotation_euler = (math.radians(45), 0, math.radians(45))

    # Fill
    bpy.ops.object.light_add(type='AREA', location=(-5, 5, 15))
    fill = bpy.context.active_object
    fill.name = "Fill"
    fill.data.energy = 500
    fill.data.size = 8
    fill.data.color = (0.9, 0.95, 1)
    fill.rotation_euler = (math.radians(60), 0, math.radians(-135))

    # Rim (violet tint)
    bpy.ops.object.light_add(type='AREA', location=(0, 8, 12))
    rim = bpy.context.active_object
    rim.name = "Rim"
    rim.data.energy = 400
    rim.data.size = 6
    rim.data.color = (0.85, 0.75, 1)
    rim.rotation_euler = (math.radians(30), 0, math.radians(180))


def setup_camera():
    column_height = NUM_LEVELS * (FUNNEL_HEIGHT + FUNNEL_GAP)
    center_z = column_height / 2

    bpy.ops.object.camera_add(
        location=(10, -10, center_z + 3),
        rotation=(math.radians(65), 0, math.radians(45))
    )
    cam = bpy.context.active_object
    cam.name = "Camera"
    bpy.context.scene.camera = cam
    cam.data.lens = 50

    # Target
    bpy.ops.object.empty_add(location=(0, 0, center_z))
    target = bpy.context.active_object
    target.name = "Target"

    track = cam.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'


def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = RENDER_FILE
    scene.render.image_settings.file_format = 'PNG'

    # Compositor bloom
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    rl = nodes.new('CompositorNodeRLayers')
    rl.location = (0, 0)

    glare = nodes.new('CompositorNodeGlare')
    glare.location = (300, 0)
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.threshold = 0.2
    glare.size = 9

    comp = nodes.new('CompositorNodeComposite')
    comp.location = (600, 0)

    links.new(rl.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], comp.inputs['Image'])


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("SMC COLUMN V3 - TALL ELEGANT FUNNELS")
    print("="*60 + "\n")

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

    print("\n" + "="*60)
    print("COMPLETE!")
    print(f"  Blend: {BLEND_FILE}")
    print(f"  Render: {RENDER_FILE}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
