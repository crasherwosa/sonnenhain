"""Sternenweberin (Magierin): blonde Abenteurerin in Creme und Türkis, Leder und graviertem Gold."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, math, random
from mathutils import Vector
from figurlib import Figur, plane

F = Figur('sternenweberin', 'female', skin='#f0bd9a', eye_scale=1.05)
Z = F.Z
F.mat('linen', 'cloth', '#efe5cf', 0.9, saum='#2f837f')
F.mat('linen2', 'cloth', '#e8dcc2', 0.9)
F.mat('accent', 'trim', '#2f837f', 0.85)
F.mat('leather', 'leather', '#8e5230', 0.6)
F.mat('leather2', 'leather', '#4f2f1e', 0.58)
F.mat('boot', 'leather', '#64391f', 0.55)
F.mat('gold', 'gold', '#e2b45c', 0.3, 0.9)
F.mat('fur', 'wrap', '#ece0c6', 0.95)
F.mat('hair', 'hair', '#f4d27e', 0.5)
F.mat('gem', 'glass', '#5fe0d2', 0.1, 0.1)

# Oberteil und Korsett
F.garment('Top', [F.hz(1.17), plane((0, -0.1, 1.375), (0, 0.5, -1)), F.hz(1.415, False),
                  plane((0.165, 0, 1.42), (-1, 0, -0.35)), plane((-0.165, 0, 1.42), (1, 0, -0.35))],
          'linen', lambda p: 0.008 + 0.012 * min(1, max(0, 1.23 - p.z) / 0.06), smooth=6, cover=True)
F.ring('Corset', 1.155, 1.235, 'leather', lambda p: 0.02 + 0.008 * max(0, 1.2 - p.z) / 0.045, rim=0.008, smooth=4, cover=True)

# Hose, Gürtel, Taschen, Stoffbahnen vorne und hinten
def pants_off(p):
    if p.z > 0.8: return 0.009
    if p.z > 0.55: return 0.009 + 0.018 * (0.8 - p.z) / 0.25
    return 0.027 - 0.01 * min(1, (0.55 - p.z) / 0.2)
F.ring('Pants', 0.26, 1.07, 'linen2', pants_off, rim=0.005, smooth=3, cover=True)
F.ring('Belt', 0.99, 1.035, 'leather2', 0.02, rim=0.012, smooth=2)
F.buckle(1.012, 'gold')
F.pouch(62, (0.075, 0.04, 0.085), 0.975, 'leather')
F.pouch(-70, (0.06, 0.035, 0.07), 0.975, 'leather')
F.panel('Tabard', 'accent', 0.995, 0.215, 0.075, 0.063, side=-1, lift=0.032, flare=0.02)
F.panel('Panel', 'linen', 1.0, 0.36, 0.11, 0.13, side=1, lift=0.03, flare=0.03, rows=8)

# Stiefel mit Stoffstulpen
F.ring('Boots', 0.09, 0.44, 'boot', lambda p: 0.012 + 0.016 * min(1, max(0, p.z - 0.12) / 0.28), rim=0.01, smooth=6)
F.cover.append(([F.hz(0.44, False)], None))
F.shoes('boot', 'leather2')
F.ring('Cuff', 0.40, 0.50, 'fur', lambda p: 0.048 - 0.016 * abs(p.z - 0.45) / 0.05, rim=0.012, smooth=6, cover=True)
for z0 in (0.425, 0.462):
    F.ring('CuffStrap', z0, z0 + 0.014, 'leather2', 0.052, rim=0.006, smooth=2)

# Arme: Armschienen mit Goldband, Riemen, Handschuhe; Oberschenkelriemen
F.sleeve('Bracer', 0.44, 0.61, 'leather', lambda p: 0.012 + 0.01 * (abs(p.x) - 0.44) / 0.17, rim=0.01, smooth=3, cover=True)
F.sleeve('BracerGold', 0.545, 0.565, 'gold', lambda p: 0.026 + 0.01 * 0.105 / 0.17, rim=0.006)
F.sleeve('BracerStrap', 0.47, 0.488, 'leather2', 0.029, rim=0.006)
F.sleeve('ArmStrap', 0.27, 0.295, 'leather2', 0.007, rim=0.006)
F.sleeve('Glove', 0.612, 0.712, 'leather2', 0.004, rim=0.004, smooth=1)
F.cover += [([F.ax(0.62, sg), F.ax(0.70, sg, False)], None) for sg in (1, -1)]
for sg in (1, -1):
    F.ring('ThighStrap', 0.70, 0.725, 'leather2', lambda p: pants_off(p) + 0.007, rim=0.008, smooth=2, filt=lambda p, sg=sg: p.x * sg > 0.03)

# Schulterstück links: gravierte Goldschale über zwei Lederlagen
F.pauldron('l', ['gold', 'leather', 'leather2'])
F.ring('Choker', 1.505, 1.528, 'leather2', 0.004, rim=0.004)
import bpy
F.bandolier('Bandolier', [bpy.data.objects['Top'], bpy.data.objects['Corset']], 'leather')

# Haare: lange Strähnen mit Durchsicht (MakeHuman long01), blond
H = F.frisur('long01', '#e9c46e')

# Goldreif mit türkisem Stein statt Brille
ring, bv = F.circlet('KopfReif', 'gold', z=1.712, width=0.007, front_up=0.012, extra=[H])
hit = bv.ray_cast(Vector((0, -0.5, Z(1.712) - 0.012 + 0.006)), Vector((0, 1, 0)))[0]
F.gem('KopfStein', 0.011, hit + Vector((0, -0.01, 0)), 'gem')

F.finish(brow_color='#b5874a')
