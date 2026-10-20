# Interior Design Skill

**Describe your space. Explore the design. Open the complete delivery in your browser.**

English · [繁體中文](README.zh-TW.md)

For **Codex, Claude Code, Cursor and GitHub Copilot**. Tell your agent how you want to live, what you like and what needs to fit. It develops the spatial proposal, creates image-gen visualizations, prepares dimensioned drawings and opens one local review page. Plans and measurements improve precision; you can start with words and clearly marked assumptions.

## You get five connected views

**One browser page, from the first layout to the drawings you discuss with your designer and contractor.** These are actual outputs from the bundled synthetic example; click any preview to inspect its source.

<table width="100%">
  <tr>
    <td width="50%" valign="top"><strong>1. Layout</strong></td>
    <td width="50%" valign="top"><strong>2. 3D design</strong></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><a href="docs/showcase/five-deliverables/layout.svg"><img src="docs/showcase/five-deliverables/01-layout.jpg" alt="Clean plan of the shared room with openings and five furniture footprints" width="440" height="330"></a></td>
    <td width="50%" valign="top"><a href="docs/showcase/five-deliverables/02-3d.jpg"><img src="docs/showcase/five-deliverables/02-3d.jpg" alt="Colored interactive room model with daylight and the enclosure opened for review" width="440" height="330"></a></td>
  </tr>
  <tr>
    <td width="50%" valign="top">Understand room boundaries, furniture positions and circulation without the technical title block.</td>
    <td width="50%" valign="top">Rotate the actual model with the interior visible. Switch day/night and lights on/off to inspect the atmosphere.</td>
  </tr>
  <tr>
    <td width="50%" valign="top"><strong>3. Image-gen visualization</strong></td>
    <td width="50%" valign="top"><strong>4. MEP coordination</strong></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><a href="docs/showcase/same-space/mcm/presentation.jpg"><img src="docs/showcase/five-deliverables/03-imagegen.jpg" alt="Photorealistic MCM completion simulation conditioned on the shared room base" width="440" height="330"></a></td>
    <td width="50%" valign="top"><a href="docs/showcase/drawings/A102.svg"><img src="docs/showcase/five-deliverables/04-mep.jpg" alt="Lighting and power proposal showing fixture IDs, positions and mounting heights" width="440" height="330"></a></td>
  </tr>
  <tr>
    <td width="50%" valign="top">Explore materials, furniture character and light with actual image generation, grounded in a spatial base.</td>
    <td width="50%" valign="top">Review lighting/power locations and heights. Supplied HVAC and plumbing references appear in the same mode.</td>
  </tr>
  <tr>
    <td width="50%" valign="top"><strong>5. Engineering drawings</strong></td>
    <td width="50%" valign="top"><strong>Take the work with you</strong></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><a href="docs/showcase/drawings/J301.svg"><img src="docs/showcase/five-deliverables/05-engineering.jpg" alt="Dimensioned front, plan and side views of the example sideboard" width="440" height="330"></a></td>
    <td width="50%" valign="top" rowspan="2">Download the <a href="docs/showcase/drawings/design-coordination.pdf">eight-sheet A3 PDF</a>, individual SVG sheets, <a href="docs/showcase/drawings/plan.dxf">editable plan DXF</a> and <a href="docs/showcase/drawings/joinery.csv">cabinet schedule</a>.<br><br>All five modes share one browser page and one project revision. The layout explains where things go; the engineering set explains sizes and construction decisions.</td>
  </tr>
  <tr>
    <td width="50%" valign="top">Read dimensions, levels and assembly intent in plans, elevations, sections and cabinet details. Open the original sheet to zoom in.</td>
  </tr>
</table>

The agent plans image-gen viewpoints from each room's **actual polygon area or supplied area, activities and design features**, within an agreed image budget. Large and multifunctional rooms receive broader coverage. Only completed images enter the gallery.

Existing multi-room and irregular native projects keep their geometry, sheet IDs and known measurements. The rectangular starter is optional; unknown dimensions stay unknown. The public MEP sheet is a lighting/power proposal. Full circuit, HVAC and plumbing design needs corresponding project data and trade review.

## One space, four styles

The same synthetic room, openings, furniture arrangement and base camera, explored through four image-generated alternatives. All previews use the same **900 × 675** frame.

<table width="100%">
  <tr>
    <td width="50%" valign="top"><strong>Mid-century Modern</strong></td>
    <td width="50%" valign="top"><strong>Japandi</strong></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><a href="docs/showcase/same-space/mcm/presentation.jpg"><img src="docs/showcase/same-space/mcm/preview.jpg" alt="Mid-century Modern · same space and camera" width="440" height="330"></a></td>
    <td width="50%" valign="top"><a href="docs/showcase/same-space/japandi/presentation.jpg"><img src="docs/showcase/same-space/japandi/preview.jpg" alt="Japandi · same space and camera" width="440" height="330"></a></td>
  </tr>
  <tr>
    <td width="50%" valign="top">Walnut, olive fabric and a warm vintage character.</td>
    <td width="50%" valign="top">Light oak, woven textures and a quiet natural palette.</td>
  </tr>
  <tr>
    <td width="50%" valign="top"><strong>Contemporary</strong></td>
    <td width="50%" valign="top"><strong>Bauhaus</strong></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><a href="docs/showcase/same-space/contemporary/presentation.jpg"><img src="docs/showcase/same-space/contemporary/preview.jpg" alt="Contemporary · same space and camera" width="440" height="330"></a></td>
    <td width="50%" valign="top"><a href="docs/showcase/same-space/bauhaus/presentation.jpg"><img src="docs/showcase/same-space/bauhaus/preview.jpg" alt="Bauhaus · same space and camera" width="440" height="330"></a></td>
  </tr>
  <tr>
    <td width="50%" valign="top">Soft forms, tactile upholstery and stone.</td>
    <td width="50%" valign="top">Tubular metal, black leather and geometric color.</td>
  </tr>
