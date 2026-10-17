"""Saubere Hauttextur aus der Quaternius-Körpertextur: Unterwäsche entfernt, Hautton frei wählbar,
leicht weichgezeichnet (halbrealistisch, wie gemalt). Wird von figurlib.Figur aufgerufen."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage


def make_skin(src, out, target='#fccbad', size=1024, keep=0.75, warm=0.0):
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
    if warm:   # etwas dunkler und satter, wie gemalt (für die hellen, flachen MakeHuman-Texturen)
        g = tgt.mean(); tgt = np.clip((g + (tgt - g) * (1 + warm)) * (1 - warm * 0.4), 0, 1)
    ratio = 1 + (im / mean - 1) * keep
    res = np.clip(tgt * ratio, 0, 1)
    res = np.stack([ndimage.gaussian_filter(res[..., c], 0.7) for c in range(3)], -1)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    Image.fromarray((res * 255).astype(np.uint8)).save(out)
    open(out + '.' + t, 'w').close()
    return out


def tint_alpha(src, out, color, keep=0.35):
    """Textur mit Durchsicht (Haar, Brauen, Wimpern) auf eine Farbe umfärben; Helligkeitsverlauf bleibt."""
    im = np.asarray(Image.open(src).convert('RGBA')).astype(np.float32) / 255
    rgb, a = im[..., :3], im[..., 3:]
    lum = rgb @ np.array([0.3, 0.59, 0.11], np.float32)
    m = (lum * a[..., 0]).sum() / max(1e-4, a.sum())
    t = color.lstrip('#'); tgt = np.array([int(t[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
    ratio = 1 + (lum / max(m, 1e-3) - 1) * keep
    res = np.clip(tgt * ratio[..., None], 0, 1)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    Image.fromarray((np.concatenate([res, a], -1) * 255).astype(np.uint8), 'RGBA').save(out)
    return out
