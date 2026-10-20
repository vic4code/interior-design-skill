---
name: interior-design
description: Turn everyday interior-design needs, optional plans and existing projects into image-generated design visualizations, spatial layouts and dimensioned drawing deliveries, then open the results in a local browser. Use for room design, renovation, furniture/material selection, model-guided image generation and contractor/designer coordination. Continue existing geometry first; use project-specific models for arbitrary room shapes and multiple rooms.
license: MIT
compatibility: Host image tool for AI visuals; Python 3.11+ for drawings; Node.js 20.19+ or 22.12+ for browser builds; Blender 4.3+ only for native extraction/model work.
---

# Interior Design

The user describes the space they want. You handle the brief, spatial data, image generation and drawings, then **open the completed review in their browser**. Do not hand them a list of internal scripts or an ugly primitive model as the design result. Speak their language.

## Interface design dependencies

Before creating or changing the browser experience, load the bundled [Taste and UI UX Pro Max dependencies](references/design-dependencies.md). They include the design guidance, search runtime/data and licenses; no separate host skill installation is required. Preserve one frontend with five modes: clean layout, 3D arrangement, image-generated effects, available MEP coordination and engineering drawings. Use the same interface for examples and existing projects. Keep same-space style images at identical framing/aspect ratio.

## 1. Continue the actual project

Inspect the user's existing plans, models, images and recorded decisions first. Preserve the latest coherent source and SHA-256. Do not replace an existing design with the bundled sample. A recent filename alone does not prove freshness; compare actual revised geometry and saved/browser states.

If starting from words, infer a brief and make useful progress: activities, style, retained items, priorities and budget. Ask only for missing decisions that materially change the proposal. Plans, sketches, photos and dimensions improve precision but are optional starting aids. Mark assumed dimensions and request the specific measurements needed for the next revision. The agent creates structured data; the user does not write JSON.

Choose the route before modeling:

- **Existing/native project:** preserve its actual geometry and follow [native handoff](references/native-handoff.md).
- **Multiple rooms, irregular walls, rotations or detailed assemblies:** use project-specific geometry following [advanced spaces](references/advanced-spaces.md). Do not flatten it into a rectangular substitute.
- **Small synthetic demonstration only:** use the bundled demo. Its rectangular schema is one helper's scope, not a limit on the skill.

Read [intake](references/intake.md) for calibration and [project format](references/project-format.md) only when using the rectangular helper. Track each dimension as assumed, manufacturer, unreviewed site measurement or reviewed site measurement. Photos and generated images alone cannot establish construction dimensions.

## 2. Make the design visible with image gen

Use the host's available image-generation tool for the presentation result. Do not silently substitute a Blender preview when image generation was requested. If the required tool is unavailable, say so and deliver the useful outputs that can actually be made.

Translate the brief into coherent furniture forms, material choices, lighting and composition. When spatial data exists, create/use a simple base view and pass the actual image to an image-capable tool. Preserve camera, boundaries, openings and arrangement; develop material response and atmosphere. This reduces some detailed asset/material and local render work, but does not guarantee native-render geometry or lower overall cost.

Read the [fixed-frame image and lighting protocol](references/render-and-imagegen.md) before generating a comparison series. Put the canvas size/aspect ratio, identical lens/camera/horizon/vanishing points, upright verticals, unchanged crop and furniture positions in every prompt. Generate daylight/lights-off, daylight/lights-on and night/lights-on views from one approved reference when lighting comparisons are requested. Check the actual output dimensions and visual alignment; prompts alone do not prove matching geometry.

Plan view coverage from each room's actual polygon or supplied area, activities and declared design features. Start with an overview per room, then add diagonal/reverse/connection and activity/detail views as justified within an agreed image budget. Use `views --spaces /project/spaces.json --out /project/view-plan.json --budget 12` to prepare work; it does not generate images. Unknown area stays unknown, and an irregular room's bounding rectangle is not its floor area. Generate the required images with the host tool, inspect them and package completed views with their own bases/provenance. Do not deliver only a living-room view when other spaces or activities need coverage. See [browser review](references/browser-review.md) for the input and gallery contract.

Inspect base and generated result side by side or with an overlay. Record changed edges, openings, furniture and details; revise unacceptable drift. Keep the base and generated image separately. Never measure the image. If a visual idea changes the design, update the authoritative geometry and drawings together. See [image generation and review](references/render-and-imagegen.md).

Record `mode`, `image_sha256`, `review_status`, and `base_sha256` when conditioned, plus the actual tool, prompt, revision and visual findings. Use `completion-simulation` for supplied-base edits, `concept` for independent proposals; accepted visualization is not geometric certification. Do not invent model IDs, costs, seeds or approvals.

## 3. Develop drawings people can work through

