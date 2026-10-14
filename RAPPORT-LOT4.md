# Rapport Lot 4 — Habillage QR et chevalet

## Changements

- Fond papier nuancé avec texture très discrète, palette et accents adaptés à QRamen et QRoque.
- Hiérarchie renforcée entre le générateur, son aperçu et les tables enregistrées ; cartes plus lisibles et légèrement en relief.
- Chevalet A6 composé comme un support de table : fond crème propre à la maison, marque, titre, consigne « Scannez pour commander », QR sur un cartouche blanc, table et mention de la maison.
- QR produit côté navigateur par la bibliothèque locale existante. Génération et exports PNG/SVG conservés.

## Vérifications Playwright

Sur `https://qramen.ledeunf.fr/qr.html` et `https://croq.ledeunf.fr/qr.html` :

- captures écran desktop, mobile et impression ; PDF d’impression A6 d’une page par domaine ;
- aucun débordement horizontal à 390 px ;
- le logo et le thème correspondent au domaine ; 7 tables affichées ;
- les téléchargements produisent `qr-T01.svg` et `qr-T01.png` ;
- QR de la table T03 décodé depuis le rendu d’impression :
  - QRamen : `https://qramen.ledeunf.fr/menu.html?table=T03`
  - QRoque : `https://croq.ledeunf.fr/menu.html?table=T03`

Captures et PDF de contrôle dans `/tmp/qraudit/` (non ajoutés au dépôt).
