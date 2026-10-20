# Public research / prompt + Blender

Research date: 2026-10-20. This is a source-based implementation note, not a survey of all tools or a claim that demos were independently reproduced. No external example imagery/code was copied into the product.

## Sources actually read

### 1. MeltFlex AI Skills

- Source: https://github.com/MeltFlexDevs/skills
- Inspected commit: `e8dc14140d43f0a4c085c7b37f5dfb6863ae023b`.
- Read README and `skills/meltflex-design/SKILL.md`, `skills/meltflex-3d/SKILL.md`.
- Observed: Markdown agent skills split design, furniture, 3D and embed workflows. Image/3D generation is routed through MeltFlex's hosted API; README documents paid subscription/API-key requirements and credits. The 3D skill describes asynchronous job polling and downloadable GLB/world outputs.
- Adopted idea: explicit skill scope, prerequisites, repeatable steps, durable outputs and errors explained to users.
- Deliberately chosen for this project: a local Blender pipeline with one dimensional source, not a dependency on MeltFlex's paid service. We did not call its generation API or reproduce its visual quality.

### 2. MCP for Blender (formerly blender-mcp)

- User-facing source URL: https://github.com/ahujasid/blender-mcp (redirects to current repository).
- Current project: https://github.com/ahujasid/mcp-for-blender
- Inspected commit: `98b991c8daf91ab9d5451ee6b923d89367f733a5`.
- Read README: quickstart, features, asset integrations, limitations/security.
- Observed: MCP server connects to a Blender add-on. The agent can create/modify objects, change materials, execute Blender Python and inspect views. Asset integrations include Poly Haven, Sketchfab and other sources; some optional generation integrations are paid. Its README describes Poly Haven assets as CC0; we have not independently reviewed each asset's licence.
- Why a prompt can look impressive: the prompt drives a capable modelling application, often with reusable assets and iterative visual checks. It is not only a text-to-image model inventing a flat picture. Some examples use external generation services; a visually impressive demo does not establish an entirely free workflow.
- Adopted idea: editable Blender scenes, meaningful object names, explicit material/camera steps and visual verification.
- Current implementation choice: deterministic background Blender Python, not an MCP add-on. Fewer installation steps and no socket server for the free baseline. Interactive MCP could be a later opt-in integration.
- Limit: running agent-generated Python has local execution power. The upstream README specifically warns about arbitrary code and advises saving work. We did not run upstream installers or enable its telemetry/add-on.

## What makes the image convincing

This is synthesis from those tools' documented workflows and the actual Blender prototype, rather than a measurement of aesthetic quality:

1. A clear brief reduces guessed design choices.
2. Correct room and furniture proportions make a scene feel intentional.
3. Detailed geometry and licensed asset quality matter; primitive boxes are only a spatial study.
4. Materials need colour, roughness, texture and sensible scale.
5. Lighting, camera, exposure and composition determine how the choices read.
6. Feedback rounds are part of the workflow. A single impressive prompt demo is not evidence of reliable one-shot design.
7. Higher resolution adds pixels; samples/denoising affect noise; neither fixes incorrect dimensions or makes a concept construction-ready.

The first version implements dimensions, editable geometry, simple procedural materials, a cutaway camera and HD rendering. It does not claim product-level photorealism or automatic reference-image reconstruction.

## Official documentation references / access status

The following are useful authoritative links, but direct retrieval in this environment returned **proxy 403**, so their contents were not claimed as read:

- Scene properties / units: https://docs.blender.org/manual/en/latest/scene_layout/scene/properties.html
- glTF export: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
- Background CLI: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html
- Bonsai / openBIM, a possible future direction: https://bonsaibim.org/

Attempts at a guessed GitHub mirror path returned 404 and were not used as sources. CLI and exporter behaviour for the current implementation were instead verified against the installed Blender 4.3.2 and actual GLB output. This is focused primary-source research; broad web/social-media search was not available.

## Workflow synthesis

The skill combines requirements intake, product-dimension verification, stable object identifiers, versioned model/render exports and explicit drawing-handoff boundaries. These general methods are documented in [reusable design patterns](design-patterns.md); planned extensions are separated in the [implementation roadmap](implementation-roadmap.md). Public examples use synthetic data and independently authored imagery.

## Skill packaging reference

The package follows the [Anthropic skill-creator structure](https://github.com/anthropics/skills/tree/main/skills/skill-creator): a concise `SKILL.md`, progressively loaded references, executable scripts and bundled assets inside one portable skill folder.

## Style studies

[Lo-Fi House cases](https://lofi-house.com/cases/) informs the use of complete spatial studies rather than isolated furniture swatches. [Dan Retro selection](https://www.danretro.com/products) informs a workflow for selecting objects with material, proportion and provenance. The bundled MCM, Japandi, Contemporary and Bauhaus studies are original procedural geometry and artwork; no case photographs, product images or commercial 3D assets are redistributed. Exact product identities, dimensions and manufacturer specifications require separate opened-source verification. See the [style reference](../skills/interior-design/references/style-studies.md).
