"""Realistische Grundkörper aus MakeHuman (CC0) für die eigenen Figuren.

MakeHuman liefert einen Menschen mit fein modelliertem Gesicht, echten Augen, Brauen und Wimpern.
Dieses Modul formt ihn (Geschlecht, Muskeln, Gewicht, Gesichtszüge), bringt ihn in die Grundhaltung
der Quaternius-Figuren (Arme waagrecht, Beine gerade) und verschiebt ihn so, dass alle Gelenke
genau auf dem Quaternius-Skelett liegen. Dann passen alle Animationen.

Quellen (beide CC0, siehe assets/characters/eigene/README.md):
  MAKEHUMAN         Ordner makehuman/data aus github.com/makehumancommunity/makehuman (Körper, Formen, Skelett)
  MAKEHUMAN_ASSETS  Ordner public/data aus dem npm-Paket makehuman-data-v1 (Haut, Augen, Brauen, Wimpern, Haare)"""
import os, json
import bpy, bmesh
from mathutils import Vector

MH = os.environ.get('MAKEHUMAN', os.path.expanduser('~/makehuman/makehuman/data')) + '/'
MHA = os.environ.get('MAKEHUMAN_ASSETS', os.path.expanduser('~/makehuman-data/public/data')) + '/'


def read_obj(path):
    vs, vts, faces, grp = [], [], [], None
    for line in open(path):
        if line.startswith('v '): vs.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('vt '): vts.append([float(x) for x in line.split()[1:3]])
        elif line.startswith('g '): grp = line.split()[1]
        elif line.startswith('f '):
            idx = [p.split('/') for p in line.split()[1:]]
            faces.append(([int(a[0]) - 1 for a in idx], [int(a[1]) - 1 for a in idx], grp))
    return vs, vts, faces


def read_target(path):
    d = {}
    for line in open(path):
        if line[0] in '#\n': continue
        p = line.split(); d[int(p[0])] = (float(p[1]), float(p[2]), float(p[3]))
    return d


def morph(vs, targets):
    out = [list(v) for v in vs]
    for name, w in targets.items():
        if abs(w) < 1e-4: continue
        for i, (dx, dy, dz) in read_target(MH + 'targets/' + name + '.target').items():
            out[i][0] += w * dx; out[i][1] += w * dy; out[i][2] += w * dz
    return out


def _mix(v):
    """0..1 -> Anteile an min/average/max (wie die Regler in MakeHuman)."""
    if v < 0.5: return {'min': 1 - v * 2, 'average': v * 2}
    return {'average': 2 - v * 2, 'max': v * 2 - 1}


def macro(gender='female', muscle=0.5, weight=0.5, race='caucasian', prop=1.0, extra=None):
    """Grundform: muscle/weight 0..1 (0.5 = Durchschnitt), prop: Anteil idealer Proportionen."""
    t = {f'macrodetails/{race}-{gender}-young': 1.0}
    for mk, mw in _mix(muscle).items():
        for wk, ww in _mix(weight).items():
            k = f'{gender}-young-{mk}muscle-{wk}weight'
            t[f'macrodetails/universal-{k}'] = mw * ww
            if prop: t[f'macrodetails/proportions/{k}-idealproportions'] = mw * ww * prop
    for k, v in (extra or {}).items():
        t[k] = t.get(k, 0) + v
    return t


def to_blender(p):
    """MakeHuman: Dezimeter, Y oben, Gesicht nach +Z -> Blender: Meter, Z oben, Gesicht nach -Y."""
    return Vector((p[0] * 0.1, -p[2] * 0.1, p[1] * 0.1))


_SK = None
def skel():
    global _SK
    if _SK is None:
        _SK = json.load(open(MH + 'rigs/default.mhskel'))
        _SK['W'] = json.load(open(MH + 'rigs/default_weights.mhw'))['weights']
        kids = {}
        for n, b in _SK['bones'].items(): kids.setdefault(b['parent'], []).append(n)
        _SK['kids'] = kids
    return _SK


def desc(name):
    s = skel(); out = [name]; i = 0
    while i < len(out):
        out += s['kids'].get(out[i], []); i += 1
    return set(out)


