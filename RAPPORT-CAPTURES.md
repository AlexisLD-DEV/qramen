# Rapport — captures et README

Date : 14 octobre 2026

## Résultat

Huit captures Playwright Chromium ont été ajoutées dans `docs/captures/` et présentées dans la section `Aperçu` du README, dans l’ordre demandé. Chaque image est suivie d’une légende en français. Tous les liens d’image du README sont relatifs au dépôt.

Le service n’a pas fourni de PDF de commande prêt à capturer. La première image utilise donc le parcours de confirmation côté client : commande `#2401`, état « En attente » et étapes de suivi visibles. Pour ne pas créer de commande sur le service public, la réponse de création a été simulée dans le navigateur pendant cette capture.

Le chevalet QRoque Monsieur est capturé avec les styles d’impression actifs. Son format CSS A6 portrait (105 × 148 mm) donne une image de 396 × 559 pixels après arrondi du navigateur. Les vues menu et QR des tables sont en 390 × 844 pixels. Les accueils sont en 1440 × 1000/1010 et l’écran cuisine en 1440 × 2740.

## Fichiers capturés

| Fichier | Dimensions | Contenu |
|---|---:|---|
| `01-bon-de-commande.png` | 390 × 844 | Confirmation client et suivi de commande |
| `02-menu-telephone.png` | 390 × 844 | Menu QRamen sur téléphone |
| `03-chevalet-table.png` | 396 × 559 | Chevalet QRoque au rendu d’impression A6 |
| `04-qr-des-tables.png` | 390 × 844 | Page `/qr.html` sur téléphone |
| `05-ecran-cuisine.png` | 1440 × 2740 | Écran cuisine |
| `06-accueil-qramen.png` | 1440 × 1000 | Accueil QRamen |
| `07-accueil-qroque.png` | 1440 × 1010 | Accueil QRoque |
| `08-carte-qroque.png` | 390 × 844 | Menu QRoque sur téléphone |

## Vérifications

- Les huit PNG s’ouvrent et ont une taille non nulle.
- Les dimensions correspondent aux captures téléphoniques, au chevalet A6 et aux vues desktop décrites ci-dessus.
- Les huit chemins du README pointent vers les fichiers présents dans le dépôt.
- Le rendu a été inspecté visuellement, notamment le QR du chevalet, la confirmation, le menu, la page des QR et l’écran cuisine.
- Aucune modification de workflow n’a été faite.
