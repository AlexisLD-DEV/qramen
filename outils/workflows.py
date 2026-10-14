#!/usr/bin/env python3
"""Genere les workflows n8n du QRamen (versionnes ici, importables par le CLI du conteneur).

Usage : python3 outils/workflows.py            -> ecrit etat/wf-*.json
        (l'import se fait ensuite avec : sudo -n docker cp ... && n8n import:workflow)
"""
import json, pathlib

BASE = "appBHi3MxCb0hW1yH"
T_PLATS, T_TABLES, T_CMDES, T_LIGNES = "tbl4riw5L76eRvSsN", "tblsdUES4NrSjkiWT", "tblKs9b4rmMzoSAJy", "tblNmtM5qYLKyQZW9"
CLE_PDF = pathlib.Path("/srv/hermes/.hermes/.secrets/qramen-pdf.key").read_text().strip() if pathlib.Path("/srv/hermes/.hermes/.secrets/qramen-pdf.key").exists() else ""
CRED = {"httpHeaderAuth": {"id": "qramenPatCred", "name": "QRamen — Airtable"}}
AT = "https://api.airtable.com/v0/" + BASE
SORTIE = pathlib.Path(__file__).resolve().parent.parent / "etat"

CODE_RESTAU = """const q = ($('Webhook').first().json.query || {});
const concept = q.concept || 'QRamen';
const infos = {
  QRamen: { nom: 'Le QRamen', baseline: 'Scannez. Commandez. Slurpez.', ville: 'Rouen',
            cuisine: 'Cuisine japonaise', devise: 'EUR' },
  QRoque: { nom: 'QRoque Monsieur', baseline: 'Le bistrot du croque, qui se scanne.', ville: 'Rouen',
            cuisine: 'Croques & bistrot', devise: 'EUR' },
}[concept] || null;
const categories = [
  { id: 'Entree', nom: 'Entrees' }, { id: 'Plat', nom: 'Plats' },
  { id: 'Dessert', nom: 'Desserts' }, { id: 'Boisson', nom: 'Boissons' },
];
const plats = ($json.records || [])
  .map(r => ({ id: r.id, ...r.fields }))
  .filter(f => (f.Concept || 'QRoque') === concept && f.Disponible !== false)
  .map(f => ({ id: f.id, nom: f.Plat, description: f.Description || '', prix: f.Prix || 0,
               categorie: f.Categorie || 'Plat', photo: 'assets/img/' + (f.Photo || 'default.webp'),
               disponible: f.Disponible !== false, allergenes: f.Allergenes || [], tags: [] }));
return [{ json: { restaurant: infos, concept, categories, plats } }];"""


CODE_TICKET = """const cmd = $('Creer la commande').first().json;
const prep = $('Preparer les lignes').first().json;
const lignes = prep.ticketLignes || [];
const numero = (cmd.fields && cmd.fields.Numero) ? cmd.fields.Numero : '';
const name = 'Le QRamen · QRoque Monsieur';
const mascot = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 72"><path d="M14 31q36-33 72 0" fill="#eab653" stroke="#33241d" stroke-width="4"/><path d="M17 34h66l-8 24H25z" fill="#d86438" stroke="#33241d" stroke-width="4" stroke-linejoin="round"/><path d="M20 37h60" stroke="#f4d37f" stroke-width="5"/><path d="M11 62h78" stroke="#33241d" stroke-width="5" stroke-linecap="round"/></svg>`;
const html = `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><style>
@page{size:80mm 200mm;margin:6mm}
body{font-family:Arial,Helvetica,sans-serif;color:#111;margin:0}
.brand{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #bbb;padding-bottom:2mm;margin-bottom:3mm}.brand strong{font-size:12pt}.mascot{width:15mm;height:11mm;flex:none}
h1{font-size:19pt;margin:0 0 2mm}
.meta{font-size:11pt;margin-bottom:4mm;line-height:1.5}
table{width:100%;border-collapse:collapse;font-size:12pt}
td{padding:1.6mm 0;border-bottom:1px dashed #999}
.q{width:12mm;padding-right:1mm;text-align:right;font-weight:bold;white-space:nowrap}
.pied{margin-top:5mm;font-size:7pt;color:#333;line-height:1.4}
</style></head><body>
<div class="brand"><strong>${name}</strong>${mascot}</div><h1>Ticket cuisine</h1>
<div class="meta"><b>Commande #${numero}</b><br>Table ${$('Lire la commande').first().json.table}<br>${new Date().toLocaleString('fr-FR')}</div>
<table>${lignes.map(l => `<tr><td><b>${l.concept === 'QRoque' ? '🥪 QRoque Monsieur' : '🍜 Le QRamen'}</b><br>${l.nom}${l.note ? `<br><small>${l.note}</small>` : ''}</td><td class="q">x${l.quantite || 1}</td></tr>`).join('')}</table>
<div class="pied">14 rue du Gros-Horloge, 76000 Rouen<br>alexisld.fr</div>
</body></html>`;
return [{ json: { html, id: cmd.id, numero } }];"""

