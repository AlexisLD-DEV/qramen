# Les six visuels « objet » (sac, carte, boîte)

Méthode : l'ambiance (salle, table, plats) est générée, la **surface d'impression est vierge**, et
c'est le QR qui est **projeté sur cette surface**, en suivant sa perspective (les 4 coins sont
relevés à la main pour chaque image, la projection se fait en `warpPerspective`, l'encre prend la
matière du support).

Fichiers : `croc-1-sac`, `croc-2-carte`, `croc-3-boite` (QRoque Monsieur) et `ram-1-sac`,
`ram-2-carte`, `ram-3-boite` (Le QRamen).

Contrôle systématique : chaque QR est **décodé dans l'image finale** (zxing-cpp) avant livraison —
c'est la seule façon de garantir qu'un visuel reste utilisable en vrai. Les deux boîtes sont
recadrées sur l'objet pour que l'impression prenne sa place ; le QR est re-vérifié après recadrage.

Le moteur est versionné : `outils/` du dépôt côté travail, script `imprimer-perspective.py`
(relevé des quads + projection + encre).