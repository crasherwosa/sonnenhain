#!/bin/sh
# Startet einen lokalen Webserver im Projektordner.
# Danach im Browser öffnen: http://localhost:8765/client/
cd "$(dirname "$0")/.." || exit 1
PORT="${PORT:-8765}"
echo "Sonnenhain läuft auf http://localhost:$PORT/client/  (Beenden mit Strg+C)"
python3 -m http.server "$PORT"