</table>

These were generated with **the actual same base image as input**, not four unrelated apartments. Compare the [base view](docs/showcase/same-space/base.jpg) and [generation records](docs/showcase/same-space/README.md). Image generation guides appearance; small furniture and surface details may drift. Dimensions and technical details remain tied to the source model, with adopted changes reconciled before fabrication.

## Interactive 3D lighting

**See the light change in the actual 3D model.** Switch day/night and indoor lights on/off independently. Daylight remains visible with the lamps off; after dark, local warm light and shadows reveal the arrangement. These four browser screenshots use one stationary camera and the same **900 × 675 px** canvas.

<table width="100%">
  <tr>
    <td width="50%" valign="top"><strong>Day · lights on</strong></td>
    <td width="50%" valign="top"><strong>Day · lights off</strong></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><a href="docs/showcase/lighting-3d/day-on.jpg"><img src="docs/showcase/lighting-3d/day-on.jpg" alt="Day · lights on · actual interactive MCM model, same camera" width="440" height="330"></a></td>
    <td width="50%" valign="top"><a href="docs/showcase/lighting-3d/day-off.jpg"><img src="docs/showcase/lighting-3d/day-off.jpg" alt="Day · lights off · actual interactive MCM model, same camera" width="440" height="330"></a></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><strong>Night · lights on</strong></td>
    <td width="50%" valign="top"><strong>Night · lights off</strong></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><a href="docs/showcase/lighting-3d/night-on.jpg"><img src="docs/showcase/lighting-3d/night-on.jpg" alt="Night · lights on · actual interactive MCM model, same camera" width="440" height="330"></a></td>
    <td width="50%" valign="top"><a href="docs/showcase/lighting-3d/night-off.jpg"><img src="docs/showcase/lighting-3d/night-off.jpg" alt="Night · lights off · actual interactive MCM model, same camera" width="440" height="330"></a></td>
  </tr>
</table>

[Actual 3D screenshots and source records](docs/showcase/lighting-3d/README.md). This fast preview supports design review; fixture specifications and engineering calculations belong in the MEP process.

## Image-gen lighting studies

The same MCM room and camera, with three **actual image-gen lighting studies**. Daylight and artificial lighting are controlled separately, so “lights off” still shows a naturally lit room during the day.

<table width="100%">
  <tr>
    <td width="33%" valign="top"><strong>Day · lights off</strong></td>
    <td width="33%" valign="top"><strong>Day · lights on</strong></td>
    <td width="33%" valign="top"><strong>Night · lights on</strong></td>
  </tr>
  <tr>
    <td width="33%" valign="top"><a href="docs/showcase/lighting/day-off/presentation.jpg"><img src="docs/showcase/lighting/day-off/preview.jpg" alt="Day · lights off · same MCM room and camera" width="280" height="210"></a></td>
    <td width="33%" valign="top"><a href="docs/showcase/lighting/day-on/presentation.jpg"><img src="docs/showcase/lighting/day-on/preview.jpg" alt="Day · lights on · same MCM room and camera" width="280" height="210"></a></td>
    <td width="33%" valign="top"><a href="docs/showcase/lighting/night-on/presentation.jpg"><img src="docs/showcase/lighting/night-on/preview.jpg" alt="Night · lights on · same MCM room and camera" width="280" height="210"></a></td>
  </tr>
</table>

Every prompt specifies the same **4:3 canvas, level camera, vertical architectural lines, field of view, crop and furniture positions**; only the stated lighting condition changes. All previews are **900 × 675 px**. [Prompts and provenance](docs/showcase/lighting/README.md) record the inputs and review. The interactive 3D view offers the corresponding fast day/night and lights-on/off controls; it is an appearance preview, not a lux calculation.

## Start with your needs

```bash
npx skills add vic4code/interior-design-skill --skill interior-design
```

> Use interior-design. I want a warm living room with reading space, concealed storage and a work corner. Compare MCM, Japandi and Bauhaus in the same layout. Plan enough image-generated views to show each activity, including daylight with the lights off and warm lights-on views. Use matching image sizes and camera framing. Give me a layout, interactive 3D, available MEP coordination and dimensioned drawings, then open it all in my browser. I can provide a floor plan and measurements later.

The agent handles data preparation and tools. With an existing project, it uses that project. Without measured dimensions, it labels assumptions and lists what to measure next. Available outputs depend on the host's image/model tools and project evidence; [host compatibility](docs/agent-compatibility.md) distinguishes installation checks from live workflow tests.

## Actual drawing deliverables

A reproducible synthetic **eight-sheet A3 example** shares the same room geometry and style-specific finish palettes: furniture plan, lighting/power proposal, two interior elevations, cabinet arrangement, cabinet section, finish/opening schedules and drawing/issue register.

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
