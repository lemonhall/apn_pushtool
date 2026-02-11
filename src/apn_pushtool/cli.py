from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys
from typing import Any

from apn_pushtool.client import ApnsClient
from apn_pushtool.config import (
    ConfigError,
    is_valid_device_token,
    load_apns_credentials,
    normalize_device_token,
)


def _redact(value: str, *, keep_start: int = 6, keep_end: int = 4) -> str:
    v = value.strip()
    if len(v) <= keep_start + keep_end:
        return "***"
    return f"{v[:keep_start]}...{v[-keep_end:]}"


def _bool_env_hint() -> str:
    return "Use APNS_ENV=sandbox|production (or APNS_USE_SANDBOX=true|false)."


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="apn-pushtool", description="APNs push CLI tool")
    p.add_argument("--dotenv", default=".env", help="Path to .env file (default: .env). Use '' to skip.")

    sub = p.add_subparsers(dest="cmd", required=True)

    doctor = sub.add_parser("doctor", help="Validate current config (does not print private key).")
    doctor.add_argument("--device-token", default="", help="Optional device token to validate.")

    send = sub.add_parser("send", help="Send one push notification.")
    send.add_argument("--title", required=True)
    send.add_argument("--body", required=True)
    send.add_argument("--badge", type=int, default=None)
    send.add_argument("--sound", default="default")
    send.add_argument("--device-token", default="", help="Defaults to APNS_DEVICE_TOKEN if omitted.")
    send.add_argument("--topic", default="", help="Defaults to APNS_BUNDLE_ID if omitted.")
    send.add_argument("--push-type", default="alert", help="APNs push type (default: alert).")
    send.add_argument("--priority", type=int, default=10, choices=[5, 10])
    send.add_argument("--collapse-id", default="")
    send.add_argument("--json", action="store_true", help="Print result as JSON only.")

    send_long = sub.add_parser("send-long", help="Split long text and send multiple pushes (reverse order).")
    send_long.add_argument("--title", required=True)
    g = send_long.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", default="")
    g.add_argument("--text-file", default="", help="Read UTF-8 text from file.")
    send_long.add_argument("--max-chars", type=int, default=50)
    send_long.add_argument("--delay-seconds", type=float, default=2.5)
    send_long.add_argument("--start-badge", type=int, default=1)
    send_long.add_argument("--device-token", default="", help="Defaults to APNS_DEVICE_TOKEN if omitted.")
    send_long.add_argument("--json", action="store_true", help="Print result as JSON only.")

    return p.parse_args(argv)


def _dotenv_path(value: str) -> str | None:
    if value == "":
        return None
    return value


def cmd_doctor(args: argparse.Namespace) -> int:
    dotenv_path = _dotenv_path(args.dotenv)

    try:
        creds = load_apns_credentials(dotenv_path=dotenv_path)
    except ConfigError as e:
        print(f"❌ Config error: {e}", file=sys.stderr)
        print(_bool_env_hint(), file=sys.stderr)
        return 2

    print("✅ APNs credentials loaded")
    print(f"- env: {creds.environment}")
    print(f"- team_id: {_redact(creds.team_id)}")
    print(f"- key_id: {_redact(creds.key_id)}")
    print(f"- bundle_id: {creds.bundle_id}")
    print(f"- p8_private_key_pem: present ({len(creds.p8_private_key_pem)} chars)")

    token = args.device_token.strip()
    if token:
        token = normalize_device_token(token)
        ok = is_valid_device_token(token)
        print(f"- device_token: {_redact(token, keep_start=10, keep_end=10)} ({len(token)} chars) valid={ok}")

    return 0


async def _send_one(args: argparse.Namespace) -> dict[str, Any]:
    dotenv_path = _dotenv_path(args.dotenv)
    creds = load_apns_credentials(dotenv_path=dotenv_path)
    client = ApnsClient(creds)

    device_token = args.device_token.strip()
    if not device_token:
        from apn_pushtool.config import load_device_token

        device_token = load_device_token(dotenv_path=dotenv_path)
    device_token = normalize_device_token(device_token)
    if not is_valid_device_token(device_token):
        raise ConfigError("Invalid device token format. Expect 64 hex characters.")

    topic = args.topic.strip() or creds.bundle_id
    collapse_id = args.collapse_id.strip() or None

    payload = client.create_basic_payload(
        title=args.title,
        body=args.body,
        badge=args.badge,
        sound=args.sound,
        custom_data={"source": "apn-pushtool", "ts": int(asyncio.get_event_loop().time())},
    )

    return await client.send_push(
        device_token=device_token,
        payload=payload,
        topic=topic,
        push_type=args.push_type,
        priority=args.priority,
        collapse_id=collapse_id,
    )


async def _send_long(args: argparse.Namespace) -> list[dict[str, Any]]:
    dotenv_path = _dotenv_path(args.dotenv)
    creds = load_apns_credentials(dotenv_path=dotenv_path)
    client = ApnsClient(creds)

    device_token = args.device_token.strip()
    if not device_token:
        from apn_pushtool.config import load_device_token

        device_token = load_device_token(dotenv_path=dotenv_path)
    device_token = normalize_device_token(device_token)
    if not is_valid_device_token(device_token):
        raise ConfigError("Invalid device token format. Expect 64 hex characters.")

    if args.text_file:
        long_text = Path(args.text_file).read_text(encoding="utf-8")
    else:
        long_text = args.text

    return await client.send_long_message(
        device_token=device_token,
        title=args.title,
        long_text=long_text,
        max_chars=args.max_chars,
        delay_seconds=args.delay_seconds,
        start_badge=args.start_badge,
    )


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)

    try:
        if args.cmd == "doctor":
            raise SystemExit(cmd_doctor(args))

        if args.cmd == "send":
            result = asyncio.run(_send_one(args))
            if args.json:
                print(json.dumps(result, ensure_ascii=False))
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            raise SystemExit(0 if result.get("success") else 1)

        if args.cmd == "send-long":
            results = asyncio.run(_send_long(args))
            if args.json:
                print(json.dumps(results, ensure_ascii=False))
            else:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            ok = all(r.get("success") for r in results)
            raise SystemExit(0 if ok else 1)

        raise SystemExit(2)
    except ConfigError as e:
        print(f"❌ Config error: {e}", file=sys.stderr)
        raise SystemExit(2) from e
