#!/usr/bin/env python3
"""Petit service PDF local (HTML -> PDF via Chrome headless) pour n8n.

- Écoute sur 0.0.0.0:8798, protégé par un jeton partagé (en-tête X-PDF-Key).
- POST /pdf  {"html": "...", "nom": "ticket-7"}        -> PDF binaire
- POST /pdf?json=1                                     -> {"ok":true,"base64":...,"filename":...}
- GET  /sante                                          -> ok
"""
import base64
import json
import pathlib
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

CHROME = "/srv/hermes/.agent-browser/browsers/chrome-154.0.8037.92/chrome"
CLE = pathlib.Path("/srv/hermes/.hermes/.secrets/qramen-pdf.key")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if urlparse(self.path).path == "/sante":
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.headers.get("X-PDF-Key", "") != CLE.read_text().strip():
            self.send_error(403, "jeton invalide")
            return
        if urlparse(self.path).path != "/pdf":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 5_000_000:
                raise ValueError("taille de requête invalide")
            payload = json.loads(self.rfile.read(length))
            html = payload.get("html")
            nom = (payload.get("nom") or "document").strip()[:60] or "document"
            if not isinstance(html, str) or not html.strip():
                raise ValueError("champ html manquant")
        except Exception as e:
            self.send_error(400, f"requête invalide : {e}")
            return

        try:
            with tempfile.TemporaryDirectory() as d:
                src = pathlib.Path(d) / "page.html"
                out = pathlib.Path(d) / "page.pdf"
                src.write_text(html, encoding="utf-8")
                subprocess.run(
                    [CHROME, "--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                     "--no-pdf-header-footer", f"--print-to-pdf={out}", src.as_uri()],
                    check=True, capture_output=True, timeout=60,
                )
                pdf = out.read_bytes()
        except Exception as e:
            self.send_error(500, f"rendu impossible : {e}")
            return

        mode_json = "json=1" in self.path
        if mode_json:
            corps = json.dumps({"ok": True, "base64": base64.b64encode(pdf).decode(),
                                "filename": nom + ".pdf"}).encode()
            type_mime = "application/json"
        else:
            corps, type_mime = pdf, "application/pdf"
        self.send_response(200)
        self.send_header("Content-Type", type_mime)
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8798), Handler).serve_forever()
