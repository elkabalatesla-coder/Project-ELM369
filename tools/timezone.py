"""Timezone helper with compatibility for Python < 3.9.

This module provides a simple ZoneInfo fallback using backports.zoneinfo
for older Python runtimes.
"""

try:
    # Python 3.9+
    from zoneinfo import ZoneInfo
except Exception:  # ImportError on older Python versions
    from backports.zoneinfo import ZoneInfo


def get_timezone(name: str = "America/Indiana/Indianapolis") -> ZoneInfo:
    """Return a ZoneInfo instance for the given IANA timezone name.

    Defaults to America/Indiana/Indianapolis to preserve existing behavior.
    """
    return ZoneInfo(name)


if __name__ == "__main__":
    import datetime

    tz = get_timezone()
    now = datetime.datetime.now(tz)
    print(now.isoformat())
