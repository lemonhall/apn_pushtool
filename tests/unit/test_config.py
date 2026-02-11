from __future__ import annotations

from pathlib import Path

import pytest

from apn_pushtool.config import (
    ApnsCredentials,
    ConfigError,
    load_apns_credentials,
    normalize_device_token,
)


def test_normalize_device_token_strips_spaces_and_dashes() -> None:
    assert normalize_device_token(" aa-bb cc ") == "aabbcc"


def test_load_apns_credentials_requires_core_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APNS_TEAM_ID", raising=False)
    monkeypatch.delenv("APNS_KEY_ID", raising=False)
    monkeypatch.delenv("APNS_BUNDLE_ID", raising=False)
    monkeypatch.delenv("APNS_P8_PATH", raising=False)
    monkeypatch.delenv("APNS_P8_PRIVATE_KEY", raising=False)

    with pytest.raises(ConfigError):
        load_apns_credentials()


def test_load_apns_credentials_reads_p8_from_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    p8 = tmp_path / "AuthKey_TEST.p8"
    p8.write_text("-----BEGIN PRIVATE KEY-----\nTEST\n-----END PRIVATE KEY-----\n", encoding="utf-8")

    monkeypatch.setenv("APNS_TEAM_ID", "TEAM")
    monkeypatch.setenv("APNS_KEY_ID", "KEY")
    monkeypatch.setenv("APNS_BUNDLE_ID", "com.example.app")
    monkeypatch.setenv("APNS_P8_PATH", str(p8))

    creds = load_apns_credentials()
    assert isinstance(creds, ApnsCredentials)
    assert "BEGIN PRIVATE KEY" in creds.p8_private_key_pem


def test_load_apns_credentials_reads_p8_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APNS_TEAM_ID", "TEAM")
    monkeypatch.setenv("APNS_KEY_ID", "KEY")
    monkeypatch.setenv("APNS_BUNDLE_ID", "com.example.app")
    monkeypatch.setenv("APNS_P8_PRIVATE_KEY", "-----BEGIN PRIVATE KEY-----\nTEST\n-----END PRIVATE KEY-----\n")

    creds = load_apns_credentials()
    assert "BEGIN PRIVATE KEY" in creds.p8_private_key_pem

