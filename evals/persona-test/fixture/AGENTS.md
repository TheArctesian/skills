# Larder

Static site, no build step. Serve it locally with:

    python3 -m http.server 8765 --bind 127.0.0.1

then open http://127.0.0.1:8765/. Ready check: `curl -sf http://127.0.0.1:8765/`. State lives in the browser's
localStorage; no accounts, no payments, no email.
