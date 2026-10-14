# Rapport — quatre mascottes

Réalisé le 14 octobre 2026. Orchestration par l’agent **gpt-6-astra**, génération et corrections par l’outil intégré **imagegen**. Le modèle interne de génération d’images n’est pas exposé par cet outil ; il ne faut pas le confondre avec le modèle de l’agent.

## Fichiers livrés et contrôles

| Fichier | Dimensions | Poids (octets) | Écart-type RGB |
|---|---:|---:|---|
| `docs/mascottes/ramen-1-bol.png` | 1024 × 1024 | 825143 | 25,52 / 49,12 / 58,03 |
| `docs/mascottes/ramen-2-chat.png` | 1024 × 1024 | 833420 | 28,78 / 50,28 / 57,78 |
| `docs/mascottes/croque-1-croque.png` | 1024 × 1024 | 1034863 | 22,62 / 42,02 / 63,56 |
| `docs/mascottes/croque-2-monsieur.png` | 1024 × 1024 | 942678 | 42,56 / 58,43 / 65,43 |

Les dimensions ont été lues dans les en-têtes PNG. Chaque fichier a été décodé par FFmpeg et sa variance colorimétrique calculée : aucun n’est vide ou uniforme. Les quatre fichiers finaux ont ensuite été ouverts séparément avec `view_image` et regardés.

## Avis visuel

La série est cohérente : contours brun chaud arrondis, yeux ronds brillants, joues roses, crème, rouge brique et doré. Le bol possède ses deux volutes et des nouilles débordantes ; le chat tient une unique baguette dans sa patte ; le croque montre ses deux tranches, sa moustache et le fromage fondu ; le monsieur porte un gilet de serveur et présente un croque sur son plateau. Aucun texte ou lettre visible, aucun sujet coupé. Le rendu est dessiné, sans photographie ni rendu 3D.

Réserves honnêtes : le fond crème est visuellement simple mais présente une très légère texture et des variations de ton, ce n’est pas un aplat numérique parfaitement uniforme. Les aliments ont davantage de détails et de reflets que les visages ; l’ensemble reste une même famille graphique, avec un rendu un peu plus gourmand et peint que des aplats stricts. Quelques touches de vert apparaissent dans les garnitures. Les marges visibles sont d’environ 20 % minimum de chaque côté ; le serveur est le plus proche de cette limite. Les proportions du sujet varient légèrement selon la silhouette.

## Méthode

Quatre générations individuelles demandées et obtenues en 1536 × 1024. Prompts stylistiques communs pour le bol et le chat ; images précédentes utilisées comme références de style pour le croque et le serveur. Deux corrections supplémentaires via imagegen réduisent le sujet du bol et du croque pour obtenir les marges demandées.

Recadrage carré autorisé effectué avec FFmpeg, sans agrandissement, sans réduction et sans ajout de fond par code : `crop=1024:1024:256:0` pour les trois premiers, et `crop=1024:1024:249:0` pour le serveur afin de centrer sa silhouette. Aucun fichier préexistant remplacé. Aucun code applicatif modifié.

## Prompts transmis

### 1 — Bol

```text
Use case: illustration-story. Create ONE standalone mascot illustration, landscape canvas exactly 1536x1024 pixels. Flat warm cream background #FFF5E5. Subject centered inside central 600x600 pixels, leaving ample blank space so cropping canvas to central 1024x1024 retains at least 20 percent margin on every side. A personified ramen bowl, brick-red ceramic with cream lip, a cute expressive face on bowl: two round dark-brown shiny eyes with two tiny cream highlights each, rose-pink round cheeks, small happy curved mouth. Golden noodles visibly spill over rim, toppings kept simple and warm colored. Exactly two delicate curling spiral steam wisps above. Consistent hand-drawn kawaii manga illustration, rounded warm dark-brown outlines of even medium thickness, soft flat colors with very light warm shadows, cream / brick-red / golden ochre / brown restrained palette. Entire mascot including steam visible, generous empty background, charming crafted illustration. NO text, NO letters, NO numerals, NO logos or watermark, no 3D, no photorealism, no emoji rendering, no scene or decorative border.
```

### 2 — Chat

