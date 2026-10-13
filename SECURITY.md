# Sécurité

## Signaler

Une question ou un problème de sécurité : **contact@alexisld.fr**.
Réponse sous 72 h. Merci de ne pas ouvrir d'issue publique pour un problème sensible.

## Principes du dépôt

- **Aucun secret versionné.** Le jeton Airtable de l'exercice est stocké côté n8n (identifiants n8n),
  la clé du service PDF dans `~/.hermes/.secrets/qramen-pdf.key` (déjà couvert par `.gitignore`).
- **Le navigateur ne parle jamais directement à Airtable** : la page n'appelle que les webhooks n8n,
  qui portent l'authentification. Aucun jeton n'est exposé au client.
- **Le service PDF** applique un jeton partagé (`X-PDF-Key`), refuse les corps de plus de 5 Mo et
  n'exécute que Chrome en mode headless sur le HTML fourni ; il n'est pas exposé sur Internet.
- **Le site** ne collecte aucune donnée personnelle : les commandes ne contiennent qu'un numéro de
  table, des plats et des quantités. Aucun paiement, aucun compte client.
- Le site est une **démonstration** : le formulaire n'envoie rien à l'extérieur, aucun email ni SMS
  n'est déclenché.

## Ce que ce dépôt n'est pas

Un exercice de formation sur un restaurant **fictif**. Les noms, avis et plats sont inventés ; les
visuels sont générés par IA pour le projet.
