# Architecture

## Vue d'ensemble

```
 téléphone du client                      serveur (VPS OVH)
 ───────────────────                      ──────────────────
 scan du QR de la table
        │
        ▼
 page statique  ◄─────────── Caddy + Cloudflare ────────► qramen.ledeunf.fr  (ramen)
 (HTML/CSS/JS, pas de framework)                            croq.ledeunf.fr    (croques)
        │  fetch JSON
        ▼
 API n8n auto-hébergée  ──────────────►  Airtable (base « exo QR »)
 (webhooks /menu /commande /statut           Tables · Plats · Commandes · Lignes
  /cuisine /cuisine/statut /addition)
        │
        ▼
 service PDF local (Chrome headless)  ──►  pièces jointes Airtable
 ticket cuisine + addition (PDF)
```

## Les briques

| Brique | Rôle | Où |
| --- | --- | --- |
| Page client | menu, panier, suivi de commande, demande d'addition | `public/` (statique) |
| Écran cuisine | 3 colonnes (en attente / en cours / servi), changement de statut | `public/cuisine.html` |
| n8n | toute la logique métier (6 webhooks) | conteneur `n8n-n8n-1`, <https://n8n.ledeunf.fr> |
| Airtable | base de données | base `appBHi3MxCb0hW1yH` (4 tables) |
| Service PDF | HTML → PDF via Chrome headless, jeton partagé | `outils/pdf-service.py` (systemd `qramen-pdf`) |
| Caddy | TLS + domaine | `qramen.ledeunf.fr`, `croq.ledeunf.fr` |

## Les workflows n8n

Générés par du code (pas cliqués à la main) : `outils/workflows.py` + `outils/workflow-cuisine.py`
+ `outils/workflow-addition.py` écrivent le JSON, `outils/publier-workflows.sh` importe, publie et
redémarre.

| Workflow | Entrée | Ce qu'il fait |
| --- | --- | --- |
| `qramenMenu01` | `GET /webhook/qramen/menu?concept=` | lit les plats disponibles, filtre par concept, renvoie le menu + les infos du restaurant |
| `qramenCommande01` | `POST /webhook/qramen/commande` | trouve la table, crée la commande, crée les lignes, génère le ticket PDF et l'attache |
| `qramenStatut01` | `GET /webhook/qramen/statut?numero=` | renvoie le statut + l'addition |
| `qramenCuisine01` | `GET /webhook/qramen/cuisine` | commandes ouvertes + lignes |
| `qramenCuisine01` | `POST /webhook/qramen/cuisine/statut` | passe une commande en « en cours » ou « servi » |
| `qramenCuisine01` | `GET /webhook/qramen/cuisine/carte?concept=QRamen%7CQRoque` | renvoie les plats du restaurant avec leur disponibilité |
| `qramenCuisine01` | `POST /webhook/qramen/cuisine/disponibilite` | met à jour `Disponible` dans Airtable (`{ "id": "rec…", "disponible": false }`) |
| `qramenAddition01` | `POST /webhook/qramen/addition` | construit l'addition (lignes + total), la génère en PDF, l'attache |

Le vocabulaire de l'écran cuisine (« Servi ») est traduit vers celui de la base (« Terminee ») dans
les workflows : c'est le seul endroit où les deux vocabulaires se rencontrent.

## Base Airtable

- **Tables** : `Identifiant` (T01…T07), QR code, lien du formulaire.
- **Plats** : `Plat`, `Categorie` (Entrée/Plat/Dessert/Boisson), `Prix`, `Disponible`, `Concept`
  (QRamen / QRoque), `Description`, `Photo` (nom du fichier webp).
- **Commandes** : `Numero` (auto), `Statut` (En attente / En cours / Terminee), `Table`, `Lignes`,
  `Total` (rollup), `Ticket cuisine`, `Addition`, `Addition demandee`.
- **Lignes** : `Ligne`, `Quantite`, `Plat`, `Commande`, `Designation` (formule).

Les deux cartes vivent dans la même base : c'est le champ `Concept` qui les sépare, et le même
moteur sert les deux restaurants.

## Service PDF (le point que Make ratait)

`outils/pdf-service.py` écoute sur `0.0.0.0:8798`, protégé par un jeton partagé (`X-PDF-Key`,
stocké hors du dépôt), et rend le HTML reçu avec Chrome headless. Il accepte `?json=1` pour
renvoyer le PDF en base64 — c'est ce qui permet à n8n de le transmettre à Airtable sans manipuler
de binaire.

## Déploiement

```bash
bash outils/mettre-en-ligne.sh      # service systemd --user (port 8802) + site Caddy
bash outils/publier-workflows.sh    # workflows n8n : import + publish + redémarrage
bash outils/faire-qr.sh             # QRs des tables + planche imprimable
```

Deux pièges appris à la dure :

1. **n8n v2 publie les workflows.** Un `import:workflow` écrit le brouillon ; il faut
   `publish:workflow --id=…` **puis** activer **puis** redémarrer le conteneur, sinon le webhook
   sert l'ancienne version.
2. **Les conteneurs ne voient pas l'hôte.** Un service sur le VPS n'est joignable depuis n8n
   qu'après `ufw allow from 172.19.0.0/16 to any port 8798`.
