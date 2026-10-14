# Rapport — Adresses Rouen, pied GitHub et PDF

## Adresse et cohérence

- Le relevé initial de `public/` a trouvé « Paris 11e » dans `public/assets/menu.js` et `public/carte-demo.json`. La réponse menu du Worker et le générateur de workflow répétaient aussi cette ville. Le pied de carte QRamen contenait en plus l’ancienne adresse « 42 rue de la Folie-Méricourt, Paris 11e ».
- Ces sources affichent maintenant Rouen. Les deux concepts utilisent l’adresse publiée dans le dépôt : **14 rue du Gros-Horloge, 76000 Rouen**. QRoque l’affiche maintenant aussi sur son accueil. Aucune différence d’adresse entre les deux restaurants n’est indiquée dans les sources du dépôt.
- Le relevé final `rg -n -i 'Paris|alexisld\.fr|code open source' public/` ne retourne aucune occurrence. Aucun écran de mentions légales distinct n’existe dans `public/`.

## Pieds de page et documents imprimés

- Les pieds de page de l’accueil, de la carte, de la page QR et de l’écran cuisine ne conservent que le lien cliquable `https://github.com/AlexisLD-DEV/qramen` comme signature.
- Les chevalets et additions affichent le lien du dépôt en petit. Les générateurs QR affichent également l’adresse physique, pour conserver les informations d’adresse demandées.
- Les générateurs de tickets et additions dans `outils/workflows.py` et `outils/workflow-addition.py` intègrent un SVG de mascotte adapté au concept. Pour une addition, le workflow identifie le concept à partir des plats réellement associés à la commande.
- Le PDF de chevalets QRamen a maintenant un générateur source (`outils/chevalets-qramen.py`) et a été régénéré. Les PDFs QRoque (chevalets A5, cartes A6, carte comptoir) ont été régénérés depuis `outils/chevalets-qroque.py`. Le service PDF reste générique : les SVG sont inclus dans le HTML transmis, sans dépendance à un fichier image externe.

## Vérification des tickets

Deux tickets PDF de démonstration ont été générés, un pour chaque enseigne. Les captures montrent la mascotte vectorielle dans l’en-tête, séparée du numéro, de la table, de l’heure et des plats.

- QRamen : [PDF](/srv/projects/shared/qramen/docs/captures-rouen/ticket-qramen-test.pdf) · [capture](/srv/projects/shared/qramen/docs/captures-rouen/ticket-qramen-test.png)
- QRoque : [PDF](/srv/projects/shared/qramen/docs/captures-rouen/ticket-qroque-test.pdf) · [capture](/srv/projects/shared/qramen/docs/captures-rouen/ticket-qroque-test.png)

## Captures des pages

| Écran | Le QRamen | QRoque Monsieur |
|---|---|---|
| Accueil | [capture](/srv/projects/shared/qramen/docs/captures-rouen/qramen-index.png) | [capture](/srv/projects/shared/qramen/docs/captures-rouen/qroque-index.png) |
| Carte | [capture](/srv/projects/shared/qramen/docs/captures-rouen/qramen-menu.png) | [capture](/srv/projects/shared/qramen/docs/captures-rouen/qroque-menu.png) |
| Cuisine | [capture](/srv/projects/shared/qramen/docs/captures-rouen/qramen-cuisine.png) | [capture](/srv/projects/shared/qramen/docs/captures-rouen/qroque-cuisine.png) |
| QR | [capture](/srv/projects/shared/qramen/docs/captures-rouen/qramen-qr.png) | [capture](/srv/projects/shared/qramen/docs/captures-rouen/qroque-qr.png) |

Les captures QRamen sont nommées `qramen-…` dans `docs/captures-rouen/` (sans espace).

## Contrôles réalisés

- `python3 -m py_compile` sur les générateurs PDF et workflows.
- `node --check` sur les scripts menu, cuisine, Worker et script intégré de la page QR.
- Rendu Chrome headless des deux PDFs test et inspection visuelle des captures.
- Recherche finale de « Paris », `alexisld.fr` et « code open source » dans `public/` : aucune occurrence.

Les fichiers sources de workflows ont été corrigés, mais les workflows n8n actifs n’ont pas été importés ni redéployés depuis ce dépôt.
