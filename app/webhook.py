import hashlib
import hmac
import json
import logging

import httpx
from fastapi import FastAPI, Header, HTTPException, Request

from app.auth import GITHUB_API, installation_token
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
log = logging.getLogger("argus.webhook")

api = FastAPI(title="argus-ghtest1")


def _verify_signature(body: bytes, signature_header: str | None) -> None:
    if settings().dev_skip_signature:
        log.warning("DEV_SKIP_SIGNATURE on — signature NOT verified")
        return
    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(status_code=401, detail="missing sha256 signature")
    expected = (
        "sha256="
        + hmac.new(settings().webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    )
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail="bad signature")


@api.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@api.post("/webhook")
async def webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_github_delivery: str = Header(...),
    x_hub_signature_256: str | None = Header(default=None),
) -> dict[str, str]:
    body = await request.body()
    _verify_signature(body, x_hub_signature_256)
    payload = json.loads(body) if body else {}
    action = payload.get("action", "")
    repo = (payload.get("repository") or {}).get("full_name", "")
    sender = (payload.get("sender") or {}).get("login", "")
    log.info(
        "event=%s action=%s repo=%s sender=%s delivery=%s",
        x_github_event,
        action,
        repo,
        sender,
        x_github_delivery,
    )

    handler = _HANDLERS.get(x_github_event)
    if handler:
        await handler(payload)
    return {"ok": "true"}


async def _handle_ping(payload: dict) -> None:
    log.info("ping zen=%r", payload.get("zen"))


async def _handle_installation(payload: dict) -> None:
    inst = payload.get("installation") or {}
    log.info(
        "installation action=%s id=%s account=%s",
        payload.get("action"),
        inst.get("id"),
        (inst.get("account") or {}).get("login"),
    )


_PR_COMMENT_ACTIONS = {"opened", "reopened", "synchronize"}

DUMMY_COMMENT = (
    "Hello from Argus! 🦉\n\n"
    "_This is a placeholder comment — real review logic coming soon._"
)


async def _handle_pull_request(payload: dict) -> None:
    pr = payload.get("pull_request") or {}
    action = payload.get("action", "")
    log.info(
        "pull_request #%s [%s] %s -> %s",
        pr.get("number"),
        action,
        (pr.get("head") or {}).get("ref"),
        (pr.get("base") or {}).get("ref"),
    )
    if action not in _PR_COMMENT_ACTIONS:
        return

    installation_id = (payload.get("installation") or {}).get("id")
    repo_full = (payload.get("repository") or {}).get("full_name")
    pr_number = pr.get("number")
    if not (installation_id and repo_full and pr_number):
        log.warning("missing installation/repo/pr fields; skipping comment")
        return

    token = await installation_token(installation_id)
    url = f"{GITHUB_API}/repos/{repo_full}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=headers, json={"body": DUMMY_COMMENT})
    if r.status_code >= 300:
        log.error("comment POST failed: %s %s", r.status_code, r.text[:300])
    else:
        log.info("posted dummy comment on #%s (%s)", pr_number, r.status_code)


async def _handle_issues(payload: dict) -> None:
    iss = payload.get("issue") or {}
    log.info("issue #%s [%s] %s", iss.get("number"), payload.get("action"), iss.get("title"))


_HANDLERS = {
    "ping": _handle_ping,
    "installation": _handle_installation,
    "installation_repositories": _handle_installation,
    "pull_request": _handle_pull_request,
    "issues": _handle_issues,
}