WF_MENU = {
    "id": "qramenMenu01",
    "name": "QRamen — menu",
    "nodes": [
        {"parameters": {"httpMethod": "GET", "path": "qramen/menu", "responseMode": "responseNode", "options": {"allowedOrigins": "*"}},
         "id": "m1", "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2,
         "position": [0, 0], "webhookId": "qramen-menu"},
        {"parameters": {"url": AT + "/" + T_PLATS + "?filterByFormula=%7BDisponible%7D%3DTRUE()&pageSize=100",
                        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
                        "options": {}},
         "id": "m2", "name": "Airtable — plats", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [220, 0], "credentials": CRED},
        {"parameters": {"jsCode": CODE_RESTAU}, "id": "m3", "name": "Mettre en forme", "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [440, 0]},
        {"parameters": {"respondWith": "json", "responseBody": "={{ $json }}", "options": {}},
         "id": "m4", "name": "Repondre", "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.1,
         "position": [660, 0]},
    ],
    "connections": {"Webhook": {"main": [[{"node": "Airtable — plats", "type": "main", "index": 0}]]},
                    "Airtable — plats": {"main": [[{"node": "Mettre en forme", "type": "main", "index": 0}]]},
                    "Mettre en forme": {"main": [[{"node": "Repondre", "type": "main", "index": 0}]]}},
    "settings": {"executionOrder": "v1"},
    "active": False,
}

CODE_CMD = """const b = $json.body || $json;
const ordre = { QRamen: 0, QRoque: 1 };
const lignes = (b.lignes || []).map(l => ({ platId: l.platId, quantite: Math.max(1, Number(l.quantite) || 1),
  note: l.note || '', nom: l.nom || '', concept: l.concept || b.concept || 'QRamen' }))
  .sort((a, b) => (ordre[a.concept] ?? 9) - (ordre[b.concept] ?? 9) || a.nom.localeCompare(b.nom));
if (!b.table || !lignes.length) { throw new Error('table et lignes sont obligatoires'); }
return [{ json: { table: b.table, concept: b.concept || 'QRamen', lignes, total: b.total || 0 } }];"""

CODE_LIGNES = """const cmd = $('Creer la commande').first().json;
const prep = $('Lire la commande').first().json;
const labels = { QRamen: '🍜 Le QRamen', QRoque: '🥪 QRoque Monsieur' };
const recs = prep.lignes.map(l => ({ fields: { Ligne: '[' + (labels[l.concept] || l.concept) + ']' + (l.note ? ' ' + l.note : ''), Quantite: l.quantite,
  Plat: [l.platId], Commande: [cmd.id] } }));
return [{ json: { commande: cmd.id, numero: cmd.fields.Numero, statut: cmd.fields.Statut, records: recs,
  ticketLignes: prep.lignes.map(l => ({ nom: l.nom || l.platId, quantite: l.quantite, concept: l.concept, note: l.note })) } }];"""

WF_CMD = {
    "id": "qramenCommande01",
    "name": "QRamen — commande",
    "nodes": [
        {"parameters": {"httpMethod": "POST", "path": "qramen/commande", "responseMode": "responseNode", "options": {"allowedOrigins": "*"}},
         "id": "c1", "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2,
         "position": [0, 0], "webhookId": "qramen-commande"},
        {"parameters": {"jsCode": CODE_CMD}, "id": "c2", "name": "Lire la commande",
         "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [220, 0]},
        {"parameters": {"url": "={{ '" + AT + "/" + T_TABLES + "?maxRecords=1&filterByFormula=' + encodeURIComponent('{Identifiant}=\"' + $json.table + '\"') }}",
                        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}},
         "id": "c3", "name": "Trouver la table", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [440, 0], "credentials": CRED},
        {"parameters": {"method": "POST", "url": AT + "/" + T_CMDES,
                        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
                        "sendBody": True, "specifyBody": "json",
                        "jsonBody": "={{ JSON.stringify({ fields: { Statut: 'En attente', Table: [ $json.records[0].id ] } }) }}",
                        "options": {}},
         "id": "c4", "name": "Creer la commande", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [660, 0], "credentials": CRED},
        {"parameters": {"jsCode": CODE_LIGNES}, "id": "c5", "name": "Preparer les lignes",
         "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [880, 0]},
        {"parameters": {"method": "POST", "url": AT + "/" + T_LIGNES,
                        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
                        "sendBody": True, "specifyBody": "json",
                        "jsonBody": "={{ JSON.stringify({ records: $json.records }) }}", "options": {}},
         "id": "c6", "name": "Creer les lignes", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [1100, 0], "credentials": CRED},
        {"parameters": {"jsCode": CODE_TICKET}, "id": "c9", "name": "PDF ticket cuisine",
         "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1320, 300]},
        {"parameters": {"method": "POST", "url": "http://172.19.0.1:8798/pdf?json=1", "sendBody": True,
                        "sendHeaders": True, "headerParameters": {"parameters": [{"name": "X-PDF-Key", "value": CLE_PDF}]},
                        "specifyBody": "json", "jsonBody": "={{ JSON.stringify({ html: $json.html, nom: 'ticket-' + $json.numero }) }}",
                        "options": {}},
         "id": "c10", "name": "Imprimer le ticket", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [1540, 300]},
        {"parameters": {"method": "POST",
                        "url": "={{ 'https://content.airtable.com/v0/appBHi3MxCb0hW1yH/' + $('Creer la commande').item.json.id + '/Ticket%20cuisine/uploadAttachment' }}",
                        "sendBody": True, "specifyBody": "json",
                        "jsonBody": "={{ JSON.stringify({ contentType: 'application/pdf', filename: $json.filename, file: $json.base64 }) }}",
                        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}},
         "id": "c11", "name": "Attacher le ticket", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [1760, 300], "credentials": CRED},
        {"parameters": {"method": "PATCH", "url": "={{ 'https://api.airtable.com/v0/appBHi3MxCb0hW1yH/Commandes/' + $('Creer la commande').item.json.id }}",
                        "sendBody": True, "specifyBody": "json",
                        "jsonBody": "={{ JSON.stringify({ fields: { 'Ticket imprime': true } }) }}",
                        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}},
         "id": "c12", "name": "Marquer imprime", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [1980, 300], "credentials": CRED},
        {"parameters": {"jsCode": "const p = $('Preparer les lignes').first().json;\nreturn [{ json: { ok: true, numero: p.numero, statut: p.statut, commande: p.commande } }];"},
         "id": "c7", "name": "Reponse", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1320, 0]},
        {"parameters": {"respondWith": "json", "responseBody": "={{ $json }}", "options": {}},
         "id": "c8", "name": "Repondre", "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.1,
         "position": [1540, 0]},
    ],
    "connections": {
        "Webhook": {"main": [[{"node": "Lire la commande", "type": "main", "index": 0}]]},
        "Lire la commande": {"main": [[{"node": "Trouver la table", "type": "main", "index": 0}]]},
        "Trouver la table": {"main": [[{"node": "Creer la commande", "type": "main", "index": 0}]]},
        "Creer la commande": {"main": [[{"node": "Preparer les lignes", "type": "main", "index": 0}]]},
        "Preparer les lignes": {"main": [[{"node": "Creer les lignes", "type": "main", "index": 0}]]},
        "Creer les lignes": {"main": [[{"node": "PDF ticket cuisine", "type": "main", "index": 0}]]},
        "PDF ticket cuisine": {"main": [[{"node": "Imprimer le ticket", "type": "main", "index": 0}]]},
        "Imprimer le ticket": {"main": [[{"node": "Attacher le ticket", "type": "main", "index": 0}]]},
        "Attacher le ticket": {"main": [[{"node": "Marquer imprime", "type": "main", "index": 0}]]},
        "Marquer imprime": {"main": [[{"node": "Reponse", "type": "main", "index": 0}]]},
        "Reponse": {"main": [[{"node": "Repondre", "type": "main", "index": 0}]]},
    },
    "settings": {"executionOrder": "v1"},
    "active": False,
}

