# Rapport — refonte manga kawaii

## Direction visuelle

- **Titres :** Baloo 2 variable, auto-hébergée (`public/assets/fonts/baloo-2*.woff2`).
- **Texte :** Nunito variable, auto-hébergée (`public/assets/fonts/nunito*.woff2`). Corps courant réglé à 16 px; les libellés secondaires et allergènes ont été agrandis.
- **Palette :** crème chaud `#FFF7E9`, brun doux `#35251F`, rouge brique `#A93627`, doré `#9A6900`, vert sauge `#526944`, touches de rose/terre cuite dans les pastilles allergènes. Les boutons principaux et les textes courants gardent un contraste lisible.
- **Mascottes :** assets validés réutilisés depuis `docs/mascottes/`, copiés dans `public/assets/mascottes/` pour le bol ramen, le croque moustachu et les deux favicons.

## Pages modifiées

- `public/index.html` : scène d’accueil avec mascotte QRamen ou QRoque selon la maison; ambiance crème et brique.
- `public/menu.html` / `public/assets/style.css` : cartes plus douces, typographie lisible, pastilles allergènes harmonisées. Panier, suivi, commande, addition, langue et thème restent pilotés par le JS existant.
- `public/qr.html` : générateur conservé; chevalet A6 imprimable avec mascotte, nom de la maison, et QR noir sur fond blanc. Le lien décodé reste `https://croq.ledeunf.fr/menu.html?table=T01` pour QRoque dans le contrôle effectué.
- `public/assets/favicon-qramen.svg` et `favicon-croque.svg` : favicon dérivée de la mascotte correspondante.
- Cuisine et salle : écrans de travail toujours sombres et sobres; police harmonisée et libellés de réglages plus lisibles.

## Vérifications et captures

Captures regardées et archivées sous `docs/captures-refonte/` : accueil des deux maisons, menus desktop et mobiles des deux maisons, et deux chevalets A6.

- Chromium headless, largeurs 320, 390, 768 et 1440 px : aucune largeur de document supérieure au viewport sur accueil, carte et QR des deux maisons.
- axe-core sur la carte QRamen et QRoque : **0 violation WCAG 2.1 A/AA** après correction du focus du panier masqué et des noms accessibles des boutons.
- QR QRamen et QRoque décodés avec jsQR; destinations `https://qramen.ledeunf.fr/menu.html?table=T01` et `https://croq.ledeunf.fr/menu.html?table=T01`. Le chevalet A6 QRoque a aussi été décodé après rendu imprimable.
- `node --check public/assets/menu.js` passe.

## Éléments restant sobres

Les vues cuisine et salle restent des outils de travail : fond sombre, cartes à fort contraste, états de commande différenciés. Elles reçoivent uniquement la police Nunito/Baloo 2 et quelques réglages de taille/couleur cohérents avec la palette.
