import json, pathlib
AT = "https://api.airtable.com/v0/appBHi3MxCb0hW1yH"
T_CMD = "tblKs9b4rmMzoSAJy"
T_PLATS = "tbl4riw5L76eRvSsN"
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
const rows = lignes.map(l => { const raw = String(l.fields.Ligne || ''); const badge = raw.match(/^\\[(🍜 Le QRamen|🥪 QRoque Monsieur)\\]/)?.[1] || (l.fields.Designation || '').match(/croque/i) && '🥪 QRoque Monsieur' || '🍜 Le QRamen'; const name = String(l.fields.Designation || raw).replace(/^\\[[^\\]]+\\] ?/, ''); return '<tr><td><b>' + badge + '</b><br>' + name + '</td><td class="prix">' + Number(l.fields['Sous-total'] || 0).toFixed(2) + ' EUR</td></tr>'; }).join('');
const plats = $('Lire les plats').first().json.records || [];
const isCroque = plats.some(p => p.fields.Concept === 'QRoque');
const name = 'Le QRamen · QRoque Monsieur';
const mascot = isCroque ? '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 72"><path d="M16 28h68l-8 30H24z" fill="#d99a42" stroke="#35251d" stroke-width="4"/><path d="M22 31h56l-7 19H29z" fill="#f5e6c7"/><path d="M29 31 40 20l12 11 12-11 14 11" fill="#f0c05a" stroke="#8d4b2b" stroke-width="4"/><path d="M11 61h78" stroke="#35251d" stroke-width="5"/></svg>' : '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 72"><path d="M14 31q36-33 72 0" fill="#eab653" stroke="#33241d" stroke-width="4"/><path d="M17 34h66l-8 24H25z" fill="#d86438" stroke="#33241d" stroke-width="4"/><path d="M20 37h60" stroke="#f4d37f" stroke-width="5"/><path d="M11 62h78" stroke="#33241d" stroke-width="5"/></svg>';
const html = '<!doctype html><meta charset="utf-8"><style>body{font-family:Helvetica,Arial,sans-serif;padding:26px;color:#222}.entete{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #ddd;padding-bottom:8px;margin-bottom:12px}.entete h1{margin:0;font-size:22px}.mascotte{width:48px;height:35px} .petit{color:#666;margin:0 0 18px;font-size:12px}table{width:100%;border-collapse:collapse;font-size:13px}td{padding:6px 0;border-bottom:1px solid #eee}.prix{text-align:right}.total td{font-weight:700;font-size:15px;border-top:2px solid #222;border-bottom:0}.pied{margin-top:24px;color:#333;font-size:9px;line-height:1.4}</style><div class="entete"><h1>' + name + '</h1><div class="mascotte">' + mascot + '</div></div><p class="petit">Addition - commande no ' + cmd.fields.Numero + '</p><table>' + rows + '<tr class="total"><td>Total</td><td class="prix">' + Number(cmd.fields.Total || 0).toFixed(2) + ' EUR</td></tr></table><div class="pied">14 rue du Gros-Horloge, 76000 Rouen<br>alexisld.fr</div>';
return [{ json: { html, nom: 'addition-' + cmd.fields.Numero, id: cmd.id, numero: cmd.fields.Numero } }];"""

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
        n("a6", "Lire les plats", "httpRequest", 4.2, [1100, 0],
          {"url": "={{ '" + AT + "/" + T_PLATS + "?filterByFormula=' + encodeURIComponent((($('Lire lignes').first().json.records || []).flatMap(r => r.fields.Plat || [])).length ? 'OR(' + ($('Lire lignes').first().json.records || []).flatMap(r => r.fields.Plat || []).map(id => \"RECORD_ID()='\" + id + \"'\").join(',') + ')' : \"RECORD_ID()=''\") }}",
           "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {}}, {"credentials": CRED}),
        n("a12", "Preparer addition", "code", 2, [1320, 0], {"jsCode": CODE_ADDITION}),
        n("a7", "Imprimer", "httpRequest", 4.2, [1540, 0],
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
        "Lire lignes": {"main": [[{"node": "Lire les plats", "type": "main", "index": 0}]]},
        "Lire les plats": {"main": [[{"node": "Preparer addition", "type": "main", "index": 0}]]},
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
