"""Imprime marque + QR + accroche sur la surface d'un objet, en suivant sa perspective."""
import io, pathlib, sys
import numpy as np, cv2, segno
from PIL import Image, ImageDraw, ImageFont

POL = pathlib.Path("/srv/hermes/work/exo-qr/polices")
IMG = pathlib.Path("/srv/projects/shared/qramen/public/assets/img")
SORTIE = pathlib.Path("/srv/hermes/work/exo-qr/mockups")
ENCRIER = (0, 0, 0)
ACCENT_CROC = (123, 45, 38)
ACCENT_RAM = (226, 84, 58)
ACCROCHE = "Scannez pour commander"


def masque_surface(im, frac=(0.03, 0.03, 0.97, 0.97), seuil=150):
    a = np.asarray(im.convert("L")).astype(np.float32)
    hsv = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2HSV)
    sat = hsv[:, :, 1].astype(np.float32)
    h, w = a.shape
    x0, y0, x1, y1 = int(frac[0] * w), int(frac[1] * h), int(frac[2] * w), int(frac[3] * h)
    z, zs = a[y0:y1, x0:x1], sat[y0:y1, x0:x1]
    moy = cv2.blur(z, (11, 11))
    lisse = cv2.blur(np.abs(z - moy), (51, 51))
    # papier/carton : clair, peu sature, peu rugueux (le bois est plus fonce et plus sature)
    m = ((moy > seuil) & (zs < 75) & (lisse < 14)).astype(np.uint8)
    if m.sum() < 40000:
        # 2e passe plus permissive : carton kraft (plus fonce, plus texture)
        m = ((moy > seuil - 35) & (zs < 120) & (lisse < 22)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((11, 11), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    n, et, st, cen = cv2.connectedComponentsWithStats(m, 8)
    if n < 2:
        return None
    i = 1 + int(np.argmax(st[1:, 4]))
    mono = (et == i).astype(np.uint8)
    cnts, _ = cv2.findContours(mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key=cv2.contourArea)
    rect = cv2.minAreaRect(c)
    (cx, cy), (rw, rh), ang = rect
    if rw * rh < 40000:
        return None
    (cx, cy) = (cx + x0, cy + y0)
    boite = cv2.boxPoints(((cx, cy), (rw, rh), ang))
    return boite.astype(np.float32), c + np.array([x0, y0])


def ordonner(pts):
    """Ordonne 4 points en haut-gauche, haut-droit, bas-droit, bas-gauche."""
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)], pts[np.argmax(s)], pts[np.argmax(d)]], dtype=np.float32)


