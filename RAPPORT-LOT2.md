# Rapport Lot 2 — Marques et QR des tables

## Changements réalisés

- Marques officielles copiées sous `public/assets/marque-qramen.svg` et `marque-croque.svg`, utilisées sur les deux accueils et les deux cartes. Favicon dédié avec pastille adaptée à chaque restaurant.
- Titre d’accueil QRoque conservé en serif; interlettrage et interligne ajustés aux tailles bureau et téléphone.
- Nouvelle page statique `public/qr.html` : générateur immédiat, choix restaurant/table, téléchargement PNG/SVG, impression A6, et liste T01–T07 avec chargement optionnel des tables retournées par `/menu`.
- Bibliothèque QR locale `public/assets/vendor/qrcode.js`, sans CDN ni service externe.
- Captures remplacées/créées dans `docs/captures/` : accueil QRamen, accueil QRoque, carte QRamen, carte QRoque, cuisine et QR des tables.
- README français complété et guide [mode opératoire restaurateur](docs/mode-operatoire-restaurateur.md) ajouté.

## Contrôles effectués

Playwright Chromium sur le service local port 8802 avec résolution locale des deux hôtes :

- `http://qramen.ledeunf.fr:8802/`
- `http://croq.ledeunf.fr:8802/`
- `http://qramen.ledeunf.fr:8802/menu.html`
- `http://croq.ledeunf.fr:8802/menu.html`
- `http://qramen.ledeunf.fr:8802/cuisine.html`
- `http://qramen.ledeunf.fr:8802/qr.html`
- `http://croq.ledeunf.fr:8802/qr.html`

Aucune erreur JavaScript, 7 tables listées sur chaque domaine, aucune barre de défilement horizontale en vue téléphone. Le décodage indépendant des images QR donne `https://qramen.ledeunf.fr/menu.html?table=T01` et `https://croq.ledeunf.fr/menu.html?table=T01`. En média impression, le chevalet s’affiche en 105 × 148 mm (A6 portrait).

## Point à confirmer au déploiement

Le workflow `/menu` actuel ne renvoie que le restaurant, catégories et plats (pas de liste de tables). Le générateur utilise donc T01–T07 par défaut. Il remplacera ces valeurs si le webhook expose les tables via un des champs reconnus; le nom de champ définitif est à confirmer avec le modèle Airtable/workflow en production.
