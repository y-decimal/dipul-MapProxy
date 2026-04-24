#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

HOST="${MAPPROXY_HOST:-127.0.0.1}"
PORT="${MAPPROXY_PORT:-8080}"

if ss -ltn "sport = :${PORT}" 2>/dev/null | grep -q "LISTEN"; then
  echo "[start-mapproxy] Port ${PORT} is already in use."
  echo "[start-mapproxy] Stop the existing process or set MAPPROXY_PORT to another free port."
  exit 1
fi

if [[ ! -x ".venv/bin/mapproxy-util" ]]; then
  echo "[start-mapproxy] Missing .venv/bin/mapproxy-util"
  echo "[start-mapproxy] Creating venv and installing dependencies from requirements.txt"
  python3 -m venv .venv
  . .venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

echo "[start-mapproxy] Starting MapProxy at http://${HOST}:${PORT}/service?"
echo "[start-mapproxy] Press Ctrl+C to stop"
export MAPPROXY_HOST="$HOST"
export MAPPROXY_PORT="$PORT"

if [[ "$HOST" == "0.0.0.0" ]]; then
  LOCAL_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
  echo "[start-mapproxy] For iNav, do not use 0.0.0.0 as the URL."
  echo "[start-mapproxy] Use http://127.0.0.1:${PORT}/service? if iNav runs on this machine."
  if [[ -n "${LOCAL_IP:-}" ]]; then
    echo "[start-mapproxy] Use http://${LOCAL_IP}:${PORT}/service? if iNav runs on another device on your LAN."
  fi
fi

# Run in foreground without the development reloader so closing the terminal stops the server cleanly.
exec ./.venv/bin/python - <<'PY'
import os
from wsgiref.simple_server import make_server

from mapproxy.wsgiapp import make_wsgi_app

host = os.environ.get("MAPPROXY_HOST", "0.0.0.0")
port = int(os.environ.get("MAPPROXY_PORT", "8080"))

app = make_wsgi_app(services_conf="mapproxy_config/mapproxy.yaml", debug=False, reloader=False)
with make_server(host, port, app) as server:
  server.serve_forever()
PY
