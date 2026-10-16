"""Hellere, saubere Hauttextur aus der Quaternius-Körpertextur (Unterwäsche entfernt)."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

Q = os.environ.get('QUATERNIUS', os.path.expanduser('~/quaternius')) + '/textures/'
ARBEIT = os.environ.get('ARBEIT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arbeit'))
OUT = ARBEIT + '/tex/'
os.makedirs(OUT, exist_ok=True)

im = np.asarray(Image.open(Q + 'd366843ee7d9e9f37ec87a0e1c98c7f2e45573c08eeb80a51a6d9344e68cf288.png').convert('RGB').resize((1024, 1024), Image.LANCZOS)).astype(np.float32) / 255
mx, mn = im.max(2), im.min(2)
sat = (mx - mn) / np.maximum(mx, 1e-4)
# Unterwäsche: dunkel und grau
mask = (mx < 0.42) & (sat < 0.45)
mask = ndimage.binary_dilation(mask, iterations=4)
w = (~mask).astype(np.float32)
fill = np.empty_like(im)
for c in range(3):
    num = ndimage.gaussian_filter(im[..., c] * w, 18); den = ndimage.gaussian_filter(w, 18)
    fill[..., c] = num / np.maximum(den, 1e-4)
soft = ndimage.gaussian_filter(mask.astype(np.float32), 3)[..., None]
im = im * (1 - soft) + fill * soft

# Hautton aufhellen: Abweichung vom mittleren Hautton bleibt (Lippen, Wangen), Grundton wird hell-pfirsich
mean = np.array([0.80, 0.55, 0.40], np.float32)   # ungefährer Mittelwert der Vorlage
target = np.array([0.99, 0.80, 0.68], np.float32)
ratio = im / mean
ratio = 1 + (ratio - 1) * np.array([0.6, 0.62, 0.62])
out = np.clip(target * ratio, 0, 1)
# weicher (gemalter) Look: feine Struktur etwas glätten
out = np.stack([ndimage.gaussian_filter(out[..., c], 0.8) for c in range(3)], -1)
Image.fromarray((out * 255).astype(np.uint8)).save(OUT + 'skin.png')
print('skin ok', mask.mean())
