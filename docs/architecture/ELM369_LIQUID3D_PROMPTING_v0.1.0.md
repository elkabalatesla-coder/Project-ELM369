# Liquid-3D Prompting v0.1.0

Project: ELM369_JMR08241978202646902  
Status: Scaffolding (from archived `New-Promting-for-Liquid-3D-and-it-s-audio-and-animation`)  
Related UI sketch: `Liquid3D Coloring ` (Artifact Registry React demo)

## Purpose

Provide a **command-line prompt composer** for Liquid-3D workstreams:

- **visual** — liquid motion, particle fields, color mapping
- **audio** — accompanying sound / ambience cues
- **animation** — timing, loops, transitions

Prompts are structured packets (JSON + rendered text) so they can be stored in DAX memory or handed to image/video/audio models.

## Type color map (from Artifact Registry)

| Type | Hex |
|------|-----|
| code | `#00D4FF` |
| docs | `#FFB800` |
| image | `#FF006E` |
| dataset | `#8B00FF` |
| schema | `#00FF88` |
| model | `#FF3366` |
| policy | `#4169E1` |
| log | `#C0C0C0` |

## CLI

```bash
python3 -m tools.liquid3d_prompting compose --mode visual --subject "artifact registry galaxy"
python3 -m tools.liquid3d_prompting compose --mode audio --subject "cyan droplet pulse"
python3 -m tools.liquid3d_prompting compose --mode animation --subject "network nodes breathe"
python3 -m tools.liquid3d_prompting list-templates
```

## Safety

Prompt generation only — no media generation APIs, no credentials, no destructive repo actions.
