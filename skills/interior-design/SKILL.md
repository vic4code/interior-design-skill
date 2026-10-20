---
name: interior-design
description: Turn everyday room requests, optional measured plans and reference images into compelling image-generated design concepts, editable Blender scenes, browser reviews and dimensioned drawings for interior designers, contractors and engineers. Use for interior layouts, furniture placement, renovation visualization, material studies and design coordination, even when the user does not name this skill. Build project-specific geometry when the starter does not fit; track the technical evidence and issue status of drawing deliverables.
license: MIT
compatibility: Host image-generation tool for optional AI concepts; Python 3.11+ for drawings; Node.js 20.19+ or 22.12+ for the optional viewer; Blender 4.3+ for native scenes, GLB and renders.
---

# Interior Design

Help the user lead their own design and give the people refining or building it concrete drawings to discuss. Speak the user's language. Distinguish visual agreement, dimensional evidence and professional technical review.

## Use the bundled resources

Treat the directory containing this SKILL.md as the **skill root**, independent of the user's working directory. Resolve scripts, assets and references from it. The complete skill folder works without the parent repository. Read only the references relevant to the task:

- [Intake](references/intake.md): plan, sketch and photo starting points; calibration before modeling.
- [Project format](references/project-format.md): the quick-start generator schema, units and axes. Read before using its project JSON.
- [Advanced spaces](references/advanced-spaces.md): project-specific Blender workflows for multiple rooms, irregular walls, rotations and detailed assemblies.
- [Native handoff](references/native-handoff.md): extract an existing Blender scene, cut actual geometry, verify dimension evidence and issue a model-derived drawing set.
- [Construction documents](references/construction-documents.md): professional sheet registers, dimension chains, component details, specifications and technical evidence.
- [Style studies](references/style-studies.md): MCM, Japandi, Contemporary and Bauhaus; references, original assets and reproduction commands.
- [Furniture sourcing](references/furniture-sourcing.md): exact model/variant, official dimensions, installation envelopes and model licensing.
- [Design methods](references/design-method.md): daily activities, editable/native versus browser geometry, stable IDs and evaluated-scene snapshots.
- [Rendering](references/render-and-imagegen.md): model-faithful base renders, optional image enhancement, provenance and geometry drift.
- [Overlays and services](references/overlays-and-mep.md): source drawing registration and evidence for lighting, power, plumbing and HVAC. These are extension workflows, not implemented viewer features.
- [Drawing handoff](references/drawing-handoff.zh-TW.md): sheet meanings, trade questions and dimensional limitations. Read before issuing a package; explain it in the user's language.
- [Prompt examples](references/prompt-workflow.md): iterating from brief to layout, materials, lighting and delivery.

Keep the local workflow independent of paid APIs. Optional web search, image tools and Blender MCP depend on the host's available tools. Do not introduce paid calls, upload project content or redistribute reference assets without the user's authorization.

## Start from the user’s words

The user can describe a room, needs and taste in ordinary language. They do not need to write JSON, install a renderer or prepare a full drawing brief before seeing a proposal. Inspect existing context, translate the request into a brief and handle structured inputs and tooling for them.

Deliver an initial design direction, a compelling visual concept when an image tool is available, a spatial proposal and a drawing package with stated dimensional evidence. Prefer the host's image-generation tool for aspirational appearance studies; reserve Blender rendering for model-faithful checks or requested editable 3D. See [rendering modes](references/render-and-imagegen.md). Do not run a heavy render just to produce an appearance concept.

Plans, dimensions and photos are optional starting aids. If measurements are missing, proceed with a clearly labeled synthetic/assumed layout and drawing draft, list the specific dimensions needed to refine it and request them without holding up independent concept work. Never present assumed dimensions as measured, invent product verification, or imply that an independent concept image is represented by the drawing model. If a requested deliverable cannot actually be generated, report the unavailable tool and deliver the useful outputs that can be produced.

## Establish the design brief

Inspect provided files and existing decisions first. Ask only for missing information that changes the design: room and activities, retained items, priorities/budget, desired mood and references, measured internal dimensions, height, structure, openings and service points. A dimensioned plan is enough to start; photos can clarify existing conditions.

Record each dimension's basis: assumed, manufacturer, unreviewed site measurement or reviewed site measurement. An uncalibrated photo cannot establish reliable dimensions. Continue concept work with explicit assumptions; never invent verified measurements or pretend inaccessible files informed the design.

Translate references into concrete layout, material, furniture and lighting decisions. Compare layouts against pulled-out chairs, open doors, storage retrieval and equipment servicing. Distinguish geometric gaps from comfortable circulation and product dimensions from installation clearances.

