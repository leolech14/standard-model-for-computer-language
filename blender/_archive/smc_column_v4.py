#!/usr/bin/env python3
"""
SMC Column V4 - Elegant Curved Vase Forms
Creates proper elongated funnel shapes with clear cyan-violet gradient

Run with: blender --background --python smc_column_v4.py
"""

import bpy
import bmesh
import math
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = "/Users/lech/PROJECTS_all/PROJECT_elements"
BLEND_FILE = os.path.join(OUTPUT_DIR, "SMC_Column_v4.blend")
RENDER_FILE = os.path.join(OUTPUT_DIR, "SMC_Column_v4_render.png")

NUM_LEVELS = 16
LEVEL_HEIGHT = 2.0  # Height of each level
LEVEL_GAP = 0.15    # Gap between levels

# Radius progression (funnel: wide at bottom, narrow at top)
BASE_RADIUS_BOTTOM = 2.2   # Bottom of lowest level
BASE_RADIUS_TOP = 0.9      # Top of lowest level
TOP_RADIUS_BOTTOM = 0.7    # Bottom of highest level
TOP_RADIUS_TOP = 0.25      # Top of highest level

# OKLCH-inspired colors (Linear RGB)
# Clear progression: Cyan → Teal → Amber → Violet → Magenta
COLORS = {
    'deep_cyan':  (0.02, 0.45, 0.75, 1.0),   # L-3 to L-2 (Physical base)
    'cyan':       (0.08, 0.60, 0.85, 1.0),   # L-1 to L0
    'teal':       (0.12, 0.75, 0.60, 1.0),   # L1 to L2 (Syntactic)
    'amber':      (0.95, 0.70, 0.15, 1.0),   # L3 to L4 (Semantic core)
    'orange':     (0.92, 0.50, 0.20, 1.0),   # L5 (Transition)
    'violet':     (0.55, 0.30, 0.90, 1.0),   # L6 to L9 (Systemic)
    'magenta':    (0.80, 0.25, 0.75, 1.0),   # L10 to L12 (Cosmological)
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
    for block in bpy.data.curves:
        if block.users == 0:
            bpy.data.curves.remove(block)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def get_level_color(idx, total):
    """
    Get color for level with smooth 7-stop gradient matching OKLCH aesthetic
    idx 0 = L-3 (cyan base), idx 15 = L12 (magenta top)
    """
    t = idx / (total - 1) if total > 1 else 0

    # 7-stop gradient
    if t < 0.12:      # L-3, L-2: Deep cyan
        return lerp_color(COLORS['deep_cyan'], COLORS['cyan'], t / 0.12)
    elif t < 0.25:    # L-1, L0: Cyan to teal
        return lerp_color(COLORS['cyan'], COLORS['teal'], (t - 0.12) / 0.13)
    elif t < 0.38:    # L1, L2: Teal (syntactic)
        return lerp_color(COLORS['teal'], COLORS['amber'], (t - 0.25) / 0.13)
    elif t < 0.50:    # L3, L4: Amber (semantic core - brightest)
        return COLORS['amber']
    elif t < 0.62:    # L5: Amber to orange transition
        return lerp_color(COLORS['amber'], COLORS['orange'], (t - 0.50) / 0.12)
    elif t < 0.75:    # L6, L7, L8: Orange to violet
        return lerp_color(COLORS['orange'], COLORS['violet'], (t - 0.62) / 0.13)
    elif t < 0.88:    # L9, L10: Violet
        return lerp_color(COLORS['violet'], COLORS['magenta'], (t - 0.75) / 0.13)
    else:             # L11, L12: Magenta (cosmological)
        return COLORS['magenta']


# ============================================================================
# MATERIALS - Frosted Glass with Volumetric Glow
# ============================================================================

def create_ethereal_glass(name, color, emission_strength=2.5):
    """
    Create ethereal frosted glass material with internal glow
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (1000, 0)

    # === SURFACE SHADER ===

    # Glass BSDF - frosted translucent
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.location = (200, 200)
    glass.inputs['Color'].default_value = color
    glass.inputs['Roughness'].default_value = 0.08  # Slightly frosted
    glass.inputs['IOR'].default_value = 1.35

    # Emission for glow
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (200, 0)
    emission.inputs['Color'].default_value = color
    emission.inputs['Strength'].default_value = emission_strength

    # Transparent for ethereal effect
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    transparent.location = (200, -150)
    transparent.inputs['Color'].default_value = (1, 1, 1, 1)

    # Mix glass + emission
    mix1 = nodes.new('ShaderNodeMixShader')
    mix1.location = (450, 100)
    mix1.inputs[0].default_value = 0.35  # 35% emission, 65% glass

    links.new(glass.outputs['BSDF'], mix1.inputs[1])
    links.new(emission.outputs['Emission'], mix1.inputs[2])

    # Add transparency
    add_shader = nodes.new('ShaderNodeAddShader')
    add_shader.location = (650, 50)

    links.new(mix1.outputs['Shader'], add_shader.inputs[0])
    links.new(transparent.outputs['BSDF'], add_shader.inputs[1])

    links.new(add_shader.outputs['Shader'], output.inputs['Surface'])

    # === VOLUME SHADER - Internal glow ===
    vol_scatter = nodes.new('ShaderNodeVolumeScatter')
    vol_scatter.location = (400, -300)
    vol_scatter.inputs['Color'].default_value = color
    vol_scatter.inputs['Density'].default_value = 0.15
    vol_scatter.inputs['Anisotropy'].default_value = 0.6

    vol_emission = nodes.new('ShaderNodeEmission')
    vol_emission.location = (400, -450)
    vol_emission.inputs['Color'].default_value = color
    vol_emission.inputs['Strength'].default_value = 0.4

    add_vol = nodes.new('ShaderNodeAddShader')
    add_vol.location = (650, -350)

    links.new(vol_scatter.outputs['Volume'], add_vol.inputs[0])
    links.new(vol_emission.outputs['Emission'], add_vol.inputs[1])
    links.new(add_vol.outputs['Shader'], output.inputs['Volume'])

    return mat


# ============================================================================
# GEOMETRY - Elegant Curved Vase Profile
# ============================================================================

def create_vase_segment(idx, num_segments):
    """
    Create an elegant vase/funnel segment with curved profile
    Uses revolution surface from bezier-like profile
    """
    z_pos = idx * (LEVEL_HEIGHT + LEVEL_GAP)

    # Interpolate radii based on position in column
    t = idx / (num_segments - 1) if num_segments > 1 else 0
    r_bottom = lerp(BASE_RADIUS_BOTTOM, TOP_RADIUS_BOTTOM, t)
    r_top = lerp(BASE_RADIUS_TOP, TOP_RADIUS_TOP, t)

    # Create mesh via bmesh for curved profile
    mesh = bpy.data.meshes.new(f"Vase_L{idx-3}")
    obj = bpy.data.objects.new(f"Level_L{idx-3}", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    # Create curved profile (vase shape)
    # Profile goes from bottom-wide to pinched-middle to top-narrow
    segments_v = 24  # Vertical resolution
    segments_u = 64  # Circular resolution

    # Build profile points (r, z) - elegant vase curve
    profile = []
    for i in range(segments_v + 1):
        v = i / segments_v
        z = v * LEVEL_HEIGHT

        # Vase curve: wide bottom → pinch at 40% → slight bulge → narrow top
        if v < 0.4:
            # Bottom section curves inward
            curve = math.sin(v / 0.4 * math.pi / 2)
            r = lerp(r_bottom, r_bottom * 0.6, curve)
        elif v < 0.6:
            # Middle pinch
            local_t = (v - 0.4) / 0.2
            r = lerp(r_bottom * 0.6, r_bottom * 0.55, local_t)
        else:
            # Upper section tapers to top
            local_t = (v - 0.6) / 0.4
            curve = local_t ** 0.6  # Smooth taper
            r = lerp(r_bottom * 0.55, r_top, curve)

        profile.append((r, z))

    # Create vertices by revolving profile
    for i, (r, z) in enumerate(profile):
        for j in range(segments_u):
            angle = 2 * math.pi * j / segments_u
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            bm.verts.new((x, y, z + z_pos))

    bm.verts.ensure_lookup_table()

    # Create faces
    for i in range(segments_v):
        for j in range(segments_u):
            v1 = i * segments_u + j
            v2 = i * segments_u + (j + 1) % segments_u
            v3 = (i + 1) * segments_u + (j + 1) % segments_u
            v4 = (i + 1) * segments_u + j

            try:
                bm.faces.new([bm.verts[v1], bm.verts[v2], bm.verts[v3], bm.verts[v4]])
            except:
                pass

    # Cap bottom
    bottom_verts = [bm.verts[j] for j in range(segments_u)]
    try:
        bmesh.ops.convex_hull(bm, input=bottom_verts)
    except:
        pass

    # Cap top
    top_start = segments_v * segments_u
    top_verts = [bm.verts[top_start + j] for j in range(segments_u)]
    try:
        bmesh.ops.convex_hull(bm, input=top_verts)
    except:
        pass

    bm.to_mesh(mesh)
    bm.free()

    # Smooth shading
    for poly in mesh.polygons:
        poly.use_smooth = True

    # Add subdivision for extra smoothness
    subsurf = obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 1
    subsurf.render_levels = 2

    return obj


def create_column():
    """Create the complete SMC column with 16 levels"""

    if "SMC_Column" not in bpy.data.collections:
        col = bpy.data.collections.new("SMC_Column")
        bpy.context.scene.collection.children.link(col)
    else:
        col = bpy.data.collections["SMC_Column"]

    segments = []

    for i in range(NUM_LEVELS):
        segment = create_vase_segment(i, NUM_LEVELS)
        color = get_level_color(i, NUM_LEVELS)

        # Emission strength varies by layer type
        level_idx = i - 3  # L-3 to L12
        if 3 <= level_idx <= 4:      # Semantic core (L3-L4)
            emission = 4.5
        elif level_idx < 0:          # Physical (L-3 to L-1)
            emission = 2.0
        elif level_idx <= 2:         # Syntactic (L0 to L2)
            emission = 2.8
        elif level_idx <= 8:         # Systemic (L5 to L8)
            emission = 3.2
        else:                        # Cosmological (L9 to L12)
            emission = 3.5

        mat = create_ethereal_glass(f"Glass_L{level_idx}", color, emission)
        segment.data.materials.append(mat)

        # Move to collection
        if segment.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(segment)
        col.objects.link(segment)

        segments.append(segment)
        print(f"Created L{level_idx}: color=({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f}), emission={emission}")

    return segments


# ============================================================================
# SCENE SETUP
# ============================================================================

def setup_world():
    """Dark graphite background"""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    # Very dark blue-gray background
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Color'].default_value = (0.008, 0.010, 0.018, 1)
    bg.inputs['Strength'].default_value = 1.0

    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)

    links.new(bg.outputs['Background'], output.inputs['Surface'])


def setup_lighting():
    """Subtle studio lighting to complement emission"""

    # Key light (warm, from above-front)
    bpy.ops.object.light_add(type='AREA', location=(8, -8, 25))
    key = bpy.context.active_object
    key.name = "Key"
    key.data.energy = 600
    key.data.size = 12
    key.data.color = (1, 0.95, 0.88)
    key.rotation_euler = (math.radians(50), 0, math.radians(45))

    # Fill (cool, opposite side)
    bpy.ops.object.light_add(type='AREA', location=(-6, 6, 18))
    fill = bpy.context.active_object
    fill.name = "Fill"
    fill.data.energy = 350
    fill.data.size = 10
    fill.data.color = (0.85, 0.92, 1.0)
    fill.rotation_euler = (math.radians(55), 0, math.radians(-135))

    # Rim (violet tint for cosmic feel)
    bpy.ops.object.light_add(type='AREA', location=(0, 10, 15))
    rim = bpy.context.active_object
    rim.name = "Rim"
    rim.data.energy = 300
    rim.data.size = 8
    rim.data.color = (0.8, 0.7, 1.0)
    rim.rotation_euler = (math.radians(35), 0, math.radians(180))


def setup_camera():
    """Camera positioned to capture full column"""
    column_height = NUM_LEVELS * (LEVEL_HEIGHT + LEVEL_GAP)
    center_z = column_height / 2

    # Position camera to see entire column
    distance = column_height * 0.6
    bpy.ops.object.camera_add(
        location=(distance, -distance, center_z + 4),
        rotation=(math.radians(72), 0, math.radians(45))
    )
    cam = bpy.context.active_object
    cam.name = "Camera"
    bpy.context.scene.camera = cam
    cam.data.lens = 35  # Wider lens to capture more
    cam.data.clip_end = 200

    # Target at column center
    bpy.ops.object.empty_add(location=(0, 0, center_z))
    target = bpy.context.active_object
    target.name = "Target"

    track = cam.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'


def setup_render():
    """Configure Eevee render with bloom"""
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

    # Glare for bloom effect
    glare = nodes.new('CompositorNodeGlare')
    glare.location = (300, 0)
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.threshold = 0.15  # Lower threshold for more bloom
    glare.size = 9

    # Color balance to enhance cyan-violet
    color_balance = nodes.new('CompositorNodeColorBalance')
    color_balance.location = (550, 0)
    color_balance.correction_method = 'LIFT_GAMMA_GAIN'

    comp = nodes.new('CompositorNodeComposite')
    comp.location = (800, 0)

    links.new(rl.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], color_balance.inputs['Image'])
    links.new(color_balance.outputs['Image'], comp.inputs['Image'])


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("SMC COLUMN V4 - ELEGANT CURVED VASE FORMS")
    print("="*60 + "\n")

    clear_scene()
    setup_world()

    print("Creating column with curved vase profiles...")
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
