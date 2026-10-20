# Model the actual space

The skill is an agent-led Blender and frontend workflow. The included rectangular-room JSON generator is a quick-start tool, not a geometric limit on the skill.

## Select an implementation route

Use `scripts/interior_design.py project` when the project fits its documented schema and the user wants a fast, reproducible coordination study. Its room/furniture bounds protect that particular primitive model and fixed-sheet layout.

Use project-specific Blender Python, an available Blender connection or an existing native scene when the task needs multiple rooms, nonrectangular walls, rotated furniture, detailed joinery, changes of level or other real project geometry. Keep the scripts, source contract and export adapter with the project. Do not silently clamp a real room to the starter limits or delete unsupported geometry to make validation pass.

The four supplied style studies demonstrate a second route: detailed procedural geometry and materials, including furniture components much thinner than the starter's furniture envelopes. They still share a synthetic single-room fixture so their layout and drawing evidence can be compared directly.

## Preserve one spatial contract

Record a project origin, axes, units, floor datum, source plan/revision and calibration evidence. A suitable richer contract records:

- Rooms and closed floor polygons; wall segments with thickness, height, material/state and stable IDs.
- Openings referenced to host walls, station offsets, sill/head levels and dimension basis; distinguish nominal, finished-clear and rough openings.
- Furniture instances with local product W/D/H, translation, rotation, model source and fidelity.
- Casework assemblies and component dimensions, internal clearances, panel thicknesses, finish, hardware status and maintenance envelopes.
- Service proposals with XYZ, height datum, existing/proposed state, equipment reference and responsible trade.
- Camera transforms, material specifications and source revision/hash for each output.

Derive room polygons, wall cuts and dimension strings from this contract. Validate closed boundaries, opening containment, duplicate IDs, transformed solids and frame conversions. Treat uncertain structure and surveyed positions separately from proposed work.

## Build and compare

Model native assemblies before making lightweight browser derivatives. Retain stable IDs across collections, GLB nodes, drawing tags and schedules. Evaluate world-space vertices after transforms; a rotated world-axis bounding box is not a manufacturer's product W/D/H.

Inspect plan, eye-level views, operations and sections. Test doors, drawers, chairs, maintenance access and retrieval using actual swept geometry when available. Report which checks were modeled and which remain site or product questions. Browser inspection and geometric clearance are different evidence.

If the browser contains later edits, reconcile them into the authoritative source or freeze an evaluated scene snapshot before export. Never replace current geometry with an older Blender file merely because the starter accepts it.

## Scale the drawings to the project

Choose sheet count and scale for legibility. An apartment may need room plans, enlarged details and cross-referenced sections instead of one compressed sheet. Preserve model-space mm in CAD exports. Keep titles, section markers, dimensions and schedules tied to element IDs. Read [construction-documents.md](construction-documents.md) before issuing a detailed package.
