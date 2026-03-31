import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

# src/audit/config.py → project root is three levels up
_PROJECT_ROOT = Path(__file__).parent.parent.parent

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
