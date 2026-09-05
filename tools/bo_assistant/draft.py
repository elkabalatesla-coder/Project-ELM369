"""Bo communications draft generator — never sends SMS/email/calls."""

from __future__ import annotations

from typing import Any

TONES = {
    "corporate": "Polished, efficient, customer-service excellence.",
    "government": "Formal, structured, authoritative, neutral.",
    "both": "Adaptive — match formality to context.",
    "formal": "Formal with personal warmth.",
}
CHANNELS = ("sms", "email", "phone")


def draft(message: str, *, channel: str = "sms", tone: str = "corporate") -> dict[str, Any]:
    channel = channel.lower()
    tone = tone.lower()
    if channel not in CHANNELS:
        raise ValueError("channel must be sms|email|phone")
    if tone not in TONES:
        raise ValueError("tone must be corporate|government|both|formal")
    opener = {
        "corporate": "Thank you for reaching out to Project ELM369.",
        "government": "This is an official response regarding your inquiry.",
        "both": "Thank you for your message.",
        "formal": "Hello — thank you for contacting us.",
    }[tone]
    body = (
        f"{opener} Regarding: “{message.strip()}”. "
        "Bo (Communications Assistant for Project ELM369, ref JMR08241978202646902) "
        "has prepared this draft for your review. No message was sent."
    )
    if channel == "email":
        text = f"Subject: Re: your inquiry\n\n{body}\n\nRespectfully,\nBo\nProject ELM369"
    elif channel == "phone":
        text = f"[Phone script]\n{body}\n[End script — do not auto-dial]"
    else:
        text = body
    return {
        "assistant": "Bo",
        "channel": channel,
        "tone": tone,
        "tone_guide": TONES[tone],
        "draft": text,
        "sends": False,
        "disclaimer": "Draft only — never transmits SMS, email, or phone calls.",
    }
