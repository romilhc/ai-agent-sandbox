# ghtest1-app-romilhc

Argus prototype scaffold — minimal FastAPI GitHub App webhook handler with a
pure-Python smee.io forwarder. App ID `4129070`, installed on
`romilhc/ai-agent-sandbox`.

## Run

```bash
# terminal 1 — webhook handler
.venv/bin/uvicorn app.webhook:api --host 127.0.0.1 --port 8000 --reload

# terminal 2 — smee.io forwarder
.venv/bin/python scripts/smee_forward.py
```

Then hit "Redeliver" on any delivery in the App's
[Advanced settings](https://github.com/settings/apps/ghtest1-app-romilhc/advanced)
or open / comment on a PR in `romilhc/ai-agent-sandbox`.

Healthcheck: `curl http://127.0.0.1:8000/healthz`.

## Layout

```
app/
  config.py    # env + key loading
  auth.py      # App JWT + installation access token (TTL cache)
  webhook.py   # FastAPI app, HMAC verify, event routing
scripts/
  smee_forward.py  # SSE -> POST forwarder
```

## Secrets

`.env` and `*.pem` are gitignored. `.env` is `chmod 600`.