WF_STATUT = {
    "id": "qramenStatut01",
    "name": "QRamen — statut",
    "nodes": [
        {"parameters": {"httpMethod": "GET", "path": "qramen/statut", "responseMode": "responseNode", "options": {"allowedOrigins": "*"}},
         "id": "s1", "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2,
         "position": [0, 0], "webhookId": "qramen-statut"},
        {"parameters": {"url": "=" + AT + "/" + T_CMDES + "?maxRecords=1&filterByFormula=%7BNumero%7D%3D" + "{{ $json.query.numero }}",
                        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}},
         "id": "s2", "name": "Chercher la commande", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [220, 0], "credentials": CRED},
        {"parameters": {"jsCode": "const r = ($json.records || [])[0];\nif (!r) return [{ json: { trouve: false } }];\nconst f = r.fields;\nreturn [{ json: { trouve: true, id: r.id, numero: f.Numero, statut: (f.Statut === 'Terminee' ? 'Servi' : f.Statut),\n  addition: { demandee: !!f['Addition demandee'], url: (f.Addition && f.Addition[0] && f.Addition[0].url) || null } } }];"},
         "id": "s3", "name": "Mettre en forme", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [440, 0]},
        {"parameters": {"respondWith": "json", "responseBody": "={{ $json }}", "options": {}},
         "id": "s4", "name": "Repondre", "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.1,
         "position": [660, 0]},
    ],
    "connections": {"Webhook": {"main": [[{"node": "Chercher la commande", "type": "main", "index": 0}]]},
                    "Chercher la commande": {"main": [[{"node": "Mettre en forme", "type": "main", "index": 0}]]},
                    "Mettre en forme": {"main": [[{"node": "Repondre", "type": "main", "index": 0}]]}},
    "settings": {"executionOrder": "v1"},
    "active": False,
}

SORTIE.mkdir(parents=True, exist_ok=True)
for wf in (WF_MENU, WF_CMD, WF_STATUT):
    p = SORTIE / f"wf-{wf['id']}.json"
    p.write_text(json.dumps(wf, ensure_ascii=False, indent=2))
    print("ecrit", p)
