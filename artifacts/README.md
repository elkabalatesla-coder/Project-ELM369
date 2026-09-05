# ELM369 Artifacts

## Browse

Open [`index.html`](index.html) in a browser for the sandbox gallery.

## Layout

- `sandboxes/NNN-name/` — one folder per GitHub issue artifact
  - `index.html` — runnable preview when possible
  - `source.raw.txt` — exact issue body
  - React issues also keep `component.jsx`
- `from-issues/` — earlier HTML extracts (kept for compatibility)
- `sandboxes/manifest.json` — machine-readable catalog

## CLI

```bash
python3 -m tools.elm_artifacts list
python3 -m tools.elm_artifacts verify
```