Choose the modeling route that fits the real project. The quick-start generator handles one rectangular room and simple furniture; its schema bounds apply only to that tool. For multi-room layouts, irregular walls, rotated furniture, detailed casework and operations, follow [advanced-spaces.md](references/advanced-spaces.md) and create a project-specific scene and data contract. Do not simplify away requirements merely to fit the starter. Photos and CAD/PDF inputs still require source inspection and dimensional evidence; do not claim automatic reconstruction that has not been performed.

## Build from one source of dimensions

Copy [the synthetic example](assets/example-project.json) into the user's project workspace before editing. Validate against [the schema](assets/project.schema.json). Use millimetres in JSON and drawings; Blender uses metres and the GLB exporter converts to Y-up. Origin is the inside southwest corner, +X east, +Y north, +Z up. Furniture positions are minimum corners. N/S opening offsets run west to east; E/W offsets run south to north. Room dimensions are clear internal faces; walls extend outward.

Keep stable IDs and update the revision after changes. `project.status` remains `coordination_draft`. Reconcile browser overrides into the input, or freeze the evaluated scene before rebuilding. Match source hashes and revisions instead of assuming an older native file is current.

Run commands from the skill root, substituting the user's actual project path and output directory. Initial setup installs the pinned Python and viewer dependencies, not Blender:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/project.py validate /path/to/project.json
.venv/bin/python scripts/project.py build /path/to/project.json --out /path/to/review --blender
.venv/bin/python scripts/verify_outputs.py /path/to/review
```

Omit `--blender` for drawings only. Python dependencies are listed in `scripts/requirements.lock.txt`. On Windows create `.venv` using `py -m venv .venv`, install dependencies with `.venv\Scripts\python -m pip install -r scripts/requirements.lock.txt`, use `.venv\Scripts\python` for commands, and run `npm --prefix assets/viewer ci --ignore-scripts`.

For the bundled synthetic browser demo:

```bash
.venv/bin/python scripts/project.py build assets/example-project.json --out assets/viewer/public/generated --blender
npm --prefix assets/viewer run dev
```

The viewer serves its own asset directory on localhost. Keep private outputs in the user's project; preview them in a separate copy of `assets/viewer/` when needed. Copy the entire review package into that copy's `public/generated/`, install its npm dependencies and run its dev command. Do not serve the user's workspace root or publish private projects.

## Visualize, inspect and revise

Inspect the actual model, PNG and drawings. Check room proportions, door/window locations, furniture IDs, dimensions and revision consistency; exercise the browser's plan/3D views and downloads. Report failed or unavailable checks accurately.

The bundled starter’s model-faithful render is a 1920×1440 Cycles CPU render with 32 samples and denoising when available, or 128 samples without denoising. Higher resolution increases pixels; detailed geometry, materials and lighting determine realism. For a separate final image:

```bash
blender -b /path/to/review/scene.blend --threads 2 --python-exit-code 1 --python scripts/render_hd.py -- --width 3840 --height 2880 --samples 128 --out /path/to/final-4k.png
```

Keep this image linked to its source revision. If optional image generation changes appearance, preserve the base render and label the new image as an AI visual simulation, with its inputs/prompt and a geometry-drift review. Do not measure generated imagery.

Show actual outputs for feedback on layout, materials, lighting and furniture. Change the authoritative input and rebuild affected outputs together. Manual Blender decoration is a separate presentation variant unless encoded back into the generator.

## Deliver drawings for discussion

Choose sheets and details using [construction-documents.md](references/construction-documents.md). The quick-start generator produces `.blend`, GLB and PNG when Blender runs; A101 furniture plan, A201–A204 wall datum elevations, five-page A3 PDF, SVG, plan-only DXF, furniture/opening/material CSV, source JSON, unresolved reviews and a checksummed manifest.

Explain the purpose and limits:

- Plans show placement and dimensions; datum elevations locate wall openings and heights, not complete furniture or service elevations.
- Drawings use mm. Print A3 at 100% and follow each sheet's stated scale; A101 uses 1:100 when room depth exceeds 8000 mm, otherwise 1:50. Written dimensions control. The plan table lists the first ten furniture items; CSV contains the full schedule.
- DXF is model-space mm without native associative CAD dimensions. Material areas are net geometric quantities, not purchasing allowances.
- Nominal openings do not specify door swing, frame, hardware or finished clear width. The quick-start primitive generator has a 150 mm minimum on each furniture envelope; this is not a minimum for detailed model components or a skill-wide size limit. Verify real product fit separately.

Record unresolved site survey, circulation, joinery/fixings, substrate, services, ceiling, material build-ups, waterproofing and professional review responsibilities. Separate manufacturer sizes, model bounds, internal clear sizes and installation cutouts. Functional lighting groups are not electrical circuits; renderer energy is not rated electrical load.

Return actual file paths, revision, resolution, checks and open questions. Issue the package as a coordination draft for the designer, contractor or engineer; do not describe it as an approved construction, shop or permit set.
