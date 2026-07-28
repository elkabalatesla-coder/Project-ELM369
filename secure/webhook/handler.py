# secure/webhook/handler.py

"""
Simple webhook receiver for Auto‑Amend Engine.
- Verifies X-Hub-Signature using SHARED_SECRET (HMAC-SHA256)
- Parses incoming event (email/webhook payload)
- Writes audit record to ./audit/ and creates a draft PR file for human review

NOTE: This is a template. Do NOT deploy to production without securing secrets, TLS, and rate limiting.
"""

from flask import Flask, request, jsonify, abort
import os
import hmac
import hashlib
import json
import uuid
from datetime import datetime

APP_SECRET = os.environ.get("AUTOAMEND_SHARED_SECRET", "change-me")
AUDIT_DIR = os.environ.get("AUTOAMEND_AUDIT_DIR", "./security/audit/webhook")

app = Flask(__name__)

os.makedirs(AUDIT_DIR, exist_ok=True)


def verify_signature(payload, signature_header):
    if not signature_header:
        return False
    try:
        sig_type, sig_hex = signature_header.split('=')
    except Exception:
        return False
    if sig_type.lower() != 'sha256':
        return False
    mac = hmac.new(APP_SECRET.encode('utf-8'), payload, hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), sig_hex)


@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig = request.headers.get('X-Hub-Signature-256') or request.headers.get('X-Hub-Signature')
    if not verify_signature(payload, sig):
        abort(401)

    event = request.get_json(silent=True) or {}
    # Minimal extraction: sender, subject, body
    sender = event.get('sender') or event.get('from') or event.get('email')
    subject = event.get('subject') or event.get('title')
    body = event.get('body') or event.get('text') or json.dumps(event)

    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + 'Z'

    audit = {
        'request_id': request_id,
        'timestamp': timestamp,
        'sender': sender,
        'subject': subject,
        'watermark': 'ELM369-JMR08241978202646902-IX-JR-🌹',
        'tags': ['email','auto-amend','incoming'],
        'payload_preview': body[:1024]
    }

    audit_path = os.path.join(AUDIT_DIR, f'{request_id}.json')
    with open(audit_path, 'w') as f:
        json.dump(audit, f, indent=2)

    # Create a draft PR file for human review (do not auto-push changes)
    draft_dir = './auto-amend/drafts'
    os.makedirs(draft_dir, exist_ok=True)
    draft_path = os.path.join(draft_dir, f'pr_draft_{request_id}.md')
    with open(draft_path, 'w') as f:
        f.write(f"# Auto‑Amend PR Draft\n\nRequest ID: {request_id}\n\nSender: {sender}\n\nSubject: {subject}\n\n---\n\n{body}\n")

    return jsonify({'status':'accepted','request_id':request_id}), 202


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
