from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Literal

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    pass


ApnsEnvironment = Literal["sandbox", "production"]


@dataclass(frozen=True, slots=True)
class ApnsCredentials:
    team_id: str
    key_id: str
    bundle_id: str
    p8_private_key_pem: str
    environment: ApnsEnvironment


def normalize_device_token(token: str) -> str:
    return token.strip().replace(" ", "").replace("-", "")


def is_valid_device_token(token: str) -> bool:
    token = normalize_device_token(token)
    if len(token) != 64:
        return False
    try:
        int(token, 16)
    except ValueError:
        return False
    return True


def load_device_token(*, dotenv_path: str | None = None) -> str:
    if dotenv_path:
        load_dotenv(dotenv_path, override=False)
    token = os.getenv("APNS_DEVICE_TOKEN", "").strip()
    if not token:
        raise ConfigError("Missing APNS_DEVICE_TOKEN (or pass --device-token).")
    token = normalize_device_token(token)
    if not is_valid_device_token(token):
        raise ConfigError("Invalid device token format. Expect 64 hex characters.")
    return token


def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise ConfigError(f"File not found: {path}") from e


def _resolve_path(path_str: str, *, dotenv_path: str | None) -> Path:
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path

    if dotenv_path:
        base = Path(dotenv_path).expanduser()
        base_dir = base if base.is_dir() else base.parent
    else:
        base_dir = Path.cwd()

    return (base_dir / path).resolve()


def load_apns_credentials(*, dotenv_path: str | None = None) -> ApnsCredentials:
    """
    Load APNs credentials from environment variables (optionally loading a .env first).

    Required:
    - APNS_TEAM_ID
    - APNS_KEY_ID
    - APNS_BUNDLE_ID
    - APNS_P8_PATH or APNS_P8_PRIVATE_KEY

    Optional:
    - APNS_ENV: sandbox|production (default: production)
    - APNS_USE_SANDBOX: 1|0 / true|false (legacy, overrides APNS_ENV if set)
    """
    if dotenv_path:
        load_dotenv(dotenv_path, override=False)

    team_id = os.getenv("APNS_TEAM_ID", "").strip()
    key_id = os.getenv("APNS_KEY_ID", "").strip()
    bundle_id = os.getenv("APNS_BUNDLE_ID", "").strip()

    p8_path = os.getenv("APNS_P8_PATH", "").strip()
    p8_inline = os.getenv("APNS_P8_PRIVATE_KEY", "").strip()

    if not team_id or not key_id or not bundle_id or (not p8_path and not p8_inline):
        raise ConfigError(
            "Missing required env vars. Need APNS_TEAM_ID, APNS_KEY_ID, APNS_BUNDLE_ID and APNS_P8_PATH or APNS_P8_PRIVATE_KEY."
        )

    p8_private_key_pem = p8_inline
    if p8_path:
        resolved_p8 = _resolve_path(p8_path, dotenv_path=dotenv_path)
        p8_private_key_pem = _read_text_file(resolved_p8)

    # Environment
    env_value = os.getenv("APNS_ENV", "").strip().lower()
    use_sandbox_value = os.getenv("APNS_USE_SANDBOX", "").strip().lower()

    environment: ApnsEnvironment = "production"
    if env_value in ("sandbox", "production"):
        environment = env_value  # type: ignore[assignment]

    if use_sandbox_value:
        if use_sandbox_value in ("1", "true", "yes", "y", "on"):
            environment = "sandbox"
        elif use_sandbox_value in ("0", "false", "no", "n", "off"):
            environment = "production"
        else:
            raise ConfigError("Invalid APNS_USE_SANDBOX value. Use 1/0 or true/false.")

    return ApnsCredentials(
        team_id=team_id,
        key_id=key_id,
        bundle_id=bundle_id,
        p8_private_key_pem=p8_private_key_pem,
        environment=environment,
    )
