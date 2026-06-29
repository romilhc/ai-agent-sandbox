import time
from dataclasses import dataclass

import httpx
import jwt

from app.config import settings

GITHUB_API = "https://api.github.com"
JWT_TTL_SECONDS = 9 * 60  # GitHub allows up to 10; leave a 1-min safety margin
INSTALL_TOKEN_SAFETY_SECONDS = 60


@dataclass
class _InstallationToken:
    token: str
    expires_at: float  # epoch seconds


_install_token_cache: dict[int, _InstallationToken] = {}


def app_jwt() -> str:
    cfg = settings()
    now = int(time.time())
    payload = {"iat": now - 30, "exp": now + JWT_TTL_SECONDS, "iss": cfg.app_id}
    return jwt.encode(payload, cfg.private_key, algorithm="RS256")


async def installation_token(installation_id: int) -> str:
    cached = _install_token_cache.get(installation_id)
    if cached and cached.expires_at - INSTALL_TOKEN_SAFETY_SECONDS > time.time():
        return cached.token

    headers = {
        "Authorization": f"Bearer {app_jwt()}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"{GITHUB_API}/app/installations/{installation_id}/access_tokens"
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=headers)
        r.raise_for_status()
    data = r.json()
    # expires_at is ISO-8601 UTC, e.g. "2026-06-23T19:42:11Z"
    expires_at = _parse_github_iso(data["expires_at"])
    tok = _InstallationToken(token=data["token"], expires_at=expires_at)
    _install_token_cache[installation_id] = tok
    return tok.token


def _parse_github_iso(s: str) -> float:
    # avoid full datetime overhead; strptime works fine for the fixed shape
    import datetime as _dt

    return _dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc).timestamp()
