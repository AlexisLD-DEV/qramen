import importlib.util, pathlib
import numpy as np, cv2
from PIL import Image, ImageFilter

RACINE = pathlib.Path("/srv/hermes/work/exo-qr")
_sp = importlib.util.spec_from_file_location("cds", str(RACINE / "carte-dans-scene.py"))
cds = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(cds)
IMG = cds.IMG
SORTIE = RACINE / "mockups"

QUAD = [(158, 90), (688, 90), (688, 744), (158, 748)]   # feuille calee dans le support


def support_depuis_ramen():
    """Copie le support (et son pied) du ramen sur la photo croque, a la meme position."""
    ram = Image.open(IMG / "support-ramen.png").convert("RGB")
    cro = Image.open(IMG / "support-croque.png").convert("RGB")
    x0, y0, x1, y1 = 130, 680, 720, 860
    bande = ram.crop((x0, y0, x1, y1))
    masque = Image.new("L", bande.size, 255).filter(ImageFilter.GaussianBlur(10))
    cro.paste(bande, (x0, y0), masque)
    tmp = IMG / "_croque-support-ramen.png"
    cro.save(tmp)
    print("support du ramen pose sur la photo croque")
    return tmp


if __name__ == "__main__":
    tmp = support_depuis_ramen()
    cds.inserer("support-ramen.png", "ram", QUAD, "uniforme-ramen.jpg")
    cds.inserer(str(tmp), "croc", QUAD, "uniforme-croque.jpg")
    tmp.unlink(missing_ok=True)
