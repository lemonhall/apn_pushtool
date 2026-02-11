from __future__ import annotations

import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import httpx
import pytest

from apn_pushtool.client import ApnsClient
from apn_pushtool.config import ApnsCredentials


def _creds(env: str = "sandbox") -> ApnsCredentials:
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    return ApnsCredentials(
        team_id="TEAM",
        key_id="KEY123",
        bundle_id="com.example.app",
        p8_private_key_pem=pem,
        environment=env,  # type: ignore[arg-type]
    )


@pytest.mark.asyncio
async def test_send_push_builds_correct_request_and_parses_success() -> None:
    device_token = "a" * 64

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "api.sandbox.push.apple.com"
        assert request.url.path == f"/3/device/{device_token}"
        assert request.headers["apns-topic"] == "com.example.app"
        assert request.headers["apns-push-type"] == "alert"
        assert request.headers["apns-priority"] == "10"
        assert request.headers["authorization"].startswith("bearer ")
        body = json.loads(request.content.decode("utf-8"))
        assert body["aps"]["alert"]["title"] == "T"
        return httpx.Response(status_code=200, json={})

    transport = httpx.MockTransport(handler)
    client = ApnsClient(_creds("sandbox"), transport=transport)

    payload = client.create_basic_payload(title="T", body="B", badge=1)
    result = await client.send_push(device_token=device_token, payload=payload)
    assert result["success"] is True
    assert result["status_code"] == 200


@pytest.mark.asyncio
async def test_send_push_includes_error_body_for_non_200() -> None:
    device_token = "b" * 64

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=400, json={"reason": "BadDeviceToken"})

    transport = httpx.MockTransport(handler)
    client = ApnsClient(_creds("production"), transport=transport)
    payload = client.create_basic_payload(title="T", body="B")

    result = await client.send_push(device_token=device_token, payload=payload)
    assert result["success"] is False
    assert result["status_code"] == 400
    assert result["error"]["reason"] == "BadDeviceToken"
