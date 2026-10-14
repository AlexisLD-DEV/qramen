# Rapport — pieds et crédit alexisld.fr

## Modifications

- Ticket cuisine et ticket d’addition : adresse `14 rue du Gros-Horloge, 76000 Rouen` et crédit `alexisld.fr` ; les mentions techniques ont été retirées.
- Modèle des chevalets QRoque : ajout de la même adresse et du crédit.
- Accueil : remplacement de la mention de formation par `Site réalisé par alexisld.fr`.
- Captures d’accueil QRamen et QRoque régénérées pour retirer l’ancienne mention de formation.
- `docs/captures/01-bon-de-commande.png` régénérée après un POST au service PDF local, puis rendue depuis son PDF en PNG à 300 dpi. Dimensions : 946 × 2363 px, correspondant à 80 × 200 mm. L’OCR confirme l’adresse et le crédit, sans mention technique.

## Vérifications

- `bash outils/publier-workflows.sh` : publication terminée avec succès ; les cinq workflows ont été importés, publiés et le conteneur n8n redémarré.
- Accueils `qramen.ledeunf.fr` et `croq.ledeunf.fr` : HTTP 200, le HTML servi contient le nouveau crédit et plus l’ancienne mention.
- Webhooks : depuis le conteneur local n8n, menu répond HTTP 200. Commande et addition ont répondu HTTP 500 aux requêtes de contrôle volontairement invalides (`{}` et numéro inexistant), ce qui confirme que les routes actives reçoivent les requêtes, sans créer de commande ni modifier une addition.
- Les requêtes vers les trois webhooks via le domaine public ont été bloquées par Cloudflare (HTTP 403, code 1010) depuis cet environnement ; leur réponse publique n’a donc pas pu être contrôlée ici.
- OCR des captures dans `docs/captures/` : aucune mention « n8n », « Chrome headless », « exercice de formation » ou « restaurant fictif » ne subsiste.
