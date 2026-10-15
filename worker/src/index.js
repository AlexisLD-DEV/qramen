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
let tablesCache = { at: 0, rows: null };
async function tableRecords(env, refresh = false) {
  if (!refresh && tablesCache.rows && Date.now() - tablesCache.at < 45000) return tablesCache.rows;
  const rows = await allRecords(env, TABLES.tables);
  tablesCache = { at: Date.now(), rows };
  return rows;
}
function activeTable(record) { return fields(record).Active !== false; }
function resolveTable(records, identifier) {
  const wanted = String(identifier || "").trim();
  const exact = records.find(record => String(fields(record).Identifiant || fields(record).Nom || "").trim() === wanted);
  if (exact) return exact;
  const normalized = wanted.toLocaleLowerCase("fr");
  return records.find(record => String(fields(record).Identifiant || fields(record).Nom || "").trim().toLocaleLowerCase("fr") === normalized);
}
function publicTable(record) {
  const f = fields(record);
  return { identifiant: f.Identifiant || f.Nom || "", nom: f.Nom || f.Identifiant || "", active: activeTable(record) };
}
function lineLabel(line, designation) {
  const raw = String(line || ""), tag = raw.match(/^\[(🍜 Le QRamen|🥪 QRoque Monsieur)\]/)?.[1];
  const name = String(designation || raw).replace(/^\[[^\]]+\] ?/, ""), note = raw.replace(/^\[[^\]]+\] ?/, "").trim();
  return `${tag ? `${tag} · ` : ""}${name}${tag && designation && note && !note.includes(name) && !name.includes(note) ? ` — Note : ${note}` : ""}`;
}

