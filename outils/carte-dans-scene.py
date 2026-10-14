"""Fait ma propre carte (creme, typo exacte, QR net) et l'insere dans une scene photo a la place de celle du modele."""
import io, pathlib, sys
import numpy as np, cv2, segno
from PIL import Image, ImageDraw, ImageFont, ImageFilter

POL = pathlib.Path("/srv/hermes/work/exo-qr/polices")
IMG = pathlib.Path("/srv/projects/shared/qramen/public/assets/img")
SORTIE = pathlib.Path("/srv/hermes/work/exo-qr/mockups")
CREME = (246, 241, 231)
ENCRIER = (28, 30, 34)
ACCROCHE = "Scannez pour commander"


def ma_carte(famille, largeur=1040, hauteur=1420):
    """Carte creme : marque, QR, accroche. Rendu net, aucune zone blanche rapporte."""
    accent = (123, 45, 38) if famille == "croc" else (226, 84, 58)
    parties = ([("QR", accent), ("oque Monsieur", ENCRIER)] if famille == "croc"
               else [("Le ", ENCRIER), ("QR", accent), ("amen", ENCRIER)])
    carte = Image.new("RGB", (largeur, hauteur), CREME)
    # grain de papier
    bruit = np.random.normal(0, 2.2, (hauteur, largeur, 1))
    fin = cv2.GaussianBlur(np.random.normal(0, 1.4, (hauteur, largeur, 1)).astype(np.float32), (0, 0), 2)
    arr = np.clip(np.asarray(carte).astype(np.float32) + bruit + fin[..., None], 0, 255)
    carte = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(carte)
    texte = "".join(t for t, _ in parties)
    fs = int(hauteur * 0.075)
    f = ImageFont.truetype(str(POL / "Fraunces.ttf"), fs)
    while fs > 12:
        g = d.textbbox((0, 0), texte, font=f)
        if (g[2] - g[0]) <= largeur * 0.82:
            break
        fs = int(fs * 0.95)
        f = ImageFont.truetype(str(POL / "Fraunces.ttf"), fs)
    g = d.textbbox((0, 0), texte, font=f)
    cx = (largeur - (g[2] - g[0])) // 2 - g[0]
    for t, coul in parties:
        gg = d.textbbox((0, 0), t, font=f)
        d.text((cx, hauteur * 0.075), t, font=f, fill=coul)
        cx += gg[2] - gg[0]
    url = "https://croq.alexisld.fr/menu.html" if famille == "croc" else "https://qramen.alexisld.fr/menu.html"
    buf = io.BytesIO()
    segno.make(url, error="h").save(buf, kind="png", scale=22, border=4, dark="#1c1e22", light=None)
    qr = Image.open(buf).convert("RGBA")
    cote = int(largeur * 0.52)
    qr = qr.resize((cote, cote), Image.LANCZOS)
    qy = int(hauteur * 0.30)
    carte.paste(qr, ((largeur - cote) // 2, qy), qr)
    fa = ImageFont.truetype(str(POL / "Inter.ttf"), int(hauteur * 0.032))
    ga = d.textbbox((0, 0), ACCROCHE, font=fa)
    d.text(((largeur - (ga[2] - ga[0])) // 2 - ga[0], qy + cote + int(hauteur * 0.045)), ACCROCHE, font=fa, fill=accent)
    return carte


def inserer(scene, famille, quad, sortie, rayon=26):
    im = Image.open(IMG / scene).convert("RGB")
    q = np.array(quad, dtype=np.float32)
    haut = np.linalg.norm(q[1] - q[0])
    bas = np.linalg.norm(q[2] - q[3])
    gauche = np.linalg.norm(q[3] - q[0])
    droite = np.linalg.norm(q[2] - q[1])
    L, H = int(max(haut, bas)), int(max(gauche, droite))
    carte = ma_carte(famille, L * 2, H * 2).resize((L, H), Image.LANCZOS)
    # ombre portee douce sous la carte
    a = np.asarray(im).astype(np.float32)
    ombre = np.zeros(a.shape[:2], np.float32)
    m = np.zeros((H, L), np.float32)
    cv2.fillConvexPoly(m, np.array([[0, 0], [L - 1, 0], [L - 1, H - 1], [0, H - 1]], np.int32), 1.0)
    Ms = cv2.getPerspectiveTransform(np.array([[0, 0], [L - 1, 0], [L - 1, H - 1], [0, H - 1]], np.float32), q)
    cv2.warpPerspective(m, Ms, (im.width, im.height), dst=ombre)
    ombre = cv2.GaussianBlur(ombre, (0, 0), 18)
    a = a * (1 - np.clip(ombre, 0, 1)[..., None] * 0.35)
    # carte
    M = cv2.getPerspectiveTransform(np.array([[0, 0], [L - 1, 0], [L - 1, H - 1], [0, H - 1]], np.float32), q)
    c = cv2.warpPerspective(np.asarray(carte), M, (im.width, im.height), flags=cv2.INTER_LANCZOS4)
    masque = np.zeros(a.shape[:2], np.float32)
    cv2.fillConvexPoly(masque, np.int32(q), 1.0)
    masque = cv2.GaussianBlur(masque, (0, 0), 0.8)[..., None]
    out = np.clip(a * (1 - masque) + c * masque, 0, 255)
    Image.fromarray(out.astype(np.uint8)).save(SORTIE / sortie, quality=94)
    print(scene, "->", SORTIE / sortie)


if __name__ == "__main__":
    inserer("support-croque.png", "croc", [(170, 92), (644, 90), (644, 714), (170, 716)], "carte-croque-scene.jpg")
    inserer("support-ramen.png", "ram", [(156, 96), (689, 96), (689, 729), (156, 729)], "carte-ramen-scene.jpg")
