#!/usr/bin/env python3
"""
SMC Column V2 - Ethereal Funnel Aesthetic
Matches the cyan-violet glowing vase reference images

Run with: blender --background --python smc_column_v2.py
"""

import bpy
import math
import os
from mathutils import Vector

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = "/Users/lech/PROJECTS_all/PROJECT_elements"
BLEND_FILE = os.path.join(OUTPUT_DIR, "SMC_Column_v2.blend")
RENDER_FILE = os.path.join(OUTPUT_DIR, "SMC_Column_v2_render.png")

# Column parameters - taller, more elegant funnels
NUM_LEVELS = 16
TOTAL_HEIGHT = 20.0
BASE_RADIUS = 2.0
TOP_RADIUS = 0.8
SEGMENT_HEIGHT = 1.0  # Individual segment height
SEGMENT_GAP = 0.15

# OKLCH-inspired colors (more saturated for glow)
COLORS = {
    'cyan_deep': (0.05, 0.5, 0.7, 1.0),      # L-3 to L-1 (Physical)
    'teal': (0.1, 0.7, 0.6, 1.0),             # L0-L2 (Syntactic)
    'amber': (0.95, 0.65, 0.15, 1.0),         # L3-L4 (Semantic core)
    'violet': (0.5, 0.25, 0.85, 1.0),         # L5-L8 (Systemic)
    'magenta': (0.75, 0.2, 0.7, 1.0),         # L9-L12 (Cosmological)
}


def clear_scene():
    """Remove all objects from scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    """Interpolate between two colors"""
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def get_level_color(idx, total):
    """Get color for level with smooth multi-stop gradient"""
    t = idx / (total - 1)

    if t < 0.2:  # Physical (L-3 to L-1)
        return lerp_color(COLORS['cyan_deep'], COLORS['teal'], t / 0.2)
    elif t < 0.35:  # Syntactic (L0 to L2)
        return lerp_color(COLORS['teal'], COLORS['amber'], (t - 0.2) / 0.15)
    elif t < 0.45:  # Semantic core (L3-L4) - stays amber
        return COLORS['amber']
    elif t < 0.7:  # Systemic (L5-L8)
        return lerp_color(COLORS['amber'], COLORS['violet'], (t - 0.45) / 0.25)
    else:  # Cosmological (L9-L12)
        return lerp_color(COLORS['violet'], COLORS['magenta'], (t - 0.7) / 0.3)


# ============================================================================
# MATERIAL - Ethereal Glass with Volumetric Glow
# ============================================================================

def create_ethereal_material(name, color, emission_strength=2.0):
    """
    Create ethereal glowing glass material
    Designed to match the reference images
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    # shadow_method removed in Blender 4.x

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (1000, 0)

    # Add Shader for combining
    add_shader = nodes.new('ShaderNodeAddShader')
    add_shader.location = (800, 0)

    # Glass component (very translucent)
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.location = (400, 100)
    glass.inputs['Color'].default_value = color
    glass.inputs['Roughness'].default_value = 0.1
    glass.inputs['IOR'].default_value = 1.3

    # Emission component (for glow)
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (400, -100)
    emission.inputs['Color'].default_value = color
    emission.inputs['Strength'].default_value = emission_strength

    # Mix glass and emission
    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (600, 0)
    mix.inputs[0].default_value = 0.6  # 60% glass, 40% emission

    # Connect surface
    links.new(glass.outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], add_shader.inputs[0])

    # Add transparent component for ethereal look
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    transparent.location = (400, -300)
    transparent.inputs['Color'].default_value = (1, 1, 1, 1)

    links.new(transparent.outputs['BSDF'], add_shader.inputs[1])
    links.new(add_shader.outputs['Shader'], output.inputs['Surface'])

    # Volume for internal glow
    volume = nodes.new('ShaderNodeVolumeAbsorption')
    volume.location = (600, -400)
    volume.inputs['Color'].default_value = color
    volume.inputs['Density'].default_value = 0.1

    volume_emission = nodes.new('ShaderNodeEmission')
    volume_emission.location = (400, -500)
    volume_emission.inputs['Color'].default_value = color
    volume_emission.inputs['Strength'].default_value = 0.5

    add_volume = nodes.new('ShaderNodeAddShader')
    add_volume.location = (800, -400)

    links.new(volume.outputs['Volume'], add_volume.inputs[0])
    links.new(volume_emission.outputs['Emission'], add_volume.inputs[1])
    links.new(add_volume.outputs['Shader'], output.inputs['Volume'])

    return mat


# ============================================================================
# GEOMETRY - Elegant Funnel Shape
# ============================================================================

def create_funnel_segment(index, num_segments):
    """Create an elegant funnel/vase segment"""

    # Calculate position
    segment_total = SEGMENT_HEIGHT + SEGMENT_GAP
    z_pos = index * segment_total

    # Radius interpolation (larger at bottom)
    t = index / (num_segments - 1) if num_segments > 1 else 0
    radius_bottom = lerp(BASE_RADIUS, TOP_RADIUS, t)
    radius_top = lerp(BASE_RADIUS, TOP_RADIUS, min(1.0, t + 0.08))

    # Create using bezier profile + lathe (for smooth curves)
    # Fallback: use cylinder with scale
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64,
        radius=radius_bottom,
        depth=SEGMENT_HEIGHT,
        location=(0, 0, z_pos + SEGMENT_HEIGHT/2)
    )

    segment = bpy.context.active_object
    segment.name = f"Level_L{index-3}"

    # Scale top to create taper
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Select top vertices and scale
    mesh = segment.data
    for v in mesh.vertices:
        if v.co.z > 0:  # Top half
            scale_factor = radius_top / radius_bottom
            v.co.x *= scale_factor
            v.co.y *= scale_factor

    # Smooth shading
    bpy.ops.object.shade_smooth()

    # Subdivision for smoothness
    subsurf = segment.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    # Slight bevel for soft edges
    bevel = segment.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.03
    bevel.segments = 4

    return segment


