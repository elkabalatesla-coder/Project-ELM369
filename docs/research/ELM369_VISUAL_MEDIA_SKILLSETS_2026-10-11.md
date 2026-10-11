# ELM369 Visual Media Skillsets: Research and Practice Guide

**Date:** 2026-10-11  
**Related camera research:** `docs/research/ELM369_CAMERA_TECHNIQUES_RESEARCH_2026-10-11.md`  
**Implementation:** `tools/liquid3d_prompting/skillsets.json` and `tools/liquid3d_prompting/`

## Purpose and scope

This guide turns the camera-techniques research into a practical, reusable skill catalog for image, video, animation, and visual-art work in Project ELM369. Skillsets are prompt guidance and practice plans selected during prompt composition. They do not capture, draw, paint, edit, render, or inspect media; the existing tool has no media-generation or editing API.

“All” image and video techniques is not a finite list. Tools, workflows, formats, and artistic practices change, and technique names vary by discipline. This catalog therefore provides a broad, extensible foundation rather than claiming exhaustive coverage. A selected skillset is not a claim that ELM369, its operator, or a model has mastered a technique. Demonstrated competence requires practice and review against observable criteria.

## Skill catalog

The catalog contains small, composable skillsets. Apply only those relevant to the task; a short prompt does not need every skill.

### Capture and moving image

| ID | Skill | Coverage |
|---|---|---|
| `camera-capture` | Camera capture and cinematography | Framing, camera placement and movement, shot planning, focus, exposure, frame rate, and continuity. |
| `composition` | Composition and visual storytelling | Hierarchy, balance, negative space, depth, lines, shape, and visual attention. |
| `optics-focus` | Optics, lenses, and focus | Focal length, camera distance, perspective, depth of field, focus transitions, filters, and close focus. |
| `exposure-motion` | Exposure and motion rendering | Aperture, shutter/exposure time, ISO/gain, motion blur, frame rate, and highlight handling. |
| `lighting` | Lighting and light shaping | Direction, softness, contrast, practicals, bounce, and separation of lighting from exposure. |
| `video-storyboarding` | Video planning and storyboarding | Shot sequences, action, screen direction, coverage, transitions, and planning for accessible delivery. |
| `video-editing` | Video editing and continuity | Selection, continuity, pacing, transitions, sound, captions, and final review. |
| `animation-motion` | Animation and motion design | Timing, key poses, spacing, easing, arcs, anticipation, follow-through, and loop review. |

### Image making and visual art

| ID | Skill | Coverage |
|---|---|---|
| `image-editing` | Image editing and retouching | Nondestructive correction, restrained retouching, source preservation, and versioning. |
| `drawing` | Observational drawing | Gesture, proportion, negative shapes, construction, perspective, and line hierarchy. |
| `sketching` | Sketching and ideation | Rapid thumbnails, silhouette, composition alternatives, and readable roughs. |
| `etching-printmaking` | Etching and printmaking | Mark direction and density, proofing, print contrast, and material/tool safety. |
| `color-theory` | Color selection and color theory | Hue, value, saturation, temperature, palette relationships, contrast, and contextual legibility. |
| `shading-values` | Shading and value structure | Light family, form modeling, value grouping, edge control, and three-dimensional form. |
| `shadowing` | Cast shadows and occlusion | Light direction, cast/form/contact shadows, shadow length and softness, and consistent occlusion. |
| `painting` | Painting and paint handling | Medium-aware sequencing, color masses, layers, transparency/opacity, edges, and surface. |
| `digital-illustration` | Digital illustration and rendering | Layered sketch-to-finish workflow, masks, value checks, and output-size review. |
| `texture-material` | Texture and material rendering | Shape, reflection, roughness, edges, and mark behavior to distinguish materials. |

### Newly added production-quality skills

Research into accessible publishing, authenticity/provenance, and real-world delivery adds skills beyond image-making technique itself:

| ID | Skill | Why it matters |
|---|---|---|
| `image-accessibility` | Image and video accessibility | Alternative text, captions, transcripts, and descriptions help people access visual and audio information through different modalities. |
| `provenance` | Media provenance and rights | Accurate source, permission, authorship, edit, and synthetic-origin records support transparency without making unsupported authenticity claims. |
| `quality-delivery` | Visual quality and delivery | Reviewing target crop, resolution, compression, playback, metadata, accessibility, and editable masters avoids failures after creation. |

These skills supplement, rather than replace, applicable legal requirements, platform guidance, production standards, or specialist accessibility review.

## Practice and skill development

The catalog includes a short practice exercise for each skill. Use the following repeatable cycle to turn prompt guidance into demonstrable proficiency:

