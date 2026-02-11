from __future__ import annotations

import os
import time

import pytest

from apn_pushtool.client import ApnsClient
from apn_pushtool.config import ConfigError, load_apns_credentials, load_device_token


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_real_apns_push_returns_200() -> None:
    """
    REQ-0001-004: E2E opt-in real push

    Hard evidence: APNs returns HTTP 200.
    Manual evidence: user confirms the phone received the notification.
    """
    if os.getenv("APNS_E2E", "").strip() not in ("1", "true", "yes", "on"):
        pytest.skip("Set APNS_E2E=1 to enable real APNs E2E test.")

    dotenv_path = os.getenv("APNS_DOTENV", ".env")

    try:
        creds = load_apns_credentials(dotenv_path=dotenv_path)
        device_token = load_device_token(dotenv_path=dotenv_path)
    except ConfigError as e:
        pytest.skip(f"Missing/invalid config for E2E: {e}")

    client = ApnsClient(creds)
    payload = client.create_basic_payload(
        title="apn-pushtool E2E",
        body=f"E2E ping {int(time.time())}",
        badge=None,
        custom_data={"source": "apn-pushtool-e2e"},
    )

    result = await client.send_push(device_token=device_token, payload=payload, push_type="alert")
    assert result["success"] is True, result
    assert result["status_code"] == 200, result

