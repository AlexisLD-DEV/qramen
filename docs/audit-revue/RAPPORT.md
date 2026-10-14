# Revue indépendante et critique de l’audit QR

14 octobre 2026 — dépôt `/srv/projects/shared/qramen` — référence relue : `15d4a6e`.

## Verdict

L’audit précédent a amélioré la présentation, mais ses tests avec moteur bloqué ne permettaient pas de conclure à la robustesse des commandes réelles. Cette revue a trouvé des régressions liées à la confirmation persistante, des corrections de contraste/préchargement incomplètes, et des défauts antérieurs du moteur et du mode dégradé. Les corrections fonctionnelles ci-dessous sont déployées sur les deux domaines et sur le Worker partagé. Des limites serveur restent ouvertes ; elles sont détaillées sans présenter le système comme entièrement fiabilisé.

Le rapport précédent, tout le diff applicatif du commit et l’historique récent des changements de thème/accueil ont été relus. Les tests de cette revue sont de nouvelles exécutions Chromium/Playwright, pas une reprise de ses résultats. Preuves et scripts : `/srv/projects/shared/qramen/docs/audit-revue/`.

## Défauts corrigés

| Défaut | Origine / constat critique | Correction |
|---|---|---|
| Confirmation d’un envoi échoué | Antérieur : une erreur HTTP ou réseau produisait un numéro fictif, vidait le panier et ouvrait une confirmation « cuisine ». | Simulation réservée au mode démo explicite ; échec réel affiché dans le tiroir, panier conservé. |
| Rejeu d’un POST sur deux moteurs | Antérieur : après erreur/timeout du Worker, le même POST était envoyé à n8n ; le premier pouvait déjà avoir créé la commande. | Repli automatique limité aux GET/HEAD. Les écritures échouent explicitement sur le moteur principal. |
| Double clic et modifications pendant l’envoi | Le simple `disabled` pouvait être annulé par un nouveau rendu du panier ; aucun verrou logique. | Verrou d’envoi, panier vide refusé, quantités bloquées pendant l’envoi ; double clic testé : un POST. |
| Rechargement pendant un POST | Le panier survivait, mais rien n’indiquait qu’un envoi pouvait déjà avoir eu lieu. | Trace persistante de l’envoi non confirmé, avertissement au retour, aucune reprise automatique. Cela ne constitue pas une garantie d’idempotence serveur. |
| Confirmation persistante et clavier | Correction de `15d4a6e` incomplète : fond accessible, Shift+Tab depuis le titre échappait au dialogue ; Escape déplaçait le focus même hors panier. | Fond rendu inert, confirmation inactive inert/ARIA-hidden, boucle limitée aux boutons visibles, Escape limité au tiroir ouvert. |
| Quantités/filtres au clavier | Rendus reconstruisant les boutons : focus perdu après Enter sur +/− ou un filtre. | Focus restauré sur le contrôle correspondant, filtres `aria-pressed`, conservation du focus pendant la synchronisation. |
| Nom accessible du panier | Audit ajoutant une annonce au compteur, mais le bouton gardait « Panier, 0 article ». | Nom accessible mis à jour avec la quantité et la langue. |
| Identité d’ordre et addition | Le Worker renvoie `commande`, le client ne lisait que `id`. Une commande démo restaurée pouvait demander une addition réelle après retour du réseau ; une erreur d’addition affichait un succès. | Lecture des deux champs, mode de l’ordre séparé du mode du menu, erreur d’addition explicite, bouton réinitialisé entre commandes. |
| Quantités altérées et grands paniers | Stockage/paramètre `panier` sans validation ; serveur transformant 0 en 1 ; Airtable accepte au maximum dix créations par lot. | Entrées invalides écartées ; entier 1–999 contrôlé client/serveur, plafonnement à 999 ; écritures par lots de dix. Test moteur : 16 lignes en lots 10+6. |
| Enseignes des commandes mixtes | Le Worker supprimait `concept` lors de la normalisation, donc toutes les lignes étaient étiquetées QRamen. | Concept conservé ; tickets et cuisine distinguent QRamen/QRoque. |
| Table en cuisine et en salle | Cuisine affichant « Sur place » ; nouvelle commande sur une table Libre masquée en salle par son état. | Identifiant Txx résolu en cuisine ; table mise En cours après création de la commande. |
| Notes perdues dans les tickets | Désignation Airtable affichée sans la note conservée dans `Ligne`. | Note ajoutée à la désignation cuisine/ticket ; vérification en ligne sur la commande 25. |
| Tickets inaccessibles | Le Worker renvoyait un booléen, le front attendait `ticketUrl`. Les nouveaux ordres n’ont pas de PDF joint. | URL des pièces jointes exposée ; bouton « Imprimer ticket » produisant un ticket depuis les données cuisine, enregistrable en PDF par le navigateur. |
| Cuisine hors connexion | « Épuiser » reconstruisait une autre liste de quatre plats et pouvait perdre l’élément modifié. | Modification de la liste effectivement affichée ; huit plats conservés, disponibilité correctement basculée. |
| Générateur QR | Vider le champ le remettait immédiatement à T01 ; texte de table interpolé en HTML imprimable ; impression après 80 ms sans attendre les images, rappel `print()` depuis `beforeprint`. | Champ librement éditable, HTML échappé, attente du décodage des images, préparation sans réimpression dans `beforeprint`. Avertissement pour les tables hors T01–T07, choix du nom conservé. |
| Contraste du compteur | Correction précédente non effective pour QRamen : texte sombre sur or sombre, **3,06:1**. | Fond or clair et texte sombre explicite, y compris en mode sombre : **10,15:1**. Messages d’erreur également lisibles en mode sombre. |
| Préchargement des polices | `15d4a6e` préchargeait Fraunces/Inter, mais les règles finales du thème utilisent Baloo 2/Nunito. | Préchargements des polices effectivement utilisées ; aucune modification du choix typographique. |
| Rendus de menu inutiles | Carte de secours initiale différente du snapshot local, puis reconstruction complète à la réponse moteur. | Snapshot local chargé en parallèle de la requête ; ajout désactivé jusqu’au résultat moteur/repli ; cartes identiques conservées dans le DOM. Pas de promesse de LCP inférieur à une seconde. |

