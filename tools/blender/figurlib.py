"""Baukasten für eigene Figuren auf dem Quaternius-Grundkörper (CC0).

Jede Figur ist ein kurzes Rezept in tools/blender/figuren/<name>.py, das diese Teile benutzt:
Kleidung wird aus der Körperoberfläche ausgeschnitten (erbt die Bewegungsgewichte), Platten,
Stoffbahnen, Umhänge, Röcke, Kapuzen, Riemen, Haare und Schmuck entstehen aus einfachen Formen.

Maße stehen in den Rezepten im Raum des Frauenkörpers (Füße auf 0, Kopf oben ca. 1,77 m).
Für den Männerkörper rechnet der Baukasten sie über die Gelenkpunkte um (F.Z für Höhen,
F.X für Abstände entlang der Arme), so passen dieselben Zahlen auf beide Körper."""
import os, math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from blib import ARBEIT, Q, reset, import_gltf, srgb, relaxed_pose, setup_render, camera, render

# Gelenkpunkte (Höhe) Frau -> Mann, für die Umrechnung der Maße
_ZF = [0.0, 0.071, 0.535, 0.944, 1.055, 1.164, 1.291, 1.418, 1.485, 1.55, 1.767, 2.5]
_ZM = [0.0, 0.086, 0.542, 0.971, 1.072, 1.178, 1.311, 1.456, 1.52, 1.6, 1.81, 2.543]
_XF = [0.0, 0.152, 0.392, 0.641, 0.834, 2.0]
_XM = [0.0, 0.212, 0.463, 0.706, 0.929, 2.1]


def _pl(x, a, b):
    s = 1 if x >= 0 else -1; x = abs(x)
    for i in range(len(a) - 1):
        if x <= a[i + 1]:
            return s * (b[i] + (b[i + 1] - b[i]) * (x - a[i]) / (a[i + 1] - a[i]))
    return s * (b[-1] + x - a[-1])


def plane(co, no):
    return (Vector(co), Vector(no).normalized())


def inside(p, planes, margin=0.0):
    return all((p - co).dot(no) >= margin for co, no in planes)


def mk(fn, **kw):
    me = bpy.data.meshes.new('tmp'); bm = bmesh.new(); fn(bm, **kw); bm.to_mesh(me); bm.free(); return me


def edge_smooth(bm, iters):
    """Glättet offene Ränder entlang des Randes (saubere Säume)."""
    bverts = [v for v in bm.verts if v.is_boundary]
    for _ in range(iters):
        new = {}
        for v in bverts:
            nb = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if len(nb) == 2: new[v] = v.co * 0.5 + (nb[0].co + nb[1].co) * 0.25
        for v, c in new.items(): v.co = c


SKIN_TEX = {'female': 'd366843ee7d9e9f37ec87a0e1c98c7f2e45573c08eeb80a51a6d9344e68cf288.png',
            'male': 'df680cbc1967a61e85998bfafb8f7bc0a36dd604bb3266486c4b06b1a184bb45.png'}
EYE_TEX = 'd08e3356a83211bc6ca21fe3a8e39f4b5c1a3b8f85457fc2c0fb57be09935025.png'


