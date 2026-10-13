import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pathlib

IMG = pathlib.Path("/srv/projects/shared/qramen/public/assets/img")
MOCK = pathlib.Path("/srv/hermes/work/exo-qr/mockups")
POL = pathlib.Path("/srv/hermes/work/exo-qr/polices")
QR = "/srv/hermes/work/exo-qr/qr-croq.png"
ENCRIER = (34, 36, 40)
ACCENT = (123, 45, 38)
ACCROCHE = "Scannez pour commander"
import cv2

def blanc(im, frac):
    """Plus grande zone blanche unie dans une zone d'interet -> (x, y, w, h, aire)."""
    a = np.asarray(im.convert("L"))
    h, w = a.shape
    x0, y0, x1, y1 = int(frac[0] * w), int(frac[1] * h), int(frac[2] * w), int(frac[3] * h)
    z = a[y0:y1, x0:x1]
    masque = (z > 242).astype(np.uint8)
    nb, etiq, stats, _ = cv2.connectedComponentsWithStats(masque, 8)
    if nb < 2:
        return None
    i = 1 + int(np.argmax(stats[1:, 4]))
    x, y, ww, hh, aire = stats[i]
    if aire < 3000:
        return None
    return (x0 + x, y0 + y, int(ww), int(hh), int(aire))


def encrer(im, box, marque=("Le ", "QR", "amen")):
    """Dessine la marque + le QR + l'accroche en encrage multiplicatif (rendu imprime)."""
    x, y, w, h, _ = box
    S = 3
    calque = Image.new("L", (w * S, h * S), 255)
    d = ImageDraw.Draw(calque)
    fs = int(h * S * 0.115)
    f = ImageFont.truetype(str(POL / "Fraunces.ttf"), fs)
    largeur = sum(d.textbbox((0, 0), t, font=f)[2] - d.textbbox((0, 0), t, font=f)[0] for t in marque if t)
    while fs > 10 and largeur > w * S * 0.84:
        fs = int(fs * 0.93)
        f = ImageFont.truetype(str(POL / "Fraunces.ttf"), fs)
        largeur = sum(d.textbbox((0, 0), t, font=f)[2] - d.textbbox((0, 0), t, font=f)[0] for t in marque if t)
    yb = int(h * S * 0.085)
    cx = w * S // 2 - largeur // 2
    for t in marque:
        if not t:
            continue
        gg = d.textbbox((0, 0), t, font=f)
        d.text((cx - gg[0], yb), t, font=f, fill=0)
        cx += gg[2] - gg[0]
    fa = ImageFont.truetype(str(POL / "Inter.ttf"), int(h * S * 0.062))
    ga = d.textbbox((0, 0), ACCROCHE, font=fa)
    hauteur_texte = ga[3] - ga[1]
    dispo = h * S * 0.97 - yb - (fs * 1.15) - hauteur_texte
    qg = int(min(w * S * 0.60, dispo))
    qr = Image.open(QR).convert("L").resize((qg, qg), Image.LANCZOS)
    qx = (w * S - qg) // 2
    qy = int(h * S * 0.085 + fs * 1.25)
    calque.paste(qr, (qx, qy))
    ty = qy + qg + int(h * S * 0.045)
    d.text((w * S // 2 - (ga[2] - ga[0]) // 2, ty), ACCROCHE, font=fa, fill=0)
    calque = calque.resize((w, h), Image.LANCZOS)
    tinta = np.clip(np.asarray(calque).astype(np.float32) / 255.0, 0, 1)
    orig = np.asarray(im).astype(np.float32)
    zone = orig[y:y + h, x:x + w]
    # on garde le blanc du panneau (zone imprimee) : pas de teinte, juste l'encre + le grain
    resultat = zone * tinta[..., None]
    grain = np.random.normal(0, 2.4, resultat.shape)
    resultat = np.clip(resultat + grain, 0, 255)
    orig[y:y + h, x:x + w] = resultat
    return Image.fromarray(orig.astype(np.uint8))


if __name__ == "__main__":
    import sys
    for nom in sys.argv[1:]:
        im = Image.open(IMG / f"{nom}.png").convert("RGB")
        b = blanc(im, (0.12, 0.08, 0.88, 0.92))
        print(nom, "-> panneau", b)
        if not b:
            continue
        marque = ("QR", "oque Monsieur") if nom.startswith("croque") else ("Le ", "QR", "amen")
        out = encrer(im, b, marque)
        chemin = MOCK / f"{nom}-propre.jpg"
        out.save(chemin, quality=92)
        print("  ecrit", chemin)