1. **Define the brief:** identify the intended subject, audience, medium, output, constraints, rights, and accessibility needs.
2. **Select a small skill combination:** use `list-skills` and choose only the IDs needed for the work.
3. **Plan and produce a study:** apply the listed practice exercise to a small, reviewable sample. Use safe, permissioned subjects and materials.
4. **Inspect observable results:** assess task-specific criteria such as legibility, proportion, perspective, focus, consistent lighting, color/value hierarchy, continuity, clean transitions, captions, or correct export.
5. **Compare and revise:** check against the brief and references, record what changed, and try a controlled variation.
6. **Keep evidence, not mastery claims:** retain the brief, source assets where permitted, versions, review notes, and accessible final deliverables. A successful prompt or single output is not proof of general mastery.

### Review checklist

- **Intent:** Does the image or sequence communicate its stated subject and purpose?
- **Visual structure:** Are framing, composition, form, value, color, focus, and movement internally consistent?
- **Craft:** Are unwanted artifacts, accidental clipping, muddy values, unstable framing, and discontinuous edits corrected?
- **Access:** Are meaningful images described appropriately, and are speech and important audio/visual information accessible in video?
- **Rights and provenance:** Are sources, permissions, authorship, transformations, and generated contributions represented accurately?
- **Delivery:** Does the final file work at its intended dimensions, crop, display, playback, and compression level?

The checklist is a production aid, not a substitute for formal accessibility conformance testing, legal review, or audience testing.

## Use in Project ELM369

Discover IDs and exercises:

```bash
python3 -m tools.liquid3d_prompting list-skills
```

Compose a visual prompt using more than one skill:

```bash
python3 -m tools.liquid3d_prompting compose \
  --mode visual \
  --subject "observational portrait study in window light" \
  --skill camera-capture \
  --skill drawing \
  --skill shading-values \
  --skill image-accessibility \
  --json
```

The JSON packet records selected skill IDs and the rendered prompt includes their guidance. Rendered prompt text remains unchanged when no `--skill` option is supplied; JSON packets include an additive `skills` field. Catalog entries are reusable instructions; they do not independently evaluate generated output.

## Research findings that informed new skills

1. **Accessibility belongs in planning, not only post-production.** W3C WAI guidance differentiates informative, decorative, functional, and complex images, and addresses captions, transcripts, and descriptions of visual information for audio/video. This supports a dedicated access skill and bringing access planning into storyboarding and delivery.
2. **Provenance is not truth verification.** C2PA describes a technical provenance and authenticity framework for recording information about media. A provenance record can help establish origin and edit history, but cannot by itself demonstrate that depicted events or claims are true. The skill therefore requires accurate records and prohibits invented verification.
3. **Technique follows observable visual principles.** Camera placement, motion, focus, exposure, composition, and editing work together but are distinct choices. The guide and catalog keep those concepts separately selectable so that a prompt can combine them without confusing a zoom with a dolly, camera movement with a cut, or lighting with exposure.
4. **Visual-art practice is iterative and medium-aware.** Drawing and printmaking rely on observation, mark/value structure, and proofing; color and painting depend on medium and output context. The skill catalog therefore includes small studies and comparisons instead of treating style words as a substitute for practice.
5. **A final asset must be checked in context.** Cropping, compression, playback, display size, captions, and metadata can change the usefulness of work. The `quality-delivery` skill adds a final review across target contexts.

## References

- ACMI, [Film It: Cinematography](https://www.acmi.net.au/education/school-program-and-resources/film-it-cinematography/) — introductory cinematography and learning activities.
- StudioBinder, [Ultimate Guide to Camera Shots](https://www.studiobinder.com/blog/ultimate-guide-to-camera-shots/) — shot-size and framing terminology.
- Canon Europe, [How to control exposure](https://www.canon-europe.com/get-inspired/tips-and-techniques/how-to-control-exposure/) — exposure concepts for photography.
- The Metropolitan Museum of Art, [The Head of the Virgin in Three-Quarter View Facing Right](https://www.metmuseum.org/art/collection/search/337496) — collection example for drawing materials and mark-making analysis.
- National Gallery of Art, [Monet’s Waterscapes](https://www.nga.gov/educational-resources/sense-place-france/monets-waterscapes) — art education resource for color, light, and painting.
- W3C Web Accessibility Initiative, [Images Tutorial](https://www.w3.org/WAI/tutorials/images/) — contextual image text alternatives.
- W3C Web Accessibility Initiative, [Making Audio and Video Media Accessible](https://www.w3.org/WAI/media/av/) — planning and creating accessible audio/video.
- W3C Web Accessibility Initiative, [Description of Visual Information](https://www.w3.org/WAI/media/av/description/) — conveying important visual information in media.
- C2PA, [Specifications](https://spec.c2pa.org/specifications/specifications/latest/) — technical specifications for content provenance and authenticity.

For specific productions, use the current camera, software, material, platform, and accessibility documentation that applies to the deliverable. The research is a starting point, not an exhaustive or timeless inventory.
