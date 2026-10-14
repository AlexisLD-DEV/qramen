# Captures et mesures — audit QRamen / QRoque

- [`index.html`](index.html) : galerie avant/après des deux enseignes, cinq pages et neuf largeurs.
- `avant/` : référence du commit `1be5d9b` avant corrections.
- `apres/` : rendu final local Pages/Cloudflare, avant publication.
- `avant-mesures.json`, `apres-mesures.json` : largeur de document, erreurs de page et images pour chaque capture.
- `mesures-4g.json` : LCP et CLS en simulation 4G.
- `verification.json` : résumé responsive et essais des tables T01–T07.
- `verification-en-ligne.json` : contrôle Chromium des dix routes publiques après déploiement.
- `targets-320.json`, `contrastes.json` : cibles tactiles et ratios de contraste.

Les images sont nommées `{enseigne}-{page}-{largeur}.png`. Les vues menu affichent `table=T01`; les sept valeurs T01–T07 sont également testées dans `verification.json`.
