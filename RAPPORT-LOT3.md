# Rapport lot 3 — Confort cuisine

## Changements

- L'écran cuisine identifie les commandes reçues depuis le chargement initial : le premier affichage reste silencieux, puis chaque nouvel identifiant déclenche un bip sinusoïdal bref (Web Audio API) et un flash de sa carte. Le bouton **Activer le son** déverrouille l'audio après un geste utilisateur; le choix est mémorisé en `localStorage` et le déverrouillage est refait à chaque session navigateur.
- Ajout du sélecteur QRamen/QRoque et du panneau **Carte du jour** avec état et bascule disponible/épuisé. En cas d'indisponibilité des endpoints carte, le panneau et la bascule restent fonctionnels en démonstration locale.
- Le workflow versionné `qramenCuisine01` expose `GET /webhook/qramen/cuisine/carte?concept=QRamen|QRoque` et `POST /webhook/qramen/cuisine/disponibilite` (`{ "id": "rec…", "disponible": false }`). Cette dernière route met à jour le champ Airtable `Disponible`. Le workflow menu renvoie également la disponibilité, utilisée par le filtre déjà présent dans `menu.js`.
- Ajustements mobiles de l'en-tête client pour tenir à 390 px, et documentation des deux routes dans `docs/architecture.md`.

## Vérifications

- `node --check public/assets/cuisine.js`, compilation Python des deux générateurs, validation JSON des workflows générés et `git diff --check` : OK.
- Playwright Chromium sur `qramen.ledeunf.fr` et `croq.ledeunf.fr`, menu en 390×844 : 8 cartes chargées, largeur document 390 px sur les deux domaines.
- Playwright sur `/cuisine.html` sur les deux domaines en 390×844 : panneau carte et bouton son visibles, aucune erreur navigateur, largeur document 390 px.
- Playwright avec API simulée sur l'écran cuisine : aucun flash au premier chargement, flash au nouvel identifiant du rafraîchissement suivant, préférence audio mémorisée, bascule de disponibilité vérifiée. Vue bureau : 3 colonnes de commandes et panneau carte visibles.

## Mise en service n8n

Le code des routes est inclus dans `outils/workflow-cuisine.py`. Pour activer l'écriture Airtable réelle, exécuter `bash outils/publier-workflows.sh` sur le serveur : le script régénère, importe, publie et active le workflow cuisine. L'essai Playwright de la mutation a utilisé une réponse API simulée et n'a pas modifié Airtable. Aucun déploiement n8n ni push Git n'a été effectué dans ce lot.
