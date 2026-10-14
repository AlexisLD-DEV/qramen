# Mode opératoire restaurateur

## Générer un QR de table

1. Ouvrez `https://qramen.ledeunf.fr/qr.html` ou `https://croq.ledeunf.fr/qr.html`.
2. Choisissez le restaurant, puis saisissez le nom ou numéro de table (par exemple `T08`, `Terrasse 2`). Le QR et son adresse se mettent à jour immédiatement.
3. Pour une table déjà enregistrée, utilisez son bouton **Imprimer ce chevalet**. Pour une nouvelle table, utilisez le générateur.
4. Téléchargez le QR au format SVG (vectoriel) ou PNG (1200 × 1200 px), selon le support choisi.

## Imprimer un chevalet

Cliquez sur **Imprimer ce chevalet** ou **Imprimer le chevalet**. Dans la fenêtre d’impression, choisissez le papier A6, l’échelle 100 % et activez les arrière-plans si le navigateur les désactive. Le chevalet contient le nom du restaurant, la table et « Scannez pour commander ».

## Ajouter une table

Ajoutez un enregistrement dans la table Airtable **Tables**, avec son numéro (par exemple `T08`) et le champ **Concept** (`QRamen` ou `QRoque`). Le menu `/menu` doit inclure ces tables dans sa réponse pour qu’elles apparaissent dans la liste. Le générateur accepte également un identifiant personnalisé.

## Ajouter un plat dans Airtable

Ajoutez un enregistrement à la table **Plats** et renseignez le nom, le prix, la catégorie, la disponibilité et le concept. Complétez description, tags et photo si disponibles. Utilisez le même concept que celui des tables (`QRamen` ou `QRoque`), puis vérifiez l’affichage dans la carte correspondante. Les champs exacts dépendent de la base configurée dans les workflows n8n du déploiement.
