"""Deterministic, bounded NFT asset generation; never signs or mints tokens."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import re
import shutil
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from tools.liquid3d_prompting.compose import compose, load_config

VERSION = 1
MAX_COMBINATIONS = 100_000
MAX_SUPPLY = 1000
MAX_CONFIG_BYTES = 65_536
SHAPES = {"circle", "diamond", "square", "triangle"}
COLOR = re.compile(r"#[0-9a-fA-F]{6}")


def _json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _text(value: Any, field: str, limit: int = 256) -> None:
    if (not isinstance(value, str) or not value.strip() or len(value) > limit
            or any(ord(char) < 32 or 0xD800 <= ord(char) <= 0xDFFF for char in value)):
        raise ValueError(f"{field} must be non-empty text of at most {limit} characters")


def _integer(value: Any, field: str, low: int, high: int) -> None:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{field} must be an integer from {low} to {high}")


def validate(config: Any) -> dict[str, Any]:
    """Validate the complete data-only input, including work and rendering limits."""
    fields = {"version", "name", "description", "seed", "supply", "layers", "image_base_uri"}
    if not isinstance(config, dict) or set(config) - fields:
        raise ValueError("configuration must be an object with supported fields only")
    if type(config.get("version")) is not int or config["version"] != VERSION:
        raise ValueError("unsupported configuration version")
    _text(config.get("name"), "name", 100)
    _text(config.get("description"), "description", 2000)
    _text(config.get("seed"), "seed", 128)
    _integer(config.get("supply"), "supply", 1, MAX_SUPPLY)
    base = config.get("image_base_uri", "")
    if base:
        _text(base, "image_base_uri", 2048)
        uri = urlsplit(base)
        if (uri.scheme not in {"https", "ipfs"} or not uri.netloc
                or uri.username or uri.password or uri.query or uri.fragment
                or any(char.isspace() for char in base) or "\\" in base):
            raise ValueError("image_base_uri must be an https:// or ipfs:// directory URI")
    elif not isinstance(base, str):
        raise ValueError("image_base_uri must be text")
    layers = config.get("layers")
    if not isinstance(layers, list) or len(layers) != 3:
        raise ValueError("layers must contain background, shape, and color")
    names = []
    capacity = 1
    for layer in layers:
        if not isinstance(layer, dict) or set(layer) != {"name", "options"}:
            raise ValueError("each layer requires only name and options")
        name = layer["name"]
        if not isinstance(name, str) or name not in {"background", "shape", "color"}:
            raise ValueError("unsupported layer name")
        names.append(name)
        options = layer["options"]
        if not isinstance(options, list) or not 1 <= len(options) <= 32:
            raise ValueError("each layer needs 1 to 32 options")
        values = set()
        for option in options:
            if not isinstance(option, dict) or set(option) != {"value", "weight"}:
                raise ValueError("each option requires only value and weight")
            value = option["value"]
            _text(value, "option value", 32)
            if name == "shape":
                if value not in SHAPES:
                    raise ValueError("unsupported shape")
            elif not COLOR.fullmatch(value):
                raise ValueError("colors must use six-digit #RRGGBB notation")
            key = value.lower()
            if key in values:
                raise ValueError("duplicate option value")
            values.add(key)
            _integer(option["weight"], "weight", 1, 1_000_000)
        capacity *= len(options)
    if len(set(names)) != 3:
        raise ValueError("layer names must be unique")
    palettes = {layer["name"]: {option["value"].lower() for option in layer["options"]}
                for layer in layers if layer["name"] != "shape"}
    if palettes["background"] & palettes["color"]:
        raise ValueError("background and foreground palettes must not overlap")
    if capacity > MAX_COMBINATIONS or config["supply"] > capacity:
        raise ValueError("supply exceeds unique capacity or combination limit")
    # Copy to prevent callers mutating validated state while a job is running.
    return json.loads(_json(config))


def read_config(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        raw = handle.read(MAX_CONFIG_BYTES + 1)
    if len(raw) > MAX_CONFIG_BYTES:
        raise ValueError("configuration exceeds 64 KiB")
    return validate(json.loads(raw))


def plan(config: dict[str, Any]) -> dict[str, Any]:
    cfg = validate(config)
    capacity = math.prod(len(layer["options"]) for layer in cfg["layers"])
    return {
        "version": VERSION,
        "name": cfg["name"],
        "supply": cfg["supply"],
        "unique_capacity": capacity,
        "tasks": ["validate", "weighted_selection", "render_svg", "score_rarity",
                  "compose_prompts", "export_metadata", "hash_manifest", "verify"],
        "network_required": False,
        "minting": False,
    }


def _select(cfg: dict[str, Any]) -> list[tuple[dict[str, Any], ...]]:
    rng = random.Random(cfg["seed"])
    candidates = []
    # Exponential races implement weighted sampling WITHOUT replacement.
    # Log-space priority avoids underflow and terminates even at full capacity.
    for index, combo in enumerate(itertools.product(
            *(layer["options"] for layer in cfg["layers"]))):
        log_weight = sum(math.log(option["weight"]) for option in combo)
        priority = math.log(-math.log(max(rng.random(), 2 ** -53))) - log_weight
        candidates.append((priority, index, combo))
    candidates.sort(key=lambda entry: (entry[0], entry[1]))
    return [entry[2] for entry in candidates[:cfg["supply"]]]


def _svg(title: str, traits: dict[str, str]) -> bytes:
    color = traits["color"]
    shapes = {
        "circle": '<circle cx="256" cy="256" r="150" fill="{}"/>',
        "square": '<rect x="106" y="106" width="300" height="300" fill="{}"/>',
        "diamond": '<polygon points="256,56 456,256 256,456 56,256" fill="{}"/>',
        "triangle": '<polygon points="256,66 446,426 66,426" fill="{}"/>',
    }
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" '
        'viewBox="0 0 512 512" role="img">'
        f'<title>{escape(title)}</title>'
        f'<rect width="512" height="512" fill="{traits["background"]}"/>'
        f'{shapes[traits["shape"]].format(color)}'
        '<text x="20" y="490" fill="#ffffff" font-size="16">ELM369</text>'
        '</svg>\n'
    ).encode("utf-8")


def build(config: dict[str, Any]) -> dict[str, bytes]:
    """Build reproducible assets in memory before making any filesystem changes."""
    cfg = validate(config)
    selected = _select(cfg)
    counts = Counter((layer["name"], option["value"])
                     for combo in selected
                     for layer, option in zip(cfg["layers"], combo))
    files = {"collection.json": _json(cfg)}
    tokens = []
    # Include the actual prompt configuration in the bundle for offline replay.
    prompt_config = load_config()
    files["prompt-config.json"] = _json(prompt_config)
    for token_id, combo in enumerate(selected, 1):
        traits = {layer["name"]: option["value"]
                  for layer, option in zip(cfg["layers"], combo)}
        name = f'{cfg["name"]} #{token_id}'
        image_path = f"images/{token_id}.svg"
        base = cfg.get("image_base_uri", "").rstrip("/")
        image_uri = f"{base}/{token_id}.svg" if base else f"../{image_path}"
        attributes = [{"trait_type": key, "value": value} for key, value in traits.items()]
        # Observed self-information, not a price estimate or a probability of minting.
        score = sum(-math.log2(counts[(key, value)] / cfg["supply"])
                    for key, value in traits.items())
        prompt = compose(name, palette=[traits["background"], traits["color"]],
                         config=prompt_config).rendered
        files[image_path] = _svg(name, traits)
        metadata_path = f"metadata/{token_id}.json"
        files[metadata_path] = _json({
            "name": name, "description": cfg["description"], "image": image_uri,
            "attributes": attributes,
            "properties": {"generator": "ELM369 NFT", "version": VERSION,
                           "project_id": prompt_config["project_id"],
                           "token_id": token_id, "rarity_score": round(score, 8),
                           "liquid3d_prompt": prompt},
        })
        tokens.append({"token_id": token_id, "score": round(score, 8)})
    ranked = sorted(tokens, key=lambda token: (-token["score"], token["token_id"]))
    files["rarity.json"] = _json({
        "method": "sum(-log2(observed_trait_count / supply)); ordinal tie-break by token_id",
        "ranking": [dict(token, rank=rank) for rank, token in enumerate(ranked, 1)],
        "frequencies": [
            {"trait_type": key, "value": value, "count": count,
             "frequency": count / cfg["supply"]}
            for (key, value), count in sorted(counts.items())
        ],
    })
    hashes = {path: _sha(content) for path, content in sorted(files.items())}
    files["manifest.json"] = _json({
        "version": VERSION, "generator": "ELM369 NFT", "minted": False,
        "supply": cfg["supply"], "files": hashes,
        "collection_sha256": _sha(_json(hashes)),
    })
    return files


def generate(config: dict[str, Any], output: Path) -> dict[str, Any]:
    """Write a fresh collection directory; never merge into or overwrite one."""
    files = build(config)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    try:
        for relative, content in files.items():
            path = output / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(content)
    except BaseException:
        shutil.rmtree(output)
        raise
    return {"ok": True, "output": str(output), "files": len(files),
            "supply": config["supply"], "minted": False}


def verify(output: Path) -> dict[str, Any]:
    """Check fixed local paths and digests, never follow manifest-supplied paths."""
    output = Path(output)
    manifest_path = output / "manifest.json"
    if output.is_symlink() or manifest_path.is_symlink():
        raise ValueError("symbolic links are not allowed in a collection")
    with manifest_path.open("rb") as handle:
        raw = handle.read(1_048_577)
    if len(raw) > 1_048_576:
        raise ValueError("manifest exceeds 1 MiB")
    manifest = json.loads(raw)
    if (not isinstance(manifest, dict) or type(manifest.get("version")) is not int
            or manifest["version"] != VERSION):
        raise ValueError("unsupported manifest")
    supply = manifest.get("supply")
    _integer(supply, "manifest supply", 1, MAX_SUPPLY)
    expected = {"collection.json", "prompt-config.json", "rarity.json"}
    expected.update(f"{folder}/{number}.{extension}"
                    for number in range(1, supply + 1)
                    for folder, extension in (("images", "svg"), ("metadata", "json")))
    hashes = manifest.get("files")
    if not isinstance(hashes, dict) or set(hashes) != expected:
        raise ValueError("manifest contains an invalid file inventory")
    for folder in ("images", "metadata"):
        if (output / folder).is_symlink():
            raise ValueError("symbolic links are not allowed in a collection")
    errors = []
    for relative in sorted(expected):
        path = output / relative
        digest = hashes[relative]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("invalid SHA-256 digest")
        if path.is_symlink() or not path.is_file():
            errors.append(relative)
            continue
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65_536), b""):
                h.update(chunk)
        if h.hexdigest() != digest:
            errors.append(relative)
    root_ok = manifest.get("collection_sha256") == _sha(_json(hashes))
    return {"ok": not errors and root_ok, "checked": len(expected),
            "mismatched_or_missing": errors, "root_matches": root_ok,
            "authenticity_verified": False}
