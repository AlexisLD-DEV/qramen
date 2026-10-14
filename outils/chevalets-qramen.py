"""Génère les chevalets A5 QRamen avec QR haute définition et mascotte vectorielle."""
import base64
import io
import json
import pathlib
import urllib.request
import segno

CLE = pathlib.Path("/srv/hermes/.hermes/.secrets/qramen-pdf.key").read_text().strip()
DOM = "https://qramen.alexisld.fr"
SORTIE = pathlib.Path("/srv/projects/shared/qramen/public/assets/chevalets-tables.pdf")
MASCOTTE = base64.b64encode(pathlib.Path("/srv/projects/shared/qramen/public/assets/mascottes/ramen-1-bol-print.png").read_bytes()).decode()


def qr_data(table):
    buf = io.BytesIO()
    segno.make(f"{DOM}/menu.html?table=T{table:02d}", error="h").save(
        buf, kind="png", scale=48, border=4, dark="#14161A")
    return base64.b64encode(buf.getvalue()).decode()


def card(table):
    qr = qr_data(table)
    return f'''<article>
    <img class="mascotte" src="data:image/png;base64,{MASCOTTE}" alt="Mascotte QRamen"><img class="qr" src="data:image/png;base64,{qr}" alt="">
    <div class="call">Scannez pour commander</div><div class="foot">Table T{table:02d}<br>
    14 rue du Gros-Horloge, 76000 Rouen<br>github.com/AlexisLD-DEV/qramen</div></article>'''


style = ''':root{--print-color-00:#cfc6b8;--print-color-01:#a93627;--print-color-02:#625d54;}
@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif}
.sheet{width:297mm;height:210mm;padding:5mm;display:flex;flex-wrap:wrap;gap:4mm;align-content:flex-start;page-break-after:always}
article{width:141mm;height:100mm;border:1px dashed var(--print-color-00);border-radius:3mm;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:5mm}
article .mascotte{width:38mm;height:38mm;object-fit:contain;margin-bottom:1mm;mix-blend-mode:multiply}.qr{width:49mm;height:49mm;image-rendering:pixelated}.call{font-size:5mm;color:var(--print-color-01);font-weight:bold;margin-top:2mm}
.foot{font-size:3mm;color:var(--print-color-02);line-height:1.35;margin-top:2mm}'''
pages = []
for start in range(1, 8, 2):
    pages.append('<section class="sheet">' + card(start) + (card(start + 1) if start < 7 else '') + '</section>')
html = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>' + style + '</style></head><body>' + ''.join(pages) + '</body></html>'
request = urllib.request.Request(
    "http://172.19.0.1:8798/pdf?json=1",
    data=json.dumps({"html": html, "nom": "chevalets-tables"}).encode(),
    headers={"Content-Type": "application/json", "X-PDF-Key": CLE})
response = json.load(urllib.request.urlopen(request, timeout=180))
SORTIE.write_bytes(base64.b64decode(response["base64"]))
print(SORTIE, SORTIE.stat().st_size, "octets")
