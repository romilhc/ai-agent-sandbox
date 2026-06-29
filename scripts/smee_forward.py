"""Python smee.io -> local webhook forwarder.

Subscribes to a smee.io channel over SSE and POSTs each event payload to a
local URL (e.g. http://127.0.0.1:8000/webhook). Mirrors the behavior of the
`smee-client` Node CLI, minus Node.

Usage:
    SMEE_URL=https://smee.io/xxxx TARGET=http://127.0.0.1:8000/webhook \
        python scripts/smee_forward.py
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Make `app.config` importable when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from httpx_sse import aconnect_sse

from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s smee :: %(message)s")
log = logging.getLogger("argus.smee")


async def forward() -> None:
    cfg = settings()
    smee_url = os.environ.get("SMEE_URL", cfg.smee_url)
    target = os.environ.get("TARGET", f"http://{cfg.listen_host}:{cfg.listen_port}/webhook")
    if not smee_url:
        raise SystemExit("SMEE_URL is required (set in .env or env var)")

    log.info("forwarding %s -> %s", smee_url, target)

    async with httpx.AsyncClient(timeout=None) as sse_client, httpx.AsyncClient(timeout=30) as post_client:
        async with aconnect_sse(sse_client, "GET", smee_url, headers={"Accept": "text/event-stream"}) as events:
            async for event in events.aiter_sse():
                if event.event != "message" or not event.data:
                    continue
                try:
                    msg = json.loads(event.data)
                except json.JSONDecodeError:
                    log.warning("non-json sse data, skipping")
                    continue
                await _forward_one(post_client, target, msg)


async def _forward_one(client: httpx.AsyncClient, target: str, msg: dict) -> None:
    body = msg.get("body")
    if body is None:
        return
    # smee preserves the raw JSON body under "body" and headers as siblings;
    # GitHub headers come through with their original X-* names.
    headers = {k: v for k, v in msg.items() if k.lower().startswith("x-") or k.lower() == "content-type"}
    headers.setdefault("Content-Type", "application/json")
    payload = body if isinstance(body, (bytes, str)) else json.dumps(body)
    if isinstance(payload, str):
        payload = payload.encode()
    try:
        r = await client.post(target, content=payload, headers=headers)
        log.info("POST %s -> %s (%s bytes)", target, r.status_code, len(payload))
    except httpx.HTTPError as e:
        log.error("forward failed: %s", e)


if __name__ == "__main__":
    asyncio.run(forward())
