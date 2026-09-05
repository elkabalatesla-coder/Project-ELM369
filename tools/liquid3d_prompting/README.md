# Liquid-3D Prompting

Compose structured prompts for Liquid-3D **visual**, **audio**, and **animation** work.

## Run

```bash
python3 -m tools.liquid3d_prompting list-templates
python3 -m tools.liquid3d_prompting compose --mode visual --subject "artifact registry galaxy"
python3 -m tools.liquid3d_prompting compose --mode combo --subject "breathing network" --json
```

## Tests

```bash
python3 -m unittest discover -s tools/liquid3d_prompting/tests -v
```

Prompt composition only — no media APIs or credentials.
