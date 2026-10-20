# User preparation and plan-to-3D intake

Offer the easiest available start, not a demand for every document upfront.

| Starting input | Ask for next | First deliverable |
| --- | --- | --- |
| Dimensioned floor plan (PDF/image/CAD) | Ceiling height, intended changes, references | Traceable initial 3D; mark missing vertical information |
| Hand sketch | Wall lengths, door/window locations and heights | Normalized plan, then initial 3D |
| Room photos only | Four directions per room; wall lengths, openings and ceiling height | Existing-condition inventory and approximate concept, then dimensioned model after calibration |
| Empty brief | Activities, room count and approximate area | Concept alternatives, explicitly fictional/assumed geometry |

Photos supplement a plan with beams, columns, window sills, services, finishes and obstructions. They are not mandatory for a plan-based first model. Useful later photos: each wall, ceiling/beam edges, doors/windows, retained furniture and equipment/service connections. Avoid collecting personal/private items unnecessarily.

## Interpret a supplied plan

1. Identify its revision, units, orientation and dimension convention. Check whether dimensions are inside clear sizes, wall centres or outside edges.
2. Read dimension annotations; calibrate raster drawings with a reliable known dimension, then cross-check another dimension. If labels conflict or are unreadable, ask or flag the conflict.
3. Trace room polygons, wall thicknesses, openings, shafts, columns and beams in a structured manifest. Keep each source reference and uncertainty.
4. Add actual or assumed vertical dimensions: ceiling/beam soffit, sill, head height, door/window height. Mark unknowns visibly rather than treating a generic ceiling height as verified.
5. Show the normalized plan back alongside the initial model; identify missing walls/openings before furnishing.
6. Build the Blender scene from those definitions; generate frontend and drawings from the same revision.

An execution-capable agent can perform these modeling steps using the workflow. The included starter scripts do not automatically parse arbitrary PDFs/CAD/photos or reconstruct them into 3D. Extend the geometry contract and builder to the actual supplied plan. If the environment cannot inspect a format, request a readable export rather than claiming it was interpreted.

Suggested first response in Traditional Chinese:

> 先給我你手上的平面圖、草圖或照片即可。有標尺寸的平面圖最好；再告訴我想改哪個空間、怎麼使用，以及一兩張喜歡的風格。層高不知道也能先做概念版，我會把未知尺寸標出來，再逐步補齊。

## A useful first result without a measured plan

Treat an ordinary-language request as the entry point. Summarize the inferred brief, choose a coherent design direction and generate a concept with the host image tool if available. Create a provisional layout and dimensioned drawing draft from explicitly recorded assumptions; the agent creates and validates the structured data. Ask for only the few measurements that materially change the next revision. A provided plan improves dimensional confidence but is not a prerequisite for concept work. Track each size’s basis and preserve the distinction between an attractive concept, a model dimension and a verified site measurement.
