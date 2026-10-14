"""Génère un PDF unique avec les planches A4 et les chevalets comptoir QRoque."""
import base64
import io
import json
import pathlib
import urllib.request

import segno

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "public/assets"
CLE = pathlib.Path("/srv/hermes/.hermes/.secrets/qramen-pdf.key").read_text().strip()
DOMAINE = "https://qroque.alexisld.fr"
SORTIE = ASSETS / "chevalets-qroque.pdf"
MASCOTTE = base64.b64encode((ASSETS / "mascottes/croque-2-monsieur-print.png").read_bytes()).decode()


def qr(url):
    buf = io.BytesIO()
    segno.make(url, error="h").save(buf, kind="png", scale=12, border=4, dark="#14161A")
    return base64.b64encode(buf.getvalue()).decode()


def carte(numero, format_):
    code = qr(f"{DOMAINE}/menu.html?table=T{numero:02d}")
    return f'''<article class="carte {format_}">
      <img class="mascotte" src="data:image/png;base64,{MASCOTTE}" alt="Mascotte QRoque Monsieur">
      <img class="qr" src="data:image/png;base64,{code}" alt="">
      <div class="action">Scannez pour commander</div>
      <div class="pied">Table T{numero:02d}<br>14 rue du Gros-Horloge, 76000 Rouen</div>
    </article>'''


STYLE = '''@page{size:A4 portrait;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:#14161a}
.page{position:relative;width:210mm;height:297mm;padding:10mm 5mm 5mm;display:flex;flex-wrap:wrap;gap:3mm;align-content:flex-start;page-break-after:always}
.page:last-child{page-break-after:auto}.titre{position:absolute;top:3mm;left:5mm;font-size:2.8mm;font-weight:bold;letter-spacing:.3mm;color:#625d54}
.carte{border:.35mm dashed #8a8277;border-radius:2mm;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;overflow:hidden}
.carte.a6{width:97mm;height:132mm;padding:4mm}.carte.a5{width:148mm;height:210mm;padding:7mm;margin:auto}
.mascotte{width:24mm;height:24mm;object-fit:contain;margin-bottom:1mm;mix-blend-mode:multiply}.a5 .mascotte{width:33mm;height:33mm;margin-bottom:2mm}
.qr{width:45mm;height:45mm;image-rendering:pixelated}.a5 .qr{width:62mm;height:62mm}
.action{font-size:4mm;color:#7B2D26;font-weight:bold;margin-top:2mm}.a5 .action{font-size:5mm;margin-top:3mm}
.pied{font-size:2.8mm;color:#625d54;line-height:1.35;margin-top:1.5mm}.a5 .pied{font-size:3.4mm;margin-top:2mm}'''


def page(cards, titre):
    return f'<section class="page"><div class="titre">{titre}</div>{"".join(cards)}</section>'


pages = [page([carte(n, "a6") for n in range(start, min(start + 4, 8))],
              "A4 · IMPRESSION MAISON · 4 CHEVALETS PAR FEUILLE · DÉCOUPER SUR LES POINTILLÉS")
         for start in range(1, 8, 4)]
pages.extend(page([carte(n, "a5")], "COMPTOIR · FORMAT A5 · 1 CHEVALET PAR FEUILLE") for n in range(1, 8))
html = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>' + STYLE + '</style></head><body>' + ''.join(pages) + '</body></html>'
request = urllib.request.Request(
    "http://172.19.0.1:8798/pdf?json=1",
    data=json.dumps({"html": html, "nom": "chevalets-qroque", "format": "A4"}).encode(),
    headers={"Content-Type": "application/json", "X-PDF-Key": CLE})
response = json.load(urllib.request.urlopen(request, timeout=180))
SORTIE.write_bytes(base64.b64decode(response["base64"]))
print(SORTIE, SORTIE.stat().st_size, "octets")
