# Rendering and optional image generation

## Select a mode

| Mode | Input | Output / evidence |
| --- | --- | --- |
| Mood exploration | Brief + references | AI concept; no claim of matching a dimensioned model |
| Model-faithful visualization | Current evaluated scene + camera/materials | Blender base render, source hash and camera |
| Completion simulation | Base render + material/product references | Separately labelled AI simulation with source/prompt record |
| Local correction | Current image + bounded edit/mask where supported | Edited simulation; inspect unchanged regions too |

Use available host image tools, Google Imagen or another explicitly configured provider. Discover actual tool/model capabilities first. Do not assume every Imagen model accepts a base image, supports masks, reference conditioning or conversational editing. Use a model that supports the required edit/conditioning route; if only text-to-image exists, classify its result as an independent concept rather than a faithful render enhancement.

Google's [Imagen editing overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/edit-images-overview) describes mask-based edits, and its [image overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/overview) distinguishes image-generation and editing choices. Verify current model IDs, region, permissions, API schema and price at execution time. Keep credentials out of files and git. The core skill has no required image-provider account or SDK.

## Produce the base

Freeze the current revision. Set room/detail cameras, consistent neutral lighting, color management, resolution and quality budget. Render previews before expensive final frames. Save `.blend`, base image, camera transform/settings, source hash, engine, samples and resolution. When Blender is unavailable or crashes, preserve the source/scripts and report the failed validation; do not substitute a generated image and call it a Blender render.

## Generate a simulation

Supply the actual base render through the provider's image input, not just a text description of it. Use only cleared material/product reference images. Keep base-render geometry authoritative. Request preservation of camera, wall/opening positions, furniture count, scale and orientation. Describe the desired material/light changes separately.

Starting prompt:

> Enhance the supplied base render into a realistic interior completion simulation. Preserve the exact camera, room boundary, ceiling/beam levels, all door/window openings, furniture positions, orientations and counts. Preserve the selected product silhouettes. Improve only material texture, lighting and photographic surface response toward [confirmed palette]. Do not add furniture, plants, windows, cabinetry, decor or architectural details. Do not crop or change perspective. Treat unspecified hardware as unresolved, not a fabrication instruction.

This instruction is a request, not a geometry guarantee. Review the result against the base. Reject/rework changed openings, duplicate or missing furniture, implausible reflections, altered cabinets/handles, oversized products and newly invented service details. Use a localized mask/edit if supported; otherwise regenerate or retain the base. If a generated idea is selected as a design change, change the model/manifest first and rebuild.

## Save and compare

Keep `base/`, `simulation/`, and a per-image provenance record with:

- Actual provider and model, generation date, image filename/hash.
- Mode (`concept` or `completion-simulation`), revision/source hash, base filename/hash and camera ID if applicable.
- Full prompt, referenced inputs, mask/settings/seed when available.
- Geometry-drift review findings and status (`pending`, `accepted-for-visualization`, `rejected`).

Do not invent seeds or provider metadata. Label simulated images on their gallery cards; provide a base/simulation toggle. Keep dimensions and drawing exports attached to the model, never the simulation. Include costs only if actually known.

The README concept image is an independently generated fictional design study, not a base-render enhancement and not an output of Google Imagen. It is separate from the executable synthetic studio example.
