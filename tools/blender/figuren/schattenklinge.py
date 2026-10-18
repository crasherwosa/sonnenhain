"""Schattenklinge (Schurkin): Kapuze und Tunika in tiefem Violett, dunkles Leder, gravierte Silberbeschläge."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, math, random
from mathutils import Vector
from figurlib import Figur, plane

F = Figur('schattenklinge', 'female', skin='#eab894', eye_scale=1.04)
Z = F.Z
F.mat('violet', 'cloth', '#4b2a6b', 0.85, saum='#c9ccd6')
F.mat('hoodm', 'cloth', '#53307a', 0.85, saum='#9a8cb8')
F.mat('maskm', 'wrap', '#2a1c38', 0.95)
F.mat('pants', 'cloth', '#2c2433', 0.9)
F.mat('leather', 'leather', '#3a2a22', 0.55)
F.mat('leather2', 'leather', '#241a16', 0.6)
F.mat('leather3', 'leather', '#5a3f30', 0.58)
F.mat('strap', 'metal', '#3b2b22', 0.65)   # schmale Riemen ohne Naht
F.mat('silver', 'plate', '#c9ccd6', 0.32, 0.85, saum='#8a6fb0')
F.mat('silver2', 'gold', '#d6d8e0', 0.3, 0.9)
F.mat('hair', 'hair', '#2e2236', 0.5)
F.mat('gem', 'glass', '#a77be0', 0.1, 0.1)

# Tunika mit langen Ärmeln (unterste Lage)
F.garment('Tunic', [F.hz(0.93), F.hz(1.48, False), F.ax(0.46, 1, False), F.ax(0.46, -1, False)], 'violet',
          lambda p: 0.009 + 0.006 * min(1, max(0, 1.05 - p.z) / 0.1), rim=0.005, smooth=5, cover=True)
# Lederwams darüber (ohne Ärmel)
F.garment('Jerkin', [F.hz(0.97), F.hz(1.37, False),
                     plane((0.17, 0, 1.40), (-1, 0, -0.35)), plane((-0.17, 0, 1.40), (1, 0, -0.35))],
          'leather', lambda p: 0.022 + 0.003 * max(0, min(1, (p.z - 1.15) / 0.12)) - 0.006 * max(0, min(1, (p.z - 1.3) / 0.07)), rim=0.01, smooth=12)

# Hose, Gürtel mit Silberschnalle, Taschen
def pants_off(p):
    if p.z > 0.8: return 0.008
    return 0.011
F.ring('Pants', 0.3, 1.0, 'pants', pants_off, rim=0.004, smooth=3, cover=True)
F.ring('Belt', 0.975, 1.02, 'leather2', 0.032, rim=0.01, smooth=2)
F.ring('Belt2', 0.935, 0.962, 'leather3', lambda p: 0.026 + 0.01 * max(0, (p.x if p.x > 0 else 0)) / 0.15, rim=0.008, smooth=2)
F.buckle(0.998, 'silver2', size=(0.05, 0.012, 0.04))
F.pouch(58, (0.06, 0.035, 0.07), 0.965, 'leather3')
F.pouch(-58, (0.06, 0.035, 0.07), 0.965, 'leather3')
F.pouch(100, (0.05, 0.03, 0.06), 0.96, 'leather')
# Kurze Rockschöße vorne und hinten
F.panel('TailFront', 'violet', 0.985, 0.26, 0.07, 0.085, side=-1, lift=0.05, flare=0.03, rows=7)
F.panel('TailBack', 'violet', 0.99, 0.32, 0.10, 0.115, side=1, lift=0.05, flare=0.035, rows=8)

# Schlanke Stiefel mit Riemen
F.ring('Boots', 0.09, 0.47, 'leather2', lambda p: 0.01 + 0.012 * min(1, max(0, p.z - 0.12) / 0.3), rim=0.008, smooth=6)
F.cover.append(([F.hz(0.47, False)], None))
F.shoes('leather2', 'leather')
F.ring('BootTop', 0.44, 0.48, 'leather3', 0.026, rim=0.008, smooth=3)
for z0 in (0.22, 0.32):
    F.ring('BootStrap', z0, z0 + 0.016, 'strap', lambda p: 0.017 + 0.012 * min(1, max(0, p.z - 0.12) / 0.3), rim=0.005, smooth=2)

# Oberschenkel: Riemen mit Dolchscheiden außen
for sg in (1, -1):
    for z0 in (0.62, 0.75):
        F.ring('ThighStrap', z0, z0 + 0.02, 'strap', 0.018, rim=0.006, smooth=2, filt=lambda p, sg=sg: p.x * sg > 0.03)
    s = 'l' if sg > 0 else 'r'
    hit = F.BODY.ray_cast(Vector((sg * 0.6, 0.0, 0.69)), Vector((-sg, 0, 0)))[0]
    at = hit + Vector((sg * 0.03, 0.0, 0.0))
    F.box('Sheath', (0.026, 0.045, 0.2), at, 'leather3', bone=f'thigh_{s}', bev=0.008)
    F.box('SheathTip', (0.03, 0.05, 0.03), at + Vector((0, 0, -0.105)), 'silver2', bone=f'thigh_{s}', bev=0.006)
    F.box('SheathHilt', (0.022, 0.022, 0.06), at + Vector((0, 0, 0.13)), 'leather2', bone=f'thigh_{s}', bev=0.006)
    F.box('SheathPommel', (0.03, 0.03, 0.018), at + Vector((0, 0, 0.17)), 'silver2', bone=f'thigh_{s}', bev=0.006)

# Arme: Lederarmschienen mit Silberbändern, Handschuhe
F.sleeve('Bracer', 0.43, 0.6, 'leather', lambda p: 0.016 + 0.01 * (abs(p.x) - 0.43) / 0.17, rim=0.009, smooth=3, cover=True)
for x0 in (0.45, 0.57):
    F.sleeve('BracerBand', x0, x0 + 0.016, 'silver2', lambda p: 0.021 + 0.01 * (abs(p.x) - 0.43) / 0.17, rim=0.005)
F.sleeve('Glove', 0.6, 0.712, 'leather2', 0.004, rim=0.004, smooth=1, cover=False)
F.cover += [([F.ax(0.61, sg), F.ax(0.70, sg, False)], None) for sg in (1, -1)]
F.sleeve('ArmStrap', 0.26, 0.28, 'strap', 0.016, rim=0.006)

# Schulterstück links: kleine gravierte Silberschale über Leder
F.pauldron('l', ['silver', 'leather', 'leather2'], size=0.078, layers=3, z=1.43, tilt=-30, thick=0.007)
# Kapuze und Gesichtstuch
F.frisur('short01', '#2b1d18')   # kurze dunkle Haare unter der Kapuze
hood = F.hood('Hood', 'hoodm', off=0.05, zlow=1.38)
# Kapuze hinten etwas spitz ausziehen (klassische Kapuzenform)
for v in hood.data.vertices:
    t = max(0, min(1, (v.co.z - 1.62) / 0.2)) * max(0, min(1, (v.co.y + 0.02) / 0.12))
    v.co.y += 0.05 * t * t; v.co.z += 0.02 * t * t
F.mask('Mask', 'maskm', z0=1.47, z1=1.605, off=0.008)
F.cover.append(([F.hz(1.40), F.hz(1.50, False)], lambda p: abs(p.x) < 0.12))   # Hals unter der Kapuze

# Brustriemen (über Wams und Kapuze) und zwei Querriemen mit Silberschnallen
F.bandolier('Bandolier', [bpy.data.objects['Jerkin'], bpy.data.objects['Tunic'], bpy.data.objects['Hood']], 'leather3', width=0.036)
# oben unter der Kapuze abschneiden (kein Überstand an der Schulter)
import bmesh
bo = bpy.data.objects['Bandolier']
bm = bmesh.new(); bm.from_mesh(bo.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 1.39], context='VERTS')
bm.to_mesh(bo.data); bm.free()
for z0, bx in ((1.06, 0.06), (1.13, 0.065)):
    F.ring('WaistStrap', z0, z0 + 0.02, 'strap', 0.037, rim=0.006, smooth=2)
    hit = F.ray_body(bx, z0 + 0.01)
    F.box('StrapBuckle', (0.03, 0.01, 0.026), hit + Vector((0, -0.045, 0)), 'silver2', bone='spine_01', bev=0.004)

# Ein paar dunkle Strähnen schauen vorne aus der Kapuze
F.M['hair']['root'] = (1.62, 1.72)
F.long_strands('HairLock', 'hair', [(38, 1.52, 0.022), (322, 1.53, 0.02), (52, 1.56, 0.016)],
               [bpy.data.objects['Hood']], top=1.70, spread=(0.07, 0.02))

# Silberne Spange vorne an der Kapuze
hit = F.ray_body(0, 1.43)
F.gem('HoodGem', 0.012, hit + Vector((0, -0.05, 0)), 'gem', bone='spine_03')

F.finish(brow_color='#2e2236')
