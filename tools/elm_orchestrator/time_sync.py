"""Geo-NTP precision sync scaffold using stdlib NTP (no third-party deps)."""

from __future__ import annotations

import socket
import struct
from datetime import datetime, timezone
from typing import Any

NTP_SERVERS = (
    "time.google.com",
    "time.cloudflare.com",
    "pool.ntp.org",
)


def query_ntp(host: str = NTP_SERVERS[0], timeout: float = 2.0) -> dict[str, Any]:
    """Return NTP vs local UTC offset. Fail soft with status=error."""
    NTP_DELTA = 2208988800  # 1900 -> 1970
    try:
        addr = (host, 123)
        msg = b"\x1b" + 47 * b"\0"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.sendto(msg, addr)
            data, _ = sock.recvfrom(512)
        if len(data) < 48:
            return {"status": "error", "error": "short NTP packet", "host": host}
        unpacked = struct.unpack("!12I", data[0:48])
        tx_seconds = unpacked[10] - NTP_DELTA
        ntp_dt = datetime.fromtimestamp(tx_seconds, tz=timezone.utc)
        local = datetime.now(timezone.utc)
        offset = (ntp_dt - local).total_seconds()
        return {
            "status": "ok",
            "host": host,
            "ntp_utc": ntp_dt.isoformat(),
            "local_utc": local.isoformat(),
            "offset_seconds": round(offset, 6),
            "within_2s": abs(offset) <= 2.0,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "host": host, "error": str(exc)}


def sync_report() -> dict[str, Any]:
    results = [query_ntp(h) for h in NTP_SERVERS]
    ok = [r for r in results if r.get("status") == "ok"]
    return {
        "project_id": "ELM369_JMR08241978202646902",
        "agent": "ELM369-VAULT-LOGGER-04",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "ok": bool(ok) and all(r.get("within_2s") for r in ok),
        "results": results,
    }
