# Unified browser review

Use the single entry `scripts/interior_design.py`, resolved from the directory containing SKILL.md. The browser frontend serves the same code for a synthetic four-style example or an existing multi-room project. Keep project output outside the skill.

## Finish and open the real project

After generating the actual presentation through the host image tool, package the existing drawing delivery:

```bash
.venv/bin/python scripts/interior_design.py review --drawings /project/drawings --image /project/presentation.jpg --base-image /project/base.jpg --provenance /project/image-provenance.json --model /project/space.glb --out /project/review
```

The browser opens automatically. `--model` is optional only when no matching model is available; explain unavailable outputs rather than inventing them. The five modes separate clean layout, interactive 3D, image-generated effects, available MEP and engineering drawings. MEP is available only with registered source content. The model loads only when its mode is selected.

For native source geometry:

```bash
.venv/bin/python scripts/interior_design.py native --blend /project/current.blend --config /project/views.json --image /project/presentation.jpg --base-image /project/base.jpg --provenance /project/image-provenance.json --model /project/space.glb --out /project/delivery
```

Use `--inventory /project/geometry-inventory.json` instead of `--blend` to reuse a verified extraction. The inventory belongs to the private working project, not the public review or installed skill. Native geometry and annotated dimensions must share the source revision; camera-based image generation remains appearance evidence.

The clean layout presents room/furniture placement without the full title block and technical tables. Engineering mode opens a detail or section when available, preserving the complete dimensioned sheet set. Start 3D in a view-only cutaway with the interior visible and an option to restore the enclosure. Use one consistent viewing frame and fit/zoom controls across drawing modes; avoid vertical scroll containers nested inside the page.

The 3D toolbar also offers **走入空間** for floor-supported eye-level movement. Drag to look, tap **前進 / 後退**, or focus the canvas and use W/S or up/down. Reset returns to the entry pose; **返回旋轉** restores overview. This conservatively checks supported single-level floor geometry and mesh obstacles; unsupported models keep overview with walking unavailable. See [lightweight walkthrough](lightweight-walkthrough.md) for limits, resource budgets and verification. Lighting and source GLB downloads remain the same in both modes.

Reopen with `review --existing /project/review`; stop its local server with the same arguments plus `--stop`. `--no-open` serves for automated browser checks, and `--no-serve` builds artifacts only. The server exposes only its built UI and selected review artifacts on loopback, not the workspace root.

## Same space, several alternatives

The bundled `demo --out /project/demo` creates four branches from one spatial source and one image-generation base, then opens one page. It does not generate new images; genuinely conditioned results are bundled for a reproducible trial. New project visuals must be generated with the host image tool.

For another same-space study, pass `review --variants /project/alternatives.json --out /project/review`. The config contains a `variants` list. Each entry has an `id`, display `label`, `source` drawing package, `presentation`, `base_image`, `provenance`, and optional `model`, `metadata`, `swatch`. Paths resolve relative to the config file. Spatial project/opening/joinery sources and the conditioning base must match; style-specific finish palettes can differ. Do not group different apartments and call them a same-space comparison.

## Plan and produce several views

The agent prepares `spaces.json` from the actual project, not from invented image measurements:

```json
{
  "spaces": [{
    "id": "living",
    "name": "Living and reading",
    "polygon_mm": [[0, 0], [6000, 0], [6000, 4800], [0, 4800]],
    "functions": ["Conversation", "Reading"],
    "features": ["Storage wall"],
    "existing_views": [{"id": "living-entry", "role": "overview", "base_image": "bases/living-entry.png"}]
  }]
}
```

Use supplied `area_m2` when no scaled polygon is available; omit both when unknown. Polygon coordinates are millimetres, and concave area is calculated from the polygon rather than its bounds. Reference image paths resolve relative to the input file.

```bash
.venv/bin/python scripts/interior_design.py views --spaces /project/spaces.json --out /project/view-plan.json --budget 12
```

The planner allocates an overview to each room before extra angles, then uses area, activities and features to propose additional coverage within the budget. A missing area gets an overview and a measurement request. Jobs without a real base remain `needs-base`; jobs with one remain `pending-image-generation` until the agent performs the actual image-tool work. The command does not call a provider or create imagery.

Create missing base views from the project's geometry, pass each actual base to the image tool, inspect the results and record provenance. Add completed views through `--metadata /project/review-metadata.json`:

```json
{
  "presentations": [{
    "id": "living-reverse",
    "title": "Living · reverse view",
    "space": "Living",
    "image": "views/living-reverse/image.jpg",
    "base_image": "views/living-reverse/base.png",
    "provenance": "views/living-reverse/provenance.json"
  }]
}
```

These paths resolve relative to the metadata file. The primary visual comes from `--image`; `presentations` adds actual completed files for room filters, viewpoint selection and thumbnails. Each view keeps its own base hash and review status. Display pending visual reviews honestly; do not turn an unfinished planner job into a gallery image.

## Register available MEP

The bundled A102 sheet is registered as lighting/electrical intent. For existing services drawings, add a `mep` list to the same metadata object:

```json
{
  "mep": [{
    "id": "HVAC01",
    "title": "HVAC coordination reference",
    "source": "services/hvac.svg",
    "sha256": "<actual 64-character SHA-256 of the source file>",
    "kind": "hvac-reference",
    "status": "pending-trade-review",
    "reference": "Supplied services drawing; reconcile with the current layout"
  }]
}
```

Attachments must be actual SVG/PDF files with matching hashes. PDF pages are rasterized locally into separate fit-to-frame previews; the original PDF remains registered and available through the original/download controls. PDF import uses the pinned CPU-only dependency in the requirements file, with explicit page/size limits; it does not need Blender or a GPU. Keep issue/review status and revision relationships explicit. MEP mode presents these references; it does not size equipment, design circuits or invent plumbing. Missing disciplines remain a recorded input/review requirement.

## Presentation evidence

Provenance includes `mode` (`completion-simulation` or `concept`), `image_sha256`, `review_status` (`pending` or `accepted-for-visualization`) and `base_sha256` for conditioned imagery. Record actual prompts and visual findings too. The packer verifies image/source file hashes, not the artistic or geometric truth of those findings. Never mark an unchecked image reviewed to pass packaging.

The viewer separates presentation and base, preserves actual sheet IDs, omits unknown area/height and offers registered downloads. Check all five available modes with real project files at desktop and mobile widths, including room/view switching, cutaway/full-enclosure controls, readable drawings and PDF download. Verify a single coherent scrolling experience. Print scales and written dimensions belong to the sheets; generated imagery is not a measurement source.
