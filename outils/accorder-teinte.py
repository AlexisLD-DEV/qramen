import sys
import numpy as np, cv2
from PIL import Image

def boite_qr(im):
    """Repere le QR : gros amas sombre compact et carre (les modules)."""
    a = np.asarray(im.convert("L"))
    sombre = (a < 145).astype(np.uint8)
    sombre = cv2.morphologyEx(sombre, cv2.MORPH_CLOSE, np.ones((35, 35), np.uint8))
    n, et, st, _ = cv2.connectedComponentsWithStats(sombre, 8)
    best = None
    for i in range(1, n):
        x, y, w, h, aire = [int(v) for v in st[i]]
        if aire < 8000 or h == 0:
            continue
        ratio = w / h
        if 0.72 <= ratio <= 1.38 and (best is None or aire > best[4]):
            best = (x, y, w, h, aire)
    return best[:4] if best else None


def accorder(chemin, sortie, marge=0.06, sigma=70, bande=44, flou=10):
    im = Image.open(chemin).convert("RGB")
    b = boite_qr(im)
    if not b:
        print(chemin, ": QR non trouve")
        return
    x, y, w, h = b
    mx, my = int(w * marge), int(h * marge)
    x0, y0 = max(0, x - mx), max(0, y - my)
    x1, y1 = min(im.width, x + w + mx), min(im.height, y + h + my)
    a = np.asarray(im).astype(np.float32)
    dedans = a[y0:y1, x0:x1].reshape(-1, 3)
    # anneau : bande autour du carre, on exclut le carre lui-meme
    haut = a[max(0, y0 - bande):y0, x0:x1].reshape(-1, 3)
    bas = a[y1:y1 + bande, x0:x1].reshape(-1, 3)
    gauche = a[y0:y1, max(0, x0 - bande):x0].reshape(-1, 3)
    droite = a[y0:y1, x1:x1 + bande].reshape(-1, 3)
    anneau = np.concatenate([p for p in (haut, bas, gauche, droite) if len(p)])
    if not len(anneau):
        print(chemin, ": pas d'anneau")
        return
    delta = np.median(dedans, axis=0) - np.median(anneau, axis=0)
    # reconstruction : le fond du QR reprend la lumiere interpolee des bords (invisible),
    # l'encre (modules sombres) est conservee telle quelle
    h_l, w_l = y1 - y0, x1 - x0
    haut = a[max(0, y0 - bande):y0, x0:x1].mean(axis=0)
    bas = a[y1:y1 + bande, x0:x1].mean(axis=0)
    gauche = a[y0:y1, max(0, x0 - bande):x0].mean(axis=1)
    droite = a[y0:y1, x1:x1 + bande].mean(axis=1)
    v = np.linspace(0, 1, h_l)[:, None, None]
    u = np.linspace(0, 1, w_l)[None, :, None]
    horiz = (1 - v) * haut[None, :, :] + v * bas[None, :, :]
    vert = (1 - u) * gauche[:, None, :] + u * droite[:, None, :]
    lumiere = 0.5 * horiz + 0.5 * vert
    lum = a[y0:y1, x0:x1].mean(axis=2) / 255.0
    neuf = np.zeros_like(a)
    neuf[y0:y1, x0:x1] = lumiere * lum[..., None]
    masque = np.zeros(a.shape[:2], np.float32)
    masque[y0:y1, x0:x1] = 1.0
    masque = cv2.GaussianBlur(masque, (0, 0), flou)[..., None]
    out = np.clip(a * (1 - masque) + neuf * masque + np.random.normal(0, 1.2, a.shape), 0, 255)
    Image.fromarray(out.astype(np.uint8)).save(sortie, quality=93)
    print(chemin, "->", sortie, "| QR", (x, y, w, h), "| ecart initial", np.round(delta, 1))


if __name__ == "__main__":
    for c in sys.argv[1:]:
        accorder(c, c.rsplit(".", 1)[0] + "-accorde.jpg")
