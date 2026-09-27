"""CLI for the ELM369 security scaffold."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from tools.elm_security.security import list_security_tools, registry_summary, resolve_identity, safe_security_posture


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="elm-security", description="ELM369 security identity + registry scaffold")
    sub = parser.add_subparsers(dest="command", required=True)

    identity = sub.add_parser("identity", help="Resolve the canonical + companion identifiers")
    identity.add_argument("identifiers", nargs="*", help="Identifiers to verify. Defaults to the known anchor pair.")

    tools = sub.add_parser("tools", help="List registered security tools")
    tools.add_argument("--required-for", default="", help="Filter tools by required capability")
    tools.add_argument("--category", default="", help="Filter tools by category")

    sub.add_parser("registry", help="Summarize the security tool registry")
    sub.add_parser("verify", help="Run the scaffold posture checks")

    args = parser.parse_args(argv)

    if args.command == "identity":
        result = resolve_identity(identifiers=args.identifiers or None)
        print(json.dumps(result, indent=2))
        return 0 if result.get("integrity_status", {}).get("ok") else 1

    if args.command == "tools":
        result = list_security_tools(required_for=args.required_for or None, category=args.category or None)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "registry":
        result = registry_summary()
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 1

    if args.command == "verify":
        result = safe_security_posture()
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 1

    return 2
