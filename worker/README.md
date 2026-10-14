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

## Basculer le site

Le site utilise actuellement `https://n8n.ledeunf.fr/webhook/qramen` comme base API. Après déploiement et vérification, remplacer uniquement cette constante par l'URL fournie par Wrangler, en gardant le suffixe `/webhook/qramen` (par exemple `https://qramen-engine.<compte>.workers.dev/webhook/qramen`). Vérifier menu, commande, suivi, cuisine et salle. Cette modification n'est pas faite dans ce livrable.

## Revenir en arrière

Remettre la constante API du site à `https://n8n.ledeunf.fr/webhook/qramen`, puis republier le site. L'ancien endpoint n8n et le service PDF restent la référence pendant la validation.
