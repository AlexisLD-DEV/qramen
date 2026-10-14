# QRamen Engine (Cloudflare Worker)

Worker autonome qui remplace les endpoints JSON n8n sous `/webhook/qramen`. Il lit et écrit Airtable par REST. Le PAT Airtable doit rester un secret Wrangler, jamais une variable versionnée.

## Routes couvertes

Les méthodes et contrats des six exports présents dans `../etat/wf-qramen*.json` sont conservés. Le site appelle aussi les routes cuisine et salle ci-dessous, déclarées dans ces exports :

- `GET /webhook/qramen/menu?concept=QRamen|QRoque`
- `POST /webhook/qramen/commande` — `{table, lignes:[{platId,quantite,note}], total, concept}`
- `GET /webhook/qramen/statut?numero=…`
- `POST /webhook/qramen/addition` — `{numero}`
- `GET /webhook/qramen/cuisine`
- `POST /webhook/qramen/cuisine/statut` — `{id,statut}`
- `GET /webhook/qramen/cuisine/carte?concept=…`
- `POST /webhook/qramen/cuisine/disponibilite` — `{id,disponible}`
- `GET /webhook/qramen/salle?concept=…`
- `POST /webhook/qramen/salle/statut` — `{id,etat}`
- `GET /webhook/qramen/ping`
- `POST /webhook/qramen/demo/generate` — crée 4 commandes sur quatre tables libres, vérifie les écritures Airtable et journalise le lot. Ouverte sans jeton; requiert `{confirmation:"GENERER LA DEMO"}`.
- `POST /webhook/qramen/reset` — réinitialise les commandes et lignes de démo après confirmation explicite `{confirmation:"REINITIALISER LA DEMO"}`. Ouverte sans jeton.
- `GET|POST /webhook/qramen/test-pdf` — `numero` en query string ou dans le JSON POST

Les exports locaux ne contiennent pas `ping` ni `test-pdf`; l'instance n8n n'était pas accessible par Docker. `ping` renvoie `{ok:true,service:"qramen-engine"}`. `test-pdf` renvoie les données JSON brutes du ticket (`type:"ticket-data"`, commande, table, lignes, total), sans produire de PDF. Le rendu et l'impression PDF restent au service du VPS jusqu'à décision contraire. `/addition` garde la réponse `{ok:true,numero}` et marque l'addition demandée, mais n'appelle ni le service PDF ni son stockage de pièce jointe.

## Développement local

Depuis ce dossier, créer `.dev.vars` (ignoré par Git) avec le secret localement, puis lancer :

```sh
printf 'AIRTABLE_PAT=%s\n' 'PAT_AIRTABLE' > .dev.vars
npx wrangler dev --local
```

Ne jamais mettre le PAT dans `wrangler.toml`. Pour les tests réels, le Worker doit pouvoir joindre `api.airtable.com`. La compatibilité est réglée à la dernière date disponible dans le runtime local testé (`2026-10-13`).

## Déployer (quand le jeton Cloudflare sera prêt)

Depuis `worker/`, authentifier Wrangler avec le jeton Cloudflare autorisé, puis exécuter :

```sh
npx wrangler secret put AIRTABLE_PAT
npx wrangler deploy
```

Coller le PAT Airtable à l'invite Wrangler. `AIRTABLE_BASE_ID` est déjà défini dans `wrangler.toml`. Le nom du Worker est `qramen-engine`.

## Intégration du site

`public/assets/api.js` centralise l'API. Le site essaie le Worker `qramen-engine.alexisledeunf.workers.dev` puis `n8n.ledeunf.fr` ; les pages menu, cuisine, salle et QR disposent aussi de leur repli local.

## Retour arrière

Pour revenir au moteur n8n en premier, modifier `public/assets/api.js` afin de placer `https://n8n.ledeunf.fr/webhook/qramen` dans `QRAMEN_API` et republier Cloudflare Pages. Le Worker reste déployé et peut être remis en premier en restaurant sa constante.
