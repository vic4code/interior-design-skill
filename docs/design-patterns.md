# Reusable design patterns

These patterns guide the skill's communication workflow. They describe methods and implementation boundaries rather than a collection of reusable production components.

| Pattern | Practical use | Current boundary |
| --- | --- | --- |
| One dimensional source | Share stable object IDs, millimetres and revisions across the model, drawings and schedules. | Implemented by the synthetic single-room generator. |
| Modular room assembly | Keep room elements and named views understandable as a project grows. | Multi-room support remains future work. |
| Demand rendering | Render when the scene or camera changes and lower expensive effects during interaction. | A performance pattern for future viewer work. |
| Activity-based review | Check doors, chair pull-out, storage access and maintenance space. | Use the checklist; full swept-envelope simulation is not implemented. |
| Native/export separation | Preserve native materials and evaluated transforms while creating portable web assets. | The current pipeline exports a Blender scene and GLB; advanced asset baking remains future work. |
| Evidence labels | Distinguish measured, supplied, assumed and visually estimated dimensions. | Agent workflow; uncertain inputs remain explicit. |
| Model/render synchronization | Reconcile browser edits with the source model before rendering or handoff. | Viewer editing and browser-scene recovery are future work. |
| Drawing handoff | Use sheet IDs, source revision, dimensions, unresolved items and artifact checksums. | Existing PDF/SVG/DXF/CSV generator supports the single-room contract. |
| Base render and AI concept separation | Keep the model-derived render and optional appearance simulation separately labelled. | AI imagery never establishes dimensional correctness. |

See [implementation roadmap](implementation-roadmap.md) and the skill's [design workflow](../skills/interior-design/references/design-method.md).
