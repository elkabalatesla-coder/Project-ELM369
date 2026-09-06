"""Bo communications draft generator — never sends SMS/email/calls."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Sequence

from tools.elm_policy.geofence import stamp_line

TONES = {
    "corporate": "Polished, efficient, customer-service excellence.",
    "government": "Formal, structured, authoritative, neutral.",
    "both": "Adaptive — match formality to context.",
    "formal": "Formal with personal warmth.",
}
CHANNELS = ("sms", "email", "phone")

VAULT_PRIMARY = "JMR08241978202646902"
VAULT_COMPANION = "JMR0824197846902"
FOOTER_MARK = (
    "— Draft only · Project ELM369 · "
    f"primary {VAULT_PRIMARY} / companion {VAULT_COMPANION} · "
    "Kokomo IN 46902 · Joseph Michael Rose · IX JR · 🌹 · never transmits —"
)


def _opener(tone: str) -> str:
    return {
        "corporate": "Thank you for reaching out to Project ELM369.",
        "government": "This is an official response regarding your inquiry.",
        "both": "Thank you for your message.",
        "formal": "Hello — thank you for contacting us.",
    }[tone]


def _format_channel(channel: str, body: str) -> str:
    if channel == "email":
        return (
            "Subject: Re: your inquiry\n\n"
            f"{body}\n\n"
            f"{FOOTER_MARK}\n\n"
            "Respectfully,\nBo\nProject ELM369"
        )
    if channel == "phone":
        return (
            "[Phone script — do not auto-dial]\n"
            f"{body}\n"
            f"{FOOTER_MARK}\n"
            "[End script]"
        )
    return f"{body}\n\n{FOOTER_MARK}"


def draft(
    message: str,
    *,
    channel: str = "sms",
    tone: str = "corporate",
    prior_turns: Sequence[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build a single-turn or multi-turn draft. Never transmits."""
    channel = channel.lower()
    tone = tone.lower()
    if channel not in CHANNELS:
        raise ValueError("channel must be sms|email|phone")
    if tone not in TONES:
        raise ValueError("tone must be corporate|government|both|formal")

    turns: list[dict[str, str]] = []
    for t in prior_turns or []:
        role = str(t.get("role") or "user").lower()
        content = str(t.get("content") or "").strip()
        if not content:
            continue
        if role not in {"user", "assistant", "operator"}:
            role = "user"
        turns.append({"role": role, "content": content})

    turns.append({"role": "user", "content": message.strip()})

    history_block = ""
    if len(turns) > 1:
        lines = []
        for i, t in enumerate(turns[:-1], start=1):
            lines.append(f"[{i}] {t['role']}: {t['content']}")
        history_block = "Prior thread:\n" + "\n".join(lines) + "\n\n"

    opener = _opener(tone)
    latest = turns[-1]["content"]
    body = (
        f"{history_block}{opener} Regarding: “{latest}”. "
        "Bo (Communications Assistant for Project ELM369) "
        "has prepared this draft for your review. No message was sent."
    )
    text = _format_channel(channel, body)
    return {
        "assistant": "Bo",
        "channel": channel,
        "tone": tone,
        "tone_guide": TONES[tone],
        "turns": turns,
        "turn_count": len(turns),
        "draft": text,
        "sends": False,
        "disclaimer": "Draft only — never transmits SMS, email, or phone calls.",
        "provenance": {
            "stamp": stamp_line(),
            "location": "Kokomo, Indiana 46902 USA",
            "vault_primary": VAULT_PRIMARY,
            "vault_companion": VAULT_COMPANION,
            "signatory": "Joseph Michael Rose · IX JR · 🌹",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "footer": FOOTER_MARK,
        },
    }


def multi_turn_template(
    seed_message: str,
    *,
    channel: str = "sms",
    tone: str = "corporate",
    prior_turns: Sequence[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Convenience wrapper that always returns a multi-turn-ready draft envelope."""
    result = draft(seed_message, channel=channel, tone=tone, prior_turns=prior_turns)
    result["template"] = "multi_turn_v1"
    result["next_step"] = (
        "Append operator-approved reply as an assistant turn; "
        "re-run draft with prior_turns — still never sends."
    )
    return result
