import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

# Prefer an explicit env var so regular (non-editable) installs work correctly.
# Falls back to three-levels-up, which is correct for editable dev installs
# (src/audit/config.py → project root), but wrong for site-packages installs.
_PROJECT_ROOT = (
    Path(os.environ["BITCOIN_AUDIT_HOME"])
    if "BITCOIN_AUDIT_HOME" in os.environ
    else Path(__file__).parent.parent.parent
)

_config: dict | None = None
_env_loaded = False


def _ensure_env() -> None:
    global _env_loaded
    if not _env_loaded:
        load_dotenv(_PROJECT_ROOT / ".env")
        _env_loaded = True


def _load() -> dict:
    with open(_PROJECT_ROOT / "config.toml", "rb") as f:
        return tomllib.load(f)


def config() -> dict:
    global _config
    _ensure_env()
    if _config is None:
        _config = _load()
    return _config


def project_root() -> Path:
    return _PROJECT_ROOT


def env(key: str) -> str:
    _ensure_env()
    value = os.environ.get(key)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value
