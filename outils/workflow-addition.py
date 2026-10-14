import json, pathlib
AT = "https://api.airtable.com/v0/appBHi3MxCb0hW1yH"
T_CMD = "tblKs9b4rmMzoSAJy"
CRED = {"httpHeaderAuth": {"id": "qramenPatCred", "name": "QRamen - Airtable"}}
SORTIE = pathlib.Path("/srv/projects/shared/qramen/etat/wf-qramenAddition01.json")
CLE = pathlib.Path("/srv/hermes/.hermes/.secrets/qramen-pdf.key").read_text().strip()

def n(i, nom, typ, ver, pos, params, extra=None):
    noeud = {"parameters": params, "id": i, "name": nom, "type": "n8n-nodes-base." + typ,
             "typeVersion": ver, "position": pos}
    if extra:
        noeud.update(extra)
    return noeud

CODE_LIGNES = """const c = $json.records[0];
return [{ json: { id: c.id, numero: c.fields.Numero, total: c.fields.Total || 0,
  ids: c.fields.Lignes || [] } }];"""

CODE_FORMULE = """const ids = $json.ids;
return [{ json: { ...$json, formula: ids.length ? 'OR(' + ids.map(i => \"RECORD_ID()='\" + i + \"'\").join(',') + ')' : \"RECORD_ID()=''\" } }];"""

CODE_ADDITION = """const cmd = $('Commande').first().json.records[0];
const lignes = $('Lire lignes').first().json.records || [];
const rows = lignes.map(l => '<tr><td>' + (l.fields.Designation || l.fields.Ligne || '') + '</td><td class="prix">' + Number(l.fields['Sous-total'] || 0).toFixed(2) + ' EUR</td></tr>').join('');
const html = '<!doctype html><meta charset="utf-8"><style>body{font-family:Helvetica,Arial,sans-serif;padding:26px;color:#222}h1{margin:0 0 4px;font-size:22px}.petit{color:#666;margin:0 0 18px;font-size:12px}table{width:100%;border-collapse:collapse;font-size:13px}td{padding:6px 0;border-bottom:1px solid #eee}.prix{text-align:right}.total td{font-weight:700;font-size:15px;border-top:2px solid #222;border-bottom:0}.pied{margin-top:24px;color:#333;font-size:10px;line-height:1.5}.pied a{color:#111;text-decoration:underline}</style><h1>Le QRamen</h1><p class="petit">Addition - commande no ' + cmd.fields.Numero + '</p><table>' + rows + '<tr class="total"><td>Total</td><td class="prix">' + Number(cmd.fields.Total || 0).toFixed(2) + ' EUR</td></tr></table><div class="pied">14 rue du Gros-Horloge, 76000 Rouen<br><a href="https://alexisld.fr">alexisld.fr</a> - code open source : github.com/AlexisLD-DEV/qramen</div>';
return [{ json: { html, nom: 'addition-' + cmd.fields.Numero, id: cmd.id, numero: cmd.fields.Numero } }];"""
print("briques ecrites")

WF = {
    "id": "qramenAddition01",
    "name": "QRamen — addition",
    "nodes": [
        n("a1", "Webhook addition", "webhook", 2, [0, 0],
          {"httpMethod": "POST", "path": "qramen/addition", "responseMode": "responseNode",
           "options": {"allowedOrigins": "*"}}, {"webhookId": "qramen-addition"}),
        n("a2", "Lire la demande", "code", 2, [220, 0],
          {"jsCode": "const b = $('Webhook addition').first().json.body || {};\nreturn [{ json: { numero: Number(b.numero || 0) } }];"}),
        n("a3", "Commande", "httpRequest", 4.2, [440, 0],
          {"url": "={{ '" + AT + "/" + T_CMD + "?maxRecords=1&filterByFormula=' + encodeURIComponent('{Numero}=' + $json.numero) }}",
           "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}}, {"credentials": CRED}),
        n("a4", "Formule lignes", "code", 2, [660, 0], {"jsCode": CODE_LIGNES}),
        n("a5", "Lire lignes", "httpRequest", 4.2, [880, 0],
          {"url": "={{ '" + AT + "/tblNmtM5qYLKyQZW9?filterByFormula=' + encodeURIComponent($json.ids.length ? 'OR(' + $json.ids.map(i => \"RECORD_ID()='\" + i + \"'\").join(',') + ')' : \"RECORD_ID()=''\") }}",
           "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}}, {"credentials": CRED}),
        n("a6", "Preparer addition", "code", 2, [1100, 0], {"jsCode": CODE_ADDITION}),
        n("a7", "Imprimer", "httpRequest", 4.2, [1320, 0],
          {"method": "POST", "url": "http://172.19.0.1:8798/pdf?json=1", "sendBody": True,
           "specifyBody": "json", "jsonBody": "={{ JSON.stringify({ html: $json.html, nom: $json.nom }) }}",
           "sendHeaders": True, "headerParameters": {"parameters": [{"name": "X-PDF-Key", "value": CLE}]},
           "options": {}}),
        n("a8", "Attacher", "httpRequest", 4.2, [1540, 0],
          {"method": "POST", "url": "={{ 'https://content.airtable.com/v0/appBHi3MxCb0hW1yH/' + $('Preparer addition').item.json.id + '/Addition/uploadAttachment' }}",
           "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": True,
           "specifyBody": "json", "jsonBody": "={{ JSON.stringify({ contentType: 'application/pdf', filename: $('Preparer addition').item.json.nom + '.pdf', file: $json.base64 }) }}",
           "options": {}}, {"credentials": CRED}),
        n("a9", "Marquer demandee", "httpRequest", 4.2, [1760, 0],
          {"method": "PATCH", "url": "={{ '" + AT + "/" + T_CMD + "/' + $('Preparer addition').item.json.id }}",
           "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": True,
           "specifyBody": "json", "jsonBody": "={{ JSON.stringify({ fields: { 'Addition demandee': true } }) }}",
           "options": {}}, {"credentials": CRED}),
        n("a10", "Reponse", "code", 2, [1980, 0],
          {"jsCode": "const p = $('Preparer addition').first().json;\nreturn [{ json: { ok: true, numero: p.numero } }];"}),
        n("a11", "Repondre", "respondToWebhook", 1.1, [2200, 0],
          {"respondWith": "json", "responseBody": "={{ $json }}", "options": {}}),
    ],
    "connections": {
        "Webhook addition": {"main": [[{"node": "Lire la demande", "type": "main", "index": 0}]]},
        "Lire la demande": {"main": [[{"node": "Commande", "type": "main", "index": 0}]]},
        "Commande": {"main": [[{"node": "Formule lignes", "type": "main", "index": 0}]]},
        "Formule lignes": {"main": [[{"node": "Lire lignes", "type": "main", "index": 0}]]},
        "Lire lignes": {"main": [[{"node": "Preparer addition", "type": "main", "index": 0}]]},
        "Preparer addition": {"main": [[{"node": "Imprimer", "type": "main", "index": 0}]]},
        "Imprimer": {"main": [[{"node": "Attacher", "type": "main", "index": 0}]]},
        "Attacher": {"main": [[{"node": "Marquer demandee", "type": "main", "index": 0}]]},
        "Marquer demandee": {"main": [[{"node": "Reponse", "type": "main", "index": 0}]]},
        "Reponse": {"main": [[{"node": "Repondre", "type": "main", "index": 0}]]},
    },
    "settings": {"executionOrder": "v1"},
    "active": False,
}
SORTIE.write_text(json.dumps(WF, ensure_ascii=False, indent=1))
print("ecrit", SORTIE)
