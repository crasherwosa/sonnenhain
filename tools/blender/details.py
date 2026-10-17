"""Gemalte Details für eigene Figuren: Stoffgewebe, Ledermaserung, Nähte, abgenutzte Kanten
und Haarsträhnen. Alles entsteht als Shader in Blender und wird in eine Textur gebacken
(Farbe + Relief), damit das Spiel nur eine Bilddatei pro Teil laden muss."""
import bpy, bmesh
from mathutils.kdtree import KDTree

# Art des Materials -> Muster
KIND = {
    'M_linen': 'cloth', 'M_accent': 'trim', 'M_fur': 'wrap',
    'M_leather': 'leather', 'M_leather2': 'leather', 'M_boot': 'leather',
    'M_brass': 'metal', 'M_steel': 'metal', 'M_lens': 'glass',
    'M_hair': 'hair',
}


def add_edge_attr(o):
    """Abstand jedes Punkts zum nächsten Rand (offene Kante oder scharfe Kante, z. B. am
    Rand dicker Platten) als Attribut 'edge'. Dazu 'wide': 1 für Teile, die breit genug für
    eine Steppnaht sind (schmale Riemen bekommen keine)."""
    bm = bmesh.new(); bm.from_mesh(o.data)
    rim = set()
    for e in bm.edges:
        if e.is_boundary: rim.update(e.verts)
    if not rim:   # geschlossene Teile (Platten, Bahnen mit Dicke): scharfe Kanten zählen als Rand
        for e in bm.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0) > 1.0: rim.update(e.verts)
    a = o.data.attributes.get('edge') or o.data.attributes.new('edge', 'FLOAT', 'POINT')
    w = o.data.attributes.get('wide') or o.data.attributes.new('wide', 'FLOAT', 'POINT')
    if not rim:
        for d in a.data: d.value = 1.0
        for d in w.data: d.value = 1.0
        bm.free(); return
    kd = KDTree(len(rim))
    for i, v in enumerate(rim): kd.insert(v.co, i)
    kd.balance()
    dist = [kd.find(v.co)[2] for v in bm.verts]
    for i, x in enumerate(dist): a.data[i].value = x
    # zusammenhängende Teile: größter Randabstand entscheidet
    seen = set()
    for v in bm.verts:
        if v.index in seen: continue
        isl, stack = [], [v]; seen.add(v.index)
        while stack:
            u = stack.pop(); isl.append(u.index)
            for e in u.link_edges:
                t = e.other_vert(u)
                if t.index not in seen: seen.add(t.index); stack.append(t)
        big = 1.0 if max(dist[i] for i in isl) > 0.011 else 0.0
        for i in isl: w.data[i].value = big
    bm.free()


class N:
    """Kleiner Helfer zum Bauen von Shader-Knoten."""
    def __init__(self, mat):
        self.nt = mat.node_tree; self.L = self.nt.links
    def n(self, typ, **inp):
        node = self.nt.nodes.new(typ)
        for k, v in inp.items():
            if k.startswith('_'): setattr(node, k[1:], v)
            else: node.inputs[k].default_value = v
        return node
    def link(self, a, b): self.L.new(a, b)
    def math(self, op, a, b=None, clamp=False):
        m = self.n('ShaderNodeMath', _operation=op, _use_clamp=clamp)
        for i, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (int, float)): m.inputs[i].default_value = x
            else: self.link(x, m.inputs[i])
        return m.outputs[0]
    def mix(self, fac, a, b):
        m = self.n('ShaderNodeMix', _data_type='RGBA')
        for sock, x in ((m.inputs[0], fac), (m.inputs[6], a), (m.inputs[7], b)):
            if isinstance(x, (int, float)): sock.default_value = x
            elif isinstance(x, tuple): sock.default_value = x
            else: self.link(x, sock)
        return m.outputs[2]
    def band(self, x, lo, hi, soft):
        """1 zwischen lo und hi, weich auslaufend"""
        a = self.n('ShaderNodeMapRange', _interpolation_type='SMOOTHSTEP')
        self.link(x, a.inputs[0]); a.inputs[1].default_value = lo - soft; a.inputs[2].default_value = lo
        b = self.n('ShaderNodeMapRange', _interpolation_type='SMOOTHSTEP')
        self.link(x, b.inputs[0]); b.inputs[1].default_value = hi + soft; b.inputs[2].default_value = hi
        return self.math('MULTIPLY', a.outputs[0], b.outputs[0])


