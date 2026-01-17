#!/usr/bin/env python3
"""
SMC Column - Standard Model of Code Cosmological Visualization
Creates a 16-level vertical column with frosted glass + cyan-violet glow aesthetic

Run with: blender --background --python smc_column_blender.py
"""

import bpy
import math
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = "/Users/lech/PROJECTS_all/PROJECT_elements"
BLEND_FILE = os.path.join(OUTPUT_DIR, "SMC_Column_Cosmology.blend")
RENDER_FILE = os.path.join(OUTPUT_DIR, "SMC_Column_render.png")

# Column parameters
NUM_LEVELS = 16  # L-3 to L12
COLUMN_HEIGHT = 12.0
BASE_RADIUS = 1.5
TOP_RADIUS = 0.6
SEGMENT_GAP = 0.05  # Small gap between segments

# Colors (OKLCH-inspired, converted to RGB linear)
# Cyan base → Violet top gradient
COLOR_CYAN = (0.0, 0.6, 0.8, 1.0)      # L-3 (physical)
COLOR_TEAL = (0.0, 0.7, 0.6, 1.0)      # L0-L2 (syntactic)
COLOR_AMBER = (0.9, 0.6, 0.1, 1.0)     # L3 (semantic core - NODE)
COLOR_VIOLET = (0.5, 0.2, 0.9, 1.0)    # L8-L12 (cosmological)
COLOR_MAGENTA = (0.8, 0.2, 0.7, 1.0)   # L12 (universe)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clear_scene():
    """Remove all objects from scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def lerp_color(color1, color2, t):
    """Linear interpolate between two colors"""
    return tuple(c1 + (c2 - c1) * t for c1, c2 in zip(color1, color2))


def get_level_color(level_index, num_levels):
    """Get color for a specific level based on position"""
    t = level_index / (num_levels - 1)  # 0 to 1

    # Multi-stop gradient: cyan → teal → amber → violet → magenta
    if t < 0.2:  # Physical (L-3 to L-1)
        return lerp_color(COLOR_CYAN, COLOR_TEAL, t / 0.2)
    elif t < 0.4:  # Syntactic (L0 to L2)
        return lerp_color(COLOR_TEAL, COLOR_AMBER, (t - 0.2) / 0.2)
    elif t < 0.5:  # Semantic core (L3-L4)
        return lerp_color(COLOR_AMBER, COLOR_AMBER, (t - 0.4) / 0.1)  # Stay amber
    elif t < 0.75:  # Systemic (L5-L8)
        return lerp_color(COLOR_AMBER, COLOR_VIOLET, (t - 0.5) / 0.25)
    else:  # Cosmological (L9-L12)
        return lerp_color(COLOR_VIOLET, COLOR_MAGENTA, (t - 0.75) / 0.25)


# ============================================================================
# MATERIAL CREATION
# ============================================================================

def create_glass_glow_material(name, base_color, emission_strength=0.5):
    """
    Create frosted glass material with internal glow
    Matches the ethereal cyan-violet aesthetic from reference images
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)

    # Mix Shader for combining glass and emission
    mix_shader = nodes.new('ShaderNodeMixShader')
    mix_shader.location = (600, 0)
    mix_shader.inputs[0].default_value = 0.7  # 70% glass, 30% emission

    # Principled BSDF for glass
    glass = nodes.new('ShaderNodeBsdfPrincipled')
    glass.location = (200, 100)
    glass.inputs['Base Color'].default_value = base_color
    glass.inputs['Metallic'].default_value = 0.0
    glass.inputs['Roughness'].default_value = 0.15  # Slightly frosted
    glass.inputs['IOR'].default_value = 1.45
    glass.inputs['Transmission Weight'].default_value = 0.95  # Highly transmissive
    glass.inputs['Alpha'].default_value = 0.8

    # Emission for glow
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (200, -100)
    emission.inputs['Color'].default_value = base_color
    emission.inputs['Strength'].default_value = emission_strength

    # Connect nodes
    links.new(glass.outputs['BSDF'], mix_shader.inputs[1])
    links.new(emission.outputs['Emission'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])

    # Add Volume for internal glow (subtle)
    volume = nodes.new('ShaderNodeVolumePrincipled')
    volume.location = (400, -200)
    volume.inputs['Color'].default_value = base_color
    volume.inputs['Density'].default_value = 0.02
    volume.inputs['Anisotropy'].default_value = 0.8
    volume.inputs['Emission Strength'].default_value = 0.1
    volume.inputs['Emission Color'].default_value = base_color

    links.new(volume.outputs['Volume'], output.inputs['Volume'])

    return mat


