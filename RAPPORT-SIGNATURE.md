# Rapport — signature, PDF et menu

## Changements

- Ajout de la signature `alexisld.fr - code open source : github.com/AlexisLD-DEV/qramen` aux pieds de page de l’accueil, du menu et du générateur QR, avec des liens HTML sur les sites.
- Ajout de la même signature en texte aux chevalets générés et imprimés. Le chevalet garde uniquement le QR de la commande.
- Ajout de la signature aux tickets cuisine et additions. Le lien vers `https://alexisld.fr` est un vrai `<a href>` et son style reste souligné et sombre à l’impression.
- Suppression du décor de menu qui créait la zone beige vide à droite du bandeau. Les cartes de démonstration utilisent désormais les WebP de plats existants ; le code de repli ne dessine plus de plat ni ne remplace une photo par un emoji.

## Vérifications

- Captures du menu QRoque faites en 390×844 et 1440×1000 ; elles montrent les photos WebP dans la grille et aucun bloc décoratif vide en haut à droite.
- Tickets et additions rendus en PDF par le service Chromium local : les deux contiennent une annotation `/URI` vers `https://alexisld.fr`, avec une zone cliquable. Le HTML généré contient aussi le libellé `alexisld.fr`.
- Un seul QR reste présent sur le chevalet imprimable, celui de la table choisie.