## Vérifications en navigateur

Deux domaines, **390 × 844** et **1440 × 900** pour la matrice responsive : accueil, menu T01 à T07, cuisine, salle et QR. **44 vues avant et 44 après**, puis **20 vues de contrôle final**. Zéro débordement horizontal, zéro erreur JavaScript dans ces matrices. Accueils exactement à la hauteur du viewport, sans scroll. Les images finales et les JSON sont conservés. Inspection visuelle de captures accueil/menu/cuisine/QR : aucun écart de gabarit justifiant une refonte.

- Les quatre boutons de démo ont été activés avec **Enter**, sur chaque domaine et chaque largeur.
- Parcours **Tab complet sur 20 pages** : aucune cible visitée sans outline visible ; panier, filtres et allergènes testés avec Enter/Escape ; confirmation testée avec Tab/Shift+Tab après rechargement. Ce contrôle navigateur ne remplace pas un test avec lecteur d’écran.
- Deux commandes mixtes réellement envoyées depuis les deux enseignes : **25** (départ QRamen, 390 px) et **26** (départ QRoque, 1440 px), T07, ramen tonkotsu + croque monsieur. Un POST chacune, confirmation restaurée, deux lignes correctes, commande retrouvée en cuisine et salle, passage En cours puis Servi, ticket imprimable exporté en PDF. Commande technique **24** également clôturée : premier essai interrompu par une assertion attendant la colonne mobile cachée, puis script corrigé pour sélectionner « En cours ». Aucun défaut applicatif attribué à cette assertion.
- Les commandes techniques 24–26 sont **Servies** ; T07 remise à son état initial **Libre**. Elles restent dans l’historique, identifiées comme essais techniques ; aucun ordre existant modifié.
- Pièces jointes PDF existantes ouvertes par requête depuis le contexte navigateur : **HTTP 200, application/pdf**, sur les deux sites et aux deux largeurs.
- Moteurs volontairement injoignables : menu local, commande simulée, cuisine (statut/disponibilité), salle (occupation/service/libération), sept QR locaux. **Zéro POST** vers les moteurs. 1002 ajouts rapides plafonnés à 999 sans erreur.
- Erreur HTTP 502 et délai contrôlé : double clic, panier conservé, confirmation absente ; rechargement pendant un POST lent : un POST, panier restauré, avertissement visible.
- Panier vide : envoi désactivé. Quantités serveur 0, négative, décimale et 1000 : HTTP 400 avant toute écriture, par test isolé du Worker.
- Générateur : édition T07, suppression complète du champ, téléchargements PNG/SVG, impression PDF ; entrée HTML affichée comme texte, jamais interprétée comme balise. T99 reste une commande locale.

Preuves principales : `avant-live.json`, `apres-live.json`, `final-live.json`, `clavier-live.json`, `tests-live.json`, `tests-reload.json`, `tests-engine.json`, `hors-connexion.json`, `verification-finale.json`, `commandes-reelles.json`, `ticket-reel-donnees-final.json`, PDFs et captures.

## Performances et contrastes mesurés

Chromium headless, contexte neuf par page, **4G simulée : 150 ms, 1,6 Mbps descendant, 750 Kbps montant**. Moteur réel laissé accessible, observation jusqu’à networkidle + 2 s, sans interaction. Une exécution par combinaison ; ce sont des mesures de laboratoire, pas un percentile de terrain. Le cumul des shifts sans interaction sert ici de relevé CLS. Les JSON bruts avant/intermédiaire/final permettent de constater la variabilité.

| Domaine | Largeur | LCP accueil | CLS accueil | LCP menu | CLS menu |
|---|---:|---:|---:|---:|---:|
| QRamen | 390 | 860 ms | 0,001872 | 5736 ms | 0,003813 |
| QRamen | 1440 | 892 ms | 0,005186 | 6424 ms | 0,002076 |
| QRoque | 390 | 956 ms | 0,002157 | 5712 ms | 0,005003 |
| QRoque | 1440 | 964 ms | 0,005356 | 5424 ms | 0,002492 |

