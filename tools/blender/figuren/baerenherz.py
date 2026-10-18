"""Bärenherz (Barbar): Bärenfell auf den Schultern, freie Brust mit Lederharnisch,
graviertes Eisen mit Bronzebeschlägen, langes rotbraunes Haar und Vollbart."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree
from figurlib import Figur, plane

F = Figur('baerenherz', 'male', skin='#d49b72', eye_scale=1.03)
Z, X = F.Z, F.X
F.mat('fur', 'fur', '#6e4c31', 0.95)
F.mat('furl', 'fur', '#9a7550', 0.95)
F.mat('iron', 'plate', '#8f969c', 0.42, 0.8, saum='#b07f45')
F.mat('iron2', 'plate', '#7c8389', 0.45, 0.8, saum='#b07f45')
F.mat('bronze', 'gold', '#b8813f', 0.35, 0.9)
F.mat('leather', 'leather', '#6c4027', 0.6)
F.mat('leather2', 'leather', '#3f2a1c', 0.6)
F.mat('kilt', 'leather', '#56371f', 0.65)
F.mat('pants', 'cloth', '#4b3a2b', 0.9)
F.mat('shoe', 'metal', '#3f2a1c', 0.6)
F.mat('wrap', 'wrap', '#a88a64', 0.9)
F.mat('hair', 'hair', '#8c3d1c', 0.55)


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
    """Wenig sichtbare, glatte Teile schon hier vereinfachen, damit für Fell und Haare mehr übrig bleibt."""
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o.name.rstrip('.0123456789') in names: F.modify(o, 'DECIMATE', ratio=r)


def straehnen(name, material, locks, objs, top=1.64, flat=0.32):
    """Lange Strähnen, die von außen auf Haar und Fell gelegt werden (liegen oben auf dem Fell).
    locks: (Winkel um den Kopf, Endhöhe, Dicke) im Frauenraum."""
    BV = F.bvh_of([F.body] + objs)
    HC = F.V(0, 0.015, 1.63)
    bm = bmesh.new(); wl = []
    for ang, zend, rad in locks:
        a = math.radians(ang); d = Vector((math.sin(a), -math.cos(a), 0)); side = Vector((-d.y, d.x, 0))
        n = 12; pts, radii, outs = [], [], []
        phase = random.random() * 6.28
        for i in range(n):
            t = i / (n - 1)
            z = Z(top) + (Z(zend) - Z(top)) * t
            o = Vector((HC.x, HC.y, z)) + side * 0.012 * math.sin(phase + t * 8) * t
            hit = BV.ray_cast(o + d * 0.6, -d)[0]
            p = (hit if hit else o + d * 0.15) + d * (0.02 + 0.02 * t)
            pts.append(p); outs.append(d.copy())
            radii.append(rad * (0.75 + 0.45 * math.sin(math.pi * min(1, t * 1.6))) * (1 - 0.55 * t ** 2))
        for _ in range(3):
            pts = [pts[0]] + [(pts[i - 1] + pts[i] * 2 + pts[i + 1]) / 4 for i in range(1, n - 1)] + [pts[-1]]
        F._strand(bm, wl, pts, radii, outs, flat)
    idx = {v: i for i, v in enumerate(bm.verts)}
    me = bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(me)
    wl2 = [(idx[v], w) for v, w in wl]; bm.free()
    o = F.add_obj(name, me); F.set_mat(o, material)
    for g in ('Head', 'neck_01', 'spine_03'): o.vertex_groups.new(name=g)
    for vi, w in wl2:
        for g, x in w.items(): o.vertex_groups[g].add([vi], x, 'REPLACE')
    F.rig(o)
    return o


# Bärenfell über den Schultern: vorne höher, hinten tiefer, unregelmäßiger Rand
fur = F.garment('FurMantle', [plane((0, 0, Z(1.33)), (0, 0.75, 1)), F.hz(1.53, False), F.ax(0.3, 1, False), F.ax(0.3, -1, False)], 'fur',
                lambda p: 0.045 + 0.04 * max(0, min(1, (p.z - Z(1.36)) / 0.14)), rim=0.02, smooth=6, noise=0.006, relax=4)

# Lederharnisch: zwei gekreuzte Riemen, vorne eine Eisenscheibe
F.bandolier('Harness', [], 'leather', right_to_left=True, width=0.046, lift=0.007, zmin=1.0)
F.bandolier('Harness', [], 'leather', right_to_left=False, width=0.046, lift=0.007, zmin=1.0)
zc = Z(1.22) + 0.06 * 0.843 / 0.538
hit = F.ray_body(0, zc)
F.cylinder('Boss', 0.042, 0.036, 0.016, hit + Vector((0, -0.022, 0)), (0, -1, 0), 'iron', {'spine_03': 1.0}, segs=20)
F.cylinder('BossRing', 0.047, 0.047, 0.008, hit + Vector((0, -0.016, 0)), (0, -1, 0), 'bronze', {'spine_03': 1.0}, segs=20)
hitb = F.ray_body(0, zc, side=1)
F.cylinder('BossBack', 0.03, 0.026, 0.012, hitb + Vector((0, 0.018, 0)), (0, 1, 0), 'bronze', {'spine_03': 1.0}, segs=16)

# Schulterpanzer links: gravierte Eisenschalen über einer Lederlage, auf dem Fell
F.pauldron('l', ['iron', 'leather', 'iron2'], size=0.1, layers=3, x=0.215, z=1.455, y=0.01, tilt=-32, squash=0.72, thick=0.01)

# Arme: Eisenarmschienen über Wickeln, Bronzereif am rechten Oberarm, gewickelte Hände
F.sleeve('Wrap', 0.40, 0.47, 'wrap', 0.012, rim=0.005, smooth=2, cover=True)
F.sleeve('Bracer', 0.45, 0.6, 'iron', lambda p: 0.024 + 0.01 * (abs(F.Xi(p.x)) - 0.45) / 0.15, rim=0.01, smooth=3, cover=True)
F.sleeve('BracerBand', 0.505, 0.52, 'leather2', 0.037, rim=0.006)
F.sleeve('ArmRing', 0.27, 0.295, 'bronze', 0.012, rim=0.006, sides=(-1,))
F.sleeve('HandWrap', 0.6, 0.69, 'wrap', 0.005, rim=0.004, smooth=1)
F.cover += [([F.ax(0.61, sg), F.ax(0.68, sg, False)], None) for sg in (1, -1)]

# Breiter Gürtel mit Eisenschnalle, Lederkilt, Fellbahn vorne, Eisenplatten an den Seiten
F.ring('Belt', 0.955, 1.045, 'leather2', 0.032, rim=0.012, smooth=2)
F.buckle(1.0, 'iron', size=(0.085, 0.016, 0.07))
F.pouch(70, (0.075, 0.045, 0.085), 0.95, 'leather')
F.pouch(-75, (0.06, 0.04, 0.07), 0.95, 'leather')
F.plates('KiltStrip', 'kilt', 0.98, 0.3, (-150, -112, 112, 150), 0.048, lift=0.04, flare=0.02, rows=7)
F.plates('Tasset', 'iron2', 0.975, 0.24, (-72, 72), 0.062, lift=0.045, flare=0.02, rows=6)
F.panel('Front', 'leather2', 1.0, 0.40, 0.1, 0.115, side=-1, lift=0.05, flare=0.03, rows=8)
F.panel('BackFur', 'fur', 1.0, 0.40, 0.11, 0.13, side=1, lift=0.05, flare=0.03, rows=8)

# Hose, Stiefel mit Fellstulpen und Riemen
F.ring('Pants', 0.3, 1.0, 'pants', lambda p: 0.009 if p.z > Z(0.6) else 0.016, rim=0.004, smooth=3, cover=True)
F.ring('Boots', 0.09, 0.42, 'leather', lambda p: 0.014 + 0.012 * min(1, max(0, p.z - Z(0.12)) / 0.3), rim=0.01, smooth=6)
F.cover.append(([F.hz(0.42, False)], None))
F.shoes('shoe', 'leather2')
F.garment('BootFur', [F.hz(0.34), F.hz(0.44, False)], 'fur', lambda p: 0.05 - 0.018 * abs(p.z - Z(0.39)) / 0.06,
          rim=0.014, smooth=6, noise=0.008, cover=True)
for z0 in (0.17, 0.27):
    F.ring('BootStrap', z0, z0 + 0.015, 'leather2', 0.03, rim=0.006, smooth=2)

# Langes rotbraunes Haar und Vollbart
H = F.frisur('long01', '#7e3a1c')   # Strähnen mit Durchsicht
B = F.hair_mesh('Hair_Beard', 'hair', name='Beard')
# lange Strähnen hinten über das Fell
random.seed(11)
locks = [(a, 1.36 + 0.04 * random.random(), 0.05 + 0.012 * random.random()) for a in (140, 153, 166, 180, 194, 207, 220)]
locks += [(a, 1.41 + 0.03 * random.random(), 0.044) for a in (147, 160, 173, 187, 200, 213)]
straehnen('HairLong', 'hair', locks, [fur, H, B])
F.M['hair']['root'] = (Z(1.62), Z(1.78))

saum_behalten(fur, 0.02)
vereinfachen({'Pants', 'Boots', 'Shoe', 'WrapL', 'WrapR', 'HandWrapL', 'HandWrapR'}, 0.55)
F.finish(brow_color='#5a2a14')
