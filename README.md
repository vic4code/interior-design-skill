# Interior Design Skill

**Describe your space. Explore the design. Open the complete delivery in your browser.**

English · [繁體中文](README.zh-TW.md)

For **Codex, Claude Code, Cursor and GitHub Copilot**. Tell your agent how you want to live, what you like and what needs to fit. It develops the spatial proposal, creates image-gen visualizations, prepares dimensioned drawings and opens one local review page. Plans and measurements improve precision; you can start with words and clearly marked assumptions.

## What you get

**One browser page to understand the space, compare the design and discuss the work with your designer or contractor.**

| View | Your result |
| --- | --- |
| **Layout** | A clean furniture and circulation plan showing the actual room outline. |
| **3D placement** | An interactive model that opens with the interior visible; rotate, zoom and restore the full enclosure. |
| **Design effects** | Image-generated alternatives, room/view selection and comparison with each spatial base image. |
| **MEP coordination** | Lighting/power proposals and supplied HVAC or plumbing references, with their source and review status. |
| **Engineering drawings** | Dimensioned plans, elevations, sections, cabinet details and schedules; downloadable PDF/SVG, plus DXF/CSV where produced. |

The agent plans additional image-gen angles from each room's **actual polygon area or supplied area, uses and design features**, within an agreed image budget. Large or multifunctional spaces get broader coverage. Completed images appear in the same gallery; a view plan alone is not a generated image.

Layout explains **where things go**. Engineering sheets explain **sizes, levels, materials and assembly decisions**. MEP uses the available project evidence: the public example includes lighting/electrical intent; complete circuit, HVAC and plumbing design requires the corresponding inputs and trade review.

One frontend and package format serve the public example and existing projects. Native multi-room projects retain their geometry, sheet IDs and known measurements. The rectangular starter is an optional helper; unknown dimensions stay unknown.

## One space, four styles

The same synthetic room, openings, furniture arrangement and base camera, explored through four image-generated alternatives. All previews use the same **900 × 675** frame.

| Mid-century Modern | Japandi |
| --- | --- |
| [![MCM — walnut, olive upholstery and warm light](docs/showcase/same-space/mcm/preview.jpg)](docs/showcase/same-space/mcm/presentation.jpg) | [![Japandi — pale oak, linen and natural stone](docs/showcase/same-space/japandi/preview.jpg)](docs/showcase/same-space/japandi/presentation.jpg) |
| Walnut, olive fabric and a warm vintage character. | Light oak, woven textures and a quiet natural palette. |
| **Contemporary** | **Bauhaus** |
| [![Contemporary — soft upholstery, stone and restrained contrast](docs/showcase/same-space/contemporary/preview.jpg)](docs/showcase/same-space/contemporary/presentation.jpg) | [![Bauhaus — chrome, leather and disciplined primary accents](docs/showcase/same-space/bauhaus/preview.jpg)](docs/showcase/same-space/bauhaus/presentation.jpg) |
| Soft forms, tactile upholstery and stone. | Tubular metal, black leather and geometric color. |

These were generated with **the actual same base image as input**, not four unrelated apartments. Compare the [base view](docs/showcase/same-space/base.jpg) and [generation records](docs/showcase/same-space/README.md). Image generation guides appearance; small furniture and surface details may drift. Dimensions and technical details remain tied to the source model, with adopted changes reconciled before fabrication.

## Start with your needs

```bash
npx skills add vic4code/interior-design-skill --skill interior-design
```

> Use interior-design. I want a warm living room with reading space, concealed storage and a work corner. Compare MCM, Japandi and Bauhaus in the same layout. Plan enough image-generated views to show each activity. Give me a layout, interactive 3D, available MEP coordination and dimensioned drawings, then open it all in my browser. I can provide a floor plan and measurements later.

The agent handles data preparation and tools. With an existing project, it uses that project. Without measured dimensions, it labels assumptions and lists what to measure next. Available outputs depend on the host's image/model tools and project evidence; [host compatibility](docs/agent-compatibility.md) distinguishes installation checks from live workflow tests.

## Actual drawing deliverables

A reproducible synthetic **eight-sheet A3 example**, using shared geometry and style-specific finish palettes:

| Dimensioned layout · A101 | Cabinet arrangement · J301 |
| --- | --- |
| [![Dimensioned layout with furniture IDs, openings and dimension chains](docs/showcase/drawings/A101.svg)](docs/showcase/drawings/A101.svg) | [![Cabinet arrangement with panel and internal dimensions](docs/showcase/drawings/J301.svg)](docs/showcase/drawings/J301.svg) |
| **Cabinet section · J401** | **Lighting/power proposal · A102** |
| [![Cabinet section with thicknesses, shelf levels and interface decisions](docs/showcase/drawings/J401.svg)](docs/showcase/drawings/J401.svg) | [![Lighting and power coordination with fixture IDs and heights](docs/showcase/drawings/A102.svg)](docs/showcase/drawings/A102.svg) |

[Complete PDF](docs/showcase/drawings/design-coordination.pdf) · [Delivery ZIP](docs/showcase/design-development-S01.zip) · [Plan DXF](docs/showcase/drawings/plan.dxf) · [Joinery schedule](docs/showcase/drawings/joinery.csv) · [Open decisions](docs/showcase/drawings/issues.csv).

Project drawings should include room/use labels, internal dimension chains, openings, section/detail references, component information and material/hardware decisions—not only mesh outlines and outer bounds. Model-derived coordination drawings still require site, product, fixing and trade review before construction or fabrication release.

## Try the complete example

From a checkout, the single workflow entry generates the four-style example and **opens the browser automatically**:

```bash
cd skills/interior-design
bash scripts/setup.sh
.venv/bin/python scripts/interior_design.py demo --out /path/to/my-design
```

Outputs are grouped under `drawings/` and `review/`. The demo includes base-conditioned image-gen results and matching example geometry; it does not call a paid image API or run Blender. Real projects use the host's image tool for new visualizations. The agent should run the workflow for you; these commands are also available for a direct local trial.

Python 3.11+ runs the drawing tools. Node.js builds the browser frontend; Blender 4.3+ is needed only for native extraction/model work and optional model-faithful rendering. Image generation needs a host tool or configured provider, with access, quotas and possible costs depending on that service. A simple spatial model/base view can reduce detailed material authoring and local render work; image generation does not guarantee Blender-equivalent geometry.

Windows: create `.venv` with `py -m venv .venv`, install `scripts/requirements.lock.txt` with `.venv\Scripts\python -m pip install -r scripts/requirements.lock.txt`, and use that Python executable for the entry point.

## A portable, organized skill

`SKILL.md` guides the agent. `references/` loads detailed workflows as needed. `assets/` contains reusable example data, the frontend and bundled **Taste + UI UX Pro Max** guidance/search dependencies. `scripts/interior_design.py` is the single entry; implementation helpers stay in `scripts/_internal/`.

[Workflow reference](skills/interior-design/references/browser-review.md) · [Native projects](skills/interior-design/references/native-handoff.md) · [Design dependencies](skills/interior-design/references/design-dependencies.md) · [Host compatibility](docs/agent-compatibility.md) · [Verification](docs/verification.md) · [Contributing](CONTRIBUTING.md).

Original project code and synthetic assets use [MIT](LICENSE). Bundled dependencies keep their own licenses and attribution in [third-party notices](skills/interior-design/THIRD_PARTY_NOTICES.md). No private project content is included.
