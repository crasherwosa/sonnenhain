"""Baut die Abenteurerin für Sonnenhain: Quaternius-Grundkörper (CC0) mit Skelett,
darauf eigene Kleidung, Haare und Ausrüstung. Aufruf: python build.py [render]"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from blib import *

OUT = ARBEIT + '/'
TEX = ARBEIT + '/tex/'
reset()
objs = import_gltf(Q + 'base/Superhero_Female_FullBody.gltf')
arm = [o for o in objs if o.type == 'ARMATURE'][0]
arm.name = 'Armature'
for o in list(objs):
    if o.name.startswith('Icosphere'): bpy.data.objects.remove(o)
body = bpy.data.objects['Superhero_Female']; body.name = 'Body'
eyes = bpy.data.objects['Eyes']
brows = bpy.data.objects['Eyebrows']

# Körperoberfläche als Referenz für Abstände (Grundhaltung)
_bm = bmesh.new(); _bm.from_mesh(body.data)
BODY = BVHTree.FromBMesh(_bm); _bm.free()

# ---------------------------------------------------------------- Materialien
C = {
    'linen':   (srgb('#f3eee4'), 0.9, 0.0),
    'leather': (srgb('#94603a'), 0.62, 0.0),
    'leather2':(srgb('#5e3c26'), 0.6, 0.0),
    'boot':    (srgb('#6e4428'), 0.55, 0.0),
    'brass':   (srgb('#d8b066'), 0.32, 0.9),
    'steel':   (srgb('#c4cacd'), 0.3, 0.9),
    'fur':     (srgb('#ece2cd'), 0.95, 0.0),
    'hair':    (srgb('#f7de9e'), 0.5, 0.0),
    'brow':    (srgb('#b98f55'), 0.7, 0.0),
    'lens':    (srgb('#86d0e0'), 0.08, 0.1),
}
M = {k: mat('M_' + k, *v) for k, v in C.items()}


def tex_mat(name, img, rough, normal=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(img)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    return m


M['skin'] = tex_mat('M_skin', TEX + 'skin.png', 0.6)
M['eyes'] = tex_mat('M_eyes', Q + 'textures/d08e3356a83211bc6ca21fe3a8e39f4b5c1a3b8f85457fc2c0fb57be09935025.png', 0.25)


def add_obj(name, me):
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.parent = arm
    return o


def rig(o, groups=None):
    """Armature-Modifier; groups: {knochen: gewicht} für starre Teile."""
    if groups:
        for b, w in groups.items():
            vg = o.vertex_groups.get(b) or o.vertex_groups.new(name=b)
            vg.add(range(len(o.data.vertices)), w, 'REPLACE')
    if not any(m.type == 'ARMATURE' for m in o.modifiers):
        m = o.modifiers.new('Armature', 'ARMATURE'); m.object = arm


def set_mat(o, m, smooth=True):
    o.data.materials.clear(); o.data.materials.append(m)
    for p in o.data.polygons: p.material_index = 0; p.use_smooth = smooth


def plane(co, no):
    return (Vector(co), Vector(no).normalized())


def clearance(v, off):
    """Punkt mindestens 'off' außerhalb der Körperoberfläche."""
    hit, n, i, d = BODY.find_nearest(v)
    if hit is None: return v
    s = (v - hit).dot(n)
    r = hit + n * max(s, off) + (v - hit - n * s)
    return r if (r - v).length < 0.12 else v


def apply_mod(o, name):
    bpy.context.view_layer.objects.active = o
    with bpy.context.temp_override(object=o):
        bpy.ops.object.modifier_apply(modifier=name)


def solidify(o, rim, rim_only=True):
    s = o.modifiers.new('Rim', 'SOLIDIFY'); s.thickness = rim; s.offset = -1; s.use_rim_only = rim_only
    s.use_even_offset = False
    o.modifiers.move(len(o.modifiers) - 1, 0)
    apply_mod(o, 'Rim')


def edge_smooth(bm, iters):
    """Glättet offene Ränder entlang des Randes (saubere Säume)."""
    bverts = [v for v in bm.verts if v.is_boundary]
    for _ in range(iters):
        new = {}
        for v in bverts:
            nb = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if len(nb) == 2: new[v] = v.co * 0.5 + (nb[0].co + nb[1].co) * 0.25
        for v, c in new.items(): v.co = c


def garment(name, planes, material, offset, filt=None, rim=0.005, smooth=0):
    """Schneidet ein Stück aus der Körperoberfläche (Skin-Gewichte bleiben erhalten),
    glättet es, schiebt es nach außen und gibt ihm eine Kante."""
    me = body.data.copy(); me.name = name
    o = add_obj(name, me)
    for vg in body.vertex_groups: o.vertex_groups.new(name=vg.name)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    for co, no in planes:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, clear_inner=True)
    if filt:
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if not filt(f.calc_center_median())], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bmesh.ops.dissolve_degenerate(bm, dist=0.002, edges=bm.edges[:])
    bm.normal_update()
    for _ in range(smooth):
        bmesh.ops.smooth_vert(bm, verts=[v for v in bm.verts if not v.is_boundary], factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    edge_smooth(bm, 4)
    for v in bm.verts: v.co = clearance(v.co, offset(v.co))
    bm.normal_update()
    bm.to_mesh(me); bm.free()
    rig(o)
    set_mat(o, material)
    if rim: solidify(o, rim)
    return o


def inside(p, planes, margin=0.0):
    return all((p - co).dot(no) >= margin for co, no in planes)


def weights_at(p):
    """Skin-Gewichte des nächsten Körperpunkts (für angesetzte Teile)."""
    hit, n, i, d = BODY.find_nearest(p)
    poly = body.data.polygons[i]
    best = min(poly.vertices, key=lambda vi: (body.data.vertices[vi].co - hit).length)
    names = {g.index: g.name for g in body.vertex_groups}
    return {names[g.group]: g.weight for g in body.data.vertices[best].groups if g.weight > 0.01}


def transfer_weights(o):
    """Jeder Punkt übernimmt die Skin-Gewichte der nächsten Körperstelle."""
    for vg in body.vertex_groups:
        if not o.vertex_groups.get(vg.name): o.vertex_groups.new(name=vg.name)
    for v in o.data.vertices:
        for g, w in weights_at(v.co).items(): o.vertex_groups[g].add([v.index], w, 'REPLACE')
    rig(o)


def prop(name, me, material, at=None, groups=None):
    o = add_obj(name, me)
    set_mat(o, material)
    rig(o, groups or weights_at(Vector(at)))
    return o


def mk(fn, **kw):
    me = bpy.data.meshes.new('tmp'); bm = bmesh.new(); fn(bm, **kw); bm.to_mesh(me); bm.free(); return me


COVER = []  # Körperteile, die unter Kleidung verschwinden

# ---------------------------------------------------------------- Oberteil
top_planes = [plane((0, 0, 1.17), (0, 0, 1)),
              plane((0, -0.1, 1.375), (0, 0.5, -1)),     # Ausschnitt vorne tiefer
              plane((0, 0, 1.415), (0, 0, -1)),
              plane((0.165, 0, 1.42), (-1, 0, -0.35)), plane((-0.165, 0, 1.42), (1, 0, -0.35))]
top = garment('Top', top_planes, M['linen'], lambda p: 0.008 + 0.012 * min(1, max(0, 1.23 - p.z) / 0.06), smooth=6)
COVER.append(top_planes)

# Lederkorsett unter der Brust
cors_planes = [plane((0, 0, 1.155), (0, 0, 1)), plane((0, 0, 1.235), (0, 0, -1))]
garment('Corset', cors_planes, M['leather'], lambda p: 0.02 + 0.008 * max(0, 1.2 - p.z) / 0.045, smooth=4, rim=0.008)
COVER.append(cors_planes)

# ---------------------------------------------------------------- Hose
pants_planes = [plane((0, 0, 1.07), (0, 0, -1)), plane((0, 0, 0.26), (0, 0, 1))]
def pants_off(p):
    if p.z > 0.8: return 0.009
    if p.z > 0.55: return 0.009 + 0.018 * (0.8 - p.z) / 0.25     # etwas weiter werdend
    return 0.027 - 0.01 * min(1, (0.55 - p.z) / 0.2)            # in die Stiefel gesteckt
garment('Pants', pants_planes, M['linen'], pants_off, smooth=3)
COVER.append(pants_planes)

# ---------------------------------------------------------------- Gürtel
belt_planes = [plane((0, 0, 1.035), (0, 0, -1)), plane((0, 0, 0.99), (0, 0, 1))]
garment('Belt', belt_planes, M['leather2'], lambda p: 0.02, rim=0.012, smooth=2)
# Schnalle vorne
buckle = prop('Buckle', mk(lambda bm: bmesh.ops.create_cube(bm, size=1)), M['brass'], groups={'pelvis': 1.0})
buckle.data.transform(Matrix.Diagonal((0.055, 0.012, 0.045, 1)))
hit = BODY.ray_cast(Vector((0, -1, 1.012)), Vector((0, 1, 0)))[0]
buckle.data.transform(Matrix.Translation(hit + Vector((0, -0.028, 0))))
bev = buckle.modifiers.new('B', 'BEVEL'); bev.width = 0.006; bev.segments = 2; buckle.modifiers.move(1, 0); apply_mod(buckle, 'B')

# Taschen an der Hüfte
for ang, size in ((62, (0.075, 0.04, 0.085)), (-70, (0.06, 0.035, 0.07))):
    a = math.radians(ang); d = Vector((math.sin(a), -math.cos(a), 0))
    hit = BODY.ray_cast(Vector((0, 0.03, 0.975)) + d, -d)[0]
    me = mk(lambda bm: bmesh.ops.create_cube(bm, size=1))
    me.transform(Matrix.Diagonal((*size, 1)))
    me.transform(Matrix.Rotation(a, 4, 'Z'))
    me.transform(Matrix.Translation(hit + d * (0.03 + size[1] / 2) + Vector((0, 0, -0.025))))
    p = prop('Pouch', me, M['leather'], groups={'pelvis': 1.0})
    bev = p.modifiers.new('B', 'BEVEL'); bev.width = 0.012; bev.segments = 3; p.modifiers.move(1, 0); apply_mod(p, 'B')

# Stoffbahn vorne am Gürtel (wie im Referenzbild), unten zwischen den Oberschenkeln gemittelt
rows, cols = 7, 6
bm = bmesh.new(); grid = []; wl = []
for i in range(rows):
    t = i / (rows - 1)
    z = 0.995 - 0.215 * t
    half = 0.075 - 0.012 * t
    row = []
    for j in range(cols):
        x = -half + 2 * half * j / (cols - 1)
        hit = BODY.ray_cast(Vector((x, -1, z)), Vector((0, 1, 0)))[0]
        y = min(hit.y if hit else -0.12, -0.105 + 0.0 * t) - 0.032 - 0.02 * t
        if t > 0.35: y = min(y, grid[-1][j].co.y - 0.004)      # unten frei hängend
        v = bm.verts.new((x, y, z)); row.append(v)
        thl = min(0.35, max(0, t - 0.2) * 0.7)
        wl.append((v, {'pelvis': 1 - 2 * thl, 'thigh_l': thl, 'thigh_r': thl}))
    grid.append(row)
for i in range(rows - 1):
    for j in range(cols - 1):
        bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
idx = {v: k for k, v in enumerate(bm.verts)}
me = bpy.data.meshes.new('Tabard'); bm.to_mesh(me); bm.free()
tab = add_obj('Tabard', me); set_mat(tab, M['linen'])
for b_ in ('pelvis', 'thigh_l', 'thigh_r'): tab.vertex_groups.new(name=b_)
for v, w in wl:
    for g, x in w.items(): tab.vertex_groups[g].add([idx[v]], x, 'REPLACE')
rig(tab)
sub = tab.modifiers.new('Sub', 'SUBSURF'); sub.levels = 1; tab.modifiers.move(1, 0); apply_mod(tab, 'Sub')
solidify(tab, 0.008, rim_only=False)

# ---------------------------------------------------------------- Stiefel
boot_planes = [plane((0, 0, 0.44), (0, 0, -1)), plane((0, 0, 0.09), (0, 0, 1))]
garment('Boots', boot_planes, M['boot'], lambda p: 0.012 + 0.016 * min(1, max(0, p.z - 0.12) / 0.28), smooth=6, rim=0.01)
COVER.append([plane((0, 0, 0.44), (0, 0, -1))])
for sg in (1, -1):
    pts = [Vector(v.co) for v in body.data.vertices if v.co.z < 0.14 and v.co.x * sg > 0.02]
    bm = bmesh.new()
    for p in pts: bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.006)
    bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if e.calc_length() > 0.03], cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for _ in range(8):
        bmesh.ops.smooth_vert(bm, verts=bm.verts[:], factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    for v in bm.verts:
        v.co = clearance(v.co, 0.022)
        v.co.z = max(v.co.z, -0.004)
    me = bpy.data.meshes.new('Shoe'); bm.to_mesh(me); bm.free()
    o = add_obj('Shoe', me); transfer_weights(o)
    o.data.materials.append(M['boot']); o.data.materials.append(M['leather2'])
    for p in o.data.polygons:
        p.use_smooth = True; p.material_index = 1 if p.normal.z < -0.6 else 0
# Stoffstulpe über dem Stiefel
cuff_planes = [plane((0, 0, 0.5), (0, 0, -1)), plane((0, 0, 0.4), (0, 0, 1))]
garment('Cuff', cuff_planes, M['fur'], lambda p: 0.048 - 0.016 * abs(p.z - 0.45) / 0.05, smooth=6, rim=0.012)
COVER.append(cuff_planes)
for z0 in (0.425, 0.462):
    garment('CuffStrap', [plane((0, 0, z0), (0, 0, 1)), plane((0, 0, z0 + 0.014), (0, 0, -1))], M['leather2'],
            lambda p: 0.052, smooth=2, rim=0.006)

# ---------------------------------------------------------------- Arme
for s, sg in (('L', 1), ('R', -1)):
    bp = [plane((0.44 * sg, 0, 0), (sg, 0, 0)), plane((0.61 * sg, 0, 0), (-sg, 0, 0))]
    garment('Bracer' + s, bp, M['leather'], lambda p: 0.012 + 0.01 * (abs(p.x) - 0.44) / 0.17, smooth=3, rim=0.01)
    COVER.append(bp)
    for x0 in (0.47, 0.545):
        sp = [plane((x0 * sg, 0, 0), (sg, 0, 0)), plane(((x0 + 0.018) * sg, 0, 0), (-sg, 0, 0))]
        garment('BracerStrap' + s, sp, M['leather2'], lambda p, x0=x0: 0.026 + 0.01 * (x0 - 0.44) / 0.17, smooth=2, rim=0.006)
    sp = [plane((0.27 * sg, 0, 0), (sg, 0, 0)), plane((0.295 * sg, 0, 0), (-sg, 0, 0))]
    garment('ArmStrap' + s, sp, M['leather2'], lambda p: 0.007, smooth=2, rim=0.006)
    gp = [plane((0.612 * sg, 0, 0), (sg, 0, 0)), plane((0.712 * sg, 0, 0), (-sg, 0, 0))]
    garment('Glove' + s, gp, M['leather2'], lambda p: 0.004, rim=0.004, smooth=1)
    COVER.append([plane((0.62 * sg, 0, 0), (sg, 0, 0)), plane((0.70 * sg, 0, 0), (-sg, 0, 0))])
    # Oberschenkelriemen
    tp = [plane((0, 0, 0.70), (0, 0, 1)), plane((0, 0, 0.725), (0, 0, -1))]
    garment('ThighStrap' + s, tp, M['leather2'], lambda p: pants_off(p) + 0.007, rim=0.008, smooth=2, filt=lambda p, sg=sg: p.x * sg > 0.03)

# Schulterstück links: drei Lederplatten mit Metallkante
for k in range(3):
    me = mk(lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=1))
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.15], context='VERTS')
    bm.to_mesh(me); bm.free()
    r = 0.095 - k * 0.012
    me.transform(Matrix.Diagonal((r * 1.15, r * 1.05, r * 0.75, 1)))
    me.transform(Matrix.Rotation(math.radians(-28), 4, 'Y'))
    me.transform(Matrix.Translation((0.2 + k * 0.035, 0.012, 1.425 - k * 0.018)))
    p = prop('Pauldron', me, M['leather'] if k else M['leather2'], groups={'upperarm_l': 0.85, 'clavicle_l': 0.15})
    solidify(p, 0.008, rim_only=False)

# Riemen quer über die Brust (rechte Schulter zur linken Hüfte) – entsteht nach dem Oberteil, siehe unten

# Halsband
garment('Choker', [plane((0, 0, 1.505), (0, 0, 1)), plane((0, 0, 1.528), (0, 0, -1))], M['leather2'], lambda p: 0.004, rim=0.004)

# ---------------------------------------------------------------- Bandolier
def bvh_of(objs):
    bm = bmesh.new()
    for o in objs:
        t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
        me = bpy.data.meshes.new('t'); t.to_mesh(me); t.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    return BVHTree.FromBMesh(bm)

def loop_band(name, objs, center, u, n, width, lift, zmin, material, steps=96, thick=0.008):
    """Band um den Körper in der Ebene (u, y) durch center, Breite entlang n."""
    bv = bvh_of(objs)
    Y = Vector((0, 1, 0))
    pts = []
    for i in range(steps):
        th = 2 * math.pi * i / steps
        d = u * math.cos(th) + Y * math.sin(th)
        hit, nrm, _, _ = bv.ray_cast(center + d * 0.7, -d)
        if hit is None or hit.z < zmin: pts.append(None); continue
        pts.append((hit, nrm))
    bm = bmesh.new(); prev = None; first = None
    for item in pts + [None]:
        if item is None: prev = None; continue
        hit, nrm = item
        nrm = (nrm - n * nrm.dot(n)).normalized()
        a = bm.verts.new(hit + nrm * lift - n * width / 2); b = bm.verts.new(hit + nrm * lift + n * width / 2)
        if prev: bm.faces.new((prev[0], prev[1], b, a))
        prev = (a, b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = add_obj(name, me); set_mat(o, material); transfer_weights(o)
    s_ = o.modifiers.new('S', 'SOLIDIFY'); s_.thickness = thick; s_.offset = 0; o.modifiers.move(len(o.modifiers) - 1, 0); apply_mod(o, 'S')
    return o

n_ = Vector((0.843, 0, 0.538)).normalized(); u_ = Vector((-0.538, 0, 0.843))
c_ = Vector((0.06, 0.0, 1.22))
loop_band('Bandolier', [body, top, bpy.data.objects['Corset']], c_, u_, n_, 0.042, 0.009, 1.0, M['leather'])

# ---------------------------------------------------------------- Körper unter Kleidung entfernen
bm = bmesh.new(); bm.from_mesh(body.data)
covered = lambda v: any(inside(v.co, pl, 0.012) for pl in COVER)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(covered(v) for v in f.verts)], context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(body.data); bm.free()
set_mat(body, M['skin']); set_mat(eyes, M['eyes']); set_mat(brows, M['brow'])

# ---------------------------------------------------------------- Haare: länger, über die Schultern fallend
hair = import_gltf(Q + 'hair/Hair_Long.gltf')
for o in hair:
    if o.type == 'MESH' and not o.name.startswith('Ico'):
        o.parent = arm; o.name = 'Hair'
        for m in o.modifiers:
            if m.type == 'ARMATURE': m.object = arm
        set_mat(o, M['hair'])
        H = o
for o in hair:
    if o.type == 'ARMATURE' or o.name.startswith('Ico'): bpy.data.objects.remove(o)


def blend_weights(z):
    """Haare: oben am Kopf, unten am Oberkörper (damit Strähnen nicht durch die Schultern schwingen)."""
    h = min(1, max(0, (z - 1.42) / 0.16))
    n = min(1 - h, max(0, (z - 1.30) / 0.12)) if h < 1 else 0
    return {k: w for k, w in (('Head', h), ('neck_01', n), ('spine_03', 1 - h - n)) if w > 0.001}

def strand(bm, wl, pts, radii, outward, flat=0.32, k=8):
    """Haarsträhne als flacher, spitz zulaufender Schlauch entlang pts."""
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        o = (outward[i] - t * outward[i].dot(t)).normalized()
        sd = t.cross(o).normalized()
        r = radii[i]
        ring = []
        for j in range(k):
            a = 2 * math.pi * j / k
            v = bm.verts.new(p + sd * math.cos(a) * r + o * math.sin(a) * r * flat)
            ring.append(v); wl.append((v, blend_weights(p.z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(k):
            bm.faces.new((r0[j], r0[(j + 1) % k], r1[(j + 1) % k], r1[j]))
    tip = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * radii[-1] * 2); wl.append((tip, blend_weights(pts[-1].z)))
    for j in range(k): bm.faces.new((rings[-1][j], rings[-1][(j + 1) % k], tip))
    bm.faces.new(list(reversed(rings[0])))

BV = bvh_of([body, top, H])
HC = Vector((0, 0.015, 1.63))   # Mitte des Hinterkopfs
bm = bmesh.new(); wl = []
import random; random.seed(7)
# Strähnen: Winkel um den Kopf (0 = vorne), Länge (Endhöhe), Dicke
locks = [(a, 1.19 + 0.06 * random.random(), 0.05 + 0.01 * random.random()) for a in
         (104, 126, 148, 170, 190, 212, 234, 256)]
locks += [(a, 1.25 + 0.04 * random.random(), 0.042) for a in (115, 137, 159, 180, 201, 223, 245)]
locks += [(64, 1.27, 0.034), (296, 1.27, 0.034), (80, 1.31, 0.03), (280, 1.31, 0.03)]   # vordere Strähnen über den Schultern
for ang, zend, rad in locks:
    a = math.radians(ang)
    d = Vector((math.sin(a), -math.cos(a), 0))
    n = 12
    pts, radii, outs = [], [], []
    phase = random.random() * 6.28
    for i in range(n):
        t = i / (n - 1)
        z = 1.66 + (zend - 1.66) * t
        p = Vector((HC.x, HC.y, z)) + d * (0.075 + 0.05 * t)
        # Wellen
        side = Vector((-d.y, d.x, 0))
        p += side * 0.012 * math.sin(phase + t * 9) * t
        # aus Körper und Kopf herausschieben
        for _ in range(4):
            hit, nrm, idx, dist = BV.find_nearest(p)
            if hit is None: break
            sgn = (p - hit).dot(nrm)
            want = 0.016 + 0.01 * t
            if sgn < want: p = p + nrm * (want - sgn)
        pts.append(p); outs.append(d.copy())
        radii.append(rad * (0.75 + 0.45 * math.sin(math.pi * min(1, t * 1.6))) * (1 - 0.55 * t ** 2))
    # Pfad glätten
    for _ in range(3):
        pts = [pts[0]] + [(pts[i - 1] + pts[i] * 2 + pts[i + 1]) / 4 for i in range(1, n - 1)] + [pts[-1]]
    strand(bm, wl, pts, radii, outs)
idx = {v: i for i, v in enumerate(bm.verts)}
me = bpy.data.meshes.new('HairLong'); bm.normal_update(); bm.to_mesh(me)
wl2 = [(idx[v], w) for v, w in wl]; bm.free()
HL = add_obj('HairLong', me); set_mat(HL, M['hair'])
for b in ('Head', 'neck_01', 'spine_03'): HL.vertex_groups.new(name=b)
for vi, w in wl2:
    for g, x in w.items(): HL.vertex_groups[g].add([vi], x, 'REPLACE')
rig(HL)

# Stirnband mit Brille
BVH_HEAD = bvh_of([H, body])
k = 40; ring_lo, ring_hi = [], []
bm = bmesh.new()
for i in range(k):
    a = 2 * math.pi * i / k
    d = Vector((math.sin(a), -math.cos(a), 0))
    zc = 1.718 - 0.02 * math.cos(a)     # vorne höher
    vs = []
    for dz in (-0.014, 0.014):
        o = Vector((0, 0.01, zc + dz)) + d * 0.3
        hit = BVH_HEAD.ray_cast(o, -d)[0]
        vs.append(bm.verts.new(hit + d * 0.006 if hit else o - d * 0.2))
    ring_lo.append(vs[0]); ring_hi.append(vs[1])
for i in range(k):
    j = (i + 1) % k
    bm.faces.new((ring_lo[i], ring_lo[j], ring_hi[j], ring_hi[i]))
me = bpy.data.meshes.new('Headband'); bm.to_mesh(me); bm.free()
hb = prop('Headband', me, M['leather2'], groups={'Head': 1.0})
s_ = hb.modifiers.new('S', 'SOLIDIFY'); s_.thickness = 0.008; s_.offset = 1; hb.modifiers.move(1, 0); apply_mod(hb, 'S')
for p in hb.data.polygons: p.use_smooth = True
for sx in (-1, 1):
    a = math.radians(14 * sx)
    d = Vector((math.sin(a), -math.cos(a), 0))
    zc = 1.718 - 0.02 * math.cos(a) + 0.004
    hit = BVH_HEAD.ray_cast(Vector((0, 0.01, zc)) + d * 0.3, -d)[0]
    for part, r, depth, m_ in (('GoggleRim', 0.024, 0.022, M['brass']), ('GoggleLens', 0.018, 0.024, M['lens'])):
        me = mk(lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=r, radius2=r * 0.92, depth=depth))
        me.transform(Matrix.Rotation(math.radians(90), 4, 'X'))           # Achse nach -Y
        me.transform(Matrix.Rotation(math.radians(-25), 4, 'X'))          # nach oben gekippt
        me.transform(Matrix.Rotation(a, 4, 'Z'))
        me.transform(Matrix.Translation(hit + d * 0.016))
        g = prop(part, me, m_, groups={'Head': 1.0})
        if part == 'GoggleRim':
            bv = g.modifiers.new('B', 'BEVEL'); bv.width = 0.003; bv.segments = 2; g.modifiers.move(1, 0); apply_mod(g, 'B')

# ---------------------------------------------------------------- Gewichte prüfen
# Punkte ohne (volle) Gewichte übernehmen die Gewichte der nächsten Körperstelle
fixed = 0
names = {}
for o in arm.children:
    if o.type != 'MESH' or o == body: continue
    gi = {g.index: g.name for g in o.vertex_groups}
    for v in o.data.vertices:
        tot = sum(g.weight for g in v.groups)
        if tot < 0.98:
            for g in list(v.groups): o.vertex_groups[gi[g.group]].remove([v.index])
            for g, w in weights_at(v.co).items():
                vg = o.vertex_groups.get(g) or o.vertex_groups.new(name=g)
                vg.add([v.index], w, 'REPLACE')
            fixed += 1
print('Gewichte ergänzt:', fixed)

# ---------------------------------------------------------------- Bericht
tris = 0
for o in arm.children:
    if o.type == 'MESH':
        t = sum(len(p.vertices) - 2 for p in o.data.polygons); tris += t
        print(f'{o.name:14s} {t:6d}')
print('Dreiecke gesamt', tris)

bpy.ops.wm.save_as_mainfile(filepath=OUT + 'figur.blend')
if 'render' in sys.argv:
    relaxed_pose(arm)
    setup_render((600, 900), 32)
    camera((0.4, -3.6, 1.1), (0, 0, 0.9), 50); render(OUT + 'b_full.png')
    camera((-2.2, 2.8, 1.2), (0, 0, 0.9), 50); render(OUT + 'b_back.png')
    camera((0.15, -1.2, 1.5), (0, 0, 1.4), 55); render(OUT + 'b_upper.png')
    camera((0.3, -1.3, 0.4), (0, 0, 0.4), 55); render(OUT + 'b_legs.png')
