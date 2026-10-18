"""Schlanke, verzierte Waffen im Stil der Rüstungen (ersetzen die klobigen KayKit-Waffen).
Jede Waffe entsteht aus Querschnitten (Klingen mit Mittelgrat, runde Griffe, Bögen), bekommt
gemalte Details (details.py) und wird als eigene .glb nach assets/characters/eigene/waffen/ exportiert.

Lage wie bei den KayKit-Waffen: Griff im Ursprung, Klinge/Schaft nach oben (im Spiel +Y),
Breite entlang X. Maße in Metern. Aufruf: python waffen.py [name ...]"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math
import bpy, bmesh
from mathutils import Vector, Matrix
from blib import reset, srgb
from details import add_edge_attr, bake_details

ZIEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'characters', 'eigene', 'waffen')
os.makedirs(ZIEL, exist_ok=True)
MATS = {}


def mat(key, kind, color, rough=0.6, metal=0.0, saum=None):
    m = bpy.data.materials.new('M_' + key); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb(color), 1)
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    m['kind'] = kind
    if saum: m['saum'] = list(srgb(saum))
    MATS[key] = m
    return m


def obj(name, bm, material, smooth=True):
    me = bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(MATS[material])
    for p in o.data.polygons: p.use_smooth = smooth
    return o


def loft(name, rings, material, cap0=True, cap1=True, smooth=True, closed=True):
    """Verbindet Ringe (Listen von 3D-Punkten gleicher Länge). Ein Ring mit nur einem Punkt = Spitze."""
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in r] for r in rings]
    for a, b in zip(vs, vs[1:]):
        n = max(len(a), len(b))
        if len(a) == 1:
            for j in range(len(b) - (0 if closed else 1)): bm.faces.new((a[0], b[j], b[(j + 1) % len(b)]))
        elif len(b) == 1:
            for j in range(len(a) - (0 if closed else 1)): bm.faces.new((a[j], b[0], a[(j + 1) % len(a)]))
        else:
            for j in range(n - (0 if closed else 1)):
                bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
    if cap0 and len(vs[0]) > 2: bm.faces.new(list(reversed(vs[0])))
    if cap1 and len(vs[-1]) > 2: bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj(name, bm, material, smooth)


def circle(c, r, n=12, axis='Z', ry=None):
    ry = ry or r
    out = []
    for j in range(n):
        a = 2 * math.pi * j / n
        x, y = math.cos(a) * r, math.sin(a) * ry
        out.append(c + (Vector((x, y, 0)) if axis == 'Z' else Vector((0, x, y)) if axis == 'X' else Vector((x, 0, y))))
    return out


def rod(name, profile, material, n=12, smooth=True):
    """Runder Stab entlang Z: profile = [(z, radius), ...]"""
    return loft(name, [circle(Vector((0, 0, z)), r, n) for z, r in profile], material, smooth=smooth)


def blade(name, profile, material, tip=None, ridge=1.0):
    """Klinge entlang Z mit Mittelgrat: profile = [(z, halbe Breite, halbe Dicke), ...], tip = Spitze (z)."""
    rings = [[Vector((-w, 0, z)), Vector((0, -t * ridge, z)), Vector((w, 0, z)), Vector((0, t * ridge, z))] for z, w, t in profile]
    if tip is not None: rings.append([Vector((0, 0, tip))])
    return loft(name, rings, material, smooth=False)


def guard(name, half, z, w, t, material, curl=0.02):
    """Parierstange quer (entlang X), Enden leicht nach oben gebogen."""
    rings = []
    for i in range(11):
        u = -1 + 2 * i / 10
        x = u * half; zc = z + curl * u ** 4
        s = 1 - 0.35 * abs(u)
        rings.append(circle(Vector((x, 0, zc)), t * s, 8, axis='X', ry=w * s))
    rings[0] = [Vector((-half - 0.01, 0, z + curl))]; rings[-1] = [Vector((half + 0.01, 0, z + curl))]
    return loft(name, rings, material)


def ball(name, c, r, material, sz=1.0):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=r)
    bmesh.ops.scale(bm, vec=(1, 1, sz), verts=bm.verts); bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return obj(name, bm, material)


def crystal(name, c, r, h, material, n=6):
    rings = [[c + Vector((0, 0, -h))], circle(c + Vector((0, 0, -h * 0.2)), r, n), circle(c + Vector((0, 0, h * 0.35)), r * 0.8, n), [c + Vector((0, 0, h))]]
    return loft(name, rings, material, smooth=False)


def finish(name, parts, size=512, rot_x=0):
    for o in parts: add_edge_attr(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active; o.name = name
    if rot_x: o.data.transform(Matrix.Rotation(math.radians(rot_x), 4, 'X'))
    bake_details(o, size, size // 2)
    for m in o.data.materials: m.use_backface_culling = True
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
    path = os.path.join(ZIEL, name + '.glb')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_image_format='JPEG',
                              export_jpeg_quality=86, export_yup=True)
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
    print(f'{name}: {tris} Dreiecke, {os.path.getsize(path) / 1e3:.0f} kB')


def common():
    reset()
    MATS.clear()
    mat('steel', 'metal', '#d3d8dc', 0.25, 0.85)
    mat('silver', 'gold', '#d9dde2', 0.25, 0.9)
    mat('gold', 'gold', '#e2b45c', 0.3, 0.9)
    mat('bronze', 'gold', '#c08a45', 0.32, 0.9)
    mat('iron', 'plate', '#8e959b', 0.4, 0.8, saum='#c08a45')
    mat('leather', 'leather', '#5a3621', 0.6)
    mat('wood', 'wood', '#7a4a2a', 0.65)
    mat('wood2', 'wood', '#4e2f1c', 0.6)


# ------------------------------------------------------------------ Waffen
def schwert():
    """Langschwert des Klingenwächters: schlanke Klinge, Bronzeparierstange, Lederheft."""
    common()
    p = [blade('Klinge', [(0.1, 0.03, 0.006), (0.4, 0.027, 0.0055), (0.72, 0.022, 0.0045), (0.8, 0.014, 0.0035)], 'steel', tip=0.87)]
    p.append(guard('Parier', 0.1, 0.095, 0.014, 0.012, 'bronze', curl=0.025))
    p.append(rod('Heft', [(-0.075, 0.017), (-0.07, 0.016), (0.0, 0.015), (0.08, 0.016), (0.09, 0.017)], 'leather'))
    p.append(ball('Knauf', Vector((0, 0, -0.095)), 0.026, 'bronze', 1.2))
    p.append(crystal('Stein', Vector((0, -0.012, 0.095)), 0.008, 0.012, 'gold', 6))
    finish('schwert', p)


def schild():
    """Wappenschild: Stahlrand mit Bronze, rotes Feld mit goldener Sonne."""
    common()
    mat('field', 'cloth', '#8e2a24', 0.7)
    # Umriss (Wappenschild), X = Breite, Z = Höhe
    pts = []
    for i in range(9):   # oben, leicht gewölbt
        u = -1 + 2 * i / 8; pts.append((u * 0.26, 0.3 + 0.03 * (1 - u * u)))
    for i in range(1, 13):   # rechte Seite bis zur Spitze
        t = i / 12; a = t * math.pi / 2
        pts.append((0.26 * math.cos(a) ** 0.8 if t < 1 else 0.0, 0.3 - 0.68 * math.sin(a) ** 1.3))
    pts += [(-x, z) for x, z in reversed(pts[9:-1])]
    bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]
    f = bm.faces.new(vs)
    rings = [vs]
    # Ringe nach innen (Rand, Feld), Wölbung nach vorne (-Y)
    rim = set()
    for k, (d, bulge) in enumerate(((0.035, 0.012), (0.012, 0.016), (0.06, 0.03), (0.08, 0.045))):
        before = set(bm.faces)
        bmesh.ops.inset_individual(bm, faces=[f], thickness=d, depth=0)
        if k < 2: rim |= set(bm.faces) - before
        for v in f.verts: v.co.y -= bulge
    for x in bm.faces: x.material_index = 0 if x in rim else 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('Schild'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('Schild', me); bpy.context.scene.collection.objects.link(o)
    for m in ('iron', 'field'): o.data.materials.append(MATS[m])
    for poly in o.data.polygons: poly.use_smooth = True
    s = o.modifiers.new('S', 'SOLIDIFY'); s.thickness = 0.014; s.offset = 1
    bpy.context.view_layer.objects.active = o
    with bpy.context.temp_override(object=o): bpy.ops.object.modifier_apply(modifier='S')
    p = [o]
    # Sonne in der Mitte: Buckel mit Strahlen
    p.append(ball('Buckel', Vector((0, -0.11, 0.04)), 0.05, 'gold', 0.9))
    for k in range(12):
        a = 2 * math.pi * k / 12
        d = Vector((math.cos(a), 0, math.sin(a)))
        L = 0.11 if k % 2 == 0 else 0.08
        rings = [[Vector((0, -0.105, 0.04)) + d * 0.045 + Vector((-d.z, 0, d.x)) * 0.014, Vector((0, -0.115, 0.04)) + d * 0.045,
                  Vector((0, -0.105, 0.04)) + d * 0.045 - Vector((-d.z, 0, d.x)) * 0.014],
                 [Vector((0, -0.09, 0.04)) + d * L]]
        p.append(loft('Strahl', rings, 'gold', smooth=False, closed=False, cap0=False))
    # Schild wird am Unterarm getragen: Mitte ungefähr am Griff
    finish('schild', p)


def stab():
    """Stab der Sternenweberin: schlanker Holzschaft, Goldbeschläge, Mondsichel mit türkisem Kristall."""
    common()
    mat('crystal', 'glass', '#5fe0d2', 0.1, 0.0)
    p = [rod('Schaft', [(-0.85, 0.012), (-0.8, 0.015), (0.0, 0.017), (0.6, 0.018), (0.72, 0.02)], 'wood')]
    p.append(rod('Fuss', [(-0.86, 0.0), (-0.86, 0.014), (-0.8, 0.018), (-0.76, 0.016)], 'gold'))
    for z in (-0.12, 0.12, 0.68):
        p.append(rod('Ring', [(z - 0.012, 0.019), (z, 0.023), (z + 0.012, 0.019)], 'gold'))
    p.append(rod('Wicklung', [(-0.1, 0.02), (0.1, 0.02)], 'leather'))
    # Mondsichel: Bogen um den Kristall
    rings = []
    for i in range(15):
        a = math.radians(-200 + 220 * i / 14)
        c = Vector((math.cos(a) * 0.085, 0, 0.82 + math.sin(a) * 0.085))
        w = 0.004 + 0.012 * math.sin(math.pi * i / 14)
        rings.append(circle(c, w, 6, axis='Y', ry=0.007))
    rings[0] = [rings[0][0]]; rings[-1] = [rings[-1][0]]
    p.append(loft('Sichel', rings, 'gold'))
    p.append(rod('Halter', [(0.7, 0.022), (0.74, 0.026), (0.76, 0.012)], 'gold'))
    p.append(crystal('Kristall', Vector((0, 0, 0.84)), 0.03, 0.07, 'crystal'))
    finish('stab', p)


def bogen():
    """Reiterbogen des Waldläufers: geschwungene Wurfarme, Ledergriff, Goldspitzen, Sehne."""
    common()
    rings = []
    N = 25
    for i in range(N):
        u = -1 + 2 * i / (N - 1)
        z = u * 0.62
        x = 0.07 * u * u - 0.035 * max(0, abs(u) - 0.75) ** 2 * 16 - 0.07 * 0
        w = 0.022 - 0.012 * abs(u); t = 0.011 - 0.005 * abs(u)
        rings.append(circle(Vector((x, 0, z)), t, 8, axis='Z', ry=w))
    p = [loft('Arme', rings, 'wood2')]
    p.append(rod('Griff', [(-0.07, 0.016), (-0.06, 0.017), (0.06, 0.017), (0.07, 0.016)], 'leather'))
    tips = []
    for sg in (-1, 1):
        u = sg
        tip = Vector((0.07 * u * u - 0.035 * max(0, abs(u) - 0.75) ** 2 * 16, 0, u * 0.62))
        tips.append(tip)
        p.append(ball('Spitze', tip, 0.009, 'gold', 1.6))
    # Sehne
    a, b = tips
    p.append(loft('Sehne', [circle(a, 0.0016, 4), circle(b, 0.0016, 4)], 'leather'))
    # wie der KayKit-Bogen: Wurfarme entlang der Tiefe (im Spiel Z), Griff im Ursprung, Spitzen nach -X
    for o in p: o.data.transform(Matrix.Diagonal((-1, 1, 1, 1)))
    finish('bogen', p, rot_x=90)


def dolch():
    """Dolch der Schattenklinge: schmale Silberklinge, violetter Griff."""
    common()
    mat('violet', 'leather', '#4a2a5e', 0.6)
    p = [blade('Klinge', [(0.04, 0.016, 0.004), (0.15, 0.014, 0.0035), (0.22, 0.008, 0.003)], 'steel', tip=0.27)]
    p.append(guard('Parier', 0.045, 0.035, 0.01, 0.008, 'silver', curl=-0.012))
    p.append(rod('Heft', [(-0.06, 0.013), (0.0, 0.012), (0.03, 0.013)], 'violet'))
    p.append(ball('Knauf', Vector((0, 0, -0.075)), 0.017, 'silver', 1.3))
    finish('dolch', p)


def axt():
    """Zweihandaxt von Bärenherz: langer Schaft, gravierte Eisenklinge als Halbmond, Lederwicklungen."""
    common()
    p = [rod('Schaft', [(-0.5, 0.017), (-0.45, 0.019), (0.5, 0.021), (0.84, 0.02)], 'wood')]
    for z0, z1 in ((-0.42, -0.25), (-0.05, 0.12)):
        p.append(rod('Wicklung', [(z0, 0.022), (z1, 0.022)], 'leather'))
    p.append(rod('Fuss', [(-0.53, 0.0), (-0.53, 0.016), (-0.5, 0.021), (-0.47, 0.019)], 'iron'))
    # Klinge: Querschnitte entlang X, Höhe wächst zur Schneide (Halbmond), Dicke nimmt ab
    rings = []
    N = 9
    for i in range(N):
        t = i / (N - 1)
        x = 0.02 + 0.25 * t
        h = 0.06 + 0.15 * t ** 1.5
        zc = 0.7 + 0.01 * t
        th = 0.018 * (1 - t) + 0.0018
        rings.append([Vector((x, -th, zc - h)), Vector((x, th, zc - h)), Vector((x, th, zc + h)), Vector((x, -th, zc + h))])
    p.append(loft('Klinge', rings, 'iron', smooth=False))
    # Rückseite: kurzer Dorn
    p.append(loft('Dorn', [[Vector((-0.02, -0.012, 0.67)), Vector((-0.02, 0.012, 0.67)), Vector((-0.02, 0.012, 0.73)), Vector((-0.02, -0.012, 0.73))],
                            [Vector((-0.1, 0, 0.71))]], 'iron', smooth=False))
    p.append(rod('Kopf', [(0.64, 0.024), (0.66, 0.028), (0.76, 0.028), (0.78, 0.024)], 'bronze'))
    # Klinge quer zur Blickrichtung drehen, damit sie in der Kampfhaltung von vorne als Axt lesbar ist
    for o in p: o.data.transform(Matrix.Rotation(math.radians(90), 4, 'Z'))
    finish('axt', p)


ALLE = {'schwert': schwert, 'schild': schild, 'stab': stab, 'bogen': bogen, 'dolch': dolch, 'axt': axt}
if __name__ == '__main__':
    namen = [a for a in sys.argv[1:] if a in ALLE] or list(ALLE)
    for n in namen: ALLE[n]()
