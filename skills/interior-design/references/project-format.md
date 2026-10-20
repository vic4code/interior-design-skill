# Project format v1.0

`assets/project.schema.json` is the machine-readable contract. `scripts/project.py validate` additionally checks finite numbers, unique IDs, openings contained within walls, non-overlapping opening rectangles, door sill=0 and furniture contained in the clear room. Overlapping furniture is a review issue, not silently accepted as a good layout. The validator does not claim circulation or code compliance.

- Required fields: `schema_version`, `project`, `room`, `finishes`, `openings`, `furniture`. Unknown fields fail validation.
- All input lengths are millimetres. Room bounds: width/depth 1000–10000; height 2000–5000; wall thickness 50–500.
- Room is rectangular, with clear interior X=[0,width], Y=[0,depth], Z=[0,height]. Walls extend outward. No furniture rotations or nested rooms.
- Origin: inside southwest corner; +X east, +Y north, +Z up. Furniture x/y are minimum corner; width/depth/height are bounding envelopes.
- Opening `wall`: south/north station measured west→east; east/west station measured south→north. `offset`=start station; `width`, `height`, `sill` are nominal envelope, not certified rough openings. A door is a hole; no door swing geometry.
- The shared wall partitioner subtracts opening rectangles from actual solids; it does not paint a window on an uncut wall.
- Material colours: 6-digit hex. Furniture kinds: sofa, table, chair, cabinet. Rendering uses primitive modelling, not product CAD. Names and material descriptions are display labels, not executable content.
- `project.status` only accepts `coordination_draft`. `measurement_status` is a declaration of measurement provenance, not approval.

## Output conventions

- Blender: meters, Z-up; GLB uses exporter coordinate conversion, meters and Y-up. Object IDs encoded as names such as `furniture_F01_top` and `wall_south`.
- PDF/SVG: A3 landscape, 420×297 mm, 1:50 at 100%. Text uses English on drawings for portable PDF fonts; guide, viewer and data can use Traditional Chinese. SVG text is XML-escaped.
- A101 is plan; A201–A204 are **datum** wall elevations, with increasing station left→right. They omit cabinetry/MEP and are not conventional interior-facing mirrored projections.
- DXF: plan only, ASCII basic LINE/TEXT, `$INSUNITS=4`; layers WALL, OPENING, FURNITURE, LABEL, DIM, NOTES. Dimension annotations are editable primitives, not associative CAD dimensions. Opening locations are indicated by boxes on OPENING layer, not an interior door/window detail.
- CSV: UTF-8 BOM for spreadsheet compatibility. Net floor area = width×depth; net wall face area = 2(width+depth)×height minus all openings. No waste, reveals, material layers, pricing, purchasing or structural quantities.
- `manifest.json` is written last, only after required outputs exist; SHA-256 records package files and source. It is a reproducibility record, not a digital signature or approval certificate. Optional Blender artifacts are removed before rebuilding so a drawing-only build cannot expose stale models. Use a dedicated generated folder; do not store originals there.
- `render.png`: 1920×1440, Cycles 32 samples with denoising where supported, otherwise 128 samples without denoising (`render-settings.json` records actual settings); cutaway south/east walls hidden in render. Full wall geometry retained in GLB. `.blend` retains the render cutaway settings.

Run builds sequentially into a given output directory. The CLI is not a concurrent job server. A failed Blender build leaves diagnostic partial outputs but no successful manifest; regenerate before serving. Do not edit generated outputs as the source of truth.


Scale note / 比例補充：A101 深度超過 8000 mm 時改用 1:100；其餘為 1:50。請以各張圖框比例為準。平面表最多列前十件家具，完整清單在 furniture.csv。家具各邊至少 150 mm；示意家具不代表實品。

Rendering note: Blender procedural oak nodes are not baked into GLB textures; the browser shows a simpler PBR base-colour material. Geometry and dimensions share the source; offline render and browser shading are not pixel-identical.
