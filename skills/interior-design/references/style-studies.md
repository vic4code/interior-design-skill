# Style studies and selected objects

Use style as a set of spatial, material and furniture decisions, not a paint filter. Start from the user's activities, actual plan and references. Keep layout evidence independent of appearance.

## Two visual routes

For an attractive initial appearance proposal, use the host image-generation tool with a concrete furniture/material/lighting brief. The README leads with four independent generated concepts; these do not share the room geometry of the drawing sample. The public [concept provenance](https://github.com/vic4code/interior-design-skill/blob/main/docs/showcase/concepts/README.md) is a repository showcase, not an installed runtime dependency. If only the installed skill folder is available, use the workflow in [render-and-imagegen.md](render-and-imagegen.md).

The reproducible Blender studies below retain one shared synthetic room for model/drawing inspection. Their simple procedural assets are geometry examples, not a promise of finished editorial image quality. An independent image-generated concept cannot be used as proof that its furniture or architecture is present in those scenes.

## Four original Blender studies

| Direction | Furniture language | Material and lighting decisions |
| --- | --- | --- |
| Mid-century Modern / MCM | Exposed timber frame, tapered legs, low upholstered seating, sculptural table | Walnut tones, olive/rust textiles, warm metals and a composed vintage-object grouping |
| Japandi | Low platforms, generous cushions, restrained joinery, fewer objects | Light oak, natural textile, mineral plaster and soft diffuse light |
| Contemporary | Rounded upholstered masses, monolithic table, quiet cabinet planes | Layered neutrals, stone, dark metal and broad light gradients |
| Bauhaus | Tubular metal frames, crisp cushions, clear geometric relationships | Chrome/black surfaces with a restrained red/yellow/blue accent system |

These are original interpretations. They do not identify an exact manufacturer product or reproduce a reference apartment. The shared fictional room is deliberately held constant so geometry and finish decisions can be compared.

## Reference and selection workflow

The user's reference directions include the [Lo-Fi House case portfolio](https://lofi-house.com/cases/) and [Dan Retro product selection](https://www.danretro.com/products). Use case studies to discuss composition and material relationships, and retailer selections to discover potential furniture/lighting candidates. Keep the sources linked rather than redistribute their photographs or commercial models.

For an actual selection, record the exact product/variant and opened manufacturer dimensions, finish, installation needs, model licence and source date. A retailer category or stylistic resemblance is not verified product identity. Vintage pieces may need seller measurements, condition records and confirmation that the actual item matches the listing. Follow [furniture-sourcing.md](furniture-sourcing.md).

When the user names a specific piece, use a cleared original model if available; otherwise build a measured approximation and label it. Do not silently claim a procedural shape is that exact product.

## Reproduce the original studies

From the skill root, after setup and with Blender on PATH:

```bash
blender --background --threads 4 --python-exit-code 1 --python scripts/render_style_studies.py -- --style mcm --out /path/to/mcm-study
```

Use `japandi`, `contemporary`, `bauhaus` or `all` for other directions. The renderer reads the bundled `assets/style-studies/project.json`, `styles.json` and `joinery.json`; custom paths can be supplied through its command-line options. Save the native scene, GLB, model dimensions, cameras and render provenance alongside the images.

Generate the coordinated technical study:

```bash
.venv/bin/python scripts/build_drawing_studies.py --out /path/to/drawing-study
```

It uses the same room and cabinet dimensions, producing eight A3 sheets, a PDF, CAD plan, schedules and a file/source manifest. Geometry and component dimensions are design assumptions for a fictional project; read the issue register before using the sample as a starting point for real fabrication.

## Review

Inspect the actual renders for framing, material scale, light, object count and geometric fidelity. Inspect real-size sheets for dimensions, references and legibility. Compare model-derived cabinet bounds with the drawing's width/depth/height and panel stacks. Preserve model-faithful base images if an optional AI appearance simulation is generated later.

## Review the detailed scene in the frontend

For a matching style scene and drawing set, create a browser package from the verified outputs:

```bash
.venv/bin/python scripts/build_style_review.py --study /path/to/mcm-study --drawings /path/to/drawing-study --out assets/viewer/public/generated
npm --prefix assets/viewer run dev
```

The packer rejects different source hashes, revisions, styles or nominal furniture dimensions and checks the drawing file hashes before combining them. It strips PNG metadata from the browser copy and preserves source provenance. For other styles, generate the drawing set with the matching `--style` first.
