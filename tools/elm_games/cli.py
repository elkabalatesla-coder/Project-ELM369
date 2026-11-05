"""Generate portable game projects or a browser maker without external services."""

import argparse
import json
import sys
from pathlib import Path

from .engine import GENRES, MODES, load_project, make_project, render_html


def main(argv=None):
    parser = argparse.ArgumentParser(prog="elm-games")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("catalog", help="List playable templates and platform limits")
    check = commands.add_parser("validate", help="Validate a declarative JSON project")
    check.add_argument("project")
    generate = commands.add_parser("generate", help="Create a project or playable HTML studio")
    generate.add_argument("--project", help="Load an existing JSON project instead of settings")
    generate.add_argument("--title", default="ELM369 Arcade")
    generate.add_argument("--genre", choices=GENRES, default="snake")
    generate.add_argument("--mode", choices=MODES, default="standard")
    generate.add_argument("--seed", type=int, default=369)
    generate.add_argument("--difficulty", type=int, default=2)
    generate.add_argument("--color", default="#69e0af")
    generate.add_argument("--format", choices=("html", "json"), default="html")
    generate.add_argument("--output", required=True)
    generate.add_argument("--force", action="store_true", help="Allow replacing an existing export")
    args = parser.parse_args(argv)
    try:
        if args.command == "catalog":
            print(json.dumps({
                "genres": list(GENRES), "modes": list(MODES),
                "runtime": "HTML5 Canvas; keyboard, touch, standard gamepad",
                "online": "Static hosting; no multiplayer or backend",
                "console": "Browser/controller prototype only; no native console SDK export",
            }, indent=2))
            return 0
        if args.command == "validate":
            print(json.dumps(load_project(args.project), indent=2))
            return 0
        project = load_project(args.project) if args.project else make_project(
            title=args.title, genre=args.genre, mode=args.mode, seed=args.seed,
            difficulty=args.difficulty, color=args.color,
        )
        output = render_html(project) if args.format == "html" else json.dumps(project, indent=2) + "\n"
        with Path(args.output).open("w" if args.force else "x", encoding="utf-8") as handle:
            handle.write(output)
        print(args.output)
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print("elm-games: {}".format(exc), file=sys.stderr)
        return 2