class Mensch:
    """Ein geformter MakeHuman-Körper. P: alle Punkte (auch Hilfspunkte für Augen, Brauen, Haare)."""
    def __init__(self, targets):
        vs, self.vts, self.faces = read_obj(MH + '3dobjs/base.obj')
        self.P = [to_blender(p) for p in morph(vs, targets)]
        body = {i for f, _, g in self.faces if g == 'body' for i in f}
        self.zmin = min(self.P[i].z for i in body); self.top = max(self.P[i].z for i in body)
        self.k = 0.1
        self.W = [dict() for _ in self.P]
        for b, lst in skel()['W'].items():
            for v, w in lst: self.W[v][b] = self.W[v].get(b, 0) + w
        for d in self.W:
            t = sum(d.values())
            for b in d: d[b] /= t

    def scale_to(self, height):
        k = height / (self.top - self.zmin)
        self.P = [Vector((p.x * k, p.y * k, (p.z - self.zmin) * k)) for p in self.P]
        self.k *= k

    def J(self, joint):
        vv = skel()['joints'][joint]
        return sum((self.P[i] for i in vv), Vector()) / len(vv)

    def head(self, b): return self.J(skel()['bones'][b]['head'])
    def tail(self, b): return self.J(skel()['bones'][b]['tail'])

    def align(self, bones, pivot, a, b, extra=None):
        """Dreht die Punkte dieser Knochen (mit ihren Gewichten) um pivot, so dass a nach b zeigt."""
        R = a.normalized().rotation_difference(b.normalized()).to_matrix()
        extra = extra or {}
        for i, d in enumerate(self.W):
            f = sum(w for bn, w in d.items() if bn in bones) + sum(w * extra[bn] for bn, w in d.items() if bn in extra)
            if f <= 0: continue
            p = self.P[i]
            self.P[i] = p + (R @ (p - pivot) + pivot - p) * min(1.0, f)

    def displace(self, pairs):
        """Schiebt die Gelenke (pairs: Gelenkname -> Ziel) aufs Ziel, weich entlang der Knochen."""
        s = skel(); bones = s['bones']
        D = {j: t - self.J(j) for j, t in pairs.items()}
        order, stack = [], list(s['kids'].get(None, []))
        while stack:
            b = stack.pop(0); order.append(b); stack += s['kids'].get(b, [])
        BD = {}
        for b in order:
            bb = bones[b]; par = bb['parent']
            h = D.get(bb['head'])
            if h is None: h = BD[par][1] if par else Vector()
            t = D.get(bb['tail'])
            if t is None:   # nächstes zugeordnete Gelenk weiter unten in der Kette, halber Weg
                c, t = b, None
                while s['kids'].get(c):
                    c = s['kids'][c][0]
                    for end in ('head', 'tail'):
                        if bones[c][end] in D: t = D[bones[c][end]]; break
                    if t is not None: break
                t = h if t is None else h + (t - h) * 0.5
            BD[b] = (h, t)
        HT = {b: (self.head(b), self.tail(b)) for b in order}
        new = list(self.P)
        for i, d in enumerate(self.W):
            p = self.P[i]; acc = Vector()
            for b, w in d.items():
                h, t = HT[b]; ax = t - h; L = ax.length_squared
                u = 0 if L < 1e-12 else min(1, max(0, (p - h).dot(ax) / L))
                acc += w * BD[b][0].lerp(BD[b][1], u)
            new[i] = p + acc
        self.P = new

    def fit(self, qarm):
        """In Grundhaltung und Gelenklage des Quaternius-Skeletts bringen."""
        Q = {b.name: qarm.matrix_world @ b.head_local for b in qarm.data.bones}
        for S, s in (('L', 'l'), ('R', 'r')):
            sh, el, wr = self.head(f'upperarm01.{S}'), self.head(f'lowerarm01.{S}'), self.head(f'wrist.{S}')
            self.align(desc(f'lowerarm01.{S}'), el, wr - el, el - sh)                      # Unterarm strecken
            sh, wr = self.head(f'upperarm01.{S}'), self.head(f'wrist.{S}')
            self.align(desc(f'upperarm01.{S}'), sh, wr - sh, Q[f'hand_{s}'] - Q[f'upperarm_{s}'],
                       extra={f'shoulder01.{S}': 0.5})                                          # Arm waagrecht
            hip, an = self.head(f'upperleg01.{S}'), self.head(f'foot.{S}')
            self.align(desc(f'upperleg01.{S}'), hip, an - hip, Q[f'foot_{s}'] - Q[f'thigh_{s}'])  # Bein gerade
        bones = skel()['bones']; pairs = {}
        for S, s in (('L', 'l'), ('R', 'r')):
            for mb, qb in (('upperleg01', 'thigh'), ('lowerleg01', 'calf'), ('foot', 'foot'),
                           ('upperarm01', 'upperarm'), ('lowerarm01', 'lowerarm'), ('wrist', 'hand')):
                pairs[bones[f'{mb}.{S}']['head']] = Q[f'{qb}_{s}']
        pairs[bones['neck01']['head']] = Q['neck_01']
        pairs[bones['head']['head']] = Q['Head']
        pairs[bones['spine05']['head']] = Q['pelvis']
        self.displace(pairs)

    def fit_head(self, qbvh, qtop):
        """Kopf so skalieren, dass Kinn und Scheitel auf derselben Höhe liegen wie beim Quaternius-Kopf
        (die Rezepte setzen Halsband, Reif und Kapuze nach diesen Höhen)."""
        from mathutils.bvhtree import BVHTree
        used = sorted({i for f, _, g in self.faces if g == 'body' for i in f})
        mine = BVHTree.FromPolygons([self.P[i] for i in range(len(self.P))],
                                    [f for f, _, g in self.faces if g == 'body'])
        z0 = self.head('neck01').z; z1 = z0 + 0.13   # vom Halsansatz 13 cm nach oben
        qc = chin(qbvh, z0, z1)
        mc = self.tail('jaw').z - 0.015   # Kinnspitze (Ende des Kieferknochens), Unterkante etwas tiefer
        top = max(self.P[i].z for i in used)
        k = (qtop - qc) / (top - mc)
        hb = desc('head')
        yc = self.head('head').y
        for i, d in enumerate(self.W):
            f = min(1.0, sum(w for b, w in d.items() if b in hb))
            if f <= 0: continue
            p = self.P[i]
            q = Vector((p.x * k, yc + (p.y - yc) * k, qc + (p.z - mc) * k))
            self.P[i] = p.lerp(q, f)
        return qc, mc, k

    def mesh(self, name, groups=('body',)):
        used = sorted({i for f, _, g in self.faces if g in groups for i in f})
        remap = {o: n for n, o in enumerate(used)}
        bm = bmesh.new(); bv = [bm.verts.new(self.P[i]) for i in used]
        uv = bm.loops.layers.uv.new('UVMap')
        for f, t, g in self.faces:
            if g not in groups: continue
            try: face = bm.faces.new([bv[remap[i]] for i in f])
            except ValueError: continue
            for l, ti in zip(face.loops, t): l[uv].uv = self.vts[ti]
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        return _link(name, me)

    def proxy(self, name, kind, file=None):
        """Zusatzteil (Augen, Brauen, Wimpern, Haare) auf den geformten Körper setzen.
        Gibt (Objekt, Pfad der Textur) zurück."""
        base = MHA + f'proxies/{kind}/{name}/'
        d = json.load(open(base + (file or name) + '.json'))
        pts = []
        for r, w, o in zip(d['ref_vIdxs'], d['weights'], d['offsets']):
            p = sum((self.P[r[k]] * w[k] for k in range(3)), Vector())
            pts.append(p + Vector((o[0], -o[2], o[1])) * self.k)
        uvs = d['uvs'][0] if d['uvs'] and d['uvs'][0] else []
        bm = bmesh.new(); bv = [bm.verts.new(p) for p in pts]
        uv = bm.loops.layers.uv.new('UVMap')
        for vi, ui in _faces_v3(d['faces']):
            try: face = bm.faces.new([bv[k] for k in vi])
            except ValueError: continue
            if ui and uvs:
                for l, k in zip(face.loops, ui): l[uv].uv = (uvs[2 * k], uvs[2 * k + 1])
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        tex = [m['mapDiffuse'] for m in d['materials'] if m.get('mapDiffuse')]
        return _link(name, me), (base + tex[0]) if tex else None


def chin(bvh, z0, z1):
    """Höhe der Kinnunterkante: im Profil von vorne (x=0) die Stelle, an der es vom Hals am stärksten
    nach vorne zum Kinn springt."""
    prof, z = [], z0
    while z < z1:
        hit = bvh.ray_cast(Vector((0, -1, z)), Vector((0, 1, 0)))[0]
        prof.append((z, hit.y if hit else 1.0)); z += 0.002
    best = max(range(len(prof) - 5), key=lambda i: prof[i][1] - prof[i + 5][1])
    return prof[best][0] + 0.005


def _link(name, me):
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    for p in me.polygons: p.use_smooth = True
    return o


def _faces_v3(f):
    """Flächen aus dem three.js-JSON-Format (Version 3) lesen."""
    i, out = 0, []
    while i < len(f):
        t = f[i]; i += 1
        n = 4 if t & 1 else 3
        vi = f[i:i + n]; i += n; ui = None
        if t & 2: i += 1
        if t & 4: i += 1
        if t & 8: ui = f[i:i + n]; i += n
        if t & 16: i += 1
        if t & 32: i += n
        if t & 64: i += 1
        if t & 128: i += n
        out.append((vi, ui))
    return out
