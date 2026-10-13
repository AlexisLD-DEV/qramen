import sys
import numpy as np, cv2
from PIL import Image

def carre_du_qr(im):
    """Trouve le carre blanc qui contient reellement un QR (densite de modules sombres)."""
    a = np.asarray(im.convert("L"))
    blanc = (a > 246).astype(np.uint8)
    blanc = cv2.morphologyEx(blanc, cv2.MORPH_CLOSE, np.ones((51, 51), np.uint8))
    n, e, st, _ = cv2.connectedComponentsWithStats(blanc, 8)
    candidats = []
    for i in range(1, n):
        x, y, w, h, aire = [int(v) for v in st[i]]
        if aire < 20000 or w < 80 or h < 80:
            continue
        ratio = w / max(h, 1)
        if not (0.6 <= ratio <= 1.7):
            continue
        z = a[y:y + h, x:x + w]
        densite = float((z < 110).mean())
        if 0.12 <= densite <= 0.55:
            candidats.append((aire, x, y, w, h, densite))
    if not candidats:
        return None
    candidats.sort(reverse=True)
    return candidats[0][1:5]


def recoller(chemin, sortie, bande=14, flou=8):
    im = Image.open(chemin).convert("RGB")
    b = carre_du_qr(im)
    if not b:
        print(chemin, ": carre du QR non trouve")
        return
    px, py, pw, ph = b
    a = np.asarray(im).astype(np.float32)
    h_im, w_im = a.shape[:2]
    haut = np.median(a[max(0, py - bande):max(1, py - 2), px:px + pw], axis=0)
    bas = np.median(a[min(h_im - 1, py + ph + 2):min(h_im, py + ph + bande), px:px + pw], axis=0)
    if haut.ndim != 2 or haut.shape[0] != pw:
        haut = np.repeat(np.median(a[max(0, py - 3):max(1, py - 1), px:px + pw], axis=0, keepdims=True), pw, axis=0)
    if bas.ndim != 2 or bas.shape[0] != pw:
        bas = np.repeat(np.median(a[min(h_im - 1, py + ph + 1):min(h_im, py + ph + 2), px:px + pw], axis=0, keepdims=True), pw, axis=0)
    v = np.linspace(0, 1, ph)[:, None, None]
    fond = (1 - v) * haut[None, :, :] + v * bas[None, :, :]
    lum = a[py:py + ph, px:px + pw].mean(axis=2) / 255.0
    neuf = np.zeros_like(a)
    neuf[py:py + ph, px:px + pw] = fond * lum[..., None]
    masque = np.zeros(a.shape[:2], np.float32)
    masque[py:py + ph, px:px + pw] = 1.0
    masque = cv2.GaussianBlur(masque, (0, 0), flou)[..., None]
    out = np.clip(a * (1 - masque) + neuf * masque + np.random.normal(0, 1.1, a.shape), 0, 255)
    Image.fromarray(out.astype(np.uint8)).save(sortie, quality=94)
    print(chemin, "->", sortie, "| carre", (px, py, pw, ph))


if __name__ == "__main__":
    for c in sys.argv[1:]:
        recoller(c, c.rsplit(".", 1)[0] + "-recolle.jpg")