Use the same model revision for plans, elevations, sections and component dimensions. Establish a readable sheet register, room/use labels, internal and overall dimension chains, opening IDs/location, detail/section references, material legends and schedules appropriate to the project. A mesh outline with only a bounding-box dimension is not a complete construction drawing.

Follow [construction documents](references/construction-documents.md) and [drawing handoff](references/drawing-handoff.zh-TW.md). Verify clear sizes, panel thickness, datums and dimension closure against actual modeled faces; keep envelopes distinct from functional openings. Record hardware, joints, fixing substrates, loads, services and site items that remain unresolved. Do not invent construction details merely to fill a sheet.

Inspect the actual PDF/SVG at print scale for legibility, missing glyphs, overlaps, omitted geometry and consistent references. Explain issue status honestly. Coordination drawings become construction/fabrication releases only after the necessary site/product/trade decisions and review.

Keep the clean layout distinct from technical sheets: layout shows placement and circulation without title-block tables; engineering sheets carry dimensions, datums, sections and assembly information. Register available lighting/power, HVAC or plumbing drawings in the separate MEP mode with their source revision and review status. The demo's A102 is lighting/electrical intent. Do not invent complete circuits, service sizing or plumbing routes from a furniture plan; list missing inputs and trade decisions instead.

## 4. Package and open the browser

The single entry point is `scripts/interior_design.py`, resolved relative to this SKILL.md. Internal implementation belongs under `scripts/_internal/`; users should not operate those helpers separately. Keep all private project output outside the installed skill/repository.

For an existing drawing delivery and its generated visual:

```bash
.venv/bin/python scripts/interior_design.py review --drawings /path/to/drawings --image /path/to/presentation.jpg --base-image /path/to/base.jpg --provenance /path/to/image-provenance.json --out /path/to/review
```

Provide `--model /path/to/space.glb` when an actual matching model is available. For native extraction plus delivery, use the entry point's `native --help`; preserve the real view/selection profile. Never force an existing project through the synthetic demo.

The review command packages the actual sheet register, clean layout and separate visual/base/provenance, builds the viewer when needed, serves only that review package on localhost and opens the browser automatically. Show presentation first, room/view selection, base comparison, spatial/model inspection, available MEP and drawings/downloads. Do not require a separate terminal/server command from the user. Return the URL and saved delivery location. See [browser review](references/browser-review.md) for same-space variants and metadata. Reopen with `review --existing /path/to/review`; `--stop` stops its local review server.

Start 3D with the interior visible through a view-only cutaway, with a control to restore the full enclosure; preserve source geometry. Keep plan, MEP and drawing content in a consistent viewing frame with fit/zoom controls. Avoid nested vertical scrolling inside the page's content blocks.

The 3D viewer must also demonstrate lighting: start with daylight and warm interior lights, offer day/night and indoor-light on/off controls, and retain daylight when indoor lights are off. Preserve authored texture colors and multiply factors in GLB export; inspect wood/fabric under neutral light before blaming exposure or recoloring objects. Keep a corrected export separate from the source. Interactive lighting is a visual study, not an illuminance calculation or electrical approval.

Verify in a real browser: generated image/base and room/view selections load, layout differs from detailed engineering sheets, supplied MEP opens, actual sheet selection and PDF download work, and the page fits mobile/desktop without nested vertical scroll traps. Check failed requests/script errors and inspect 3D colors, framing and default interior visibility. Functional WebGL success is not aesthetic acceptance. Unknown area/height stays unknown; the viewer must not invent a rectangle.

## Optional setup and demo

The agent handles setup when needed; explain unavailable dependencies rather than invent execution. Python dependencies are in `scripts/requirements.lock.txt`; browser builds require Node.js. Blender is needed for native extraction or editable/model-faithful 3D, not the image-gen presentation route or synthetic drawing generator. Do not assume a separately configured image API or SDK. Respect existing authorization; do not upload private references or introduce paid services without it.

For a separate synthetic demonstration, never as a replacement for the user's project:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/interior_design.py demo --out /path/to/demo
```

The demo uses four genuinely same-base-conditioned image-generated alternatives, matching 3D examples and four eight-sheet drawing sets in one switchable page; no Blender render is required to view it. `--no-serve` is for artifact-only CI. Windows uses `.venv\Scripts\python` after creating the environment with `py -m venv .venv` and installing the lock file.

## Load references as needed

- [Furniture sourcing](references/furniture-sourcing.md): exact products, manufacturer sizes, installation envelopes and licensing.
- [Design methods](references/design-method.md): activities, stable IDs, native/browser states and evaluated snapshots.
- [Styles](references/style-studies.md): MCM, Japandi, Contemporary and Bauhaus; original proposals and geometry studies.
- [Services/overlays](references/overlays-and-mep.md): source registration and evidence; no automatic complete MEP promise.
- [Prompt iteration](references/prompt-workflow.md): brief, materials, lighting and delivery revisions.
