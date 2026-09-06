# ELM FLUX — Image Prompt Composer (dry-run)

Issue #28. Composes FLUX-style prompts with style / aspect / negative fields.

**Hard rule: no live FLUX API.** Dry-run only until Joseph explicitly opts in later.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
Vault: `JMR08241978202646902` · companion `JMR0824197846902`

## Scope (DONE as dry-run composer)

| Action | Allowed? |
|--------|----------|
| Compose / enrich prompts | Yes |
| List styles & aspects | Yes |
| Call Wavespeed / HF / FLUX network APIs | **Never** (scaffold-gated stub) |

## Commands

```bash
python3 -m tools.elm_flux styles
python3 -m tools.elm_flux compose "cyberpunk street at night"
python3 -m tools.elm_flux compose "bridge at dusk" --style noir --aspect 16:9
python3 -m tools.elm_flux compose "schematic" --style schematic --generate  # still refuses live call
```

## Remaining intentional gap

Live image generation is **not** part of this ship. `--generate` documents token requirements and returns `generator_not_wired` / `missing_token` without network I/O.

## Tests

```bash
python3 -m unittest tools.elm_flux.tests.test_compose -v
```
