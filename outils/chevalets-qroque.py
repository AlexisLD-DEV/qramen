"""Chevalets QRoque Monsieur : A5 (2/A4), A6 (4/A4) et une carte comptoir, QR segno haute definition."""
import base64, io, json, pathlib, urllib.request
import segno

CLE = pathlib.Path("/srv/hermes/.hermes/.secrets/qramen-pdf.key").read_text().strip()
DOM = "https://croq.ledeunf.fr"
SORTIE = pathlib.Path("/srv/projects/shared/qramen/public/assets")
ACCENT = "#7B2D26"
MASCOTTE = '<svg class="mascotte" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 72"><path d="M16 28h68l-8 30H24z" fill="#d99a42" stroke="#35251d" stroke-width="4"/><path d="M22 31h56l-7 19H29z" fill="#f5e6c7"/><path d="M29 31 40 20l12 11 12-11 14 11" fill="#f0c05a" stroke="#8d4b2b" stroke-width="4"/><path d="M11 61h78" stroke="#35251d" stroke-width="5"/></svg>'


def qr_data(url, taille=1200):
    """QR haute definition, encode en PNG base64 (net a l'impression)."""
    buf = io.BytesIO()
    segno.make(url, error="h").save(buf, kind="png", scale=taille // 25, border=4, dark="#14161A")
    return base64.b64encode(buf.getvalue()).decode()


def carte(numero, image, format_="a5"):
    pied = (f"Table {numero:02d} · commandez depuis votre téléphone,<br>on apporte tout à table."
            if numero else "Commandez depuis votre téléphone,<br>on apporte tout à table.")
    pied += "<br>14 rue du Gros-Horloge, 76000 Rouen<br>github.com/AlexisLD-DEV/qramen"
    return f"""
<div class="carte {format_}">
  <div class="marque"><b>QR</b>oque Monsieur</div>
  <div class="filet"></div>
  {MASCOTTE}
  <img src="data:image/png;base64,{image}" alt="">
  <div class="action">Scannez pour commander</div>
  <div class="pied">{pied}</div>
</div>"""


STYLE = """
@page { size: A4 %(sens)s; margin: 0 }
* { box-sizing: border-box }
body { margin: 0; font-family: 'Inter', Arial, sans-serif }
.page { width: %(larg)s; height: %(haut)s; display: flex; flex-wrap: wrap; padding: 5mm; gap: 4mm; page-break-after: always; align-content: flex-start }
.carte { border: 1px dashed #cfc6b8; border-radius: 3mm; text-align: center; display: flex;
         flex-direction: column; align-items: center; justify-content: center; }
.carte.a5 { width: 141mm; height: 100mm; padding: 6mm }
.carte.a6 { width: 100mm; height: 138mm; padding: 5mm }
.carte.a5 .marque { font-family: Georgia, serif; font-size: 13mm; letter-spacing: -.4mm; color: #14161A }
.carte.a6 .marque { font-family: Georgia, serif; font-size: 9mm; letter-spacing: -.3mm; color: #14161A }
.marque b { color: %(accent)s }
.carte.a5 .filet { width: 24mm; height: 1mm; background: %(accent)s; margin: 3mm 0 4mm }
.carte.a6 .filet { width: 18mm; height: .8mm; background: %(accent)s; margin: 2.5mm 0 3.5mm }
.carte .mascotte { width: 21mm; height: 15mm; margin-bottom: 2mm; flex:none }
.carte.a5 img { width: 62mm; height: 62mm; image-rendering: pixelated }
.carte.a6 img { width: 62mm; height: 62mm; image-rendering: pixelated }
.carte.a5 .action { margin-top: 4mm; font-size: 5.6mm; color: %(accent)s; font-weight: 600 }
.carte.a6 .action { margin-top: 3.5mm; font-size: 4.4mm; color: %(accent)s; font-weight: 600 }
.carte.a5 .pied { margin-top: 3mm; font-size: 3.8mm; color: #6f6b63; line-height: 1.45 }
.carte.a6 .pied { margin-top: 2.5mm; font-size: 3.2mm; color: #6f6b63; line-height: 1.45 }
""" % {"accent": ACCENT, "sens": "landscape", "larg": "297mm", "haut": "210mm"}


def feuille(cartes, sens="landscape"):
    style = STYLE if sens == "landscape" else STYLE.replace("A4 landscape", "A4 portrait").replace("297mm; height: 210mm", "210mm; height: 297mm")
    return f"<div class='page'>{''.join(cartes)}</div>"


def rendre(pages, nom, style=None):
    st = style or STYLE
    html = ("<!doctype html><html lang='fr'><head><meta charset='utf-8'><style>" + st
            + "</style></head><body>" + "".join(pages) + "</body></html>")
    req = urllib.request.Request("http://172.19.0.1:8798/pdf?json=1",
                                 data=json.dumps({"html": html, "nom": nom, "format": "A4"}).encode(),
                                 headers={"Content-Type": "application/json", "X-PDF-Key": CLE})
    rep = json.load(urllib.request.urlopen(req, timeout=180))
    chemin = SORTIE / f"{nom}.pdf"
    chemin.write_bytes(base64.b64decode(rep["base64"]))
    print(nom, "->", chemin, chemin.stat().st_size, "octets |", len(pages), "feuille(s)")


if __name__ == "__main__":
    # 1. Chevalets A5 : une carte par table, QR vers le menu QRoque Monsieur
    cartes_a5 = [carte(n, qr_data(f"{DOM}/menu.html?table=T{n:02d}"), "a5") for n in range(1, 8)]
    rendre([feuille(cartes_a5[i:i + 2]) for i in range(0, len(cartes_a5), 2)], "chevalets-qroque-a5")
    # 2. Cartes A6 (comptoir / petites tables) : 4 par feuille A4 portrait
    st_a6 = (STYLE.replace("A4 landscape", "A4 portrait")
                  .replace("297mm; height: 210mm", "210mm; height: 297mm")
                  .replace(".page { width: 210mm; height: 297mm; display: flex; flex-wrap: wrap; padding: 5mm; gap: 4mm;",
                           ".page { width: 210mm; height: 297mm; display: flex; flex-wrap: wrap; padding: 4mm; gap: 3mm;")
                  .replace(".carte.a6 { width: 100mm; height: 138mm; padding: 5mm }",
                           ".carte.a6 { width: 97mm; height: 132mm; padding: 4mm }"))
    cartes_a6 = [carte(n, qr_data(f"{DOM}/menu.html?table=T{n:02d}"), "a6") for n in range(1, 8)]
    rendre([feuille(cartes_a6[i:i + 4]) for i in range(0, len(cartes_a6), 4)], "cartes-qroque-a6", st_a6)
    # 3. Carte comptoir (sans numero de table)
    rendre([feuille([carte(0, qr_data(f"{DOM}/menu.html"), "a5")])], "carte-comptoir-qroque")
