# Image generation and model-faithful rendering

## Choose a route before installing tools

For an attractive initial style proposal, use the host's available image-generation tool directly. The agent translates the ordinary-language request into an art-directed prompt with concrete furniture forms, material palette, spatial composition, selected objects and photographic lighting. Generate original concepts rather than reproducing third-party photographs or artwork. The user need not install Blender, Python image SDKs or a local GPU for a host-provided image tool. Availability, network access, quotas and possible service charges depend on that host; do not invent a price or switch to a paid API without authorization.

For dimensioned drawings, use structured geometry and Python drawing dependencies; Blender is not needed for the bundled synthetic PDF/SVG/DXF generator. For editable 3D, extraction of a native scene or a camera-faithful render, use Blender. Blender's own `bpy` runtime is included with Blender; the core does not require installing a separate Blender Python package through pip. Detailed Cycles rendering consumes local CPU/GPU time and memory, so start with previews and render a final only when it serves the task. The optional browser viewer additionally needs Node.js dependencies.

A high-quality generated image improves presentation; it does not recover reliable dimensions or complete construction details. Derive drawings from measured/assumed geometry, label the evidence, and reconcile any selected visual changes back into that geometry. Keep independent concepts separate from the drawing sample when they depict different rooms.

## Lightweight spatially grounded visualization

Use room dimensions, plan outlines, openings and furniture positions as spatial priors. If the user supplies geometry or a measured plan, create a simplified model/base view without first investing in detailed presentation assets, high-resolution textures or high-sample path tracing. Use an inexpensive solid/neutral preview or low-sample render when it provides enough structure. Then pass the actual base image to a tool that supports image input; a text description alone does not condition the output on that view.

Keep its camera, perspective, boundary and arrangement explicit in the prompt; ask image generation to develop material response, light and atmosphere. This is a lightweight alternative for design iteration, not a guarantee of equivalent geometric fidelity to native rendering. It reduces some local asset/render work and shifts appearance synthesis to a hosted tool; do not promise lower total cost or latency without measuring them.

Compare base and generated image side by side or with an overlay. Inspect wall/floor edges, opening corners, ceiling levels and furniture footprints; reject or revise material spatial drift. Do not describe overlay review as an implemented automatic validator or infer construction dimensions from the image. Record actual findings in the image provenance; use geometry for dimensioned deliverables.

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

The README’s four image-generated concepts are independent fictional style proposals made with the host image-generation tool. They are separate from the executable synthetic room and its drawing example. Original Blender renders and reproducible scene scripts remain available as geometry examples.
