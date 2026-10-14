# Mode opératoire restaurateur


**14 rue du Gros-Horloge, 76000 Rouen** — ouvert tous les jours, 12h–14h30 et 19h–22h30. Un lieu, deux comptoirs : Le QRamen (bar a ramen) et QRoque Monsieur (croque-monsieur).

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


## Mettre à jour les allergènes d’un plat

1. Ouvrez la base Airtable QRamen, table **Plats**, puis la fiche du plat concerné.
2. Dans **Allergenes**, sélectionnez toutes les familles effectivement présentes dans la recette ou susceptibles d’être présentes selon les ingrédients fournisseurs : gluten, crustacés, œufs, poissons, arachides, soja, lait, fruits à coque, céleri, moutarde, sésame, sulfites, lupin et mollusques.
3. Vérifiez les fiches techniques des ingrédients et les risques de contamination croisée avec la cuisine avant d’enregistrer. La liste affichée au client reflète uniquement les sélections Airtable.
4. Vérifiez la carte publique et le détail sous le plat. Le bouton **Allergènes** donne accès à la liste complète des 14 familles.

Ne laissez pas une fiche vide après une modification de recette : renseignez les allergènes avant de remettre le plat en vente. La valeur `Allergenes` est une sélection multiple ; les valeurs initiales du projet sont indicatives et doivent être confirmées par le restaurateur à partir des recettes et des fournisseurs.

## Vue salle

Ouvrez `/salle.html` depuis la page QR des tables ou depuis l’écran cuisine. La liste montre les tables Airtable et place en tête les additions demandées, puis les commandes les plus anciennes. **Marquer servie** et **Libérer la table** enregistrent l’état dans le champ `Etat` d’Airtable ; l’écran retombe sur des tables de démonstration si le webhook n’est pas joignable.
