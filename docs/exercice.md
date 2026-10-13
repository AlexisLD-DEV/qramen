# L'exercice, et ce qui a été livré

## La consigne (exercice « commander par QR code »)

D'après les fichiers de l'exercice (base Airtable, formulaire par table, automatisation) :

1. une **base Airtable** avec des tables (T01…T07), une carte de plats et des commandes ;
2. un **QR code par table** qui ouvre un **formulaire** de commande ;
3. une **automatisation** qui enregistre la commande et produit un **ticket** ;
4. le tout doit tourner **sans intervention** : le client commande, la cuisine reçoit.

## Ce qui a été fait

| Élément de l'exercice | Remplacé / poussé par |
| --- | --- |
| Formulaire Zite par table | **page de menu complète** (photos, panier, notes de commande), servie sur son propre domaine |
| Automatisation Make | **n8n auto-hébergé** : menu, commande, statut, écran cuisine, addition |
| Ticket en PDF | **généré et attaché automatiquement** dans la commande (+ addition en un clic) |
| QR codes « bruts » | QR **testés** (décodage vérifié), déclinés en **chevalets A5**, **cartes A6** et **carte comptoir** prêtes à imprimer |
| 1 seule carte | **2 restaurants** dans la même base (ramen / croques), même moteur, thèmes différents |
| — | **écran cuisine** 3 colonnes avec changement de statut en un clic |
| — | **visuels** : 16 plats photographiés par IA + mockups en situation (chevalet, comptoir, vitrine, terrasse) |
| — | **schémas Excalidraw** pour présenter le projet |
| — | dépôt **public** documenté (ce dépôt) |

## Ce que ça démontre techniquement

- une **API** (webhooks n8n) qui parle à une base (Airtable) et à un service local (PDF/Chrome) ;
- un **contrat d'API** clair entre une page statique et des automatisations (JSON, CORS) ;
- de la **génération de documents** côté serveur (ticket, addition) rattachée aux données ;
- une **mise en ligne** réelle (DNS, TLS, cache) sur un vrai domaine ;
- et une règle tenue : **aucun secret dans le dépôt** (jetons et clés hors versionnement).

## Pour présenter à l'oral

1. Montrer la page du menu sur un téléphone, scanner le QR d'une carte imprimée.
2. Commander : la commande apparaît **en direct** sur l'écran cuisine.
3. Passer la commande en « servi » : le bouton **addition** apparaît côté client.
4. Ouvrir Airtable : le **ticket PDF** et l'**addition PDF** sont attachés à la commande.
5. Terminer sur le dépôt : tout est versionné, documenté, sans secret.
