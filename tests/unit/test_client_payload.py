from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from apn_pushtool.client import ApnsClient
from apn_pushtool.config import ApnsCredentials


def _dummy_creds() -> ApnsCredentials:
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    return ApnsCredentials(
        team_id="TEAM",
        key_id="KEY",
        bundle_id="com.example.app",
        p8_private_key_pem=pem,
        environment="sandbox",
    )


def test_create_basic_payload_includes_custom_data() -> None:
    client = ApnsClient(_dummy_creds())
    payload = client.create_basic_payload(
        title="T", body="B", badge=3, custom_data={"custom_data": {"a": 1}}
    )
    assert payload["aps"]["alert"]["title"] == "T"
    assert payload["aps"]["alert"]["body"] == "B"
    assert payload["aps"]["badge"] == 3
    assert payload["custom_data"]["a"] == 1
