#!/usr/bin/env python3
"""Ecrit le workflow n8n « cuisine » (liste des commandes ouvertes + changement de statut).
Ecrit directement le JSON dans etat/ (pas via le generateur) : plus simple a relire."""
import json, pathlib

BASE, T_PLATS, T_CMD, T_LIGNES = "appBHi3MxCb0hW1yH", "tbl4riw5L76eRvSsN", "tblKs9b4rmMzoSAJy", "tblNmtM5qYLKyQZW9"
AT = "https://api.airtable.com/v0/" + BASE
CRED = {"httpHeaderAuth": {"id": "qramenPatCred", "name": "QRamen — Airtable"}}

CODE_CUISINE = """const cmds = ($json.records || []).map(r => ({
  id: r.id,
  numero: r.fields.Numero,
  table: (r.fields.Table || []).length ? 'Sur place' : 'A emporter',
  statut: (r.fields.Statut === 'Terminee' ? 'Servi' : (r.fields.Statut || 'En attente')),
  heure: r.fields['Passee le'],
  passee: r.fields['Passee le'],
  additionDemandee: !!r.fields['Addition demandee'],
  ticket: !!(r.fields['Ticket cuisine'] || []).length,
  liens: r.fields.Lignes || [],
}));
const ids = cmds.flatMap(c => c.liens);
const retenu = cmds.filter(c => c.statut !== 'Terminee');
return [{ json: { commandes: retenu, lignesFormula: ids.length ? "OR(" + ids.map(i => "RECORD_ID()='" + i + "'").join(',') + ")" : "RECORD_ID()=''" } }];"""

CODE_FIN = """const lignes = ($json.records || []).map(r => ({
  id: r.id,
  commande: (r.fields.Commande || [])[0],
  designation: r.fields.Designation || r.fields.Ligne || '',
  quantite: r.fields.Quantite || 1,
}));
const premier = $('Preparer les commandes').first().json.commandes;
return [{ json: { commandes: premier.map(c => ({ ...c, lignes: lignes.filter(l => l.commande === c.id) })) } }];"""

CODE_MAJ = """const b = $('Webhook statut').first().json.body || {};
let statut = b.statut || 'En cours';
if (statut === 'Servi') statut = 'Terminee';
if (!['En attente', 'En cours', 'Terminee'].includes(statut)) statut = 'En cours';
return [{ json: { id: b.id, statut } }];"""

CODE_CARTE = """const concept = $('Webhook carte').first().json.query?.concept || 'QRamen';
const plats = ($json.records || []).map(r => ({ id: r.id, nom: r.fields.Plat || '',
  categorie: r.fields.Categorie || 'Plat', disponible: r.fields.Disponible !== false,
  concept: r.fields.Concept || 'QRoque' })).filter(p => p.concept === concept);
return [{ json: { concept, plats } }];"""

CODE_DISPO = """const b = $('Webhook disponibilite').first().json.body || {};
if (!b.id || typeof b.disponible !== 'boolean') throw new Error('id et disponible sont obligatoires');
return [{ json: { id: b.id, disponible: b.disponible } }];"""

def n(nid, name, typ, tv, pos, params, extra=None):
    d = {"parameters": params, "id": nid, "name": name, "type": typ, "typeVersion": tv, "position": pos}
    if extra:
        d.update(extra)
    return d