class Figur:
    def __init__(self, name, base='female', skin='#f6c9a8', eye_scale=1.05, seed=7):
        self.name, self.base = name, base
        self.out = os.path.join(ARBEIT, name) + '/'
        os.makedirs(self.out, exist_ok=True)
        random.seed(seed)
        reset()
        B = 'Female' if base == 'female' else 'Male'
        objs = import_gltf(Q + f'base/Superhero_{B}_FullBody.gltf')
        self.arm = [o for o in objs if o.type == 'ARMATURE'][0]; self.arm.name = 'Armature'
        self.body = [o for o in objs if o.type == 'MESH' and o.name.lower().startswith('superhero')][0]
        for o in list(objs):
            if o.name.startswith('Icosphere'): bpy.data.objects.remove(o)
        self.body.name = 'Body'
        self.eyes = bpy.data.objects['Eyes']; self.brows = bpy.data.objects['Eyebrows']
        self.male = base == 'male'
        self.cover = []
        self.M = {}
        self._grow_eyes(eye_scale)
        self.refresh_body()
        # Haut aus textures.py (eigene Hautfarbe je Figur)
        from textures import make_skin
        skin_png = make_skin(Q + 'textures/' + SKIN_TEX[base], self.out + 'skin.png', skin)
        self.M['skin'] = self._tex_mat('M_skin', skin_png, 0.6)
        self.M['eyes'] = self._tex_mat('M_eyes', Q + 'textures/' + EYE_TEX, 0.25)

    # ------------------------------------------------------------ Maße
    def Z(self, z):
        return _pl(z, _ZF, _ZM) if self.male else z

    def Zi(self, z):
        return _pl(z, _ZM, _ZF) if self.male else z

    def X(self, x):
        return _pl(x, _XF, _XM) if self.male else x

    def Xi(self, x):
        return _pl(x, _XM, _XF) if self.male else x

    def V(self, x, y, z):
        """Punkt im Frauenraum -> Punkt auf diesem Körper (x über die Armachse)."""
        return Vector((self.X(x), y, self.Z(z)))

    def hz(self, z, up=True):
        """Waagrechte Schnittebene (Frauen-Höhe z); up: behält, was darüber liegt."""
        return plane((0, 0, self.Z(z)), (0, 0, 1 if up else -1))

    def ax(self, x, sg, outward=True):
        """Senkrechte Schnittebene quer zum Arm bei |x| (Frauenraum); sg = Seite (+1 links)."""
        return plane((self.X(x) * sg, 0, 0), (sg if outward else -sg, 0, 0))

    def refresh_body(self):
        bm = bmesh.new(); bm.from_mesh(self.body.data)
        self.BODY = BVHTree.FromBMesh(bm); bm.free()

    def _grow_eyes(self, scale, radius=0.032):
        if abs(scale - 1) < 1e-3: return
        ev = [self.eyes.matrix_world @ v.co for v in self.eyes.data.vertices]
        cs = [sum((p for p in ev if (p.x > 0) == s), Vector()) / max(1, sum(1 for p in ev if (p.x > 0) == s)) for s in (True, False)]
        def grow(o, full=False):
            mw = o.matrix_world; inv = mw.inverted()
            for v in o.data.vertices:
                p = mw @ v.co; c = cs[0] if p.x > 0 else cs[1]
                d = p - c; dist = math.hypot(d.x, d.z) + abs(d.y) * 0.5
                f = 1.0 if full else max(0.0, 1 - dist / radius); f = f * f * (3 - 2 * f)
                k = 1 + (scale - 1) * f
                v.co = inv @ Vector((c.x + d.x * k, c.y + d.y * (1 + (k - 1) * 0.4), c.z + d.z * k))
        grow(self.body); grow(self.brows); grow(self.eyes, full=True)

    # ------------------------------------------------------------ Materialien
    def mat(self, key, kind, color, rough=0.7, metal=0.0, saum=None):
        """kind steuert die gemalten Details (details.py): cloth, wrap, trim, leather, plate, metal,
        fur, hair, glass, gem. saum: Farbe eines Musters am Stoffrand."""
        m = bpy.data.materials.new('M_' + key); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*srgb(color), 1)
        b.inputs['Roughness'].default_value = rough
        b.inputs['Metallic'].default_value = metal
        m['kind'] = kind
        if saum: m['saum'] = list(srgb(saum))
        self.M[key] = m
        return m

    def _tex_mat(self, name, img, rough):
        m = bpy.data.materials.new(name); m.use_nodes = True
        nt = m.node_tree; b = nt.nodes['Principled BSDF']
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(img)
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        b.inputs['Roughness'].default_value = rough
        return m

    def _m(self, m):
        return self.M[m] if isinstance(m, str) else m

    # ------------------------------------------------------------ Grundwerkzeuge
    def add_obj(self, name, me):
        o = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(o)
        o.parent = self.arm
        return o

    def rig(self, o, groups=None):
        if groups:
            for b, w in groups.items():
                vg = o.vertex_groups.get(b) or o.vertex_groups.new(name=b)
                vg.add(range(len(o.data.vertices)), w, 'REPLACE')
        if not any(m.type == 'ARMATURE' for m in o.modifiers):
            m = o.modifiers.new('Armature', 'ARMATURE'); m.object = self.arm

    def set_mat(self, o, m, smooth=True):
        o.data.materials.clear(); o.data.materials.append(self._m(m))
        for p in o.data.polygons: p.material_index = 0; p.use_smooth = smooth

    def apply_mod(self, o, name):
        bpy.context.view_layer.objects.active = o
        with bpy.context.temp_override(object=o):
            bpy.ops.object.modifier_apply(modifier=name)

    def modify(self, o, typ, **kw):
        m = o.modifiers.new('X', typ)
        for k, v in kw.items(): setattr(m, k, v)
        o.modifiers.move(len(o.modifiers) - 1, 0)
        self.apply_mod(o, 'X')

    def solidify(self, o, rim, rim_only=True, offset=-1):
        self.modify(o, 'SOLIDIFY', thickness=rim, offset=offset, use_rim_only=rim_only, use_even_offset=False)

    def bevel(self, o, width, segments=2):
        self.modify(o, 'BEVEL', width=width, segments=segments)

    def clearance(self, v, off):
        """Punkt mindestens 'off' außerhalb der Körperoberfläche."""
        hit, n, i, d = self.BODY.find_nearest(v)
        if hit is None: return v
        s = (v - hit).dot(n)
        r = hit + n * max(s, off) + (v - hit - n * s)
        return r if (r - v).length < 0.15 else v

    def weights_at(self, p):
        hit, n, i, d = self.BODY.find_nearest(p)
        me = self.body.data
        poly = me.polygons[i]
        best = min(poly.vertices, key=lambda vi: (me.vertices[vi].co - hit).length)
        names = {g.index: g.name for g in self.body.vertex_groups}
        return {names[g.group]: g.weight for g in me.vertices[best].groups if g.weight > 0.01}

    def transfer_weights(self, o):
        for vg in self.body.vertex_groups:
            if not o.vertex_groups.get(vg.name): o.vertex_groups.new(name=vg.name)
        for v in o.data.vertices:
            for g, w in self.weights_at(v.co).items(): o.vertex_groups[g].add([v.index], w, 'REPLACE')
        self.rig(o)

    def prop(self, name, me, material, at=None, groups=None):
        o = self.add_obj(name, me)
        self.set_mat(o, material)
        self.rig(o, groups or self.weights_at(Vector(at)))
        return o

    def bvh_of(self, objs):
        bm = bmesh.new()
        for o in objs:
            t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
            me = bpy.data.meshes.new('t'); t.to_mesh(me); t.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
        return BVHTree.FromBMesh(bm)

    def ray_body(self, x, z, side=-1):
        """Treffpunkt auf dem Körper von vorne (side -1) oder hinten (+1) bei (x, z) im echten Raum."""
        return self.BODY.ray_cast(Vector((x, side * 1.0, z)), Vector((0, -side, 0)))[0]

    # ------------------------------------------------------------ Kleidung aus der Körperoberfläche
    def garment(self, name, planes, material, offset, filt=None, rim=0.005, smooth=0, cover=False, noise=0.0, relax=0):
        """Schneidet ein Stück aus der Körperoberfläche, glättet es, schiebt es nach außen
        (offset(p) in Metern, p im echten Raum) und gibt ihm eine Kante."""
        me = self.body.data.copy(); me.name = name
        o = self.add_obj(name, me)
        for vg in self.body.vertex_groups: o.vertex_groups.new(name=vg.name)
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
        for v in bm.verts:
            off = offset(v.co) if callable(offset) else offset
            if noise: off += noise * random.random()
            v.co = self.clearance(v.co, off)
        if relax:   # Platten: Muskeln und Mulden glätten (gewölbte, ruhige Form), danach wieder über den Körper
            for _ in range(relax):
                bmesh.ops.smooth_vert(bm, verts=[v for v in bm.verts if not v.is_boundary], factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
            for v in bm.verts:
                off = offset(v.co) if callable(offset) else offset
                v.co = self.clearance(v.co, off * 0.8)
        bm.normal_update()
        bm.to_mesh(me); bm.free()
        self.rig(o)
        self.set_mat(o, material)
        if rim: self.solidify(o, rim)
        if cover: self.cover.append((planes, filt))
        return o

    def ring(self, name, z0, z1, material, off, rim=0.006, smooth=2, filt=None, cover=False):
        """Waagrechtes Band um Rumpf oder Beine zwischen den Höhen z0 < z1 (Frauenraum)."""
        return self.garment(name, [self.hz(z0), self.hz(z1, False)], material, off, filt=filt, rim=rim, smooth=smooth, cover=cover)

    def sleeve(self, name, x0, x1, material, off, rim=0.006, smooth=2, cover=False, sides=(1, -1)):
        """Band um beide Arme zwischen |x0| < |x1| (Frauenraum, entlang der Armachse)."""
        out = []
        for sg in sides:
            s = 'L' if sg > 0 else 'R'
            out.append(self.garment(name + s, [self.ax(x0, sg), self.ax(x1, sg, False)], material, off, rim=rim, smooth=smooth, cover=cover))
        return out

    def leg_band(self, name, z0, z1, material, off, rim=0.006, smooth=2, cover=False, front=False):
        """Band um beide Beine (Höhen im Frauenraum); front: nur die Vorderseite (Beinschienen)."""
        filt = (lambda p: p.y < 0.015) if front else None
        return self.ring(name, z0, z1, material, off, rim=rim, smooth=smooth, filt=filt, cover=cover)

    # ------------------------------------------------------------ Schuhe
    def shoes(self, material, sole, zmax=0.14, clear=0.022):
        for sg in (1, -1):
            pts = [Vector(v.co) for v in self.body.data.vertices if v.co.z < self.Z(zmax) and v.co.x * sg > 0.02]
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
                v.co = self.clearance(v.co, clear)
                v.co.z = max(v.co.z, -0.004)
            me = bpy.data.meshes.new('Shoe'); bm.to_mesh(me); bm.free()
            o = self.add_obj('Shoe', me); self.transfer_weights(o)
            o.data.materials.append(self._m(material)); o.data.materials.append(self._m(sole))
            for p in o.data.polygons:
                p.use_smooth = True; p.material_index = 1 if p.normal.z < -0.6 else 0
        self.cover.append(([self.hz(zmax - 0.02, False)], None))

    # ------------------------------------------------------------ Stoffbahnen, Platten, Umhänge
    def panel(self, name, material, ztop, length, wtop, wbot, side=-1, angle=0.0, lift=0.03, flare=0.02,
              rows=7, cols=6, thick=0.008, sub=1, weights='hips', follow=0.35, curve=0.0, xshift=0.0):
        """Rechteckige, nach unten hängende Bahn: vorne (side -1), hinten (+1), oder um 'angle' Grad
        um den Körper gedreht (Seitenplatten). Höhen im Frauenraum.
        weights: 'hips' (Becken/Oberschenkel), 'back' (Umhang am Rücken), oder ein Knochenname."""
        bm = bmesh.new(); grid = []; wl = []
        ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        rot = lambda x, y: (x * ca - y * sa, x * sa + y * ca)
        for i in range(rows):
            t = i / (rows - 1)
            z = self.Z(ztop - length * t)
            half = wtop + (wbot - wtop) * t
            row = []
            for j in range(cols):
                u = -1 + 2 * j / (cols - 1)
                x = xshift + half * u
                # vom Körper aus nach außen suchen (in gedrehter Richtung)
                dx, dy = rot(0, side)
                ox, oy = rot(x, 0)
                hit = self.BODY.ray_cast(Vector((ox + dx * 1.0, oy + dy * 1.0, z)), Vector((-dx, -dy, 0)))[0]
                depth = (Vector((hit.x, hit.y, 0)) - Vector((ox, oy, 0))).dot(Vector((dx, dy, 0))) if hit else 0.12
                d = max(depth, 0.06) + lift + flare * t + curve * (1 - u * u)
                if i > 0:
                    prev = grid[-1][j].co
                    pd = (Vector((prev.x, prev.y, 0)) - Vector((ox, oy, 0))).dot(Vector((dx, dy, 0)))
                    if t > 0.3: d = max(d, pd + 0.002)       # unten frei hängend
                v = bm.verts.new((ox + dx * d, oy + dy * d, z)); row.append(v)
                if weights == 'hips':
                    xs = ox
                    lw = min(follow, max(0, t - 0.15) * 0.8)
                    l = lw * (0.5 + 0.5 * max(-1, min(1, xs / 0.08)))
                    r = lw * (0.5 - 0.5 * max(-1, min(1, xs / 0.08)))
                    wl.append((v, {'pelvis': 1 - l - r, 'thigh_l': l, 'thigh_r': r}))
                elif weights == 'back':
                    s3 = max(0.0, 1 - t * 1.6)
                    wl.append((v, {'spine_03': s3, 'spine_02': (1 - s3) * 0.6, 'pelvis': (1 - s3) * 0.4}))
                else:
                    wl.append((v, {weights: 1.0}))
            grid.append(row)
        for i in range(rows - 1):
            for j in range(cols - 1):
                bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        idx = {v: k for k, v in enumerate(bm.verts)}
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        o = self.add_obj(name, me); self.set_mat(o, material)
        groups = set(g for _, w in wl for g in w)
        for g in groups: o.vertex_groups.new(name=g)
        for v, w in wl:
            for g, x in w.items(): o.vertex_groups[g].add([idx[v]], x, 'REPLACE')
        self.rig(o)
        if sub: self.modify(o, 'SUBSURF', levels=sub)
        self.solidify(o, thick, rim_only=False, offset=0)
        return o

    def plates(self, name, material, ztop, length, angles, width, **kw):
        """Mehrere Platten (Beintaschen) im Kreis um die Hüfte."""
        return [self.panel(f'{name}{k}', material, ztop, length, width, width * 1.1, angle=a, weights='hips', **kw)
                for k, a in enumerate(angles)]

    def pauldron(self, side, materials, size=0.095, layers=3, tilt=-28, x=0.2, z=1.425, y=0.012, squash=0.75, thick=0.008, rim=None):
        """Schulterstück aus gestaffelten Schalen (oben die größte). materials: je Lage ein Material."""
        sg = 1 if side == 'l' else -1
        out = []
        for k in range(layers):
            me = mk(lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=1))
            bm = bmesh.new(); bm.from_mesh(me)
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.15], context='VERTS')
            bm.to_mesh(me); bm.free()
            r = size - k * size * 0.13
            me.transform(Matrix.Diagonal((r * 1.15, r * 1.05, r * squash, 1)))
            me.transform(Matrix.Rotation(math.radians(tilt * sg), 4, 'Y'))
            p = self.V((x + k * 0.035) * sg, y, z - k * 0.018)
            me.transform(Matrix.Translation(p))
            mm = materials[min(k, len(materials) - 1)]
            o = self.prop('Pauldron' + side.upper(), me, mm, groups={f'upperarm_{side}': 0.85, f'clavicle_{side}': 0.15})
            self.solidify(o, thick, rim_only=False)
            out.append(o)
        return out

    def cape(self, name, material, ztop=1.42, length=0.75, wtop=0.15, wbot=0.24, lift=0.035, **kw):
        return self.panel(name, material, ztop, length, wtop, wbot, side=1, weights='back', lift=lift, rows=9, cols=7, **kw)

    def skirt(self, name, material, ztop, zbot, flare=0.12, segs=28, rows=8, off=0.012, thick=0.006, cover=True):
        """Rock: Kegel von der Hüfte bis zu zbot (Frauenraum), unten weiter."""
        bm = bmesh.new(); rings = []; wl = []
        z0, z1 = self.Z(ztop), self.Z(zbot)
        top_r = []
        for j in range(segs):
            a = 2 * math.pi * j / segs; d = Vector((math.sin(a), -math.cos(a), 0))
            c = Vector((0, 0.02, z0))
            hit = self.BODY.ray_cast(c + d * 0.6, -d)[0]
            top_r.append(((hit - c).length if hit else 0.17) + off)
        rmax = max(top_r)
        for i in range(rows):
            t = i / (rows - 1); z = z0 + (z1 - z0) * t
            ring_ = []
            for j in range(segs):
                a = 2 * math.pi * j / segs; d = Vector((math.sin(a), -math.cos(a), 0))
                r = top_r[j] + (rmax * 1.05 - top_r[j]) * min(1, t * 2.5) + flare * t
                c = Vector((0, 0.02, z))
                # Beine dürfen nicht durchstechen
                hit = self.BODY.ray_cast(c + d * 0.8, -d)[0]
                if hit: r = max(r, (Vector((hit.x, hit.y, 0)) - Vector((c.x, c.y, 0))).length + 0.03)
                v = bm.verts.new(c + d * r); ring_.append(v)
                x = d.x
                lw = min(0.7, t * 0.9)
                l = lw * max(0, min(1, 0.5 + x * 1.5)); rr = lw - l
                wl.append((v, {'pelvis': 1 - lw, 'thigh_l': l, 'thigh_r': rr}))
            rings.append(ring_)
        for r0, r1 in zip(rings, rings[1:]):
            for j in range(segs):
                bm.faces.new((r0[j], r0[(j + 1) % segs], r1[(j + 1) % segs], r1[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        for f in bm.faces:
            if (f.calc_center_median() - Vector((0, 0.02, f.calc_center_median().z))).dot(f.normal) < 0: f.normal_flip()
        idx = {v: k for k, v in enumerate(bm.verts)}
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        o = self.add_obj(name, me); self.set_mat(o, material)
        for g in ('pelvis', 'thigh_l', 'thigh_r'): o.vertex_groups.new(name=g)
        for v, w in wl:
            for g, x in w.items(): o.vertex_groups[g].add([idx[v]], x, 'REPLACE')
        self.rig(o)
        self.modify(o, 'SUBSURF', levels=1)
        self.solidify(o, thick, rim_only=False, offset=-1)
        if cover: self.cover.append(([self.hz(ztop - 0.02, False), self.hz(zbot + 0.12)], None))
        return o

    def hood(self, name, material, off=0.028, zlow=1.40, face=(0.07, 1.545, 1.725), rim=0.008):
        """Kapuze über Kopf, Hals und Schultern mit Gesichtsöffnung (Frauenraum)."""
        fx, fz0, fz1 = face
        Zl, Zf0, Zf1 = self.Z(zlow), self.Z(fz0), self.Z(fz1)
        cz = (Zf0 + Zf1) / 2; hz_ = (Zf1 - Zf0) / 2
        def filt(p):
            if p.y < -0.0 and ((p.x / fx) ** 2 + ((p.z - cz) / hz_) ** 2) < 1: return False   # Gesicht frei
            return abs(p.x) < self.X(0.2) or p.z > self.Z(1.5)
        def offset(p):
            h = max(0, min(1, (p.z - Zl) / 0.12))
            return off * (0.7 + 0.5 * h) + 0.02 * max(0, (p.z - self.Z(1.62)) / 0.15)
        return self.garment(name, [plane((0, 0, Zl), (0, 0, 1))], material, offset, filt=filt, rim=rim, smooth=5)

    def mask(self, name, material, z0=1.49, z1=1.615, off=0.006):
        """Tuch vor Mund und Nase."""
        return self.garment(name, [self.hz(z0), self.hz(z1, False)], material, off, rim=0.004, smooth=3,
                            filt=lambda p: p.y < 0.03 or p.z < self.Z(1.55))

    def mantle(self, name, material, z0=1.33, z1=1.56, off=0.045, noise=0.02, width=0.3):
        """Fellumhang über den Schultern (unregelmäßiger Rand)."""
        Wx = self.X(width)
        return self.garment(name, [self.hz(z0), self.hz(z1, False)], material,
                            lambda p: off * (0.6 + 0.6 * max(0, min(1, (p.z - self.Z(z0)) / 0.12))), noise=noise,
                            filt=lambda p: abs(p.x) < Wx, rim=0.02, smooth=4)

    def strap(self, name, objs, center, u, n, width, lift, zmin, material, steps=96, thick=0.008):
        """Riemen um den Körper in der Ebene (u, y) durch center (echter Raum), Breite entlang n."""
        bv = self.bvh_of(objs)
        Y = Vector((0, 1, 0))
        pts = []
        for i in range(steps):
            th = 2 * math.pi * i / steps
            d = u * math.cos(th) + Y * math.sin(th)
            hit, nrm, _, _ = bv.ray_cast(center + d * 0.7, -d)
            if hit is None or hit.z < zmin: pts.append(None); continue
            pts.append((hit, nrm))
        bm = bmesh.new(); prev = None
        for item in pts + [None]:
            if item is None: prev = None; continue
            hit, nrm = item
            nrm = (nrm - n * nrm.dot(n)).normalized()
            a = bm.verts.new(hit + nrm * lift - n * width / 2); b = bm.verts.new(hit + nrm * lift + n * width / 2)
            if prev: bm.faces.new((prev[0], prev[1], b, a))
            prev = (a, b)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        o = self.add_obj(name, me); self.set_mat(o, material); self.transfer_weights(o)
        self.modify(o, 'SOLIDIFY', thickness=thick, offset=0)
        return o

    def bandolier(self, name, objs, material, right_to_left=True, width=0.042, lift=0.009, zmin=1.0):
        """Riemen schräg über die Brust (von der rechten Schulter zur linken Hüfte)."""
        sg = 1 if right_to_left else -1
        n = Vector((0.843 * sg, 0, 0.538)).normalized(); u = Vector((-0.538 * sg, 0, 0.843))
        c = Vector((0.06 * sg, 0.0, self.Z(1.22)))
        return self.strap(name, [self.body] + objs, c, u, n, width, lift, self.Z(zmin), material)

    def box(self, name, size, at, material, bone='pelvis', rot=0.0, bev=0.008):
        me = mk(lambda bm: bmesh.ops.create_cube(bm, size=1))
        me.transform(Matrix.Diagonal((*size, 1)))
        me.transform(Matrix.Rotation(math.radians(rot), 4, 'Z'))
        me.transform(Matrix.Translation(at))
        o = self.prop(name, me, material, groups={bone: 1.0})
        if bev: self.bevel(o, bev, 3)
        return o

    def buckle(self, z, material, size=(0.055, 0.012, 0.045)):
        hit = self.ray_body(0, self.Z(z))
        return self.box('Buckle', size, hit + Vector((0, -0.028, 0)), material, bev=0.006)

    def pouch(self, ang, size, z, material):
        a = math.radians(ang); d = Vector((math.sin(a), -math.cos(a), 0))
        hit = self.BODY.ray_cast(Vector((0, 0.03, self.Z(z))) + d, -d)[0]
        at = hit + d * (0.03 + size[1] / 2) + Vector((0, 0, -0.025))
        return self.box('Pouch', size, at, material, rot=ang, bev=0.012)

    def cylinder(self, name, r1, r2, depth, at, direction, material, groups, segs=16, caps=True):
        me = mk(lambda bm: bmesh.ops.create_cone(bm, cap_ends=caps, segments=segs, radius1=r1, radius2=r2, depth=depth))
        q = Vector((0, 0, 1)).rotation_difference(Vector(direction).normalized())
        me.transform(q.to_matrix().to_4x4())
        me.transform(Matrix.Translation(at))
        return self.prop(name, me, material, groups=groups)

    def gem(self, name, r, at, material, bone='Head'):
        me = mk(lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r))
        me.transform(Matrix.Diagonal((1, 0.6, 1.3, 1))); me.transform(Matrix.Translation(at))
        return self.prop(name, me, material, groups={bone: 1.0})

    # ------------------------------------------------------------ Kopf
    def head_bvh(self, extra=()):
        return self.bvh_of([self.body] + list(extra))

    def circlet(self, name, material, z=1.718, width=0.012, front_up=0.02, extra=(), off=0.005, back=True):
        """Reif um den Kopf (Stirnband, Diadem). Höhe im Frauenraum, vorne um front_up höher."""
        bv = self.head_bvh(extra)
        k = 40; lo, hi = [], []
        bm = bmesh.new()
        for i in range(k):
            a = 2 * math.pi * i / k
            d = Vector((math.sin(a), -math.cos(a), 0))
            zc = self.Z(z) - front_up * math.cos(a)
            vs = []
            for dz in (-width, width):
                o = Vector((0, 0.01, zc + dz)) + d * 0.3
                hit = bv.ray_cast(o, -d)[0]
                vs.append(bm.verts.new(hit + d * off if hit else o - d * 0.2))
            lo.append(vs[0]); hi.append(vs[1])
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        o = self.prop(name, me, material, groups={'Head': 1.0})
        self.modify(o, 'SOLIDIFY', thickness=0.006, offset=1)
        for p in o.data.polygons: p.use_smooth = True
        return o, bv

    def hair_mesh(self, file, material, name='Hair', scale=None):
        """Quaternius-Frisur (Hair_Long, Hair_Buns, Hair_SimpleParted, Hair_Buzzed, Hair_Beard ...)."""
        objs = import_gltf(Q + 'hair/' + file + '.gltf')
        res = None
        for o in objs:
            if o.type == 'MESH' and not o.name.startswith('Ico'):
                o.parent = self.arm; o.name = name
                for m in o.modifiers:
                    if m.type == 'ARMATURE': m.object = self.arm
                if self.male and not file.endswith('Male'):
                    pass
                self.set_mat(o, material)
                res = o
        for o in objs:
            if o.type == 'ARMATURE' or o.name.startswith('Ico'): bpy.data.objects.remove(o)
        return res

    def hair_weights(self, z):
        h = min(1, max(0, (z - self.Z(1.42)) / 0.16))
        n = min(1 - h, max(0, (z - self.Z(1.30)) / 0.12)) if h < 1 else 0
        return {k: w for k, w in (('Head', h), ('neck_01', n), ('spine_03', 1 - h - n)) if w > 0.001}

    def long_strands(self, name, material, locks, avoid, top=1.66, hc=(0, 0.015, 1.63), spread=(0.075, 0.05), flat=0.32):
        """Lange Haarsträhnen. locks: Liste (Winkel um den Kopf, Endhöhe, Dicke) im Frauenraum."""
        BV = self.bvh_of([self.body] + list(avoid))
        HC = self.V(*hc)
        bm = bmesh.new(); wl = []
        for ang, zend, rad in locks:
            a = math.radians(ang); d = Vector((math.sin(a), -math.cos(a), 0))
            n = 12; pts, radii, outs = [], [], []
            phase = random.random() * 6.28
            for i in range(n):
                t = i / (n - 1)
                z = self.Z(top) + (self.Z(zend) - self.Z(top)) * t
                p = Vector((HC.x, HC.y, z)) + d * (spread[0] + spread[1] * t)
                side = Vector((-d.y, d.x, 0))
                p += side * 0.012 * math.sin(phase + t * 9) * t
                for _ in range(4):
                    hit, nrm, idx, dist = BV.find_nearest(p)
                    if hit is None: break
                    sgn = (p - hit).dot(nrm); want = 0.016 + 0.01 * t
                    if sgn < want: p = p + nrm * (want - sgn)
                pts.append(p); outs.append(d.copy())
                radii.append(rad * (0.75 + 0.45 * math.sin(math.pi * min(1, t * 1.6))) * (1 - 0.55 * t ** 2))
            for _ in range(3):
                pts = [pts[0]] + [(pts[i - 1] + pts[i] * 2 + pts[i + 1]) / 4 for i in range(1, n - 1)] + [pts[-1]]
            self._strand(bm, wl, pts, radii, outs, flat)
        idx = {v: i for i, v in enumerate(bm.verts)}
        me = bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(me)
        wl2 = [(idx[v], w) for v, w in wl]; bm.free()
        o = self.add_obj(name, me); self.set_mat(o, material)
        for b in ('Head', 'neck_01', 'spine_03'): o.vertex_groups.new(name=b)
        for vi, w in wl2:
            for g, x in w.items(): o.vertex_groups[g].add([vi], x, 'REPLACE')
        self.rig(o)
        return o

    def _strand(self, bm, wl, pts, radii, outward, flat=0.32, k=8):
        rings = []
        for i, p in enumerate(pts):
            t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            o = (outward[i] - t * outward[i].dot(t)).normalized()
            sd = t.cross(o).normalized(); r = radii[i]
            ring = []
            for j in range(k):
                a = 2 * math.pi * j / k
                v = bm.verts.new(p + sd * math.cos(a) * r + o * math.sin(a) * r * flat)
                ring.append(v); wl.append((v, self.hair_weights(p.z)))
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            for j in range(k):
                bm.faces.new((r0[j], r0[(j + 1) % k], r1[(j + 1) % k], r1[j]))
        tip = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * radii[-1] * 2); wl.append((tip, self.hair_weights(pts[-1].z)))
        for j in range(k): bm.faces.new((rings[-1][j], rings[-1][(j + 1) % k], tip))
        bm.faces.new(list(reversed(rings[0])))

    # ------------------------------------------------------------ Abschluss
    def finish(self, brow_color='#6b4a32', hide_brows=False, render_views=False):
        """Verdeckte Haut entfernen, Gewichte prüfen, speichern."""
        bm = bmesh.new(); bm.from_mesh(self.body.data)
        def covered(v):
            for planes, filt in self.cover:
                if inside(v.co, planes, 0.012) and (filt is None or filt(v.co)): return True
            return False
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(covered(v) for v in f.verts)], context='FACES')
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        bm.to_mesh(self.body.data); bm.free()
        self.set_mat(self.body, self.M['skin']); self.set_mat(self.eyes, self.M['eyes'])
        brow = self.mat('brow', 'metal', brow_color, 0.7)
        brow['kind'] = 'brow'
        self.set_mat(self.brows, brow)
        if hide_brows: bpy.data.objects.remove(self.brows)
        fixed = 0
        for o in self.arm.children:
            if o.type != 'MESH' or o == self.body: continue
            gi = {g.index: g.name for g in o.vertex_groups}
            for v in o.data.vertices:
                if sum(g.weight for g in v.groups) < 0.98:
                    for g in list(v.groups): o.vertex_groups[gi[g.group]].remove([v.index])
                    for g, w in self.weights_at(v.co).items():
                        vg = o.vertex_groups.get(g) or o.vertex_groups.new(name=g)
                        vg.add([v.index], w, 'REPLACE')
                    fixed += 1
        print('Gewichte ergänzt:', fixed)
        tris = 0
        for o in self.arm.children:
            if o.type == 'MESH': tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
        print(self.name, 'Dreiecke vor dem Vereinfachen:', tris)
        bpy.ops.wm.save_as_mainfile(filepath=self.out + 'figur.blend')
        open(self.out + 'base', 'w').write('Male' if self.male else 'Female')
        if render_views:
            relaxed_pose(self.arm)
            setup_render((600, 900), 24)
            camera((0.4, -3.6, 1.1), (0, 0, 0.9), 50); render(self.out + 'b_full.png')
            camera((-2.2, 2.8, 1.2), (0, 0, 0.9), 50); render(self.out + 'b_back.png')