# ============================================================================
# GEOMETRY CREATION
# ============================================================================

def create_column_segment(index, num_segments, total_height, base_r, top_r):
    """Create a single funnel segment of the column"""

    # Calculate segment dimensions
    segment_height = (total_height - (num_segments - 1) * SEGMENT_GAP) / num_segments

    # Position
    z_base = index * (segment_height + SEGMENT_GAP)
    z_top = z_base + segment_height

    # Radius interpolation (funnel shape - wider at bottom)
    t_base = index / num_segments
    t_top = (index + 1) / num_segments

    r_base = base_r + (top_r - base_r) * t_base
    r_top = base_r + (top_r - base_r) * t_top

    # Create cylinder with different radii (cone)
    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=r_base,
        radius2=r_top,
        depth=segment_height,
        location=(0, 0, z_base + segment_height / 2)
    )

    segment = bpy.context.active_object
    segment.name = f"Level_{index:02d}"

    # Smooth shading
    bpy.ops.object.shade_smooth()

    # Add subdivision for smoothness
    subsurf = segment.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    # Add slight bevel for soft edges
    bevel = segment.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.02
    bevel.segments = 3

    return segment


def create_smc_column():
    """Create the complete 16-level SMC column"""

    # Create collection for organization
    if "SMC_Column" not in bpy.data.collections:
        collection = bpy.data.collections.new("SMC_Column")
        bpy.context.scene.collection.children.link(collection)
    else:
        collection = bpy.data.collections["SMC_Column"]

    segments = []

    for i in range(NUM_LEVELS):
        # Create segment geometry
        segment = create_column_segment(
            i, NUM_LEVELS, COLUMN_HEIGHT, BASE_RADIUS, TOP_RADIUS
        )

        # Get color for this level
        color = get_level_color(i, NUM_LEVELS)

        # Calculate emission strength (stronger at L3/semantic core)
        if 5 <= i <= 7:  # L3-L5 region (semantic core)
            emission = 1.2
        elif i < 3:  # Physical base
            emission = 0.3
        else:  # Upper levels
            emission = 0.6

        # Create and apply material
        mat = create_glass_glow_material(
            f"GlassGlow_L{i-3}",  # L-3 to L12
            color,
            emission
        )
        segment.data.materials.append(mat)

        # Move to collection
        if segment.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(segment)
        if segment.name not in collection.objects:
            collection.objects.link(segment)

        segments.append(segment)

        # Print level info
        level_name = f"L{i-3}"
        print(f"Created {level_name}: color=({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f})")

    return segments


# ============================================================================
# SCENE SETUP
# ============================================================================

def setup_world():
    """Configure world/environment for the ethereal look"""
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("SMC_World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    nodes.clear()

    # Background
    background = nodes.new('ShaderNodeBackground')
    background.location = (0, 0)
    background.inputs['Color'].default_value = (0.02, 0.02, 0.03, 1.0)  # Dark graphite
    background.inputs['Strength'].default_value = 0.5

    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)

    links.new(background.outputs['Background'], output.inputs['Surface'])


def setup_lighting():
    """Add studio-style lighting"""

    # Key light (main illumination)
    bpy.ops.object.light_add(type='AREA', location=(4, -4, 8))
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 500
    key_light.data.size = 5
    key_light.data.color = (1.0, 0.98, 0.95)  # Warm white

    # Fill light (softer, from opposite side)
    bpy.ops.object.light_add(type='AREA', location=(-3, 3, 6))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 200
    fill_light.data.size = 4
    fill_light.data.color = (0.9, 0.95, 1.0)  # Cool white

    # Rim light (backlight for glow definition)
    bpy.ops.object.light_add(type='AREA', location=(0, 5, 4))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Light"
    rim_light.data.energy = 300
    rim_light.data.size = 3
    rim_light.data.color = (0.7, 0.8, 1.0)  # Blue tint


