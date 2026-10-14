#!/usr/bin/env python3
"""Workflow n8n dédié à la salle : état des tables et action serveuse/serveur."""
import json, pathlib
BASE='appBHi3MxCb0hW1yH'; TABLES='tblsdUES4NrSjkiWT'; CMDS='tblKs9b4rmMzoSAJy'
AT='https://api.airtable.com/v0/'+BASE; CRED={'httpHeaderAuth':{'id':'qramenPatCred','name':'QRamen — Airtable'}}
def n(i,name,typ,ver,pos,params,extra=None):
 d={'parameters':params,'id':i,'name':name,'type':'n8n-nodes-base.'+typ,'typeVersion':ver,'position':pos}
 if extra:d.update(extra)
 return d
CODE="""const tables=$('Tables Airtable').first().json.records||[];
const commandes=$('Commandes Airtable').first().json.records||[];
const out=tables.map(t=>{
 const linked=commandes.filter(c=>(c.fields.Table||[]).includes(t.id));
 const active=linked.filter(c=>!['Terminee','Servi'].includes(c.fields.Statut)).sort((a,b)=>new Date(b.fields['Passee le']||0)-new Date(a.fields['Passee le']||0))[0];
 const bill=linked.filter(c=>c.fields['Addition demandee']&&!['Terminee'].includes(c.fields.Statut)).sort((a,b)=>new Date(b.fields['Passee le']||0)-new Date(a.fields['Passee le']||0))[0];
 const cleared=['Libre','Servie'].includes(t.fields.Etat);
 const order=cleared?null:(bill||active);
 return {id:t.id,nom:t.fields.Identifiant||t.fields.Nom||'Table',etat:cleared?t.fields.Etat:bill?'Addition demandée':(active?'En cours':(t.fields.Etat||'Libre')),commande:order?{id:order.id,numero:order.fields.Numero,statut:order.fields.Statut,passee:order.fields['Passee le']}:null};
});
return [{json:{tables:out}}];"""
CODE_BODY="""const b=$('Webhook état salle').first().json.body||{};
const etat={free:'Libre',served:'Servie',busy:'En cours'}[b.action];
if(!b.id||!etat)throw new Error('id et action valides requis');
return [{json:{id:b.id,etat}}];"""
WF={'id':'qramenSalle01','name':'QRamen — salle','active':False,'nodes':[
 n('s1','Webhook salle','webhook',2,[0,0],{'httpMethod':'GET','path':'qramen/salle','responseMode':'responseNode','options':{'allowedOrigins':'*'}},{'webhookId':'qramen-salle'}),
 n('s2','Tables Airtable','httpRequest',4.2,[220,0],{'url':AT+'/'+TABLES+'?pageSize=100','authentication':'genericCredentialType','genericAuthType':'httpHeaderAuth','options':{}},{'credentials':CRED}),
 n('s3','Commandes Airtable','httpRequest',4.2,[440,0],{'url':AT+'/'+CMDS+'?pageSize=100&sort%5B0%5D%5Bfield%5D=Passee%20le&sort%5B0%5D%5Bdirection%5D=desc','authentication':'genericCredentialType','genericAuthType':'httpHeaderAuth','options':{}},{'credentials':CRED}),
 n('s4','Assembler la salle','code',2,[660,0],{'jsCode':CODE}),
 n('s5','Répondre salle','respondToWebhook',1.1,[880,0],{'respondWith':'json','responseBody':'={{ $json }}','options':{}}),
 n('s6','Webhook état salle','webhook',2,[0,240],{'httpMethod':'POST','path':'qramen/salle/statut','responseMode':'responseNode','options':{'allowedOrigins':'*'}},{'webhookId':'qramen-salle-statut'}),
 n('s7','Valider état','code',2,[220,240],{'jsCode':CODE_BODY}),
 n('s8','Écrire état Airtable','httpRequest',4.2,[440,240],{'method':'PATCH','url':"={{ '"+AT+'/'+TABLES+"/' + $json.id }}",'sendBody':True,'specifyBody':'json','jsonBody':'={{ JSON.stringify({fields:{Etat:$json.etat}}) }}','authentication':'genericCredentialType','genericAuthType':'httpHeaderAuth','options':{}},{'credentials':CRED}),
 n('s9','Répondre état','respondToWebhook',1.1,[660,240],{'respondWith':'json','responseBody':"={{ {ok:true, etat:$('Valider état').first().json.etat} }}",'options':{}})],
 'connections':{'Webhook salle':{'main':[[{'node':'Tables Airtable','type':'main','index':0}]]},'Tables Airtable':{'main':[[{'node':'Commandes Airtable','type':'main','index':0}]]},'Commandes Airtable':{'main':[[{'node':'Assembler la salle','type':'main','index':0}]]},'Assembler la salle':{'main':[[{'node':'Répondre salle','type':'main','index':0}]]},'Webhook état salle':{'main':[[{'node':'Valider état','type':'main','index':0}]]},'Valider état':{'main':[[{'node':'Écrire état Airtable','type':'main','index':0}]]},'Écrire état Airtable':{'main':[[{'node':'Répondre état','type':'main','index':0}]]}},'settings':{'executionOrder':'v1'}}
out=pathlib.Path(__file__).resolve().parent.parent/'etat/wf-qramenSalle01.json';out.write_text(json.dumps(WF,ensure_ascii=False,indent=1));print(out)
