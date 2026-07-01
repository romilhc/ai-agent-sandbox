# Argus webhook test

Testing PR webhook trigger for codimango/aai-labs-argus

- Source: romilhc/ai-agent-sandbox
- Target test: pull_request opened event
- Timestamp: 2026-07-01

This should trigger:
1. webhook POST to /webhook
2. Argus logs: event=pull_request action=opened
3. Dummy comment posted back to PR (if .pem configured)
