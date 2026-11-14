"""ELM369 Flow - Pixel Machine+ (Tool 3). Seeded, reversible, frame-consistent."""
from __future__ import annotations
import hashlib
import json
PIXEL_VERSION = "0.1.0"
MODES = ["bitmap", "ascii", "crt", "pixel", "glitch"]
ASCII_RAMP = " .:-=+*#%@"

def _seeded_hash(seed: int, *parts) -> int:
    text = f"{seed}:" + ":".join(str(p) for p in parts)
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)

def pixel_quantize(image_ref: str, mode: str = "pixel", seed: int = 369, pixel_size: int = 8, palette_k: int = 16, glitch_rate: float = 0.05) -> dict:
    mode = mode.lower()
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode}")
    palette_seed = _seeded_hash(seed, image_ref, mode, palette_k)
    glitch_seed = _seeded_hash(seed, image_ref, mode, "glitch")
    spec = {"tool": "pixel_quantize", "version": PIXEL_VERSION, "image_ref": image_ref, "mode": mode, "seed": seed, "params": {"pixel_size": pixel_size, "palette_k": palette_k, "glitch_rate": glitch_rate, "palette_seed": palette_seed, "glitch_seed": glitch_seed}, "status": "SPEC_READY", "note": f"Apply {mode} with seed {seed} to reproduce exactly."}
    if mode == "ascii":
        spec["params"]["ascii_ramp"] = ASCII_RAMP
        spec["params"]["chars_per_row"] = 120
    if mode == "crt":
        spec["params"]["scanlines"] = True
        spec["params"]["scanline_gap"] = 3
        spec["params"]["vignette"] = 0.25
    if mode == "glitch":
        spec["params"]["glitch_blocks"] = int(glitch_rate * 100)
    return spec

def pixel_temporal_lock(frame_specs: list[dict], seed: int = 369) -> dict:
    locked = []
    for i, spec in enumerate(frame_specs):
        frame_seed = _seeded_hash(seed, spec.get("image_ref", f"frame-{i}"), i)
        new_spec = dict(spec)
        new_spec["frame_index"] = i
        new_spec["frame_seed"] = frame_seed
        new_spec["temporal_locked"] = True
        locked.append(new_spec)
    return {"tool": "pixel_temporal_lock", "version": PIXEL_VERSION, "seed": seed, "count": len(locked), "frames": locked, "status": "LOCKED"}

def pixel_ascii_preview(brightness_values: list[int]) -> str:
    out = ""
    for v in brightness_values:
        v = max(0, min(255, int(v)))
        idx = int(v / 256 * len(ASCII_RAMP))
        if idx >= len(ASCII_RAMP):
            idx = len(ASCII_RAMP) - 1
        out += ASCII_RAMP[idx]
    return out

def pixel_invert(spec: dict) -> dict:
    return {"tool": "pixel_invert", "version": PIXEL_VERSION, "original_ref": spec.get("image_ref"), "mode": spec.get("mode"), "seed": spec.get("seed"), "params": spec.get("params"), "status": "INVERT_SPEC_READY", "note": "Reversible because seed + params are stored."}

def pixel_full_run(image_refs: list[str], mode: str = "pixel", seed: int = 369) -> dict:
    specs = [pixel_quantize(ref, mode, seed) for ref in image_refs]
    locked = pixel_temporal_lock(specs, seed)
    return {"specs": specs, "locked": locked, "invert_example": pixel_invert(specs[0]) if specs else None}

if __name__ == "__main__":
    demo = pixel_full_run(["frame-001.jpg", "frame-002.jpg", "frame-003.jpg"], "glitch", 369)
    print(json.dumps(demo, indent=2))
    print("ASCII demo:", pixel_ascii_preview([0, 30, 80, 130, 180, 220, 255]))
