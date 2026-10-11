# Liquid-3D Prompting

Compose structured prompts for Liquid-3D **visual**, **audio**, and **animation** work, with reusable ELM369 skillsets for image/video production and visual art.

## Run

```bash
python3 -m tools.liquid3d_prompting list-templates
python3 -m tools.liquid3d_prompting list-skills
python3 -m tools.liquid3d_prompting compose --mode visual --subject "artifact registry galaxy"
python3 -m tools.liquid3d_prompting compose --mode animation --subject "painted forest reveal" --skill camera-capture --skill painting --skill image-accessibility --json
python3 -m tools.liquid3d_prompting compose --mode combo --subject "breathing network" --json
```

## Tests

```bash
python3 -m unittest discover -s tools/liquid3d_prompting/tests -v
```

`--skill` may be repeated; available IDs and practice exercises are listed by `list-skills`. The resulting prompt packet records selected skill IDs and incorporates their guidance. See `tools/liquid3d_prompting/skillsets.json` and `docs/research/ELM369_VISUAL_MEDIA_SKILLSETS_2026-10-11.md`.

Prompt composition only — no media generation, editing, capture APIs, or credentials. Skillsets are reusable guidance and practice plans, not claims of autonomous expertise or verified output quality.