WF = {
    "id": "qramenCuisine01",
    "name": "QRamen — cuisine",
    "active": False,
    "nodes": [
        n("k1", "Webhook cuisine", "n8n-nodes-base.webhook", 2, [0, 0],
          {"httpMethod": "GET", "path": "qramen/cuisine", "responseMode": "responseNode",
           "options": {"allowedOrigins": "*"}}, {"webhookId": "qramen-cuisine"}),
        n("k2", "Commandes ouvertes", "n8n-nodes-base.httpRequest", 4.2, [220, 0],
          {"url": AT + "/" + T_CMD + "?maxRecords=40&sort%5B0%5D%5Bfield%5D=Numero&sort%5B0%5D%5Bdirection%5D=desc",
           "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}}, {"credentials": CRED}),
        n("k3", "Preparer les commandes", "n8n-nodes-base.code", 2, [440, 0], {"jsCode": CODE_CUISINE}),
        n("k4", "Lignes des commandes", "n8n-nodes-base.httpRequest", 4.2, [660, 0],
          {"url": "={{ '" + AT + "/" + T_LIGNES + "?filterByFormula=' + encodeURIComponent($json.lignesFormula) }}",
           "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}}, {"credentials": CRED}),
        n("k5", "Assembler", "n8n-nodes-base.code", 2, [880, 0], {"jsCode": CODE_FIN}),
        n("k6", "Repondre cuisine", "n8n-nodes-base.respondToWebhook", 1.1, [1100, 0],
          {"respondWith": "json", "responseBody": "={{ $json }}", "options": {}}),
        n("k7", "Webhook statut", "n8n-nodes-base.webhook", 2, [0, 220],
          {"httpMethod": "POST", "path": "qramen/cuisine/statut", "responseMode": "responseNode",
           "options": {"allowedOrigins": "*"}}, {"webhookId": "qramen-cuisine-statut"}),
        n("k8", "Lire le statut", "n8n-nodes-base.code", 2, [220, 220], {"jsCode": CODE_MAJ}),
        n("k9", "Mettre a jour", "n8n-nodes-base.httpRequest", 4.2, [440, 220],
          {"method": "PATCH", "url": "={{ '" + AT + "/" + T_CMD + "/' + $json.id }}",
           "sendBody": True, "specifyBody": "json",
           "jsonBody": "={{ JSON.stringify({ fields: { Statut: ($json.statut === 'Servi' ? 'Terminee' : $json.statut) } }) }}",
           "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}}, {"credentials": CRED}),
        n("k10", "Repondre statut", "n8n-nodes-base.respondToWebhook", 1.1, [660, 220],
          {"respondWith": "json", "responseBody": "={{ { ok: true, statut: $('Lire le statut').first().json.statut } }}",
           "options": {}}),
        n("k11", "Webhook carte", "n8n-nodes-base.webhook", 2, [0, 440],
          {"httpMethod": "GET", "path": "qramen/cuisine/carte", "responseMode": "responseNode",
           "options": {"allowedOrigins": "*"}}, {"webhookId": "qramen-cuisine-carte"}),
        n("k12", "Plats de la carte", "n8n-nodes-base.httpRequest", 4.2, [220, 440],
          {"url": AT + "/" + T_PLATS + "?pageSize=100", "authentication": "genericCredentialType",
           "genericAuthType": "httpHeaderAuth", "options": {}}, {"credentials": CRED}),
        n("k13", "Filtrer la carte", "n8n-nodes-base.code", 2, [440, 440], {"jsCode": CODE_CARTE}),
        n("k14", "Repondre carte", "n8n-nodes-base.respondToWebhook", 1.1, [660, 440],
          {"respondWith": "json", "responseBody": "={{ $json }}", "options": {}}),
        n("k15", "Webhook disponibilite", "n8n-nodes-base.webhook", 2, [0, 660],
          {"httpMethod": "POST", "path": "qramen/cuisine/disponibilite", "responseMode": "responseNode",
           "options": {"allowedOrigins": "*"}}, {"webhookId": "qramen-cuisine-disponibilite"}),
        n("k16", "Valider disponibilite", "n8n-nodes-base.code", 2, [220, 660], {"jsCode": CODE_DISPO}),
        n("k17", "Mettre a jour disponibilite", "n8n-nodes-base.httpRequest", 4.2, [440, 660],
          {"method": "PATCH", "url": "={{ '" + AT + "/" + T_PLATS + "/' + $json.id }}",
           "sendBody": True, "specifyBody": "json",
           "jsonBody": "={{ JSON.stringify({ fields: { Disponible: $json.disponible } }) }}",
           "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}}, {"credentials": CRED}),
        n("k18", "Repondre disponibilite", "n8n-nodes-base.respondToWebhook", 1.1, [660, 660],
          {"respondWith": "json", "responseBody": "={{ { ok: true, id: $('Valider disponibilite').first().json.id, disponible: $('Valider disponibilite').first().json.disponible } }}", "options": {}}),
    ],
    "connections": {
        "Webhook cuisine": {"main": [[{"node": "Commandes ouvertes", "type": "main", "index": 0}]]},
        "Commandes ouvertes": {"main": [[{"node": "Preparer les commandes", "type": "main", "index": 0}]]},
        "Preparer les commandes": {"main": [[{"node": "Lignes des commandes", "type": "main", "index": 0}]]},
        "Lignes des commandes": {"main": [[{"node": "Assembler", "type": "main", "index": 0}]]},
        "Assembler": {"main": [[{"node": "Repondre cuisine", "type": "main", "index": 0}]]},
        "Webhook statut": {"main": [[{"node": "Lire le statut", "type": "main", "index": 0}]]},
        "Lire le statut": {"main": [[{"node": "Mettre a jour", "type": "main", "index": 0}]]},
        "Mettre a jour": {"main": [[{"node": "Repondre statut", "type": "main", "index": 0}]]},
        "Webhook carte": {"main": [[{"node": "Plats de la carte", "type": "main", "index": 0}]]},
        "Plats de la carte": {"main": [[{"node": "Filtrer la carte", "type": "main", "index": 0}]]},
        "Filtrer la carte": {"main": [[{"node": "Repondre carte", "type": "main", "index": 0}]]},
        "Webhook disponibilite": {"main": [[{"node": "Valider disponibilite", "type": "main", "index": 0}]]},
        "Valider disponibilite": {"main": [[{"node": "Mettre a jour disponibilite", "type": "main", "index": 0}]]},
        "Mettre a jour disponibilite": {"main": [[{"node": "Repondre disponibilite", "type": "main", "index": 0}]]},
    },
    "settings": {"executionOrder": "v1"},
}

sortie = pathlib.Path("/srv/projects/shared/qramen/etat/wf-qramenCuisine01.json")
sortie.write_text(json.dumps(WF, ensure_ascii=False, indent=1))
print("ecrit", sortie)