async function menu(env, url) {
  const concept = url.searchParams.get("concept") || "QRamen";
  const records = await allRecords(env, TABLES.plats);
  const plats = records.map(r => ({ id: r.id, ...fields(r) }))
    .filter(f => (f.Concept || "QRoque") === concept && f["Épuisé"] !== true)
    .map(f => ({ id: f.id, nom: f.Plat, description: f.Description || "", prix: f.Prix || 0, categorie: f.Categorie || "Plat", photo: "assets/img/" + (f.Photo || "default.webp"), disponible: true, allergenes: f.Allergenes || [], tags: [] }));
  return { restaurant: RESTAURANTS[concept] || null, concept, categories: CATEGORIES, plats };
}
async function cuisineMenu(env, url) {
  const concept = url.searchParams.get("concept") || "QRamen";
  const records = await allRecords(env, TABLES.plats);
  return { concept, plats: records.map(r => ({ id: r.id, nom: fields(r).Plat || "", categorie: fields(r).Categorie || "Plat", epuise: fields(r)["Épuisé"] === true, concept: fields(r).Concept || "QRoque" })).filter(p => p.concept === concept) };
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
    const f = fields(t), linked = commandes.filter(c => (fields(c).Table || []).includes(t.id)).sort((a,b) => Date.parse(fields(b)["Passee le"] || 0) - Date.parse(fields(a)["Passee le"] || 0));
    const active = linked.filter(c => !["Terminee", "Servi"].includes(fields(c).Statut)).sort((a,b) => Date.parse(fields(b)["Passee le"] || 0) - Date.parse(fields(a)["Passee le"] || 0))[0];
    const bill = linked.filter(c => fields(c)["Addition demandee"]).sort((a,b) => Date.parse(fields(b)["Passee le"] || 0) - Date.parse(fields(a)["Passee le"] || 0))[0];
    const latest = linked[0], cleared = ["Libre", "Servie"].includes(f.Etat), latestIsDemo = latest && (String(fields(latest).Numero || "").startsWith("DEMO") || lignes.some(l => (fields(l).Commande || []).includes(latest.id) && /\bDEMO\b/.test(String(fields(l).Ligne || "")))), order = bill || (cleared ? (latestIsDemo ? latest : null) : (active || (latestIsDemo ? latest : null)));
    const orderLines = order ? lignes.filter(l => (fields(l).Commande || []).includes(order.id)) : [];
    const demo = orderLines.some(l => /\bDEMO\b/.test(String(fields(l).Ligne || "")));
    return { id: t.id, nom: f.Identifiant || f.Nom || "Table", concept: orderConcept(order || latest), etat: bill ? "Addition demandée" : cleared ? f.Etat : active ? "En cours" : (f.Etat || "Libre"), commande: order ? { id: order.id, numero: fields(order).Numero, statut: fields(order).Statut === "Terminee" ? "Servi" : fields(order).Statut, total: Number(fields(order).Total || 0), additionUrl: fields(order).Addition?.[0]?.url || null, passee: fields(order)["Passee le"], demo, lignes: orderLines.map(l => { const raw=String(fields(l).Ligne || ""), tag=raw.match(/^\[(🍜 Le QRamen|🥪 QRoque Monsieur)\]/)?.[1] || ""; return { designation: String(fields(l).Designation || raw).replace(/^\[[^\]]+\] ?/, "").replace(/\s+x\s+\d+$/, "").replace(/\s+[—-]\s+Note\s*:.+$/, "").trim(), quantite: Number(fields(l).Quantite || 1), concept: tag.includes("QRoque") ? "QRoque Monsieur" : "Le QRamen" }; }) } : null };
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
async function generateDemo(env) {
  const [tables, commands, dishes] = await Promise.all([
    tableRecords(env), allRecords(env, TABLES.commandes),
    allRecords(env, TABLES.plats),
  ]);
  const activeTableIds = new Set(commands.filter(c => !["Terminee", "Servi"].includes(fields(c).Statut)).flatMap(c => fields(c).Table || []));
  const selectedTables = tables.filter(t => activeTable(t) && !activeTableIds.has(t.id)).slice(0, 4);
  if (selectedTables.length < 4) throw new Error("Il faut quatre tables libres (sans commande active) pour créer la démo. Aucune commande n’a été créée.");
  const pick = (name, concept) => {
    const d = dishes.find(x => fields(x).Plat === name && fields(x).Concept === concept && fields(x).Disponible !== false);
    if (!d) throw new Error(`Plat de démonstration indisponible : ${name}`);
    return d;
  };
  const specs = [
    { status: "En attente", table: selectedTables[0], lines: [[pick("Ramen shoyu", "QRamen"), 2, "QRamen"], [pick("Gyoza (6 pieces)", "QRamen"), 1, "QRamen"]] },
    { status: "En cours", table: selectedTables[1], lines: [[pick("Croque madame", "QRoque"), 1, "QRoque"], [pick("Croque apéro (6 pièces)", "QRoque"), 1, "QRoque"]] },
    { status: "Terminee", table: selectedTables[2], lines: [[pick("Ramen tonkotsu", "QRamen"), 1, "QRamen"], [pick("Croque monsieur", "QRoque"), 1, "QRoque"]] },
    { status: "En cours", table: selectedTables[3], bill: true, lines: [[pick("Croque raclette", "QRoque"), 1, "QRoque"], [pick("Cidre brut 50 cl", "QRoque"), 1, "QRoque"]] },
  ];
  // Fail before writing if any required menu/table value is missing.
  if (specs.some(s => !s.lines.length)) throw new Error("Le menu ne permet pas de préparer la démo.");
  const created = [], createdLines = [];
  try {
    for (const spec of specs) {
      const response = await airtable(env, TABLES.commandes, { method: "POST", body: { fields: { Statut: spec.status, Table: [spec.table.id], ...(spec.bill ? { "Addition demandee": true } : {}) } } });
      created.push(response);
      const lineRecords = spec.lines.map(([dish, quantity, concept]) => ({ fields: { Ligne: `[${concept === "QRoque" ? "🥪 QRoque Monsieur" : "🍜 Le QRamen"}] DEMO`, Quantite: quantity, Plat: [dish.id], Commande: [response.id] } }));
      const written = await airtable(env, TABLES.lignes, { method: "POST", body: { records: lineRecords } });
      createdLines.push(...(written.records || []));
      await airtable(env, `${TABLES.tables}/${spec.table.id}`, { method: "PATCH", body: { fields: { Etat: spec.status === "Terminee" ? "Servie" : "En cours" } } });
    }
    const verified = await Promise.all(created.map(c => airtable(env, `${TABLES.commandes}/${c.id}`)));
    const verifiedLines = await Promise.all(createdLines.map(l => airtable(env, `${TABLES.lignes}/${l.id}`)));
    const createdIds = new Set(created.map(c => c.id));
    if (verified.length !== 4 || verifiedLines.length !== specs.reduce((n, s) => n + s.lines.length, 0) || verified.some((r, i) => fields(r).Statut !== specs[i].status || !(fields(r).Table || []).includes(specs[i].table.id) || (fields(r).Lignes || []).length !== specs[i].lines.length || (specs[i].bill && !fields(r)["Addition demandee"])) || verifiedLines.some(l => !/\bDEMO\b/.test(String(fields(l).Ligne || "")) || !(fields(l).Commande || []).some(id => createdIds.has(id)))) throw new Error("La vérification Airtable des commandes créées a échoué.");
    const result = { ok: true, commandes: verified.map((r, i) => ({ id: r.id, numero: fields(r).Numero, statut: fields(r).Statut === "Terminee" ? "Servi" : fields(r).Statut, table: fields(specs[i].table).Identifiant || fields(specs[i].table).Nom, additionDemandee: !!fields(r)["Addition demandee"], lignes: (fields(r).Lignes || []).length })), lignesVerifiees: verifiedLines.length };
    console.log(JSON.stringify({ event: "demo_generate", at: new Date().toISOString(), commandes: result.commandes.map(c => c.numero), lignes: result.lignesVerifiees }));
    return result;
  } catch (error) {
    console.log(JSON.stringify({ event: "demo_generate_failed", at: new Date().toISOString(), commandesCreees: created.length, lignesCreees: createdLines.length, error: error.message }));
    throw new Error(`Création incomplète : ${created.length} commande(s) ont été écrites. Vérifiez la vue avant de relancer. ${error.message}`);
  }
}
async function resetDemo(env) {
  let lines = [], commands = [];
  try {
    const [allLines, allCommands, allTables] = await Promise.all([
      allRecords(env, TABLES.lignes), allRecords(env, TABLES.commandes), allRecords(env, TABLES.tables),
    ]);
    lines = allLines;
    commands = allCommands;

    // Delete every order line before its parent command.
    for (let i = 0; i < lines.length; i += 10) {
      await airtable(env, TABLES.lignes, { method: "DELETE", query: { "records[]": lines.slice(i, i + 10).map(r => r.id) } });
    }
    for (let i = 0; i < commands.length; i += 10) {
      await airtable(env, TABLES.commandes, { method: "DELETE", query: { "records[]": commands.slice(i, i + 10).map(r => r.id) } });
    }
    for (const table of allTables) await airtable(env, `${TABLES.tables}/${table.id}`, { method: "PATCH", body: { fields: { Etat: "Libre" } } });
    const [remainingLines, remainingCommandsAfterDelete, verifiedTables] = await Promise.all([
      allRecords(env, TABLES.lignes), allRecords(env, TABLES.commandes), allRecords(env, TABLES.tables),
    ]);
    const linkedTables = verifiedTables.filter(table => (fields(table).Commandes || []).length > 0);
    const busyTables = verifiedTables.filter(table => fields(table).Etat !== "Libre");
    if (remainingCommandsAfterDelete.length || remainingLines.length || linkedTables.length || busyTables.length) throw new Error(`Vérification du reset échouée : ${remainingCommandsAfterDelete.length} commande(s), ${remainingLines.length} ligne(s), ${linkedTables.length} table(s) encore liée(s) et ${busyTables.length} table(s) non libres restent présentes.`);
    const tablesLiberees = verifiedTables.length;
    console.log(JSON.stringify({ event: "demo_reset", at: new Date().toISOString(), commands: commands.length, lines: lines.length, tablesLiberees, ok: true }));
    return { ok: true, commandesSupprimees: commands.length, lignesSupprimees: lines.length, tablesLiberees, verification: "toutes les commandes et lignes supprimées; toutes les tables libres" };
  } catch (error) {
    console.log(JSON.stringify({ event: "demo_reset_failed", at: new Date().toISOString(), commandsSeen: commands.length, linesSeen: lines.length, error: error.message }));
    throw error;
  }
}
async function route(request, env, ctx) {
  const url = new URL(request.url), path = url.pathname.replace(/\/$/, ""), method = request.method;
  if (method === "OPTIONS") return new Response(null, { status: 204, headers: { "access-control-allow-origin": "*", "access-control-allow-methods": "GET,POST,OPTIONS", "access-control-allow-headers": "Content-Type, Authorization, X-Reset-Token" } });
  if (path === "/webhook/qramen/ping" && method === "GET") return json({ ok: true, service: "qramen-engine" });
  if (path === "/webhook/qramen/tables" && method === "GET") {
    const rows = await tableRecords(env);
    return json({ tables: rows.map(publicTable).filter(t => t.identifiant).sort((a, b) => a.identifiant.localeCompare(b.identifiant, "fr", { numeric: true })) });
  }
  if (path === "/webhook/qramen/tables" && method === "POST") {
    const b = await bodyOf(request), nom = String(b.nom || "").trim().slice(0, 80);
    if (!nom) return fail("nom est obligatoire");
    const current = await tableRecords(env, true);
    let identifiant = String(b.identifiant || "").trim().slice(0, 24);
    if (!identifiant) {
      const used = new Set(current.map(t => String(fields(t).Identifiant || fields(t).Nom || "").toUpperCase()));
      let n = 1;
      while (used.has(`T${String(n).padStart(2, "0")}`)) n++;
      identifiant = `T${String(n).padStart(2, "0")}`;
    }
    if (current.some(t => String(fields(t).Identifiant || fields(t).Nom || "").toLowerCase() === identifiant.toLowerCase())) return fail("identifiant déjà utilisé", 409);
    const created = await airtable(env, TABLES.tables, { method: "POST", body: { fields: { Identifiant: identifiant, Nom: nom, Active: true } } });
    tablesCache = { at: Date.now(), rows: [...current, created] };
    console.log(JSON.stringify({ event: "table_create", at: new Date().toISOString(), identifiant, nom, record: created.id }));
    return json({ ok: true, table: publicTable(created) }, 201);
  }
  if (path === "/webhook/qramen/reset" && method === "POST") {
    const b = await bodyOf(request);
    if (b.confirmation !== "REINITIALISER LA DEMO") return fail("confirmation explicite requise", 400);
    return json(await resetDemo(env));
  }
  if (path === "/webhook/qramen/demo/generate" && method === "POST") {
    const b = await bodyOf(request);
    if (b.confirmation !== "GENERER LA DEMO") return fail("confirmation explicite requise", 400);
    return json(await generateDemo(env));
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
    if (typeof b.table !== "string" || !b.table.trim() || b.table.length > 24 || !lignes.length) return fail("table et lignes sont obligatoires");
    if (lignes.some(l => !/^rec[A-Za-z0-9]+$/.test(l.platId || "") || !Number.isSafeInteger(l.quantite) || l.quantite < 1 || l.quantite > 999)) return fail("plat ou quantité invalide (1–999)");
    const availableRecords = await Promise.all([...new Set(lignes.map(l => l.platId))].map(id => airtable(env, `${TABLES.plats}/${id}`)));
    const byDishId = new Map(availableRecords.map(record => [record.id, fields(record)]));
    for (const line of lignes) {
      const dish = byDishId.get(line.platId);
      if (!dish) return fail("Un plat de cette commande n’existe plus. Actualisez le menu.", 409);
      if (dish["Épuisé"] === true) return fail(`« ${dish.Plat || "Ce plat"} » est épuisé. Actualisez le menu.`, 409);
      if ((dish.Concept || "QRoque") !== (line.concept === "QRoque" ? "QRoque" : "QRamen")) return fail("Le menu a changé. Actualisez la page.", 409);
    }
    const tables = await tableRecords(env);
    const selectedTable = resolveTable(tables, b.table);
    if (!selectedTable || !activeTable(selectedTable)) return fail("Table inconnue", 404);
    const created = await airtable(env, TABLES.commandes, { method: "POST", body: { fields: { Statut: "En attente", Table: [selectedTable.id] } } });
    const records = lignes.map(l => ({ fields: { Ligne: `[${l.concept === "QRoque" ? "🥪 QRoque Monsieur" : "🍜 Le QRamen"}]${l.note ? ` ${l.note}` : ""}`, Quantite: l.quantite, Plat: [l.platId], Commande: [created.id] } }));
    for (let i = 0; i < records.length; i += 10) await airtable(env, TABLES.lignes, { method: "POST", body: { records: records.slice(i, i + 10) } });
    await airtable(env, `${TABLES.tables}/${selectedTable.id}`, { method: "PATCH", body: { fields: { Etat: "En cours" } } });
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
    const b = await bodyOf(request); if (!b.id || typeof b.epuise !== "boolean") return fail("id et epuise sont obligatoires");
    await airtable(env, `${TABLES.plats}/${b.id}`, { method: "PATCH", body: { fields: { "Épuisé": b.epuise } } });
    return json({ ok: true, id: b.id, epuise: b.epuise });
  }
  if (path === "/webhook/qramen/salle/statut" && method === "POST") {
    const b = await bodyOf(request); if (!b.id || !b.etat) return fail("id et etat sont obligatoires");
    await airtable(env, `${TABLES.tables}/${b.id}`, { method: "PATCH", body: { fields: { Etat: b.etat } } });
    return json({ ok: true });
  }
  if (path === "/webhook/qramen/addition" && method === "POST") {
    const b = await bodyOf(request), ticket = await ticketData(env, Number(b.numero || 0));
    if (!ticket) return json({ trouve: false }, 404);
    await airtable(env, `${TABLES.commandes}/${ticket.id}`, { method: "PATCH", body: { fields: { "Addition demandee": true } } });
    if (!ticket.addition.url && ctx?.waitUntil) {
      ctx.waitUntil(fetch("https://n8n.ledeunf.fr/webhook/qramen/addition", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ numero: ticket.numero }) }).then(response => { if (!response.ok) console.log(JSON.stringify({ event: "addition_webhook_failed", numero: ticket.numero, status: response.status })); }).catch(error => { console.log(JSON.stringify({ event: "addition_webhook_failed", numero: ticket.numero, error: String(error).slice(0, 120) })); }));
    }
    return json({ ok: true, numero: ticket.numero });
  }
  return fail("route introuvable", 404);
}
export default { async fetch(request, env, ctx) { try { return await route(request, env, ctx); } catch (error) { return fail(error.message || "erreur interne", 502); } } };