**Le menu reste lent en 4G réelle simulée avec le moteur : 5,42–6,42 s de LCP.** Avant revue : jusqu’à 6,92 s. Les 0,83–0,99 s de l’audit précédent provenaient d’un moteur bloqué et d’un environnement local ; ces chiffres ne démontraient pas la performance du parcours en production. Je ne présente pas les changements de préchargement/rendu comme une résolution complète. Un profilage réseau et rendu dédié reste nécessaire ; l’exécution distante et ses délais ne sont pas équivalents au scénario local.

Couples couleur/fond calculés avec la luminance relative WCAG, à partir des couleurs du navigateur et des valeurs finales : compteur **10,15:1**, bouton ticket **14,07:1**, message sombre **10,43:1**. Prix visibles **6,30:1** QRamen / **9,13:1** QRoque ; bouton de démo **7,11:1** ; note d’accueil minimale échantillonnée **5,19:1**. Cela couvre les ajouts/corrections échantillonnés, pas tous les pixels ni une certification générale. Preuves : `performance-live.json`, `contrastes-ajouts.json`, `verification-finale.json`.

## Non corrigé : limites et décisions à préserver

1. **Idempotence et transactions serveur.** Double clic et replay inter-moteurs évités côté client, mais deux onglets, un retry manuel après perte de réponse ou une panne entre les lots peuvent encore produire un doublon/ordre partiel. Airtable est écrit par étapes ; un identifiant unique et une persistance transactionnelle demandent une évolution du contrat/backend. L’avertissement après interruption est une réduction du risque, pas une preuve de non-création.
2. **Contrôle du personnel.** Les écrans publiquement accessibles agissent réellement sur cuisine, disponibilité et salle. Le Worker n’exige pas d’identité pour ces routes. La revue ne transforme pas les démos voulues en un parcours d’authentification : protéger les écritures demande une décision sur les accès personnel et le comportement public des démos. C’est un point opérationnel important avant usage hors démonstration.
3. **PDF automatique attaché.** `/test-pdf` du Worker produit du JSON, pas un PDF ; le Worker ne déclenche pas le pipeline n8n/PDF/Airtable. L’impression depuis la cuisine fonctionne et les anciennes pièces jointes sont accessibles, mais aucun PDF automatique n’est promis pour un nouvel ordre. Rebrancher la génération distante sans connaître le comportement voulu serait risqué.
4. **Historique Servi de la cuisine.** Le moteur exclut les commandes terminées : après « Servi », la carte disparaît au prochain refresh, alors que la colonne existe. Afficher tout l’historique ou une fenêtre récente demande de choisir une durée/règle ; cette règle n’a pas été inventée dans la revue.
5. **Addition et état Terminee.** Le moteur traite Servi comme Terminee, et sa vue salle exclut les additions liées à ce statut. Une demande d’addition peut donc ne pas remonter comme attendu. La revue corrige les faux succès réseau du client, mais ne change pas la définition du cycle service/paiement sans choisir quand une table/commande est réellement close.
6. **Confirmation/panier entre origines.** Le panier est transmis lors du changement d’enseigne ; localStorage et confirmation restent propres à chaque origine. La confirmation n’est pas synchronisée entre deux appareils/onglets/domaines. Transformer cela en session serveur dépasserait les corrections locales.
7. **Disponibilité au moment de l’envoi.** Les quantités/identifiants sont validés, mais le moteur ne revalide pas le prix et la disponibilité de chaque plat avant écriture. Un panier ancien peut viser un plat devenu indisponible. À traiter avec la validation serveur et la politique de rupture/reprise de commande.
8. **Performance du menu**, détaillée ci-dessus, reste à améliorer avec profilage dédié.

Choix subjectifs laissés : taille/pâleur de la mascotte mobile QRoque, petites notes du hero, place importante entre hero et carte, recadrages des photos, différences de palette entre les enseignes. Aucune uniformisation esthétique imposée. **Mascottes comme logos, thème clair par défaut, CROQUE, kanji QRamen, accueil sans scroll, démos dans le hero, footer alexisld.fr + GitHub conservés.** Cuisine et salle restent partagées entre les enseignes : aucune séparation des commandes mixtes inventée.

## Livraison

Pages déployées avec la commande demandée `npx wrangler pages deploy public --project-name qramen --branch main --commit-dirty=true`. Le Worker a également dû être déployé pour rendre effectives les corrections d’enseigne, table, notes, quantité et liens de ticket ; son seul code était insuffisant sans publication.

Version Worker finale : `ac9190db-9a1c-4e28-9743-8eca847e1738`. Les secrets existants ont été utilisés uniquement par Wrangler, sans être enregistrés dans les preuves ou le dépôt.

Publication Pages finale : https://657df96f.qramen.pages.dev (branche main). Contrôles des domaines publics et tests fonctionnels après publication réussis. Commit de livraison intitulé `Fix QR order regressions and document independent review` ; référence exacte ajoutée au rapport de mission après commit et push.
