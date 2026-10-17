"""Saubere Hauttextur aus der Quaternius-Körpertextur: Unterwäsche entfernt, Hautton frei wählbar,
leicht weichgezeichnet (halbrealistisch, wie gemalt). Wird von figurlib.Figur aufgerufen."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage


def make_skin(src, out, target='#fccbad', size=1024, keep=0.75):
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(__file__) and os.path.exists(out + '.' + target.lstrip('#')):
        return out
    im = np.asarray(Image.open(src).convert('RGB').resize((size, size), Image.LANCZOS)).astype(np.float32) / 255
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
    # Hautton: Abweichungen vom mittleren Ton (Lippen, Wangen, Schatten) bleiben, der Grundton wird target
    skin = im[(~mask) & (mx > 0.2)]
    mean = np.median(skin, 0)
    t = target.lstrip('#'); tgt = np.array([int(t[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
    ratio = 1 + (im / mean - 1) * keep
    res = np.clip(tgt * ratio, 0, 1)
    res = np.stack([ndimage.gaussian_filter(res[..., c], 0.7) for c in range(3)], -1)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    Image.fromarray((res * 255).astype(np.uint8)).save(out)
    open(out + '.' + t, 'w').close()
    return out
