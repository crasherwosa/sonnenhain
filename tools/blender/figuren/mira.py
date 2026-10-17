"""Mira (Bäuerin, freundliche Auftraggeberin): Leinenbluse, grünes Mieder und Rock, Schürze, Stoff-Haarreif."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from figurlib import Figur, plane, mk

F = Figur('mira', 'female', skin='#e9ae86', eye_scale=1.04)
Z = F.Z
F.mat('linen', 'cloth', '#efe4cc', 0.9)
F.mat('linen2', 'cloth', '#e2d4b6', 0.92)
F.mat('apron', 'cloth', '#f4ecd8', 0.9, saum='#4f8a3c')
F.mat('green', 'cloth', '#3f7a35', 0.85, saum='#e6d6ae')
F.mat('green2', 'cloth', '#2f6229', 0.85)
F.mat('skirtm', 'cloth', '#356b2e', 0.88)
F.mat('scarf', 'cloth', '#58963f', 0.85, saum='#efe4cc')
F.mat('leather', 'leather', '#7a4a2a', 0.6)
F.mat('leather2', 'leather', '#4e3020', 0.6)
F.mat('brass', 'gold', '#c99a52', 0.35, 0.85)
F.mat('lace', 'trim', '#efe4cc', 0.8)
F.mat('hair', 'hair', '#7a4526', 0.55)

# Leinenbluse mit weiten, langen Ärmeln
def blouse_off(p):
    ax = abs(p.x)
    if ax > 0.2:   # gebauschter Ärmel, zum Handgelenk enger
        t = min(1, (ax - 0.2) / 0.38)
        return 0.01 + 0.018 * math.sin(math.pi * min(1, t * 1.15))
    return 0.009
F.garment('Blouse', [F.hz(1.02), F.hz(1.49, False), plane((0, -0.1, 1.415), (0, 0.5, -1)),
                     F.ax(0.6, 1, False), F.ax(0.6, -1, False)], 'linen', blouse_off, rim=0.005, smooth=6, cover=True)
F.sleeve('Cuff', 0.565, 0.6, 'linen2', 0.012, rim=0.005, smooth=2)

# Grünes Mieder mit Schnürung
F.garment('Bodice', [F.hz(0.97), F.hz(1.31, False),
                     plane((0.165, 0, 1.40), (-1, 0, -0.35)), plane((-0.165, 0, 1.40), (1, 0, -0.35))],
          'green', lambda p: 0.018 + 0.006 * max(0, min(1, (p.z - 1.15) / 0.12)), rim=0.009, smooth=10, cover=True)

def lace(name, a, b, depth, material, w=0.0055):
    """Dünner Schnürriemen zwischen zwei Punkten (x, z) vor dem Körper."""
    pa, pb = F.ray_body(a[0], a[1]), F.ray_body(b[0], b[1])
    pa = pa + Vector((0, -depth, 0)); pb = pb + Vector((0, -depth, 0))
    d = pb - pa
    me = mk(lambda bm: bmesh.ops.create_cube(bm, size=1))
    me.transform(Matrix.Diagonal((w, w, d.length + w, 1)))
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    me.transform(q.to_matrix().to_4x4())
    me.transform(Matrix.Translation((pa + pb) / 2))
    return F.prop(name, me, material, groups={'spine_02': 0.5, 'spine_01': 0.5})

zs = [1.02, 1.07, 1.12, 1.17, 1.22, 1.27]
for k in range(len(zs) - 1):
    lace('Lace', (-0.026, zs[k]), (0.026, zs[k + 1]), 0.031, 'lace')
    lace('Lace', (0.026, zs[k]), (-0.026, zs[k + 1]), 0.032, 'lace')
for z in zs:
    for x in (-0.03, 0.03):
        hit = F.ray_body(x, z)
        F.box('Eyelet', (0.009, 0.006, 0.009), hit + Vector((0, -0.03, 0)), 'brass', bone='spine_02', bev=0.002)
# Schleife oben
hit = F.ray_body(0, 1.285)
F.box('LaceBow', (0.03, 0.008, 0.014), hit + Vector((0, -0.036, 0)), 'lace', bone='spine_02', bev=0.004)

# Langer Rock bis zur Wade, Bund, Strümpfe, Schuhe
skirt = F.skirt('Skirt', 'skirtm', 1.0, 0.17, flare=0.13, off=0.016, thick=0.006, cover=True)
F.ring('Waistband', 0.965, 1.0, 'green2', 0.028, rim=0.008, smooth=5)
F.ring('Stockings', 0.1, 0.4, 'linen2', 0.004, rim=0.003, smooth=2, cover=True)
F.ring('ShoeTop', 0.08, 0.15, 'leather', lambda p: 0.012, rim=0.006, smooth=4)
F.cover.append(([F.hz(0.15, False)], None))
F.shoes('leather', 'leather2')


def apron(name, material, ztop, zbot, wtop, wbot, rows=9, cols=7, gap=0.016):
    """Schürze: liegt vorne auf dem Rock auf und folgt ihm (gleiche Gewichte wie der Rock)."""
    bv = F.bvh_of([skirt])
    # Gewichte vom nächsten Rockpunkt übernehmen, damit die Schürze genau mitschwingt
    from mathutils.kdtree import KDTree
    sv = skirt.data.vertices; kd = KDTree(len(sv))
    for v in sv: kd.insert(v.co, v.index)
    kd.balance()
    gn = {g.index: g.name for g in skirt.vertex_groups}
    def near_weights(p):
        res = {}
        for co, i, d in kd.find_n(p, 2):
            for g in sv[i].groups: res[gn[g.group]] = res.get(gn[g.group], 0) + g.weight / 2
        return res
    bm = bmesh.new(); grid = []; wl = []
    for i in range(rows):
        t = i / (rows - 1)
        z = ztop + (zbot - ztop) * t
        half = wtop + (wbot - wtop) * t
        row = []
        for j in range(cols):
            u = -1 + 2 * j / (cols - 1)
            x = half * u
            hit, nrm, _, _ = bv.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))
            p = (hit if hit else Vector((x, -0.2, z))) + Vector((0, -gap - 0.004 * t, 0))
            v = bm.verts.new(p); row.append(v)
            wl.append((v, near_weights(p)))
        grid.append(row)
    for i in range(rows - 1):
        for j in range(cols - 1):
            bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
    for f in bm.faces:
        if f.normal.y > 0: f.normal_flip()
    idx = {v: k for k, v in enumerate(bm.verts)}
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = F.add_obj(name, me); F.set_mat(o, material)
    for g in ('pelvis', 'thigh_l', 'thigh_r'): o.vertex_groups.new(name=g)
    for v, w in wl:
        for g, x in w.items(): o.vertex_groups[g].add([idx[v]], x, 'REPLACE')
    F.rig(o)
    F.modify(o, 'SUBSURF', levels=1)
    F.solidify(o, 0.006, rim_only=False, offset=0)
    return o

apron('Apron', 'apron', 0.975, 0.36, 0.115, 0.16)
# Schürzenschleife hinten
hit = F.ray_body(0, 0.985, side=1)
bow = hit + Vector((0, 0.048, 0))
F.box('ApronBow', (0.05, 0.016, 0.026), bow, 'apron', bone='pelvis', bev=0.007)
for sx, ry in ((-1, 14), (1, -14)):
    me = mk(lambda bm: bmesh.ops.create_cube(bm, size=1))
    me.transform(Matrix.Diagonal((0.026, 0.006, 0.12, 1)))
    me.transform(Matrix.Translation((0, 0, -0.06)))
    me.transform(Matrix.Rotation(math.radians(ry), 4, 'Y'))
    me.transform(Matrix.Translation(bow + Vector((sx * 0.012, 0.012, -0.004))))
    o = F.prop('ApronTie', me, 'apron', groups={'pelvis': 1.0}); F.bevel(o, 0.002, 1)
# Kleine Gürteltaschen
F.pouch(70, (0.07, 0.04, 0.08), 0.95, 'leather')
F.pouch(-95, (0.04, 0.03, 0.05), 0.955, 'leather2')

# Halstuch-Band und Ärmelbänder
F.ring('Neckband', 1.505, 1.522, 'green2', 0.003, rim=0.004, filt=lambda p: abs(p.x) < 0.12)
F.sleeve('ArmBand', 0.33, 0.35, 'green2', lambda p: blouse_off(p) + 0.005, rim=0.005)

# Haare: Knoten, darüber ein grüner Stoff-Haarreif
H = F.hair_mesh('Hair_Buns', 'hair')
F.M['hair']['root'] = (1.62, 1.78)
bv = F.head_bvh([H])
def headband(name, material, width=0.016, tilt=22, off=0.005, k=40, span=105):
    """Haarreif aus Stoff: Bogen von Ohr zu Ohr über den Kopf, etwas nach hinten geneigt.
    Abstand je Richtung geglättet, aber nie ins Haar hinein."""
    c = Vector((0, 0.01, Z(1.64)))
    rot = Matrix.Rotation(math.radians(tilt), 3, 'X')
    dirs, raw = [], []
    for i in range(k):
        th = math.radians(-span + 2 * span * i / (k - 1))
        d = rot @ Vector((math.sin(th), 0, math.cos(th)))
        side = rot @ Vector((0, 1, 0))
        r = 0
        for dw in (-width, 0, width):
            o = c + side * dw + d * 0.4
            hit = bv.ray_cast(o, -d)[0]
            if hit: r = max(r, (hit - c - side * dw).length)
        dirs.append(d); raw.append((r or 0.1) + off)
    rad = raw[:]
    for _ in range(3):
        rad = [raw[0]] + [max(raw[i], (rad[i - 1] + 2 * rad[i] + rad[i + 1]) / 4) for i in range(1, k - 1)] + [raw[-1]]
    side = rot @ Vector((0, 1, 0))
    bm = bmesh.new(); a, b = [], []
    for d, r in zip(dirs, rad):
        a.append(bm.verts.new(c + d * r - side * width)); b.append(bm.verts.new(c + d * r + side * width))
    for i in range(k - 1):
        bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = F.prop(name, me, material, groups={'Head': 1.0})
    for p in o.data.polygons:
        if (o.data.vertices[p.vertices[0]].co - c).dot(p.normal) < 0: p.flip()
    F.modify(o, 'SOLIDIFY', thickness=0.007, offset=1)
    F.bevel(o, 0.002, 1)
    for p in o.data.polygons: p.use_smooth = True
    return o

headband('Kerchief', 'scarf')

F.finish(brow_color='#6a3a20')
