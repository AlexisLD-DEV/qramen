# Rapport — débordements mobiles à 320 px

## Correction

Sous 381 px, le header se replie sur plusieurs lignes afin de conserver visibles ses commandes, dont le panier. Les filtres restent des boutons tactiles dans leur conteneur défilant horizontalement; leur largeur et leur hauteur de 42 px sont conservées. La correction s'applique aux deux concepts, QRamen et QRoque.

## Vérification Playwright

Mesure : `document.documentElement.scrollWidth - window.innerWidth`, après défilement jusqu'en bas, avec le Chromium et le `PYTHONPATH` de référence de la mission.

| Page | 320 px | 360 px | 390 px | 768 px | 1440 px |
|---|---:|---:|---:|---:|---:|
| QRamen `menu.html?table=T03` | 0 px | 0 px | 0 px | 0 px | 0 px |
| QRoque `menu.html?table=T03` | 0 px | 0 px | 0 px | 0 px | 0 px |

Avant correction, la mesure de référence était de 9 px à 320 px sur QRamen; QRoque présentait 46 px à 320 px et 6 px à 360 px. Aucun push n'a été effectué.
