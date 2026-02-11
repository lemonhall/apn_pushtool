from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives import serialization
import httpx
import jwt

from apn_pushtool.config import ApnsCredentials, ApnsEnvironment


class ApnsClient:
    def __init__(
        self,
        creds: ApnsCredentials,
        *,
        timeout_seconds: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._creds = creds
        self._timeout_seconds = timeout_seconds
        self._transport = transport

        self._private_key = serialization.load_pem_private_key(
            creds.p8_private_key_pem.encode("utf-8"), password=None
        )

    @property
    def environment(self) -> ApnsEnvironment:
        return self._creds.environment

    @property
    def apns_server(self) -> str:
        return (
            "https://api.sandbox.push.apple.com"
            if self._creds.environment == "sandbox"
            else "https://api.push.apple.com"
        )

    def generate_jwt_token(self) -> str:
        headers = {"alg": "ES256", "kid": self._creds.key_id}
        payload = {"iss": self._creds.team_id, "iat": int(time.time())}
        return jwt.encode(payload, self._private_key, algorithm="ES256", headers=headers)

    def create_basic_payload(
        self,
        *,
        title: str,
        body: str,
        badge: Optional[int] = None,
        sound: str = "default",
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        aps: Dict[str, Any] = {"alert": {"title": title, "body": body}, "sound": sound}
        if badge is not None:
            aps["badge"] = badge

        payload: Dict[str, Any] = {"aps": aps}
        if custom_data:
            payload.update(custom_data)
        return payload

    async def send_push(
        self,
        *,
        device_token: str,
        payload: Dict[str, Any],
        topic: Optional[str] = None,
        push_type: str = "alert",
        priority: int = 10,
        collapse_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if topic is None:
            topic = self._creds.bundle_id

        jwt_token = self.generate_jwt_token()
        headers: Dict[str, str] = {
            "authorization": f"bearer {jwt_token}",
            "apns-topic": topic,
            "apns-push-type": push_type,
            "apns-priority": str(priority),
            "content-type": "application/json",
        }
        if collapse_id:
            headers["apns-collapse-id"] = collapse_id

        url = f"{self.apns_server}/3/device/{device_token}"

        async with httpx.AsyncClient(
            http2=True,
            timeout=self._timeout_seconds,
            transport=self._transport,
            trust_env=True,
        ) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "device_token": device_token[:8] + "...",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        result: Dict[str, Any] = {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "device_token": device_token[:8] + "...",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if response.status_code != 200:
            try:
                result["error"] = response.json()
            except Exception:
                result["error"] = {"reason": "Unknown error", "status": response.status_code}

        return result

    async def send_long_message(
        self,
        *,
        device_token: str,
        title: str,
        long_text: str,
        max_chars: int = 50,
        delay_seconds: float = 2.5,
        start_badge: int = 1,
    ) -> list[Dict[str, Any]]:
        chunks = [long_text[i : i + max_chars] for i in range(0, len(long_text), max_chars)]
        total_messages = len(chunks)
        results: list[Dict[str, Any] | None] = [None] * total_messages

        for send_order in range(total_messages, 0, -1):
            index = send_order - 1
            chunk = chunks[index]

            current_badge = start_badge + send_order - 1 if start_badge > 0 else None
            payload = self.create_basic_payload(
                title=f"{title} ({send_order}/{total_messages})",
                body=chunk,
                badge=current_badge,
                custom_data={
                    "source": "long_message",
                    "part": send_order,
                    "total": total_messages,
                    "send_order": total_messages - send_order + 1,
                    "timestamp": int(time.time()),
                },
            )

            results[index] = await self.send_push(device_token=device_token, payload=payload)

            if send_order > 1:
                await asyncio.sleep(delay_seconds)

        return [r for r in results if r is not None]
