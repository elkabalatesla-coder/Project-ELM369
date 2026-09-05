"""Enigma-style toy ASCII obfuscation for demos (NOT secure encryption)."""

from __future__ import annotations

DOMAIN_SIZE = 95
START_CHAR = 32


def obfuscate(
    plaintext: str,
    *,
    pins: list[int] | None = None,
    rotors: list[int] | None = None,
    notches: list[int] | None = None,
    plugboard: dict[str, str] | None = None,
) -> str:
    pins = list(pins or [0, 0, 0])
    rotors = list(rotors or [1, 3, 5])
    notches = list(notches or [10, 20, 30])
    if not (len(pins) == len(rotors) == len(notches)):
        raise ValueError("pins, rotors, and notches must be same length")
    pb = {chr(i): chr(i) for i in range(START_CHAR, START_CHAR + DOMAIN_SIZE)}
    if plugboard:
        for k, v in plugboard.items():
            if k in pb and v in pb:
                pb[k], pb[v] = v, k
    out: list[str] = []
    pos = pins[:]
    for char in plaintext:
        char = pb.get(char, char)
        code = ord(char)
        if START_CHAR <= code < START_CHAR + DOMAIN_SIZE:
            idx = code - START_CHAR
            shift = sum(pos) % DOMAIN_SIZE
            for r, p in zip(rotors, pos):
                shift = (shift + r + p) % DOMAIN_SIZE
            out_char = chr((idx + shift) % DOMAIN_SIZE + START_CHAR)
            out_char = pb.get(out_char, out_char)
            out.append(out_char)
            step = True
            for r in reversed(range(len(pos))):
                if step:
                    pos[r] = (pos[r] + 1) % DOMAIN_SIZE
                    step = pos[r] == notches[r]
                else:
                    step = False
        else:
            out.append(char)
    return "".join(out)


def deobfuscate(
    ciphertext: str,
    *,
    pins: list[int] | None = None,
    rotors: list[int] | None = None,
    notches: list[int] | None = None,
    plugboard: dict[str, str] | None = None,
) -> str:
    """Brute reverse by regenerating keystream steps (same settings)."""
    # For demo: try all domain chars via forward oracle per position is expensive;
    # instead re-run forward mapping inverted at each step.
    pins = list(pins or [0, 0, 0])
    rotors = list(rotors or [1, 3, 5])
    notches = list(notches or [10, 20, 30])
    pb = {chr(i): chr(i) for i in range(START_CHAR, START_CHAR + DOMAIN_SIZE)}
    if plugboard:
        for k, v in plugboard.items():
            if k in pb and v in pb:
                pb[k], pb[v] = v, k
    inv_pb = {v: k for k, v in pb.items()}
    out: list[str] = []
    pos = pins[:]
    for char in ciphertext:
        char = inv_pb.get(char, char)
        code = ord(char)
        if START_CHAR <= code < START_CHAR + DOMAIN_SIZE:
            idx = code - START_CHAR
            shift = sum(pos) % DOMAIN_SIZE
            for r, p in zip(rotors, pos):
                shift = (shift + r + p) % DOMAIN_SIZE
            plain_idx = (idx - shift) % DOMAIN_SIZE
            plain = chr(plain_idx + START_CHAR)
            plain = inv_pb.get(plain, plain)
            out.append(plain)
            step = True
            for r in reversed(range(len(pos))):
                if step:
                    pos[r] = (pos[r] + 1) % DOMAIN_SIZE
                    step = pos[r] == notches[r]
                else:
                    step = False
        else:
            out.append(char)
    return "".join(out)
