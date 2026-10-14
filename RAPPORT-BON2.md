# Rapport — régénération du bon de cuisine

- `docs/captures/01b-bon-cuisine.pdf` a été régénéré par POST `http://127.0.0.1:8798/pdf`, avec `X-PDF-Key` lu depuis `/srv/hermes/.hermes/.secrets/qramen-pdf.key`, au format 80 × 200 mm.
- Le ticket reprend l’exemple #104, table T03 : deux ramen tonkotsu, dont un sans piment, et un gyoza.
- Extraction du texte PDF : adresse `14 rue du Gros-Horloge, 76000 Rouen` et crédit `alexisld.fr` présents. Aucune mention technique (n8n, Chrome headless ou génération automatique) ne subsiste.
- `docs/captures/01-bon-de-commande.png` conserve un autre exemple de commande, mais son pied est identique au PDF : même adresse et même crédit `alexisld.fr`. Le PNG n’a donc pas eu à être régénéré.
