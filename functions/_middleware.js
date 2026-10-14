const LEGACY_HOSTS = new Map([
  ["qramen.ledeunf.fr", "qramen.alexisld.fr"],
  ["croq.alexisld.fr", "qroque.alexisld.fr"],
  ["croq.ledeunf.fr", "qroque.alexisld.fr"],
]);

export async function onRequest({ request, next }) {
  const source = new URL(request.url);
  const targetHost = LEGACY_HOSTS.get(source.hostname.toLowerCase());
  if (targetHost) {
    source.protocol = "https:";
    source.hostname = targetHost;
    source.port = "";
    return Response.redirect(source.toString(), 301);
  }
  const response = await next();
  if (request.method !== "GET" || !response.headers.get("content-type")?.includes("text/html")) return response;

  const host = source.hostname.toLowerCase();
  const qroque = host.includes("qroque") || source.searchParams.get("concept") === "QRoque";
  const brand = qroque ? "QRoque Monsieur" : "Le QRamen";
  const siteHost = qroque ? "https://qroque.alexisld.fr" : "https://qramen.alexisld.fr";
  const page = (source.pathname.split("/").pop() || "index.html").replace(/\.html$/i, "") || "index";
  const pages = {
    "index": [brand + " — Restaurant à Rouen", "Découvrez " + brand + " à Rouen : consultez le menu et commandez à votre table."],
    "menu": ["Carte — " + brand, "La carte de " + brand + " à Rouen : plats, prix et commande à table."],
    "cuisine": ["Cuisine — " + brand, "Écran cuisine de " + brand + ", restaurant à Rouen."],
    "salle": ["Vue salle — " + brand, "Suivi des tables et commandes de " + brand + " à Rouen."],
    "qr": ["QR des tables — " + brand, "Générez et imprimez les QR codes de table de " + brand + " à Rouen."],
  };
  const [title, description] = pages[page] || pages["index"];
  const image = siteHost + "/assets/mascottes/" + (qroque ? "croque-2-monsieur.png" : "ramen-1-bol.png?v=20261017-detourage");
  const canonical = siteHost + (page === "index" ? "/" : "/" + page);
  const metadata = `<meta name="description" content="${description}"><link rel="canonical" href="${canonical}"><meta property="og:type" content="website"><meta property="og:site_name" content="${brand}"><meta property="og:title" content="${title}"><meta property="og:description" content="${description}"><meta property="og:url" content="${canonical}"><meta property="og:image" content="${image}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${title}"><meta name="twitter:description" content="${description}"><meta name="twitter:image" content="${image}">`;
  let html = await response.text();
  if (qroque && page === "index") html = html.replace("ramen-1-bol.webp", "croque-2-monsieur.webp");
  const headers = new Headers(response.headers);
  headers.delete("content-length");
  headers.delete("etag");
  return new Response(html.replace(/<title>[^<]*<\/title>/i, `<title>${title}</title>`).replace(/<\/head>/i, metadata + "</head>"), {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}
