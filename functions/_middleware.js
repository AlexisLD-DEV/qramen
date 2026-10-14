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
  return next();
}
