import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings:
    app_id: str = os.environ["GITHUB_APP_ID"]
    webhook_secret: str = os.environ["GITHUB_WEBHOOK_SECRET"]
    private_key_path: Path = Path(os.environ["GITHUB_PRIVATE_KEY_PATH"]).expanduser()
    smee_url: str = os.environ.get("SMEE_URL", "")
    listen_host: str = os.environ.get("LISTEN_HOST", "127.0.0.1")
    listen_port: int = int(os.environ.get("LISTEN_PORT", "8000"))
    # Smee.io parses/reserializes the JSON body, breaking GitHub's HMAC.
    # Flip on in local dev only; never in production.
    dev_skip_signature: bool = os.environ.get("DEV_SKIP_SIGNATURE", "").lower() in {"1", "true", "yes"}

    @property
    def private_key(self) -> str:
        return self.private_key_path.read_text()


@lru_cache(maxsize=1)
def settings() -> Settings:
    return Settings()
