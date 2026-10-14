"""Génère les chevalets A5 QRamen avec QR haute définition et mascotte vectorielle."""
import base64
import io
import json
import pathlib
import urllib.request
import segno

CLE = pathlib.Path("/srv/hermes/.hermes/.secrets/qramen-pdf.key").read_text().strip()
DOM = "https://qramen.ledeunf.fr"
SORTIE = pathlib.Path("/srv/projects/shared/qramen/public/assets/chevalets-tables.pdf")
MASCOTTE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 72"><path d="M14 31q36-33 72 0" fill="#eab653" stroke="#33241d" stroke-width="4"/><path d="M17 34h66l-8 24H25z" fill="#d86438" stroke="#33241d" stroke-width="4"/><path d="M20 37h60" stroke="#f4d37f" stroke-width="5"/><path d="M11 62h78" stroke="#33241d" stroke-width="5"/><circle cx="42" cy="45" r="2"/><circle cx="59" cy="45" r="2"/></svg>'


def qr_data(table):
    buf = io.BytesIO()
    segno.make(f"{DOM}/menu.html?table=T{table:02d}", error="h").save(
        buf, kind="png", scale=48, border=4, dark="#14161A")
    return base64.b64encode(buf.getvalue()).decode()


def card(table):
    qr = qr_data(table)
    return f'''<article><div class="brand">Le <b>QR</b>amen</div><div class="rule"></div>
    {MASCOTTE}<img class="qr" src="data:image/png;base64,{qr}" alt="">
    <div class="call">Scannez pour commander</div><div class="foot">Table T{table:02d}<br>
    14 rue du Gros-Horloge, 76000 Rouen<br>github.com/AlexisLD-DEV/qramen</div></article>'''


style = '''@page{size:A4 landscape;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif}
.sheet{width:297mm;height:210mm;padding:5mm;display:flex;flex-wrap:wrap;gap:4mm;align-content:flex-start;page-break-after:always}
article{width:141mm;height:100mm;border:1px dashed #cfc6b8;border-radius:3mm;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:5mm}
.brand{font: bold 13mm Georgia,serif;color:#14161a}.brand b{color:#a93627}.rule{width:24mm;height:1mm;background:#a93627;margin:2mm 0 1mm}
article svg{width:18mm;height:13mm;margin-bottom:1mm}.qr{width:49mm;height:49mm;image-rendering:pixelated}.call{font-size:5mm;color:#a93627;font-weight:bold;margin-top:2mm}
.foot{font-size:3mm;color:#625d54;line-height:1.35;margin-top:2mm}'''
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