def detail_shader(mat, kind):
    saum = tuple(mat['saum']) + (1,) if 'saum' in mat else None
    """Ersetzt die Grundfarbe durch eine gemusterte Farbe und gibt (farbe, höhe) zurück."""
    g = N(mat)
    b = mat.node_tree.nodes['Principled BSDF']
    base = tuple(b.inputs['Base Color'].default_value)
    tc = g.n('ShaderNodeTexCoord').outputs['Object']
    def scaled(s):
        m = g.n('ShaderNodeMapping'); g.link(tc, m.inputs[0]); m.inputs['Scale'].default_value = s
        return m.outputs[0]
    edge = g.n('ShaderNodeAttribute', _attribute_name='edge').outputs['Fac']
    mott = g.n('ShaderNodeTexNoise', Scale=7.0, Detail=4.0); g.link(tc, mott.inputs['Vector'])
    dark = tuple(c * 0.55 for c in base[:3]) + (1,)
    light = tuple(min(1, c * 1.25 + 0.03) for c in base[:3]) + (1,)
    height = None
    if kind in ('cloth', 'wrap', 'trim'):
        # Leinwandbindung: feine Fäden in zwei Richtungen
        w1 = g.n('ShaderNodeTexWave', _wave_type='BANDS', _bands_direction='X', Scale=420.0, Distortion=0.6); g.link(tc, w1.inputs['Vector'])
        w2 = g.n('ShaderNodeTexWave', _wave_type='BANDS', _bands_direction='Z', Scale=420.0, Distortion=0.6); g.link(tc, w2.inputs['Vector'])
        weave = g.math('MULTIPLY', g.math('ADD', w1.outputs['Fac'], w2.outputs['Fac']), 0.5)
        col = g.mix(g.math('MULTIPLY', weave, 0.04), base, dark)
        col = g.mix(g.math('MULTIPLY', mott.outputs['Fac'], 0.15), col, light)
        height = g.math('MULTIPLY', weave, 0.12)
        if kind == 'wrap':
            # gewickelte Bandagen: breite Lagen schräg um das Bein
            m = scaled((1.0, 1.0, 1.0))
            wv = g.n('ShaderNodeTexWave', _wave_type='BANDS', _bands_direction='Z', Scale=28.0, Distortion=2.0, **{'Detail Scale': 0.5}); g.link(m, wv.inputs['Vector'])
            seam = g.math('POWER', wv.outputs['Fac'], 6.0)
            col = g.mix(g.math('MULTIPLY', seam, 0.5), col, dark)
            height = g.math('SUBTRACT', height, g.math('MULTIPLY', seam, 2.0))
        # Saum: Kante etwas dunkler, Steppnaht 6–8 mm vom Rand
        hem = g.band(edge, -1.0, 0.004, 0.002)
        col = g.mix(g.math('MULTIPLY', hem, 0.35), col, dark)
        stitch_band = g.band(edge, 0.006, 0.009, 0.0008)
        thread = tuple(c * 0.62 for c in base[:3]) + (1,)
        if saum is not None:
            # gewebte Borte am Rand: zwei Töne im Rautenmuster, innen eine feine Linie
            bd = g.band(edge, 0.003, 0.016, 0.0012)
            ck2 = g.n('ShaderNodeTexChecker', Scale=1.0); g.link(scaled((110, 110, 110)), ck2.inputs['Vector'])
            dark_s = tuple(c * 0.6 for c in saum[:3]) + (1,)
            pat = g.mix(ck2.outputs['Fac'], saum, dark_s)
            col = g.mix(bd, col, pat)
            ln = g.band(edge, 0.019, 0.0215, 0.0006)
            col = g.mix(ln, col, saum)
            height = g.math('ADD', height, g.math('MULTIPLY', bd, 0.5))
            stitch_band = g.band(edge, 0.025, 0.028, 0.0006)
        if kind == 'trim':
            # goldene Borte am Rand, Naht innen daneben
            gold = (0.78, 0.52, 0.16, 1)
            tr = g.band(edge, -1.0, 0.0045, 0.001)
            col = g.mix(tr, col, g.mix(g.math('MULTIPLY', weave, 0.3), gold, (0.55, 0.34, 0.1, 1)))
            height = g.math('ADD', height, g.math('MULTIPLY', tr, 0.8))
            stitch_band = g.band(edge, 0.006, 0.009, 0.0006)
            thread = gold
    elif kind == 'leather':
        vor = g.n('ShaderNodeTexVoronoi', Scale=160.0, _feature='DISTANCE_TO_EDGE'); g.link(tc, vor.inputs['Vector'])
        grain = g.n('ShaderNodeMapRange', _interpolation_type='SMOOTHSTEP'); g.link(vor.outputs['Distance'], grain.inputs[0])
        grain.inputs[1].default_value = 0.0; grain.inputs[2].default_value = 0.08
        col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', 1.0, grain.outputs[0]), 0.28), base, dark)
        big = g.n('ShaderNodeTexNoise', Scale=3.0, Detail=6.0, Roughness=0.6); g.link(tc, big.inputs['Vector'])
        col = g.mix(g.math('MULTIPLY', big.outputs['Fac'], 0.45), col, light)
        # abgenutzte, hellere Kanten
        worn = g.band(edge, -1.0, 0.003, 0.002)
        col = g.mix(g.math('MULTIPLY', worn, 0.5), col, light)
        height = grain.outputs[0]
        stitch_band = g.band(edge, 0.0045, 0.0075, 0.0006)
        thread = (0.78, 0.66, 0.46, 1)   # helles Garn
    elif kind in ('hair', 'wood'):
        # Strähnen: Rauschen stark in die Länge gezogen, dunklere Ansätze
        st = g.n('ShaderNodeTexNoise', Scale=1.0, Detail=8.0, Roughness=0.7); g.link(scaled((90, 90, 3)), st.inputs['Vector'])
        cr = g.n('ShaderNodeValToRGB'); g.link(st.outputs['Fac'], cr.inputs[0])
        cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = dark
        cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = light
        col = g.mix(0.6, base, cr.outputs['Color'])
        sep = g.n('ShaderNodeSeparateXYZ'); g.link(tc, sep.inputs[0])
        root = g.n('ShaderNodeMapRange'); g.link(sep.outputs['Z'], root.inputs[0])
        rz = mat.get('root', (1.62, 1.78) if kind == 'hair' else (90.0, 91.0)); root.inputs[1].default_value = rz[0]; root.inputs[2].default_value = rz[1]
        col = g.mix(g.math('MULTIPLY', root.outputs[0], 0.3), col, dark)
        height = st.outputs['Fac']
        stitch_band = None
    elif kind in ('plate', 'gold'):
        # Graviertes Metall: Rankenmuster in der Fläche, Rille und polierte Kante am Rand,
        # bei Platten mit Schmuckfarbe (saum) ein Beschlag am Rand
        wv = g.n('ShaderNodeTexWave', _wave_type='RINGS', Scale=34.0 if kind == 'plate' else 60.0, Distortion=5.0, Detail=3.0, **{'Detail Scale': 1.5}); g.link(tc, wv.inputs['Vector'])
        line = g.band(wv.outputs['Fac'], 0.46, 0.54, 0.03)
        area = g.n('ShaderNodeTexNoise', Scale=6.0, Detail=2.0); g.link(tc, area.inputs['Vector'])
        amask = g.n('ShaderNodeMapRange', _interpolation_type='SMOOTHSTEP'); g.link(area.outputs['Fac'], amask.inputs[0])
        amask.inputs[1].default_value = 0.45; amask.inputs[2].default_value = 0.55
        inner = g.n('ShaderNodeMapRange'); g.link(edge, inner.inputs[0]); inner.inputs[1].default_value = 0.014; inner.inputs[2].default_value = 0.02
        eng = g.math('MULTIPLY', g.math('MULTIPLY', line, amask.outputs[0]), inner.outputs[0])
        col = g.mix(g.math('MULTIPLY', mott.outputs['Fac'], 0.25), base, light)
        col = g.mix(g.math('MULTIPLY', eng, 0.7), col, tuple(c * 0.35 for c in base[:3]) + (1,))
        groove = g.band(edge, 0.009, 0.012, 0.001)
        col = g.mix(g.math('MULTIPLY', groove, 0.8), col, tuple(c * 0.4 for c in base[:3]) + (1,))
        polish = g.band(edge, -1.0, 0.003, 0.002)
        col = g.mix(g.math('MULTIPLY', polish, 0.5), col, (1, 1, 1, 1))
        height = g.math('SUBTRACT', g.math('MULTIPLY', polish, 0.3), g.math('ADD', eng, groove))
        if saum is not None:
            trim = g.band(edge, -1.0, 0.0075, 0.001)
            col = g.mix(trim, col, saum)
            height = g.math('ADD', height, g.math('MULTIPLY', trim, 0.6))
        stitch_band = None
    elif kind == 'fur':
        # Fell: Büschel (Voronoi) und feine Haare, Spitzen heller
        st = g.n('ShaderNodeTexNoise', Scale=1.0, Detail=8.0, Roughness=0.7); g.link(scaled((140, 140, 12)), st.inputs['Vector'])
        vo = g.n('ShaderNodeTexVoronoi', Scale=40.0); g.link(tc, vo.inputs['Vector'])
        cr = g.n('ShaderNodeValToRGB'); g.link(st.outputs['Fac'], cr.inputs[0])
        cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = dark
        cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = light
        col = g.mix(0.7, base, cr.outputs['Color'])
        col = g.mix(g.math('MULTIPLY', vo.outputs['Distance'], 0.6), col, dark)
        height = g.math('ADD', st.outputs['Fac'], g.math('MULTIPLY', vo.outputs['Distance'], -1.0))
        stitch_band = None
    else:   # Metall, Glas: nur leichte Unregelmäßigkeit
        col = g.mix(g.math('MULTIPLY', mott.outputs['Fac'], 0.3), base, dark if kind == 'metal' else light)
        stitch_band = None
    if stitch_band is not None:
        # Stiche: kurze Striche entlang der Naht
        ck = g.n('ShaderNodeTexChecker', Scale=1.0); g.link(scaled((150, 150, 150)), ck.inputs['Vector'])
        dash = ck.outputs['Fac']
        wide = g.n('ShaderNodeAttribute', _attribute_name='wide').outputs['Fac']
        st = g.math('MULTIPLY', g.math('MULTIPLY', stitch_band, dash), wide)
        col = g.mix(st, col, thread)
        height = g.math('ADD', height, g.math('MULTIPLY', st, 1.5)) if height is not None else st
    g.link(col, b.inputs['Base Color'])
    return col, height


