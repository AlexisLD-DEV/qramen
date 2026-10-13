#!/usr/bin/env bash
# Met Le QRamen en ligne : service systemd --user + site Caddy sur qramen.ledeunf.fr
set -euo pipefail
PORT=8802
DIR=/srv/projects/shared/qramen/public
SVC=~/.config/systemd/user/qramen.service
mkdir -p ~/.config/systemd/user /etc/caddy/sites 2>/dev/null || true

cat > "$SVC" <<EOF
[Unit]
Description=Le QRamen - page de commande par QR code (exercice formation)
After=network.target

[Service]
Type=simple
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 -m http.server $PORT --bind 127.0.0.1 --directory $DIR
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now qramen.service
sleep 2
systemctl --user is-active qramen.service

sudo -n tee /etc/caddy/sites/qramen.caddy >/dev/null <<'EOF'
qramen.ledeunf.fr {
	encode zstd gzip
	header Cache-Control "no-store"
	header X-Robots-Tag "noindex, nofollow"
	reverse_proxy 127.0.0.1:8802
}
EOF

sudo -n systemctl reload caddy
sleep 3
curl -s -o /dev/null -w "local 8802 : %{http_code}\n" --max-time 10 http://127.0.0.1:8802/menu.html
curl -s -o /dev/null -w "public qramen.ledeunf.fr : %{http_code}\n" --max-time 20 https://qramen.ledeunf.fr/menu.html