def setup_camera():
    """Position camera for optimal column view"""

    bpy.ops.object.camera_add(
        location=(6, -6, 7),
        rotation=(math.radians(60), 0, math.radians(45))
    )
    camera = bpy.context.active_object
    camera.name = "SMC_Camera"

    # Set as active camera
    bpy.context.scene.camera = camera

    # Adjust camera settings
    camera.data.lens = 50
    camera.data.clip_end = 100

    # Point at column center
    bpy.ops.object.constraint_add(type='TRACK_TO')
    camera.constraints["Track To"].target = None  # Will track empty

    # Create target empty at column center
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, COLUMN_HEIGHT / 2))
    target = bpy.context.active_object
    target.name = "Camera_Target"

    camera.constraints["Track To"].target = target
    camera.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    camera.constraints["Track To"].up_axis = 'UP_Y'


def setup_render_settings():
    """Configure render settings for high-quality output"""
    scene = bpy.context.scene

    # Use Eevee for faster preview (switch to Cycles for final)
    scene.render.engine = 'BLENDER_EEVEE_NEXT'  # Eevee Next in Blender 4.x

    # Resolution
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    # Eevee settings for glass and glow (Blender 4.x API)
    # Note: Bloom in 4.x is handled via compositor, not scene.eevee
    try:
        scene.eevee.use_gtao = True
    except AttributeError:
        pass  # May not exist in all versions

    # Screen space reflections (if available)
    try:
        scene.eevee.use_ssr = True
        scene.eevee.use_ssr_refraction = True
    except AttributeError:
        pass

    # Volumetrics (if available)
    try:
        scene.eevee.volumetric_start = 0.1
        scene.eevee.volumetric_end = 100
    except AttributeError:
        pass

    # Output
    scene.render.filepath = RENDER_FILE
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '16'

    # Transparent background
    scene.render.film_transparent = True

    # Setup compositor for bloom effect (Blender 4.x approach)
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links

    # Clear existing nodes
    nodes.clear()

    # Create render layers node
    render_layers = nodes.new('CompositorNodeRLayers')
    render_layers.location = (0, 0)

    # Create glare node for bloom
    glare = nodes.new('CompositorNodeGlare')
    glare.location = (300, 0)
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.threshold = 0.5
    glare.size = 8

    # Create composite output
    composite = nodes.new('CompositorNodeComposite')
    composite.location = (600, 0)

    # Create viewer for preview
    viewer = nodes.new('CompositorNodeViewer')
    viewer.location = (600, -200)

    # Connect nodes
    links.new(render_layers.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], composite.inputs['Image'])
    links.new(glare.outputs['Image'], viewer.inputs['Image'])


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*60)
    print("SMC COLUMN - STANDARD MODEL OF CODE COSMOLOGY")
    print("="*60 + "\n")

    # Clear existing scene
    print("Clearing scene...")
    clear_scene()

    # Setup world
    print("Setting up world environment...")
    setup_world()

    # Create the column
    print(f"\nCreating {NUM_LEVELS}-level SMC column...")
    segments = create_smc_column()
    print(f"Created {len(segments)} segments\n")

    # Setup lighting
    print("Adding studio lighting...")
    setup_lighting()

    # Setup camera
    print("Positioning camera...")
    setup_camera()

    # Configure render
    print("Configuring render settings...")
    setup_render_settings()

    # Save .blend file
    print(f"\nSaving .blend file to: {BLEND_FILE}")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)

    # Render preview
    print(f"Rendering to: {RENDER_FILE}")
    bpy.ops.render.render(write_still=True)

    print("\n" + "="*60)
    print("COMPLETE!")
    print(f"Blend file: {BLEND_FILE}")
    print(f"Render: {RENDER_FILE}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
