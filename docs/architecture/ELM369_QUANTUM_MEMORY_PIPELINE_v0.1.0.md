# ELM369 Quantum / HQM memory pipeline notes v0.1.0

From issues [#34](https://github.com/elkabalatesla-coder/Project-ELM369/issues/34) and [#36](https://github.com/elkabalatesla-coder/Project-ELM369/issues/36).

## Status

**Design + classical scaffold only.** The “quantum / holographic / blockchain anchor” stages remain conceptual. What ships in-repo today:

- DAX memory store/recall/index (`tools/dax_memory`)
- Optional **toy** classical obfuscation for local note-at-rest demos (`tools/elm_obfuscate`) — **not** cryptographic security, **not** a substitute for real encryption or key management.

## Pipeline stages (target)

1. Classical obfuscation (scaffold)
2. Quantum/HQM encode (planned)
3. Provenance / vault log (live via orchestrator)
4. Transfer / visualize (planned; Liquid-3D prompting related)

## Safety

Do not store real secrets with the toy obfuscator. Use OS keychain / proper crypto for credentials.
