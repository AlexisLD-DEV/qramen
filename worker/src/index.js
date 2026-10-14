const TABLES = {
  tables: "tblsdUES4NrSjkiWT",
  plats: "tbl4riw5L76eRvSsN",
  commandes: "tblKs9b4rmMzoSAJy",
  lignes: "tblNmtM5qYLKyQZW9",
};
const CATEGORIES = [
  { id: "Entree", nom: "Entrees" }, { id: "Plat", nom: "Plats" },
  { id: "Dessert", nom: "Desserts" }, { id: "Boisson", nom: "Boissons" },
];
const RESTAURANTS = {
  QRamen: { nom: "Le QRamen", baseline: "Scannez. Commandez. Slurpez.", ville: "Rouen", cuisine: "Cuisine japonaise", devise: "EUR" },
  QRoque: { nom: "QRoque Monsieur", baseline: "Le bistrot du croque, qui se scanne.", ville: "Rouen", cuisine: "Croques & bistrot", devise: "EUR" },
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "access-control-allow-origin": "*", "access-control-allow-methods": "GET,POST,OPTIONS", "access-control-allow-headers": "Content-Type, Authorization, X-Reset-Token" } });
}
function fail(message, status = 400) { return json({ error: message }, status); }
async function bodyOf(request) { try { return await request.json(); } catch { return {}; } }
function escapeFormula(value) { return String(value).replaceAll("'", "\\'"); }
async function airtable(env, table, options = {}) {
  if (!env.AIRTABLE_PAT) throw new Error("AIRTABLE_PAT secret is not configured");
  const base = env.AIRTABLE_BASE_ID || "appBHi3MxCb0hW1yH";
  const url = new URL(`https://api.airtable.com/v0/${base}/${table}`);
  for (const [key, value] of Object.entries(options.query || {})) if (value !== undefined) {
    if (Array.isArray(value)) value.forEach(item => url.searchParams.append(key, item));
    else url.searchParams.set(key, value);
  }
  const response = await fetch(url, { method: options.method || "GET", headers: { Authorization: `Bearer ${env.AIRTABLE_PAT}`, "content-type": "application/json" }, body: options.body ? JSON.stringify(options.body) : undefined });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Airtable ${response.status}: ${data.error?.message || "request failed"}`);
  return data;
}
async function allRecords(env, table, query = {}) {
  let records = [], offset;
  do {
    const page = await airtable(env, table, { query: { pageSize: "100", ...query, ...(offset ? { offset } : {}) } });
    records = records.concat(page.records || []); offset = page.offset;
  } while (offset);
  return records;
}
const fields = (record) => record.fields || {};
function lineLabel(line, designation) {
  const raw = String(line || ""), tag = raw.match(/^\[(🍜 Le QRamen|🥪 QRoque Monsieur)\]/)?.[1];
  const name = String(designation || raw).replace(/^\[[^\]]+\] ?/, ""), note = raw.replace(/^\[[^\]]+\] ?/, "").trim();
  return `${tag ? `${tag} · ` : ""}${name}${tag && designation && note && !note.includes(name) && !name.includes(note) ? ` — Note : ${note}` : ""}`;
}

async function menu(env, url) {
  const concept = url.searchParams.get("concept") || "QRamen";
  const records = await allRecords(env, TABLES.plats, { "filterByFormula": "{Disponible}=TRUE()" });
  const plats = records.map(r => ({ id: r.id, ...fields(r) }))
    .filter(f => (f.Concept || "QRoque") === concept && f.Disponible !== false)
    .map(f => ({ id: f.id, nom: f.Plat, description: f.Description || "", prix: f.Prix || 0, categorie: f.Categorie || "Plat", photo: "assets/img/" + (f.Photo || "default.webp"), disponible: f.Disponible !== false, allergenes: f.Allergenes || [], tags: [] }));
  return { restaurant: RESTAURANTS[concept] || null, concept, categories: CATEGORIES, plats };
}
async function cuisineMenu(env, url) {
  const concept = url.searchParams.get("concept") || "QRamen";
  const records = await allRecords(env, TABLES.plats);
  return { concept, plats: records.map(r => ({ id: r.id, nom: fields(r).Plat || "", categorie: fields(r).Categorie || "Plat", disponible: fields(r).Disponible !== false, concept: fields(r).Concept || "QRoque" })).filter(p => p.concept === concept) };
}
async function orders(env) {
  const [cmds, tableRows, allLines] = await Promise.all([
    allRecords(env, TABLES.commandes, { "sort[0][field]": "Passee le", "sort[0][direction]": "desc" }),
    allRecords(env, TABLES.tables), allRecords(env, TABLES.lignes),
  ]);
  const tableNames = new Map(tableRows.map(t => [t.id, fields(t).Identifiant || fields(t).Nom]));
  const demoClosed = new Set(allLines.filter(l => /\bDEMO\b/.test(String(fields(l).Ligne || ""))).flatMap(l => fields(l).Commande || []));
  const live = cmds.filter(r => !["Terminee", "Servi"].includes(fields(r).Statut) || demoClosed.has(r.id));
  const ids = new Set(live.flatMap(r => fields(r).Lignes || []));
  const lignes = allLines.filter(l => ids.has(l.id));
  return live.map(r => ({ id: r.id, numero: fields(r).Numero, table: tableNames.get((fields(r).Table || [])[0]) || "A emporter", statut: fields(r).Statut === "Terminee" ? "Servi" : (fields(r).Statut || "En attente"), heure: fields(r)["Passee le"], passee: fields(r)["Passee le"], additionDemandee: !!fields(r)["Addition demandee"], ticket: !!(fields(r)["Ticket cuisine"] || []).length, ticketUrl: fields(r)["Ticket cuisine"]?.[0]?.url || null, liens: fields(r).Lignes || [], lignes: lignes.filter(l => (fields(l).Commande || [])[0] === r.id).map(l => ({ id: l.id, commande: (fields(l).Commande || [])[0], designation: lineLabel(fields(l).Ligne, fields(l).Designation), quantite: fields(l).Quantite || 1 })) }));
}
async function room(env) {
  const [tables, commandes, lignes] = await Promise.all([allRecords(env, TABLES.tables), allRecords(env, TABLES.commandes, { "sort[0][field]": "Passee le", "sort[0][direction]": "desc" }), allRecords(env, TABLES.lignes)]);
  const orderConcept = (order) => {
    if (!order) return null;
    const labels = lignes.filter(l => (fields(l).Commande || []).includes(order.id)).map(l => String(fields(l).Ligne || ""));
    const ramen = labels.some(x => x.startsWith("[🍜 Le QRamen]")), croque = labels.some(x => x.startsWith("[🥪 QRoque Monsieur]"));
    return ramen && croque ? "all" : ramen ? "QRamen" : croque ? "QRoque" : null;
  };
  return { tables: tables.map(t => {
    const f = fields(t), linked = commandes.filter(c => (fields(c).Table || []).includes(t.id));
    const active = linked.filter(c => !["Terminee", "Servi"].includes(fields(c).Statut)).sort((a,b) => Date.parse(fields(b)["Passee le"] || 0) - Date.parse(fields(a)["Passee le"] || 0))[0];
    const bill = linked.filter(c => fields(c)["Addition demandee"] && fields(c).Statut !== "Terminee").sort((a,b) => Date.parse(fields(b)["Passee le"] || 0) - Date.parse(fields(a)["Passee le"] || 0))[0];
    const latest = linked[0], cleared = ["Libre", "Servie"].includes(f.Etat), order = cleared ? (latest && String(fields(latest).Numero || "").startsWith("DEMO") ? latest : null) : (bill || active || (latest && lignes.some(l => (fields(l).Commande || []).includes(latest.id) && /\bDEMO\b/.test(String(fields(l).Ligne || ""))) ? latest : null));
    const orderLines = order ? lignes.filter(l => (fields(l).Commande || []).includes(order.id)) : [];
    const demo = orderLines.some(l => /\bDEMO\b/.test(String(fields(l).Ligne || "")));
    return { id: t.id, nom: f.Identifiant || f.Nom || "Table", concept: orderConcept(order || latest), etat: cleared ? f.Etat : bill ? "Addition demandée" : active ? "En cours" : (f.Etat || "Libre"), commande: order ? { id: order.id, numero: fields(order).Numero, statut: fields(order).Statut === "Terminee" ? "Servi" : fields(order).Statut, passee: fields(order)["Passee le"], demo, lignes: orderLines.map(l => { const raw=String(fields(l).Ligne || ""), tag=raw.match(/^\[(🍜 Le QRamen|🥪 QRoque Monsieur)\]/)?.[1] || ""; return { designation: String(fields(l).Designation || raw).replace(/^\[[^\]]+\] ?/, "").replace(/\s+x\s+\d+$/, "").replace(/\s+[—-]\s+Note\s*:.+$/, "").trim(), quantite: Number(fields(l).Quantite || 1), concept: tag.includes("QRoque") ? "QRoque Monsieur" : "Le QRamen" }; }) } : null };
  }) };
}
async function ticketData(env, numero) {
  const cmds = await allRecords(env, TABLES.commandes, { filterByFormula: `{Numero}=${Number(numero)}` });
  const cmd = cmds[0];
  if (!cmd) return null;
  const f = fields(cmd), ids = f.Lignes || [];
  const lignes = ids.length ? await allRecords(env, TABLES.lignes, { filterByFormula: `OR(${ids.map(id => `RECORD_ID()='${escapeFormula(id)}'`).join(",")})` }) : [];
  const labels = await Promise.all(lignes.map(async l => {
    const lf = fields(l), p = (lf.Plat || [])[0];
    let nom = lf.Designation || lf.Ligne || "";
    if (!nom && p) { const record = await airtable(env, `${TABLES.plats}/${p}`); nom = fields(record).Plat || ""; }
    return { designation: lineLabel(lf.Ligne, nom), quantite: lf.Quantite || 1, sousTotal: lf["Sous-total"] || 0 };
  }));
  const tableId = (f.Table || [])[0];
  let table = "";
  if (tableId) { const tr = await airtable(env, `${TABLES.tables}/${tableId}`); table = fields(tr).Identifiant || fields(tr).Nom || ""; }
  return { id: cmd.id, numero: f.Numero, table, statut: f.Statut === "Terminee" ? "Servi" : f.Statut, total: f.Total || 0, lignes: labels, addition: { demandee: !!f["Addition demandee"], url: f.Addition?.[0]?.url || null }, ticket: !!f["Ticket cuisine"]?.length };
}
async function resetDemo(env) {
  if (!env.RESET_DEMO_TOKEN) throw new Error("RESET_DEMO_TOKEN secret is not configured");
  const lines = await allRecords(env, TABLES.lignes);
  const commands = await allRecords(env, TABLES.commandes);
  // Detach linked records before deleting commands; this also removes orphan lines.
  for (let i = 0; i < lines.length; i += 10) {
    await airtable(env, TABLES.lignes, { method: "DELETE", query: { "records[]": lines.slice(i, i + 10).map(r => r.id) } });
  }
  for (let i = 0; i < commands.length; i += 10) {
    await airtable(env, TABLES.commandes, { method: "DELETE", query: { "records[]": commands.slice(i, i + 10).map(r => r.id) } });
  }
  console.log(JSON.stringify({ event: "demo_reset", at: new Date().toISOString(), commands: commands.length, lines: lines.length }));
  return { ok: true, commandesSupprimees: commands.length, lignesSupprimees: lines.length };
}
async function route(request, env) {
  const url = new URL(request.url), path = url.pathname.replace(/\/$/, ""), method = request.method;
  if (method === "OPTIONS") return new Response(null, { status: 204, headers: { "access-control-allow-origin": "*", "access-control-allow-methods": "GET,POST,OPTIONS", "access-control-allow-headers": "Content-Type, Authorization, X-Reset-Token" } });
  if (path === "/webhook/qramen/ping" && method === "GET") return json({ ok: true, service: "qramen-engine" });
  if (path === "/webhook/qramen/reset" && method === "POST") {
    if (!env.RESET_DEMO_TOKEN || request.headers.get("authorization") !== `Bearer ${env.RESET_DEMO_TOKEN}`) return fail("non autorisé", 401);
    const b = await bodyOf(request);
    if (b.confirmation !== "REINITIALISER LA DEMO") return fail("confirmation explicite requise", 400);
    return json(await resetDemo(env));
  }
  if (path === "/webhook/qramen/menu" && method === "GET") return json(await menu(env, url));
  if (path === "/webhook/qramen/cuisine/carte" && method === "GET") return json(await cuisineMenu(env, url));
  if (path === "/webhook/qramen/cuisine" && method === "GET") return json({ commandes: await orders(env) });
  if (path === "/webhook/qramen/salle" && method === "GET") return json(await room(env));
  if (path === "/webhook/qramen/statut" && method === "GET") {
    const found = await ticketData(env, url.searchParams.get("numero"));
    if (!found) return json({ trouve: false });
    return json({ trouve: true, id: found.id, numero: found.numero, statut: found.statut, addition: found.addition });
  }
  if (path === "/webhook/qramen/test-pdf" && (method === "GET" || method === "POST")) {
    const b = method === "POST" ? await bodyOf(request) : {};
    const numero = Number(b.numero || url.searchParams.get("numero") || 0);
    if (!numero) return fail("numero est obligatoire");
    const ticket = await ticketData(env, numero);
    return ticket ? json({ ok: true, type: "ticket-data", ...ticket }) : json({ trouve: false }, 404);
  }
  if (path === "/webhook/qramen/commande" && method === "POST") {
    const b = await bodyOf(request);
    if (!Array.isArray(b.lignes)) return fail("lignes doit être une liste");
    if (b.lignes.some(l => !l || typeof l !== "object")) return fail("ligne invalide");
    const lignes = b.lignes.map(l => ({ platId: l.platId, quantite: Number(l.quantite), note: String(l.note || "").slice(0,500), concept: l.concept }));
    if (!/^T0[1-7]$/.test(b.table || "") || !lignes.length) return fail("table T01–T07 et lignes sont obligatoires");
    if (lignes.some(l => !/^rec[A-Za-z0-9]+$/.test(l.platId || "") || !Number.isSafeInteger(l.quantite) || l.quantite < 1 || l.quantite > 999)) return fail("plat ou quantité invalide (1–999)");
    const tables = await allRecords(env, TABLES.tables, { filterByFormula: `{Identifiant}="${String(b.table).replaceAll('"', '\\"')}"` });
    if (!tables[0]) return fail("table introuvable", 404);
    const created = await airtable(env, TABLES.commandes, { method: "POST", body: { fields: { Statut: "En attente", Table: [tables[0].id] } } });
    const records = lignes.map(l => ({ fields: { Ligne: `[${l.concept === "QRoque" ? "🥪 QRoque Monsieur" : "🍜 Le QRamen"}]${l.note ? ` ${l.note}` : ""}`, Quantite: l.quantite, Plat: [l.platId], Commande: [created.id] } }));
    for (let i = 0; i < records.length; i += 10) await airtable(env, TABLES.lignes, { method: "POST", body: { records: records.slice(i, i + 10) } });
    await airtable(env, `${TABLES.tables}/${tables[0].id}`, { method: "PATCH", body: { fields: { Etat: "En cours" } } });
    const f = fields(created);
    return json({ ok: true, numero: f.Numero, statut: f.Statut, commande: created.id });
  }
  if (path === "/webhook/qramen/cuisine/statut" && method === "POST") {
    const b = await bodyOf(request); let statut = b.statut || "En cours";
    if (statut === "Servi") statut = "Terminee";
    if (!["En attente", "En cours", "Terminee"].includes(statut)) statut = "En cours";
    if (!b.id) return fail("id est obligatoire");
    await airtable(env, `${TABLES.commandes}/${b.id}`, { method: "PATCH", body: { fields: { Statut: statut } } });
    return json({ ok: true, id: b.id, statut: statut === "Terminee" ? "Servi" : statut });
  }
  if (path === "/webhook/qramen/cuisine/disponibilite" && method === "POST") {
    const b = await bodyOf(request); if (!b.id || typeof b.disponible !== "boolean") return fail("id et disponible sont obligatoires");
    await airtable(env, `${TABLES.plats}/${b.id}`, { method: "PATCH", body: { fields: { Disponible: b.disponible } } });
    return json({ ok: true, id: b.id, disponible: b.disponible });
  }
  if (path === "/webhook/qramen/salle/statut" && method === "POST") {
    const b = await bodyOf(request); if (!b.id || !b.etat) return fail("id et etat sont obligatoires");
    await airtable(env, `${TABLES.tables}/${b.id}`, { method: "PATCH", body: { fields: { Etat: b.etat } } });
    return json({ ok: true });
  }
  if (path === "/webhook/qramen/addition" && method === "POST") {
    const b = await bodyOf(request), ticket = await ticketData(env, Number(b.numero || 0));
    if (!ticket) return json({ trouve: false }, 404);
    // Le Worker prépare les données d'addition; le rendu et l'attachement PDF restent au service VPS.
    await airtable(env, `${TABLES.commandes}/${ticket.id}`, { method: "PATCH", body: { fields: { "Addition demandee": true } } });
    return json({ ok: true, numero: ticket.numero });
  }
  return fail("route introuvable", 404);
}
export default { async fetch(request, env) { try { return await route(request, env); } catch (error) { return fail(error.message || "erreur interne", 502); } } };