def bloc(famille, largeur, hauteur):
    """Dessine marque + QR + accroche : renvoie (couleur RGB, masque d'encre)."""
    S = 2
    L, H = largeur * S, hauteur * S
    col = Image.new("RGB", (L, H), (255, 255, 255))
    mas = Image.new("L", (L, H), 255)
    dc, dm = ImageDraw.Draw(col), ImageDraw.Draw(mas)
    accent = ACCENT_CROC if famille == "croc" else ACCENT_RAM
    parties = ([("QR", accent), ("oque Monsieur", ENCRIER)] if famille == "croc"
               else [("Le ", ENCRIER), ("QR", accent), ("amen", ENCRIER)])
    texte = "".join(t for t, _ in parties)
    fs = int(H * 0.09)
    f = ImageFont.truetype(str(POL / "Fraunces.ttf"), fs)
    while fs > 12:
        g = dc.textbbox((0, 0), texte, font=f)
        if (g[2] - g[0]) <= L * 0.88:
            break
        fs = int(fs * 0.94)
        f = ImageFont.truetype(str(POL / "Fraunces.ttf"), fs)
    g = dc.textbbox((0, 0), texte, font=f)
    ht_marque = g[3] - g[1]
    fa = ImageFont.truetype(str(POL / "Inter.ttf"), int(H * 0.042))
    ga = dc.textbbox((0, 0), ACCROCHE, font=fa)
    ht_acc = ga[3] - ga[1]
    haut, bas = H * 0.09, H * 0.09
    espace = H * 0.045
    cote = int(min(L * 0.62, H - haut - bas - ht_marque - 2 * espace - ht_acc))
    url = "https://croq.ledeunf.fr/menu.html" if famille == "croc" else "https://qramen.ledeunf.fr/menu.html"
    buf = io.BytesIO()
    segno.make(url, error="h").save(buf, kind="png", scale=20, border=4, dark="#14161A", light=None)
    qr = Image.open(buf).convert("RGBA").resize((cote, cote), Image.LANCZOS)
    # marque : chaque partie dans sa couleur (sur le calque couleur) + noir sur le masque
    cx = (L - (g[2] - g[0])) // 2 - g[0]
    for t, coul in parties:
        gg = dc.textbbox((0, 0), t, font=f)
        dc.text((cx, haut - g[1]), t, font=f, fill=coul)
        dm.text((cx, haut - g[1]), t, font=f, fill=0)
        cx += gg[2] - gg[0]
    qy = int(haut + ht_marque + espace)
    col.paste(qr, (int((L - cote) / 2), qy), qr)
    mas.paste(0, (int((L - cote) / 2), qy), qr.split()[3])
    ty = int(qy + cote + espace - ga[1])
    dc.text(((L - (ga[2] - ga[0])) // 2 - ga[0], ty), ACCROCHE, font=fa, fill=accent)
    dm.text(((L - (ga[2] - ga[0])) // 2 - ga[0], ty), ACCROCHE, font=fa, fill=0)
    return (col.resize((largeur, hauteur), Image.LANCZOS), mas.resize((largeur, hauteur), Image.LANCZOS))


def imprimer(nom, quad=None):
    famille = "croc" if "croc" in nom else "ram"
    im = Image.open(IMG / f"{nom}.png").convert("RGB")
    if quad is None:
        r = masque_surface(im)
        if not r:
            print(nom, ": surface non trouvee")
            return
        boite, _ = r
    else:
        boite = np.array(quad, dtype=np.float32)
    q = ordonner(boite)
    cote_haut = np.linalg.norm(q[1] - q[0])
    cote_bas = np.linalg.norm(q[2] - q[3])
    cote_gauche = np.linalg.norm(q[3] - q[0])
    cote_droit = np.linalg.norm(q[2] - q[1])
    L = int(max(cote_haut, cote_bas))
    H = int(max(cote_gauche, cote_droit))
    # marge : on imprime a l'interieur de la surface, en gardant le quad reel comme cible
    m = 0.10
    centre = q.mean(axis=0)
    dst = (centre + (q - centre) * (1 - 2 * m)).astype(np.float32)
    src = np.array([[0, 0], [L, 0], [L, H], [0, H]], dtype=np.float32)
    calque, masque = bloc(famille, L, H)
    alpha = 1.0 - np.asarray(masque).astype(np.float32) / 255.0
    couleur = np.asarray(calque).astype(np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    a = cv2.warpPerspective(alpha, M, (im.width, im.height), flags=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    c = cv2.warpPerspective(couleur, M, (im.width, im.height), flags=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REPLICATE)
    a = cv2.GaussianBlur(np.clip(a, 0, 1), (3, 3), 0.5)[..., None]
    src_img = np.asarray(im).astype(np.float32)
    # encre quasi opaque : la matiere transparait a peine sous l'impression
    res = src_img * (1 - a * 0.94) + c * (a * 0.94)
    res = np.clip(res + np.random.normal(0, 1.4, res.shape), 0, 255)
    out = Image.fromarray(res.astype(np.uint8))
    SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = SORTIE / f"{nom}-qr.jpg"
    out.save(chemin, quality=93)
    print(nom, "->", chemin)
    return chemin


if __name__ == "__main__":
    # quads reperes a l'oeil sur chaque image (x, y) des 4 coins : haut-gauche, haut-droit, bas-droit, bas-gauche
    QUADS = {
        "support-2-sous-bock": [(430, 215), (1105, 215), (1105, 760), (430, 760)],
        "croc-1-sac": [(172, 192), (806, 190), (800, 878), (176, 880)],
        "croc-2-carte": [(228, 256), (760, 250), (702, 612), (224, 660)],
        "croc-3-boite": [(492, 640), (1246, 640), (1246, 872), (492, 872)],
        "ram-3-boite": [(566, 430), (1412, 548), (1278, 752), (578, 758)],
    }
    for n in sys.argv[1:]:
        imprimer(n, QUADS.get(n))
