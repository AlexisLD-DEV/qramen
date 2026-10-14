# Rapport — Lot 5

## Changements

- **Cuisine :** affichage de l’ancienneté (« il y a N min »), orange à 10 minutes et rouge à 20 minutes, cartes agrandies sur fond sombre, bouton plein écran natif et lien vers la salle.
- **Salle :** nouvelle page `/salle.html`, tri des additions demandées puis des commandes les plus anciennes, actions pour marquer une table servie ou libre, états enregistrés dans `Tables.Etat`. Le workflow `QRamen — salle` est généré par `outils/workflow-salle.py` et inclus dans le script de publication. Les tables étant partagées dans Airtable sans champ `Concept`, la page les liste sans filtre artificiel.
- **Accessibilité :** libellés, focus clavier, dialogue d’allergènes, textes alternatifs, états modaux et contrastes renforcés. Les deux fiches restaurant et les états cart/commande/allergènes ont été contrôlés.
- **Conforts :** thème sombre système et mémorisation du choix manuel ; carte et parcours de commande disponibles en anglais, avec le numéro de table conservé.
- **Allergènes :** champ multi-sélection Airtable `Allergenes` et champ `Etat` créés par l’API. Les 24 plats ont des sélections plausibles. La carte affiche pastilles, détail, légende des 14 familles et consigne de prévenir le personnel. Le mode opératoire décrit la mise à jour.

## Vérifications chiffrées

- Playwright Chromium, **390 × 844**, sur `qramen.ledeunf.fr` et `croq.ledeunf.fr` : **10 vues** (accueil, carte, cuisine, salle, QR × 2 domaines), **0 débordement horizontal**, **0 erreur JavaScript**, **0 violation axe-core WCAG 2.1 A/AA**.
- États interactifs de la carte (légende allergènes, panier, confirmation/suivi) : **3 états**, **0 violation axe-core**. Thème sombre QRamen et QRoque : **2 vues**, **0 violation axe-core**.
- Démo hors API : **3 commandes cuisine** et **3 tables salle** affichées.
- API n8n en lecture : **200** pour les deux menus (**8 plats chacun**), cuisine (**14 commandes**), carte cuisine (**8 plats**) et salle (**7 tables**).
- QR rendus puis décodés avec ZXing : QRamen → `https://qramen.ledeunf.fr/menu.html?table=T01`, QRoque → `https://croq.ledeunf.fr/menu.html?table=T01`.
- Plein écran natif Chromium : activé avec le bouton et quitté avec le même bouton. Le changement de langue conserve `T05` dans le parcours de commande simulé ; les **16 descriptions** des deux cartes ont été rendues en anglais sur les fiches API.
- Airtable : **24/24 plats renseignés**, **14 options** dans `Allergenes` ; lecture du menu publique vérifiée sur les deux concepts.

## Échecs rencontrés et corrections

- L’audit axe-core a révélé des contrastes insuffisants sur les petits textes, les commandes et les états cuisine/salle. Les couleurs ont été ajustées et les audits relancés à **0 violation**.
- L’API de métadonnées Airtable a refusé de renommer les options de sélection déjà créées (HTTP 422). Les valeurs Airtable restent sans accents (`crustaces`, `oeufs`, etc.) et la carte affiche les libellés accentués.
- Le premier test du webhook d’écriture salle a signalé une expression invalide dans le nœud HTTP. L’expression a été simplifiée pour envoyer directement le champ `Etat` ; le résultat du test de réécriture/restauration sera consigné ici après publication.

## À confirmer par le restaurateur

Les allergènes initiaux sont plausibles d’après les intitulés et descriptions des plats. Le restaurateur doit les valider avec les recettes, fiches fournisseurs et risques de contamination croisée avant de s’appuyer sur l’affichage pour le service. Aucun push n’a été effectué.
