#!/usr/bin/env python3
"""Planche unique Excalidraw (v2) : textes d'etape separes (plus de chevauchement), titre cale."""
import json, pathlib

SORTIE = pathlib.Path("/srv/projects/shared/qramen/docs/excalidraw")
SORTIE.mkdir(parents=True, exist_ok=True)
INK, GRIS = "#1e1e1e", "#757575"

def mot(i, x, y, texte, police=28, couleur=INK, centre=None):
    lignes = texte.split("\n")
    larg = max(60, int(len(max(lignes, key=len)) * police * 0.62))
    haut = int(police * 1.3 * len(lignes))
    if centre is not None:
        x = centre - larg / 2
    return {"type": "text", "id": i, "x": x, "y": y, "text": texte, "fontSize": police,
            "fontFamily": 1, "strokeColor": couleur, "originalText": texte, "autoResize": True,
            "width": larg, "height": haut}

def boite(i, x, y, w, h, texte, fond, police=16, arrondi=3):
    tid = "t_" + i
    return [
        {"type": "rectangle", "id": i, "x": x, "y": y, "width": w, "height": h,
         "roundness": {"type": arrondi}, "backgroundColor": fond, "fillStyle": "solid",
         "boundElements": [{"id": tid, "type": "text"}]},
        {"type": "text", "id": tid, "x": x + 10, "y": y + h / 2 - police * 0.7, "width": w - 20,
         "height": police * 1.3 * (texte.count("\n") + 1), "text": texte, "fontSize": police, "fontFamily": 1,
         "strokeColor": INK, "textAlign": "center", "verticalAlign": "middle",
         "containerId": i, "originalText": texte, "autoResize": True},
    ]

def fleche(i, x1, y1, x2, y2):
    return {"type": "arrow", "id": i, "x": x1, "y": y1, "width": abs(x2 - x1), "height": abs(y2 - y1),
            "points": [[0, 0], [x2 - x1, y2 - y1]], "endArrowhead": "arrow"}

e = []
e.append(mot("titre", 80, 120, "QRoque Monsieur — commander à table par QR code", 30))
e.append(mot("sous", 80, 168, "Un exercice de formation, poussé jusqu'au site en ligne", 18, GRIS))

etapes = [
    ("e1", "1. Je scanne", "le QR posé sur la table", "#ffd8a8"),
    ("e2", "2. Le menu s'ouvre", "dans le navigateur, sans appli", "#a5d8ff"),
    ("e3", "3. J'envoie", "le panier part en cuisine", "#d0bfff"),
    ("e4", "4. On me sert", "l'addition arrive en un clic", "#b2f2bb"),
]
x = 80
for i, (bid, titre, sous, fond) in enumerate(etapes):
    e += boite(bid, x, 240, 270, 80, titre, fond, 17)
    e.append(mot("s_" + bid, x + 20, 330, sous, 14, GRIS))
    if i:
        e.append(fleche("f" + bid, x - 48, 280, x - 14, 280))
    x += 315

e.append(mot("lmeca", 80, 400, "Ce qui tourne derrière", 22))
meca = [
    ("m1", "Page du site\nHTML·CSS·JS", "#ffffff"),
    ("m2", "n8n auto-hébergé\nla logique", "#d0bfff"),
    ("m3", "Airtable\nla base", "#c3fae8"),
    ("m4", "Chrome headless\nles PDF", "#fff3bf"),
    ("m5", "Caddy + Cloudflare\nle domaine", "#ffffff"),
]
x = 80
for bid, texte, fond in meca:
    e += boite(bid, x, 440, 220, 86, texte, fond, 15)
    x += 245

e += boite("r1", 80, 570, 1150, 84, "EN LIGNE · qramen.alexisld.fr/menu.html    CODE PUBLIC · github.com/AlexisLD-DEV/qramen", "#b2f2bb", 17)

chiffres = [
    ("c1", "2 cartes\nramen et croques", "#a5d8ff"),
    ("c2", "7 tables\nune carte QR chacune", "#ffd8a8"),
    ("c3", "16 visuels\ngénérés pour les plats", "#ffc9c9"),
    ("c4", "2 PDF\nticket et addition", "#fff3bf"),
]
x = 80
for bid, texte, fond in chiffres:
    e += boite(bid, x, 690, 270, 86, texte, fond, 15)
    x += 295
e.append(mot("pied", 80, 810, "Le ticket cuisine et l'addition se génèrent en PDF et se rangent tout seuls dans la base.", 15, GRIS))

scene = {"type": "excalidraw", "version": 2, "source": "hermes-agent", "elements": e,
         "appState": {"viewBackgroundColor": "#ffffff"}}
(SORTIE / "qroque-une-page.excalidraw").write_text(json.dumps(scene, ensure_ascii=False, indent=1))
print("ecrit :", SORTIE / "qroque-une-page.excalidraw", "|", len(e), "elements")
