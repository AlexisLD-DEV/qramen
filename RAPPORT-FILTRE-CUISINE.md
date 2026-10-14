# Rapport — filtre cuisine et destinations métier

## Changements

- Remplacement du menu Restaurant par trois boutons exclusifs : Le QRamen, QRoque Monsieur et Les deux (actif par défaut).
- Filtrage immédiat des commandes en mémoire, compteurs recalculés, badge d’enseigne sur chaque commande. La catégorie « Les deux » conserve les commandes mixtes ou sans étiquette exploitable.
- Accessibilité : groupe nommé, `aria-pressed`, tabulation native, navigation gauche/droite, focus visible et boutons de 44 px minimum.
- Mention discrète sous le titre sur cuisine, salle et QR ; aucune mention ajoutée au menu client.
- Styles adaptatifs au thème clair/sombre, y compris les cartes et le sélecteur.

## Vérifications

- JavaScript validé avec `node --check public/assets/cuisine.js`.
- Playwright : contrôle sur 320 px sans débordement horizontal ; boutons de 44 px ; les flèches changent le focus et l’état actif.
- Captures Playwright aux largeurs 390 et 1440 px, en clair et en sombre, dans les trois états :

| Thème / largeur | Le QRamen | QRoque Monsieur | Les deux |
|---|---|---|---|
| Clair · 390 | [PNG](docs/captures-filtre-cuisine/light-390-QRamen.png) | [PNG](docs/captures-filtre-cuisine/light-390-QRoque.png) | [PNG](docs/captures-filtre-cuisine/light-390-all.png) |
| Clair · 1440 | [PNG](docs/captures-filtre-cuisine/light-1440-QRamen.png) | [PNG](docs/captures-filtre-cuisine/light-1440-QRoque.png) | [PNG](docs/captures-filtre-cuisine/light-1440-all.png) |
| Sombre · 390 | [PNG](docs/captures-filtre-cuisine/dark-390-QRamen.png) | [PNG](docs/captures-filtre-cuisine/dark-390-QRoque.png) | [PNG](docs/captures-filtre-cuisine/dark-390-all.png) |
| Sombre · 1440 | [PNG](docs/captures-filtre-cuisine/dark-1440-QRamen.png) | [PNG](docs/captures-filtre-cuisine/dark-1440-QRoque.png) | [PNG](docs/captures-filtre-cuisine/dark-1440-all.png) |

## Déploiement

À compléter après déploiement, vérification en ligne, commit et push.

## Résultat en ligne

- Déploiement Cloudflare Pages terminé : [https://cf9266e4.qramen.pages.dev/cuisine](https://cf9266e4.qramen.pages.dev/cuisine)
- Vérification HTTP : la page de déploiement et `https://qramen.alexisld.fr/cuisine` répondent 200 ; HTML déployé contient le contrôle et les URL d’assets versionnées.
- Commit poussé sur `main` : `5fcc299` (`Add three-state restaurant filter to kitchen`).
