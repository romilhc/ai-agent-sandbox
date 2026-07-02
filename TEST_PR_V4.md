# Argus webhook test v4

Post payload-logging + reload-fix test

- Timestamp: 2026-07-01 14:54 PT
- Payload logging: webhook_payloads/*.json
- Reload: --reload-dir app (no more 35-change restarts)
- .pem: /Users/rockytang/AAI/aai-labs-argus/app/app.pem ✅

Expected: 200 OK, dummy comment, payload saved to webhook_payloads/