```text
Use case: illustration-story. ONE standalone mascot illustration in a coherent kawaii manga restaurant series. Canvas 1536x1024 landscape. Uniform warm cream #FFF5E5 background. Draw mascot SMALL, centered: all subject pixels including chopstick and shadow inside x=470..1066 y=215..809, so central square crop retains 20 percent margin. A modern cute maneki-neko cream cat sitting inside a brick-red ramen bowl with cream rim and golden noodles visible. Cat has neat triangular ears with rosy inner ears, two round dark-brown shiny eyes each with two tiny cream catchlights, pink round cheeks, little smiling cat mouth. One raised paw holds exactly one brown chopstick. Simple small brick-red collar, no coin, no writing. Use rounded medium-weight warm dark-brown outlines, soft flat cream, brick red, golden ochre, brown colors, slight warm shadows only; crafted hand-drawn manga kawaii, consistent restaurant mascot drawing. Entire cat, bowl, and chopstick visible. No extra characters. NO TEXT OR LETTERS anywhere, no numerals, logos, watermark, border, no 3D, photo, emoji style.
```

### 3 — Croque

```text
Use case: illustration-story. Create a NEW separate mascot, not a ramen bowl: a personified French croque-monsieur sandwich. Use the prior ramen illustration as STYLE REFERENCE ONLY: exactly same artist, rounded warm dark-brown outlines, round glossy brown eyes with tiny cream catchlights, rosy cheeks, cream / brick red / golden ochre / brown palette, soft flat hand-drawn kawaii manga colors and restrained light shadows. Subject: two thick golden toasted square bread slices, melted golden cheese visibly flowing between the slices, small cute curled dark-brown moustache under round shiny eyes, rosy cheeks, little happy mouth. The two bread slices must clearly form ONE sandwich. No extra character, hands or feet needed. Landscape canvas exactly 1536x1024. Flat warm cream #FFF5E5 backdrop. Center the WHOLE sandwich SMALL, no more than 590 pixels wide and 590 pixels tall, centered around x768 y512, blank space at least 220 pixels above/below; later central square crop must retain minimum 20 percent blank margins. No text, letters, numbers, watermark, logo, border or ornaments, no photorealism, no 3D, no emoji style.
```

### 4 — Monsieur

```text
Use case: illustration-story. Create ONE NEW separate mascot in the exact same illustrator style as reference images: a cute kawaii manga adult gentleman waiter, chest-up bust, neatly combed dark-brown hair, curled dark-brown moustache, two round glossy brown eyes with cream catchlights and pink round cheeks. Cream shirt, brick-red server waistcoat, small brown bow tie. He presents a golden croque-monsieur with visibly melted cheese on a small brown serving tray held with one hand. Consistent same rounded dark-brown outline strokes, softly flat colors and restrained warm shadows as references; palette warm cream, brick red, gold, brown. Entire bust silhouette, hair, elbows, tray and sandwich visible. Composition 1536x1024 landscape canvas, uniform light cream #FFF5E5 background, mascot drawn SMALL and centered within central 560x560 area, edges of all artwork at least 230px from top and bottom, large empty space required to later crop square with at least 20 percent margins on every side. NO text, letters, numbers, logos, watermark, photo, 3D or emoji style. No ramen bowl and no cat in this image; use references only for coherent drawing style.
```

### Correction de cadrage — Bol

```text
Edit target: attached ramen mascot. Change ONLY composition size and position: shrink ENTIRE illustration including exactly two steam spirals and floor shadow to 72 percent of current size, and center its complete bounding box precisely at x=768 y=512 on the same 1536x1024 landscape canvas. Target entire illustration height 535 pixels and width 520 pixels. Keep identical bowl, face, noodles, toppings, colors, linework, charming manga illustration style. Extend plain cream background smoothly; no border. Do not add anything. This is for a later square crop that requires 20 percent margins. No text or letters.
```

### Correction de cadrage — Croque

```text
Edit target: this croque-monsieur mascot. Change ONLY composition: reduce whole illustration and its floor shadow to 82 percent of current size and center the complete subject at (768,512) on unchanged 1536x1024 canvas. Final sandwich should be only 550 pixels wide and 435 pixels tall. Preserve exact sandwich appearance, two slices, melted cheese, shiny eyes, moustache, cheeks, outlines, palette and hand-drawn style. Extend plain cream backdrop seamlessly. Entire subject and shadow must fit within central 560x480 pixels; large blank margins are essential for later square crop. No new objects or text.
```

