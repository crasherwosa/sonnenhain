"""Waldläufer (Waldläufer-Klasse): Kapuze und Schulterumhang in Waldgrün, Lederbrigantine mit Nieten,
Köcher mit Pfeilen auf dem Rücken."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
import figurlib
from figurlib import Figur, plane, mk
from mathutils.kdtree import KDTree

F = Figur('waldlaeufer', 'male', skin='#e0a982', eye_scale=1.03)
Z, X = F.Z, F.X
F.mat('green', 'cloth', '#3a6230', 0.88, saum='#c9a45a')
F.mat('hoodc', 'cloth', '#3a6230', 0.88)
F.mat('green2', 'cloth', '#4f7a3c', 0.9)
F.mat('pants', 'cloth', '#3d3a26', 0.9)
F.mat('leather', 'leather', '#7a4a2b', 0.6)
F.mat('leather2', 'leather', '#45301f', 0.6)
F.mat('boot', 'leather', '#5a3820', 0.55)
F.mat('shoe', 'metal', '#4e301c', 0.6)
F.mat('bronze', 'gold', '#c08a45', 0.35, 0.9)
F.mat('shaft', 'wood', '#b08a5a', 0.7)
F.mat('feather', 'cloth', '#e9dfc8', 0.9)
F.mat('feather2', 'cloth', '#9a3b2a', 0.9)
F.mat('hair', 'hair', '#6b4527', 0.55)


def glatte_saeume(fn, *a, mal=3, **kw):
    """Wie fn (z. B. F.garment), aber mit stärker geglätteten Rändern (kein Sägezahn am Saum)."""
    alt = figurlib.edge_smooth
    figurlib.edge_smooth = lambda bm, n: alt(bm, n * mal)
    try: return fn(*a, **kw)
    finally: figurlib.edge_smooth = alt


def saum_behalten(o, dist=0.03):
    """Punkte nahe am Rand in die Gruppe 'Behalten': der Export vereinfacht sie nicht (saubere Kante)."""
    bm = bmesh.new(); bm.from_mesh(o.data)
    rim = [v.co.copy() for v in bm.verts if v.is_boundary]; bm.free()
    if not rim: return
    kd = KDTree(len(rim))
    for i, c in enumerate(rim): kd.insert(c, i)
    kd.balance()
    g = o.vertex_groups.new(name='Behalten')
    g.add([v.index for v in o.data.vertices if kd.find(v.co)[2] < dist], 1.0, 'REPLACE')


def vereinfachen(names, r):
    """Wenig sichtbare, glatte Teile schon hier vereinfachen, damit für Kapuze und Säume mehr übrig bleibt."""
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o.name.rstrip('.0123456789') in names: F.modify(o, 'DECIMATE', ratio=r)


def stab(name, size, at, ux, uy, uz, material, groups):
    """Quader mit eigenen Achsen ux, uy, uz (Federn am Pfeil)."""
    me = mk(lambda bm: bmesh.ops.create_cube(bm, size=1))
    me.transform(Matrix.Diagonal((*size, 1)))
    R = Matrix((ux, uy, uz)).transposed().to_4x4()
    me.transform(R)
    me.transform(Matrix.Translation(at))
    return F.prop(name, me, material, groups=groups)


# Tunika: nur die Ärmel sind zu sehen (Rumpf liegt unter Weste und Umhang)
for sg in (1, -1):
    F.garment('Tunic', [F.ax(0.12, sg), F.ax(0.6, sg, False), F.hz(1.2)], 'green2', 0.009, rim=0.005, smooth=5, cover=True)
# Lederbrigantine (Weste) mit Nietenreihen
cz = Z(1.42)
vest_planes = [F.hz(1.015), F.hz(1.43, False), plane((0.17, 0, cz), (-1, 0, -0.35)), plane((-0.17, 0, cz), (1, 0, -0.35))]
vest = F.garment('Vest', vest_planes,
                 'leather', lambda p: 0.034 + 0.006 * max(0, min(1, (p.z - Z(1.2)) / 0.15)), rim=0.01, smooth=25, relax=6)
F.cover.append((vest_planes, None))
bv = F.bvh_of([vest])
for zz in (1.07, 1.13, 1.19, 1.25, 1.31):
    for xx in (-0.12, -0.065, 0.065, 0.12):
        hit = bv.ray_cast(Vector((X(xx), -0.6, Z(zz))), Vector((0, 1, 0)))[0]
        if hit: F.gem('Niete', 0.0095, hit + Vector((0, -0.002, 0)), 'bronze', bone='spine_02' if zz < 1.2 else 'spine_03')

# Kapuze und kurzer Schulterumhang mit Borte
def hood(name, material, objs, zcut, hmax=0.15, off=0.03, rows=18, cols=40, open_w=64, open_h=58, open_pitch=-14, thick=0.008):
    """Kapuze als glatte Schale um den Kopf: Strahlen von außen auf Kopf, Haare und Bart,
    Abstand geglättet. Die Gesichtsöffnung ist eine Ellipse um die Blickrichtung (Winkel in Grad)."""
    hb = F.arm.data.bones['Head']
    C = F.arm.matrix_world @ hb.head_local + Vector((0, 0.012, 0.075))
    BV = F.bvh_of([F.body] + objs)
    # Achse der Öffnung: nach vorne, leicht nach unten geneigt
    pa = math.radians(open_pitch)
    fwd = Vector((0, -math.cos(pa), math.sin(pa))); up = Vector((0, math.sin(pa), math.cos(pa))); rt = fwd.cross(up)
    grid, rad = [], []
    for i in range(rows):
        t = i / (rows - 1)
        row, rr = [], []
        for j in range(cols):
            ph = 2 * math.pi * j / cols
            a0 = 1 / math.sqrt((math.cos(ph) / math.radians(open_w)) ** 2 + (math.sin(ph) / math.radians(open_h)) ** 2)
            th = a0 + (math.radians(172) - a0) * t
            d = (fwd * math.cos(th) + (rt * math.cos(ph) + up * math.sin(ph)) * math.sin(th)).normalized()
            hit = BV.ray_cast(C + d * 0.6, -d)[0]
            r = (hit - C).length if hit else 0.12
            row.append(d); rr.append(r)
        grid.append(row); rad.append(rr)
    mind = [[r + 0.014 for r in rr] for rr in rad]
    R = [[r + off for r in rr] for rr in rad]
    for _ in range(10):   # Abstand glätten (keine Beulen von Ohren und Nase)
        R2 = []
        for i in range(rows):
            row = []
            for j in range(cols):
                nb = [R[i][(j - 1) % cols], R[i][(j + 1) % cols]] + ([R[i - 1][j]] if i else []) + ([R[i + 1][j]] if i < rows - 1 else [])
                row.append(max(mind[i][j], 0.5 * R[i][j] + 0.5 * sum(nb) / len(nb)))
            R2.append(row)
        R = R2
    bm = bmesh.new(); V = []
    for i in range(rows):
        vr = []
        for j in range(cols):
            d = grid[i][j]; hl = math.hypot(d.x, d.y)
            # unten nicht seitlich über die Schultern ausladen
            r = min(R[i][j], hmax / hl) if d.z < 0.1 and hl > 1e-3 else R[i][j]
            p = C + d * r
            # nach oben und hinten etwas weiter, hinten zur Spitze ausgezogen
            tp = max(0, min(1, (p.z - C.z + 0.02) / 0.14)) * max(0, min(1, (p.y - C.y + 0.03) / 0.1))
            p = p + Vector((0, 0.05 * tp * tp, 0.012 * tp * tp))
            vr.append(bm.verts.new(p))
        V.append(vr)
    for i in range(rows - 1):
        for j in range(cols):
            bm.faces.new((V[i][j], V[i][(j + 1) % cols], V[i + 1][(j + 1) % cols], V[i + 1][j]))
    tip = bm.verts.new(sum((v.co for v in V[-1]), Vector()) / cols)
    for j in range(cols): bm.faces.new((V[-1][j], V[-1][(j + 1) % cols], tip))
    # unten gerade abschneiden (liegt als Kragen auf dem Schulterumhang)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, zcut), plane_no=(0, 0, -1), clear_outer=True)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    fc = bm.faces[0]
    if (fc.calc_center_median() - C).dot(fc.normal) < 0:
        for f in bm.faces: f.normal_flip()
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = F.add_obj(name, me); F.set_mat(o, material)
    # Gewichte: oben nur der Kopf, unten wie der Körper darunter
    for vg in F.body.vertex_groups:
        o.vertex_groups.new(name=vg.name)
    for v in o.data.vertices:
        h = max(0, min(1, (v.co.z - Z(1.47)) / 0.07))
        w = {g: x * (1 - h) for g, x in F.weights_at(v.co).items()}
        w['Head'] = w.get('Head', 0) + h
        for g, x in w.items():
            if x > 0.001: o.vertex_groups[g].add([v.index], x, 'REPLACE')
    F.rig(o)
    F.modify(o, 'SUBSURF', levels=1)
    F.solidify(o, thick, rim_only=False, offset=1)
    return o


# Haare (kurz, unter der Kapuze) und Bart, darüber die Kapuze
hair = F.hair_mesh('Hair_Buzzed', 'hair')
beard = F.hair_mesh('Hair_Beard', 'hair', name='Beard')
F.M['hair']['root'] = (Z(1.62), Z(1.78))
# Schulterumhang: vorne höher geschnitten als hinten, endet an den Oberarmen
cape = glatte_saeume(F.garment, 'Capelet', [plane((0, 0, Z(1.31)), (0, 0.55, 1)), F.hz(1.50, False), F.ax(0.25, 1, False), F.ax(0.25, -1, False)], 'green',
          lambda p: 0.042 + 0.03 * max(0, min(1, (p.z - Z(1.33)) / 0.14)), rim=0.012, smooth=6, relax=4, mal=6)
saum_behalten(cape, 0.02)
saum_behalten(hood('Hood', 'green', [hair, beard, cape], Z(1.49)), 0.025)

# Gürtel, Schnalle, Taschen, Tunikabahnen vorne und hinten
F.ring('Belt', 0.975, 1.035, 'leather2', 0.042, rim=0.012, smooth=2)
F.box('Buckle', (0.055, 0.014, 0.048), F.ray_body(0, Z(1.005)) + Vector((0, -0.05, 0)), 'bronze', bev=0.006)   # Schnalle vor dem dicken Gürtel
F.pouch(55, (0.07, 0.042, 0.08), 0.965, 'leather')
F.pouch(95, (0.055, 0.038, 0.065), 0.965, 'leather2')
F.pouch(-60, (0.065, 0.04, 0.075), 0.965, 'leather')
F.panel('TunicFront', 'green', 0.99, 0.36, 0.11, 0.13, side=-1, lift=0.05, flare=0.03, rows=8)
F.panel('TunicBack', 'green', 0.99, 0.38, 0.12, 0.135, side=1, lift=0.05, flare=0.03, rows=8)

# Hose, Stiefel mit Umschlag
F.ring('Pants', 0.3, 1.0, 'pants', lambda p: 0.008 if p.z > Z(0.6) else 0.014, rim=0.004, smooth=3, cover=True)
F.ring('Boots', 0.09, 0.47, 'boot', lambda p: 0.014 + 0.012 * min(1, max(0, p.z - Z(0.12)) / 0.3), rim=0.01, smooth=6)
F.cover.append(([F.hz(0.47, False)], None))
F.shoes('shoe', 'leather2')
F.ring('BootCuff', 0.42, 0.48, 'leather', lambda p: 0.036, rim=0.01, smooth=4)
F.ring('BootStrap', 0.25, 0.27, 'leather2', 0.03, rim=0.006, smooth=2)
for sg in (1, -1):
    F.ring('ThighStrap', 0.70, 0.718, 'leather2', 0.017, rim=0.006, smooth=2, filt=lambda p, sg=sg: p.x * sg > 0.03)

# Armschienen mit Riemen, Handschuhe
F.sleeve('Bracer', 0.43, 0.6, 'leather', lambda p: 0.018 + 0.01 * (abs(F.Xi(p.x)) - 0.43) / 0.17, rim=0.01, smooth=3, cover=True)
F.sleeve('BracerStrap', 0.47, 0.49, 'leather2', 0.03, rim=0.006)
F.sleeve('BracerStrap2', 0.545, 0.565, 'leather2', 0.035, rim=0.006)
F.sleeve('Glove', 0.6, 0.712, 'leather2', 0.005, rim=0.004, smooth=1)
F.cover += [([F.ax(0.61, sg), F.ax(0.70, sg, False)], None) for sg in (1, -1)]

# Köcherriemen schräg über die Brust, Köcher auf dem Rücken (Öffnung an der rechten Schulter)
F.bandolier('QuiverStrap', [vest, cape], 'leather2', width=0.04, lift=0.008)
top = Vector((X(-0.105), 0, Z(1.53))); bot = Vector((X(0.075), 0, Z(1.03)))
back = F.bvh_of([vest, cape, F.body])
for p in (top, bot):
    hit = back.ray_cast(Vector((p.x, 1.0, p.z)), Vector((0, -1, 0)))[0]
    p.y = (hit.y if hit else 0.15) + 0.055
mid = (top + bot) / 2; ax = (top - bot).normalized(); L = (top - bot).length
QG = {'spine_03': 1.0}
F.cylinder('Quiver', 0.042, 0.05, L, mid, ax, 'leather', QG, segs=14)
F.cylinder('QuiverRim', 0.054, 0.054, 0.03, top - ax * 0.03, ax, 'bronze', QG, segs=14, caps=False)
F.cylinder('QuiverBand', 0.048, 0.048, 0.02, bot + ax * 0.08, ax, 'leather2', QG, segs=14, caps=False)
F.cylinder('QuiverBand2', 0.052, 0.052, 0.02, mid + ax * 0.06, ax, 'leather2', QG, segs=14, caps=False)
side = ax.cross(Vector((0, 1, 0))).normalized(); fwd = ax.cross(side).normalized()
for k, (u, v, lift) in enumerate([(-0.022, 0.0, 0.11), (0.0, -0.018, 0.14), (0.022, 0.006, 0.12), (0.008, 0.02, 0.10), (-0.012, 0.022, 0.13)]):
    base = top + side * u + fwd * v
    F.cylinder('Arrow', 0.0045, 0.0045, lift + 0.06, base + ax * (lift / 2 - 0.03), ax, 'shaft', QG, segs=6)
    fm = 'feather2' if k % 2 else 'feather'
    for r in (0, 120, 240):
        rd = side * math.cos(math.radians(r + 30 * k)) + fwd * math.sin(math.radians(r + 30 * k))
        stab('Fletch', (0.0025, 0.012, 0.055), base + ax * (lift - 0.025) + rd * 0.008, rd.cross(ax), rd, ax, fm, QG)


vereinfachen({'Pants', 'Tunic', 'Boots', 'GloveL', 'GloveR', 'Shoe', 'Vest', 'BootCuff'}, 0.5)
F.finish(brow_color='#4f3220')
