"""Hilfsfunktionen für den Figurenbau in Blender (headless, bpy)."""
import os
import bpy, bmesh, math
from mathutils import Vector, Matrix

# Arbeitsordner für .blend, Zwischen-Export und Bilder
ARBEIT = os.environ.get('ARBEIT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arbeit'))
os.makedirs(ARBEIT, exist_ok=True)
Q = os.environ.get('QUATERNIUS', os.path.expanduser('~/quaternius')) + '/'


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_gltf(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def mat(name, color, rough=0.75, metal=0.0, sheen=0.0, emit=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    return m


def srgb(h):
    """'#rrggbb' -> lineare Farbe"""
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def pose_world_rot(arm, bname, axis, deg):
    pb = arm.pose.bones[bname]
    M = arm.matrix_world @ pb.matrix
    head = M.translation.copy()
    R = Matrix.Translation(head) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-head)
    pb.matrix = arm.matrix_world.inverted() @ R @ M
    bpy.context.view_layer.update()


def relaxed_pose(arm):
    pose_world_rot(arm, 'upperarm_l', 'Y', 72)
    pose_world_rot(arm, 'upperarm_r', 'Y', -72)
    pose_world_rot(arm, 'lowerarm_l', 'X', -12)
    pose_world_rot(arm, 'lowerarm_r', 'X', -12)
    pose_world_rot(arm, 'thigh_l', 'Y', 4)
    pose_world_rot(arm, 'thigh_r', 'Y', -4)
    pose_world_rot(arm, 'calf_l', 'Y', -4)
    pose_world_rot(arm, 'calf_r', 'Y', 4)


def setup_render(res=(700, 1000), samples=48):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (*srgb('#cfe3ee'), 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
    def light(name, typ, loc, rot, energy, color='#ffffff', size=1.0):
        d = bpy.data.lights.new(name, typ); d.energy = energy; d.color = srgb(color)
        if typ == 'AREA': d.size = size
        o = bpy.data.objects.new(name, d); o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(o)
    light('Key', 'SUN', (0, 0, 0), (50, 0, -30), 3.2, '#fff3e0')
    light('Rim', 'SUN', (0, 0, 0), (60, 0, 160), 2.0, '#dfeaff')
    light('Fill', 'AREA', (0, -3, 1.3), (90, 0, 0), 120, '#ffffff', 2.5)
    g = bpy.data.objects.new('Ground', bpy.data.meshes.new('G'))
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, radius=4, segments=48); bm.to_mesh(g.data)
    g.data.materials.append(mat('Ground', srgb('#9bbf72'), 1.0))
    sc.collection.objects.link(g)


def camera(loc, target, lens=50):
    sc = bpy.context.scene
    cam = sc.objects.get('Cam')
    if not cam:
        cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam)
    cam.data.lens = lens
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
