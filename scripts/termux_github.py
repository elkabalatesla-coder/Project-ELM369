#!/usr/bin/env python3
"""GitHub repositories, pull requests, and source archives for Termux pipelines."""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote


DEFAULT_REPO = "elkabalatesla-coder/Project-ELM369"


def repository(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", value):
        raise argparse.ArgumentTypeError("repository must be OWNER/REPO")
    return value


def owner(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", value):
        raise argparse.ArgumentTypeError("owner must be a GitHub username or organization")
    return value


def positive_integer(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a positive integer")
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    repos = commands.add_parser("repos", help="list repositories as a JSON array")
    repos.add_argument("owner", type=owner, nargs="?", default="elkabalatesla-coder")
    repos.add_argument("--limit", type=positive_integer, default=100)
    prs = commands.add_parser("prs", help="list pull requests as a JSON array")
    prs.add_argument("--repo", type=repository, default=DEFAULT_REPO)
    prs.add_argument("--state", choices=("open", "closed", "merged", "all"), default="open")
    prs.add_argument("--limit", type=positive_integer, default=100)
    pr = commands.add_parser("pr", help="view one pull request as a JSON object")
    pr.add_argument("number", type=positive_integer)
    pr.add_argument("--repo", type=repository, default=DEFAULT_REPO)
    archive = commands.add_parser("archive", help="download a ZIP without extracting it")
    archive.add_argument("output", type=Path)
    archive.add_argument("--repo", type=repository, default=DEFAULT_REPO)
    archive.add_argument("--ref", help="branch, tag, or commit; defaults to the default branch")
    return result


def download_archive(args, env):
    endpoint = "repos/{}/zipball".format(args.repo)
    if args.ref is not None:
        if not args.ref:
            raise ValueError("archive ref must not be empty")
        endpoint += "/" + quote(args.ref, safe="")
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError("refusing to overwrite {}".format(output))
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output.parent, prefix=".elm369-archive-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            subprocess.run(
                ["gh", "api", "--hostname", "github.com", endpoint],
                env=env, stdout=stream, check=True,
            )
        # Publishing via a hard link refuses overwrites, including racing writers.
        os.link(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink()
    print("Saved {}".format(output), file=sys.stderr)


def main(argv=None):
    args = parser().parse_args(argv)
    if shutil.which("gh") is None:
        print("Install GitHub CLI in Termux: pkg install gh", file=sys.stderr)
        return 1
    env = dict(os.environ, GH_HOST="github.com", GH_PROMPT_DISABLED="1", GH_PAGER="cat")
    try:
        if args.command == "archive":
            download_archive(args, env)
            return 0
        if args.command == "repos":
            command = [
                "repo", "list", args.owner, "--limit", str(args.limit),
                "--json", "nameWithOwner,url,description,isPrivate,isArchived,defaultBranchRef",
            ]
        elif args.command == "prs":
            command = [
                "pr", "list", "--repo", "github.com/" + args.repo,
                "--state", args.state, "--limit", str(args.limit),
                "--json", "number,title,state,url,headRefName,baseRefName,isDraft",
            ]
        else:
            command = [
                "pr", "view", str(args.number), "--repo", "github.com/" + args.repo,
                "--json", "number,title,body,state,url,headRefName,baseRefName,isDraft",
            ]
        subprocess.run(["gh"] + command, env=env, check=True)
        return 0
    except subprocess.CalledProcessError as error:
        print("GitHub command failed; check network, permissions, and gh auth status.",
              file=sys.stderr)
        return error.returncode if error.returncode > 0 else 1
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
