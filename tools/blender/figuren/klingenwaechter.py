"""Klingenwächter (Krieger): Waffenrock in Rot, gravierte Stahlplatten mit Bronzebeschlägen."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy, math, random
from mathutils import Vector
from figurlib import Figur, plane

F = Figur('klingenwaechter', 'male', skin='#dba27c', eye_scale=1.03)
Z, X = F.Z, F.X
F.mat('red', 'cloth', '#8e2a24', 0.85, saum='#c08a45')
F.mat('pants', 'cloth', '#4a3a30', 0.9)
F.mat('steel', 'plate', '#b4bbc1', 0.36, 0.75, saum='#c08a45')
F.mat('steel2', 'plate', '#a2a9b0', 0.4, 0.75, saum='#c08a45')
F.mat('bronze', 'gold', '#c08a45', 0.35, 0.9)
F.mat('leather', 'leather', '#6a4128', 0.6)
F.mat('leather2', 'leather', '#3d281b', 0.6)
F.mat('hair', 'hair', '#5e3d26', 0.55)

# Wams (Gambeson) mit langen Ärmeln
F.garment('Gambeson', [F.hz(0.97), F.hz(1.49, False), F.ax(0.6, 1, False), F.ax(0.6, -1, False)], 'red',
          lambda p: 0.009 + 0.004 * min(1, max(0, Z(1.1) - p.z) / 0.1), rim=0.006, smooth=5, cover=True)
# Brustpanzer
cz = Z(1.42)
F.garment('Cuirass', [F.hz(1.04), F.hz(1.44, False), plane((0.185, 0, cz), (-1, 0, -0.35)), plane((-0.185, 0, cz), (1, 0, -0.35))],
          'steel', lambda p: 0.026 + 0.006 * max(0, min(1, (p.z - Z(1.2)) / 0.15)), rim=0.012, smooth=8, relax=25)
# Halsberge (Kragen)
F.ring('Gorget', 1.44, 1.50, 'steel2', 0.03, rim=0.01, smooth=4)
# Schulterplatten beidseitig
for s in ('l', 'r'):
    F.pauldron(s, ['steel', 'steel2', 'steel'], size=0.088, layers=3, x=0.175, z=1.435, tilt=-30, squash=0.72, thick=0.009)
# Armschienen und Handschuhe
F.sleeve('Vambrace', 0.45, 0.6, 'steel', lambda p: 0.026 + 0.008 * (abs(F.Xi(p.x)) - 0.45) / 0.15, rim=0.01, smooth=3)
F.sleeve('Glove', 0.6, 0.712, 'leather2', 0.005, rim=0.004, smooth=1, cover=False)
F.cover += [([F.ax(0.61, sg), F.ax(0.70, sg, False)], None) for sg in (1, -1)]

# Gürtel, Waffenrock vorne und hinten, Beintaschen
F.ring('Belt', 0.985, 1.04, 'leather2', 0.036, rim=0.012, smooth=2)
F.buckle(1.012, 'bronze', size=(0.06, 0.014, 0.05))
F.pouch(-65, (0.065, 0.04, 0.075), 0.975, 'leather')
F.panel('Tabard', 'red', 1.0, 0.46, 0.105, 0.12, side=-1, lift=0.065, flare=0.03, rows=8)
F.panel('TabardBack', 'red', 1.0, 0.46, 0.11, 0.125, side=1, lift=0.065, flare=0.03, rows=8)
F.skirt('Fauld', 'steel2', 0.99, 0.85, flare=0.03, off=0.045, thick=0.01, cover=False)

# Hose, Stiefel, Beinschienen
F.ring('Pants', 0.3, 1.0, 'pants', lambda p: 0.008 if p.z > Z(0.6) else 0.016, rim=0.004, smooth=3, cover=True)
F.ring('Boots', 0.09, 0.45, 'leather', lambda p: 0.014 + 0.012 * min(1, max(0, p.z - Z(0.12)) / 0.3), rim=0.01, smooth=6)
F.cover.append(([F.hz(0.45, False)], None))
F.shoes('leather', 'leather2')
F.leg_band('Greave', 0.14, 0.47, 'steel', lambda p: 0.034, rim=0.01, smooth=4, front=True)
F.leg_band('Knee', 0.5, 0.6, 'steel2', 0.024, rim=0.008, smooth=4, front=True)

# Haare und Bart
H = F.hair_mesh('Hair_SimpleParted', 'hair')
B = F.hair_mesh('Hair_Beard', 'hair', name='Beard')
F.M['hair']['root'] = (Z(1.62), Z(1.78))

F.finish(brow_color='#4a3020')
