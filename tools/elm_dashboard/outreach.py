"""Local research and inquiry review; no network access or message submission."""

import json
from html import escape
from pathlib import Path
from urllib.parse import urlsplit


DIRECTORY = Path(__file__).resolve().parents[2] / "data/registries/elm369_outreach.json"


def build_outreach():
    """Expose source uncertainty and drafts without implying approval or delivery."""
    directory = json.loads(DIRECTORY.read_text(encoding="utf-8"))
    organizations = []
    for record in directory["organizations"]:
        url = urlsplit(record["url"])
        if (
            url.scheme != "https" or not url.hostname or url.username or url.password
            or any(character.isspace() for character in record["url"])
        ):
            raise ValueError("Outreach links must be HTTPS URLs without credentials.")
        organizations.append({
            **record,
            "status": "draft_pending_review",
            "approved": False,
            "sent": False,
            "subject": "Project ELM369 — educational engineering / organizational inquiry",
            "draft": (
                f"Hello {record['name']} team,\n\n"
                "Project ELM369 is an independent educational software project exploring "
                "planar robotics, PID control, and a simulated 1% resource allocation. "
                "It is not a university-affiliated program, production hardware controller, "
                "or established charity partnership.\n\n"
                f"{record['inquiry']}\n\n"
                "Please direct us to the appropriate public resources or inquiry channel. "
                "This inquiry does not offer payment, pledge funds, or request endorsement.\n\n"
                "Regards,\n[Sender name and reply address to be approved before submission]"
            ),
        })
    return {
        "schema": "elm369.outreach_portal.v1",
        "research_date": directory["research_date"],
        "scope": directory["scope"],
        "research_limitations": directory["research_limitations"],
        "communications_established": False,
        "transmits": False,
        "workflow": [
            "Verify the current official contact route and recipient eligibility.",
            "Approve the exact recipient, message, sender identity, and reply address.",
            "Submit manually through the approved organization portal; respect its terms.",
            "Retain the portal receipt privately; only a receipt can support a sent claim.",
            "A reply is needed before claiming two-way communications; a partnership needs explicit agreement.",
        ],
        "organizations": organizations,
    }


def render_outreach():
    """Render escaped, script-free HTML with no automatic external requests."""
    portal = build_outreach()
    parts = [
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta http-equiv="Content-Security-Policy" '
        'content="default-src \'none\'; base-uri \'none\'; form-action \'none\'">',
        '<meta name="referrer" content="no-referrer">',
        "<title>ELM369 Research and Outreach Portal</title></head><body>",
        "<main><h1>ELM369 Research and Outreach Portal</h1>",
        "<p><strong>Local draft workspace. No messages sent. "
        "No external communications or partnerships established.</strong></p>",
        f"<p>Research date: {escape(portal['research_date'])}</p>",
        f"<p>{escape(portal['scope'])}</p>",
        f"<p>{escape(portal['research_limitations'])}</p>",
        "<h2>Approval and submission workflow</h2><ol>",
    ]
    parts.extend(f"<li>{escape(step)}</li>" for step in portal["workflow"])
    parts.append("</ol><h2>Organization directory and draft inquiries</h2>")
    for organization in portal["organizations"]:
        parts.extend([
            "<article>",
            f"<h3>{escape(organization['name'])}</h3>",
            f"<p>Category: {escape(organization['category'])}. "
            f"Source: {escape(organization['source_status'])}. "
            "Status: draft pending review; not approved; not sent.</p>",
            f"<p>{escape(organization['route'])}</p>",
            f'<p><a href="{escape(organization["url"], quote=True)}" '
            'target="_blank" rel="noopener noreferrer">Open organization site '
            "(unverified route)</a></p>",
            f"<p>Subject: {escape(organization['subject'])}</p>",
            f"<pre>{escape(organization['draft'])}</pre>",
            "</article>",
        ])
    parts.append("</main></body></html>")
    return "\n".join(parts)