def create_column():
    """Create the complete SMC column"""

    # Create collection
    if "SMC_Column" not in bpy.data.collections:
        col = bpy.data.collections.new("SMC_Column")
        bpy.context.scene.collection.children.link(col)
    else:
        col = bpy.data.collections["SMC_Column"]

    segments = []

    for i in range(NUM_LEVELS):
        segment = create_funnel_segment(i, NUM_LEVELS)

        # Get color and emission strength
        color = get_level_color(i, NUM_LEVELS)

        # Emission varies by level (stronger at semantic core L3-L4)
        if 5 <= i <= 7:  # L3-L5 region
            emission = 3.5
        elif i < 3:  # Physical base
            emission = 1.5
        else:
            emission = 2.5

        # Create and apply material
        mat = create_ethereal_material(f"Ethereal_L{i-3}", color, emission)
        segment.data.materials.append(mat)

        # Move to collection
        if segment.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(segment)
        col.objects.link(segment)

        segments.append(segment)

        level = f"L{i-3}"
        print(f"Created {level}: color=({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f}), emission={emission}")

    return segments


# ============================================================================
# SCENE SETUP
# ============================================================================

def setup_world():
    """Dark graphite background with subtle gradient"""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("SMC_World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    # Gradient background
    gradient = nodes.new('ShaderNodeTexGradient')
    gradient.location = (-400, 0)
    gradient.gradient_type = 'LINEAR'

    # Mapping for gradient direction
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Rotation'].default_value = (math.radians(90), 0, 0)

    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)

    # Color ramp for dark graphite gradient
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.015, 0.015, 0.02, 1)  # Very dark
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.03, 0.03, 0.04, 1)  # Slightly lighter

    # Background
    background = nodes.new('ShaderNodeBackground')
    background.location = (0, 0)
    background.inputs['Strength'].default_value = 1.0

    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)

    # Connect
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], output.inputs['Surface'])


def setup_lighting():
    """Studio lighting setup for ethereal glow"""

    # Key light (warm)
    bpy.ops.object.light_add(type='AREA', location=(5, -5, 15))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 800
    key.data.size = 8
    key.data.color = (1.0, 0.95, 0.9)
    key.rotation_euler = (math.radians(45), 0, math.radians(45))

    # Fill light (cool, from opposite side)
    bpy.ops.object.light_add(type='AREA', location=(-4, 4, 10))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 400
    fill.data.size = 6
    fill.data.color = (0.9, 0.95, 1.0)
    fill.rotation_euler = (math.radians(60), 0, math.radians(-135))

    # Rim light (purple/violet tint)
    bpy.ops.object.light_add(type='AREA', location=(0, 6, 8))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 300
    rim.data.size = 4
    rim.data.color = (0.8, 0.7, 1.0)
    rim.rotation_euler = (math.radians(30), 0, math.radians(180))


def setup_camera():
    """Camera positioned for elegant column view"""

    # Calculate column center
    column_center_z = (NUM_LEVELS * (SEGMENT_HEIGHT + SEGMENT_GAP)) / 2

    # Camera position
    bpy.ops.object.camera_add(
        location=(8, -8, column_center_z + 2),
        rotation=(math.radians(70), 0, math.radians(45))
    )
    camera = bpy.context.active_object
    camera.name = "SMC_Camera"
    bpy.context.scene.camera = camera

    # Camera settings
    camera.data.lens = 50
    camera.data.clip_end = 200

    # Create target at column center
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, column_center_z))
    target = bpy.context.active_object
    target.name = "Camera_Target"

    # Track to target
    track = camera.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'


def setup_render():
    """Configure render settings"""
    scene = bpy.context.scene

    # Eevee for fast + good glow
    scene.render.engine = 'BLENDER_EEVEE_NEXT'

    # Resolution
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    # Film settings
    scene.render.film_transparent = False  # Keep background

    # Output
    scene.render.filepath = RENDER_FILE
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    # Compositor for bloom/glare
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    # Render layers
    rl = nodes.new('CompositorNodeRLayers')
    rl.location = (0, 0)

    # Glare (bloom effect)
    glare = nodes.new('CompositorNodeGlare')
    glare.location = (300, 0)
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.threshold = 0.3
    glare.size = 9

    # Output
    comp = nodes.new('CompositorNodeComposite')
    comp.location = (600, 0)

    # Connect
    links.new(rl.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], comp.inputs['Image'])


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("SMC COLUMN V2 - ETHEREAL COSMOLOGY")
    print("="*60 + "\n")

    print("Clearing scene...")
    clear_scene()

    print("Setting up world...")
    setup_world()

    print(f"Creating {NUM_LEVELS}-level column...")
    segments = create_column()
    print(f"\nCreated {len(segments)} segments")

    print("\nSetting up lighting...")
    setup_lighting()

    print("Positioning camera...")
    setup_camera()

    print("Configuring render...")
    setup_render()

    print(f"\nSaving: {BLEND_FILE}")
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