def bake_details(o, size, normal_size=None):
    """Neue UV-Abwicklung, Farbe (und Relief) aller Materialien in eine Textur backen.
    Danach zeigen alle Materialien des Objekts auf diese Textur."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 4
    me = o.data
    uv = me.uv_layers.new(name='Bake'); me.uv_layers.active = uv
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.004, area_weight=0.0, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new(o.name + '_farbe', size, size, alpha=False)
    nimg = bpy.data.images.new(o.name + '_relief', normal_size, normal_size, alpha=False) if normal_size else None
    if nimg: nimg.colorspace_settings.name = 'Non-Color'
    heights = {}
    kinds = {}
    keep = {}
    for i, m in enumerate(me.materials):   # eigene Kopie: dasselbe Material kann in mehreren Teilen stecken
        c = m.copy(); c.name = o.name + '_' + m.name; me.materials[i] = c; kinds[c.name] = m.get('kind') or KIND.get(m.name, 'metal')
    for m in me.materials:
        b = m.node_tree.nodes['Principled BSDF']
        keep[m.name] = (b.inputs['Roughness'].default_value, b.inputs['Metallic'].default_value)
        b.inputs['Metallic'].default_value = 0.0   # sonst backt Metall als Schwarz
        col, h = detail_shader(m, kinds[m.name])
        heights[m.name] = h
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img; t.name = 'BAKE'
        uvn = m.node_tree.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'Bake'; m.node_tree.links.new(uvn.outputs[0], t.inputs[0])
        m.node_tree.nodes.active = t
    sc.render.bake.use_pass_direct = False; sc.render.bake.use_pass_indirect = False; sc.render.bake.use_pass_color = True
    sc.render.bake.margin = 6
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
    if nimg:
        for m in me.materials:
            h = heights[m.name]
            b = m.node_tree.nodes['Principled BSDF']
            if h is not None:
                bump = m.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35
                bump.inputs['Distance'].default_value = 0.002
                m.node_tree.links.new(h, bump.inputs['Height']); m.node_tree.links.new(bump.outputs['Normal'], b.inputs['Normal'])
            m.node_tree.nodes['BAKE'].image = nimg
        sc.render.bake.normal_space = 'TANGENT'
        bpy.ops.object.bake(type='NORMAL')
    # Materialien neu: Farbe (und Relief) aus den gebackenen Bildern
    for m in me.materials:
        rough, metal = keep[m.name]
        m.node_tree.nodes.clear()
        out = m.node_tree.nodes.new('ShaderNodeOutputMaterial')
        p = m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metal
        m.node_tree.links.new(p.outputs[0], out.inputs[0])
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img
        m.node_tree.links.new(t.outputs['Color'], p.inputs['Base Color'])
        if nimg:
            tn = m.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = nimg
            nm = m.node_tree.nodes.new('ShaderNodeNormalMap')
            m.node_tree.links.new(tn.outputs['Color'], nm.inputs['Color']); m.node_tree.links.new(nm.outputs[0], p.inputs['Normal'])
    # nur die neue Abwicklung behalten (wird TEXCOORD_0)
    for l in list(me.uv_layers):
        if l.name != 'Bake': me.uv_layers.remove(l)
    img.pack()
    if nimg: nimg.pack()
    return img, nimg
