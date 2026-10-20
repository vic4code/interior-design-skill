# Plan overlays and MEP coordination

## Register original drawings before overlaying

Keep the source drawing immutable. Record revision/page, units, orientation, reference floor level and dimension convention. Calibrate image pixels/PDF/CAD coordinates into the shared mm coordinate frame using at least two reliable separated anchors for similarity alignment and a third independent check. Record anchor positions, scale/rotation/translation, residual mismatch and any distortion. Never stretch a scanned plan to force a match. Uncalibrated underlays must visibly say `UNALIGNED / NOT FOR DIMENSIONING`.

For a skewed perspective image, a planar homography needs at least four suitable points and independent dimensional checks; it is not a remedy for an unknown camera and unknown dimensions. Ask for a proper plan export when evidence is inadequate.

## Layers to offer

| Layer | Coordination purpose |
| --- | --- |
| Original architecture, opacity slider | Check model trace against walls, openings, shafts and columns |
| Existing / demolition / proposed | Separate retention from intended changes |
| Furniture / casework | Show IDs, outer envelopes and internal clear sizes where available |
| Lighting / switches / outlets / data | Distinguish existing and proposed points, intended controls and mounting heights |
| Water / drainage | Equipment connections, slopes and maintenance questions |
| HVAC / ceiling / beam | Equipment, grilles, ducts, soffit and access conflicts |
| Operation / clearance | Open doors, pulled chairs, drawers and maintenance envelopes |
| Camera / render link | Plan camera marker and view cone linked to its 3D/base-render camera |

Use one coordinate adapter and stable IDs everywhere. Selecting an element should identify it on the plan, model and schedule. A source underlay stays separate from derived annotations. Offer source-only, proposed-only, blended and comparison views.

## MEP evidence

For each point or route, record ID, system, existing/proposed state, XYZ in mm, height datum (for example AFF = above finished floor), source/revision and evidence basis. Add confirmed equipment specs, design status, route geometry, size/type and responsible professional where available. Missing details remain null/open questions. Existing surveyed points and assumed proposed points must look different.

Review outlet access behind cabinets, appliance maintenance, fixture versus beam/door conflicts, HVAC servicing, wet-service access, proposed relocation versus immutable existing positions, and selected equipment installation envelopes. Do not infer circuit/load, cable/pipe sizing, slopes, protection or structural penetrations from visual points alone. A control group is not an electrical circuit. AI appearance images cannot establish hidden services.

## Starter scope

The current main generator produces a furniture plan and wall-opening elevations. It does not implement MEP layers, raster/CAD registration, source-opacity controls, service routing, electrical calculations, operation-envelope simulation or plan-to-camera synchronization. Use this reference to scope a project extension and identify missing outputs; do not promise these as completed v0.1 features.
