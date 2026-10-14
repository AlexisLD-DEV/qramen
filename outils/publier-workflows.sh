#!/usr/bin/env bash
# Importe, publie et redemarre les workflows du QRamen (le brouillon doit etre PUBLIE pour tourner).
# IMPORTANT : les CINQ workflows du parcours doivent figurer dans la boucle d'activation.
# Sinon import:workflow les desactive et leurs webhooks repondent 404 en silence (panne du 13/10).
set -euo pipefail
cd /srv/projects/shared/qramen
python3 outils/workflows.py >/dev/null
python3 outils/workflow-cuisine.py >/dev/null
python3 outils/workflow-addition.py >/dev/null
for f in etat/wf-qramen*.json; do
  b=$(basename "$f")
  sudo -n docker cp "$f" "n8n-n8n-1:/tmp/$b" >/dev/null
  sudo -n docker exec n8n-n8n-1 n8n import:workflow --input="/tmp/$b" >/dev/null 2>&1
done
for id in qramenMenu01 qramenCommande01 qramenStatut01 qramenCuisine01 qramenAddition01; do
  sudo -n docker exec n8n-n8n-1 n8n update:workflow --id=$id --active=true >/dev/null 2>&1
  sudo -n docker exec n8n-n8n-1 n8n publish:workflow --id=$id >/dev/null 2>&1
done
sudo -n docker restart n8n-n8n-1 >/dev/null 2>&1
echo "workflows importes + publies (menu, commande, statut, cuisine/carte/disponibilite, addition), n8n redemarre"
