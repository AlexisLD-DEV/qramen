# Rapport — parcours client QR

## Changements

- L’accueil et la carte déterminent le restaurant avec `location.hostname` (`croq` → QRoque Monsieur). Sur la carte, `?concept=` garde la priorité.
- Les deux accueils affichent leur marque, leurs textes et leur palette. Les sélecteurs en haut des accueils et des cartes relient les domaines en conservant `?table=`.
- La carte démarre avec un écran d’ouverture animé et des squelettes, puis affiche un message explicite et une carte de démonstration adaptée si le menu API est indisponible.
- La carte de démonstration QRoque utilise des croques et des photos locales. La carte QRamen, le panier, l’envoi, le suivi, l’addition et l’écran cuisine conservent leur architecture et leurs flux.

## Vérifications navigateur

Chromium, viewport 390 × 844. Pour tester les changements non encore déployés, les noms d’hôte `qramen.ledeunf.fr` et `croq.ledeunf.fr` étaient dirigés vers le serveur local du dépôt.

- `http://qramen.ledeunf.fr:8765/?table=T03` et `http://croq.ledeunf.fr:8765/?table=T03` : bonne marque d’accueil et sélecteur avec `table=T03` conservée.
- `http://qramen.ledeunf.fr:8765/menu.html?table=T03` et `http://croq.ledeunf.fr:8765/menu.html?table=T03` : bonne marque, table 03, sélecteur conservant la table, huit plats affichés dans chaque carte.
- Menu QRoque servi par `https://n8n.ledeunf.fr/webhook/qramen/menu?concept=QRoque` : réponse observée avec le restaurant QRoque Monsieur et les plats croque.
- Parcours navigateur avec réponses de commande et d’addition simulées : quantité, note, total, envoi, statut « Servi » et confirmation de demande d’addition vérifiés.
- `https://qramen.ledeunf.fr/` et `https://croq.ledeunf.fr/` répondent en HTTP 200. Ces domaines servent encore la version déployée avant ce commit ; les interactions ont été exercées sur le serveur local.
- `node --check public/assets/menu.js` et `git diff --check` passent.

## À confirmer après déploiement

- La page de production réelle devra être revue après publication du commit, notamment le sélecteur inter-domaines depuis les QR de table.
- Le mode de démonstration est conservé dans le code, mais l’API répondait pendant la vérification : l’indisponibilité réelle et son délai d’expiration n’ont pas été provoqués en production.
