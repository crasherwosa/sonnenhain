"""Fasst die Teile zu wenigen Meshes zusammen, backt weiche Schatten (Umgebungsverdeckung)
in die Punktfarben und exportiert eine .glb. Aufruf: python export.py <ziel.glb>"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from blib import ARBEIT
from details import add_edge_attr, bake_details

OUT = sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=ARBEIT + '/figur.blend')
arm = bpy.data.objects['Armature']
GROUPS = {
    'Body': lambda n: n in ('Body', 'Eyes', 'Eyebrows'),
    'Hair': lambda n: n.startswith('Hair'),
    'Headgear': lambda n: n.startswith(('Headband', 'Goggle')),
}
def group_of(n):
    for g, f in GROUPS.items():
        if f(n): return g
    return 'Outfit'

parts = {}
for o in arm.children:
    if o.type == 'MESH': add_edge_attr(o)   # Abstand zum Saum, für Nähte und Kanten
# flache Teile nicht vereinfachen, sonst verschwimmen Borte und Nähte
for n in ('Tabard',):
    o = bpy.data.objects[n]; vg = o.vertex_groups.new(name='Behalten'); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
for o in arm.children:
    if o.type == 'MESH': parts.setdefault(group_of(o.name), []).append(o)
joined = []
for g, objs in parts.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = g; o.data.name = g
    joined.append(o)

# Kleidung leicht vereinfachen (Dreiecksbudget ca. 30.000)
for o in joined:
    if o.name == 'Outfit':
        d = o.modifiers.new('D', 'DECIMATE'); d.ratio = 0.8
        d.vertex_group = 'Behalten'; d.invert_vertex_group = True
        o.modifiers.move(len(o.modifiers) - 1, 0)
        bpy.context.view_layer.objects.active = o
        with bpy.context.temp_override(object=o): bpy.ops.object.modifier_apply(modifier='D')

# Weiche Schatten (Umgebungsverdeckung) selbst berechnen: Strahlen von jedem Punkt nach außen
import bmesh, math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
random.seed(3)
allbm = bmesh.new()
for o in joined:
    t = bmesh.new(); t.from_mesh(o.data); me = bpy.data.meshes.new('t'); t.to_mesh(me); t.free(); allbm.from_mesh(me)
BV = BVHTree.FromBMesh(allbm)
DIRS = []
for i in range(40):   # gleichmäßig verteilte Richtungen (kosinusgewichtet um +Z)
    u, v = (i + 0.5) / 40, (i * 0.618034) % 1
    r = math.sqrt(u); DIRS.append(Vector((r * math.cos(6.2832 * v), r * math.sin(6.2832 * v), math.sqrt(1 - u))))
DIST = 0.09
for o in joined:
    me = o.data
    for c in list(me.color_attributes): me.color_attributes.remove(c)
    ca = me.color_attributes.new('AO', 'BYTE_COLOR', 'POINT')
    me.color_attributes.active_color = ca
    me.color_attributes.render_color_index = me.color_attributes.active_color_index
    floor = {'Body': 0.78, 'Hair': 0.74}.get(o.name, 0.55)
    tot = 0
    for v in me.vertices:
        n = v.normal
        q = n.to_track_quat('Z', 'Y')
        p = v.co + n * 0.003
        hits = 0
        for d in DIRS:
            loc, nr, idx, dist = BV.ray_cast(p, q @ d, DIST)
            if loc is not None: hits += 1 - dist / DIST
        ao = 1 - hits / len(DIRS)
        tot += ao
        x = floor + (1 - floor) * min(1, ao * 1.15)
        ca.data[v.index].color = (x, x, x, 1)
    print(o.name, 'AO Mittel', round(tot / len(me.vertices), 2))

# Gemalte Details (Gewebe, Leder, Nähte, Strähnen) in Texturen backen, in Grundhaltung
arm.data.pose_position = 'REST'
SIZES = {'Outfit': (2048, 1024), 'Hair': (1024, 512), 'Headgear': (512, None)}
for o in joined:
    if o.name in SIZES:
        img, nimg = bake_details(o, *SIZES[o.name]); print(o.name, 'gebacken', img.name, nimg.name if nimg else '-')
arm.data.pose_position = 'POSE'

for m in bpy.data.materials: m.use_backface_culling = True
bpy.ops.object.select_all(action='DESELECT')
for o in joined: o.select_set(True)
arm.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=False,
                          export_vertex_color='ACTIVE', export_image_format='JPEG', export_jpeg_quality=86,
                          export_yup=True, export_skins=True, export_rest_position_armature=True)
for o in joined:
    print(o.name, sum(len(p.vertices) - 2 for p in o.data.polygons), 'Dreiecke', [m.name for m in o.data.materials])
