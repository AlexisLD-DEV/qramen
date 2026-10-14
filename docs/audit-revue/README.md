# Second regard sur l’audit QR

Rapport : [RAPPORT.md](RAPPORT.md). Captures avant/après/finales, mesures 4G avec moteur réel, parcours clavier, commandes techniques réelles et PDFs dans ce dossier.

Les scripts sous `scripts/` sont les programmes utilisés pour la revue. Ils nécessitent Playwright et Chromium ; leurs chemins correspondent à l’environnement de cette mission. Exécuter depuis la racine du dépôt. `qr-functional.cjs` et `qr-extra.cjs` utilisent `LIVE=1` pour les domaines publics, sinon un serveur public local au port 4177. `qr-real.cjs` crée de vraies commandes techniques puis les clôture : ne pas relancer comme un simple test en lecture.

Les mesures `performance-avant.json`, `performance-intermediaire.json`, `performance-live.json` sont trois passages avec réseau simulé et moteur accessible ; aucune moyenne/valeur terrain n’est revendiquée.
