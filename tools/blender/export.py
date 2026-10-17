"""Fasst die Teile zu wenigen Meshes zusammen, backt weiche Schatten (Umgebungsverdeckung)
in die Punktfarben und exportiert eine .glb. Aufruf: python export.py <figur.blend> <ziel.glb>"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from blib import ARBEIT
from details import add_edge_attr, bake_details

SRC, OUT = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
arm = bpy.data.objects['Armature']
GROUPS = {
    'Body': lambda n: n in ('Body', 'Eyes', 'Eyebrows'),
    'Hair': lambda n: n.startswith(('Hair', 'Beard')),
    'Headgear': lambda n: n.startswith(('Headband', 'Goggle', 'Kopf')),
}
def group_of(n):
    for g, f in GROUPS.items():
        if f(n): return g
    return 'Outfit'

# Fürs iPhone vereinfachen (Ziel: ca. 15.000 Dreiecke). Der Körper vorab (Gesicht bleibt fein),
# Kleidung, Haare und Kopfschmuck erst nach dem Backen: die Details entstehen auf dem feinen Netz
# und bleiben über die Texturkoordinaten erhalten. Kleine Teile und die flache Stoffbahn bleiben ganz.
ZIEL = 15000
def decimate(o, r, group=None):
    d = o.modifiers.new('D', 'DECIMATE'); d.ratio = r
    if group: d.vertex_group = group; d.invert_vertex_group = True
    o.modifiers.move(len(o.modifiers) - 1, 0)
    bpy.context.view_layer.objects.active = o
    with bpy.context.temp_override(object=o): bpy.ops.object.modifier_apply(modifier='D')
decimate(bpy.data.objects['Body'], 0.5, 'Head')
for o in arm.children:
    if o.type == 'MESH' and (o.name.startswith(('Tabard', 'Panel')) or len(o.data.polygons) < 150):
        o.vertex_groups.new(name='Behalten').add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')

parts = {}
for o in arm.children:
    if o.type == 'MESH': add_edge_attr(o)   # Abstand zum Saum, für Nähte und Kanten
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

# Gemalte Details (Gewebe, Leder, Nähte, Strähnen) in Texturen backen, in Grundhaltung
arm.data.pose_position = 'REST'
SIZES = {'Outfit': (1024, 512), 'Hair': (512, 256), 'Headgear': (256, None)}   # höchstens 1024 Pixel
for o in joined:
    if o.name in SIZES:
        img, nimg = bake_details(o, *SIZES[o.name]); print(o.name, 'gebacken', img.name, nimg.name if nimg else '-')
arm.data.pose_position = 'POSE'
tris = lambda o: sum(len(p.vertices) - 2 for p in o.data.polygons)
fixed = sum(tris(o) for o in joined if o.name in ('Body', 'Headgear'))
red = [o for o in joined if o.name == 'Outfit' or (o.name == 'Hair' and tris(o) > 2500)]   # kurze Frisuren bleiben ganz
fixed += sum(tris(o) for o in joined if o.name == 'Hair' and o not in red)
r = min(1.0, (ZIEL - fixed) / max(1, sum(tris(o) for o in red)))
print('Vereinfachen auf', round(r, 2))
for o in red:
    if r < 0.98: decimate(o, r, 'Behalten' if 'Behalten' in o.vertex_groups else None)
for o in joined:
    if 'Behalten' in o.vertex_groups: o.vertex_groups.remove(o.vertex_groups['Behalten'])

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

for m in bpy.data.materials: m.use_backface_culling = True
bpy.ops.object.select_all(action='DESELECT')
for o in joined: o.select_set(True)
arm.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=False,
                          export_vertex_color='ACTIVE', export_image_format='JPEG', export_jpeg_quality=86,
                          export_yup=True, export_skins=True, export_rest_position_armature=True)
for o in joined:
    print(o.name, sum(len(p.vertices) - 2 for p in o.data.polygons), 'Dreiecke', [m.name for m in o.data.materials])
