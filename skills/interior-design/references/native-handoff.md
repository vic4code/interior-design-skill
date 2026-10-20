# Use an existing Blender model for a real handoff

Use this route when the current project is already modeled or does not fit the rectangular starter. Preserve its actual geometry, units and revisions instead of remodeling it as a box.

## Establish the current source

Compare the native scene with newer browser changes and existing drawing registers. A recent filename or save date alone does not prove geometric freshness. Inspect specific revised assemblies, evaluated transforms and visible states. Preserve the original file and source SHA-256; extraction must not save changes back to it.

A scene exported from a browser may be batched by material and have lost semantic IDs. Do not reuse an older schedule's IDs without matching actual elements. Generate an object register and document selected groups/regions before dimensioning.

## Extract from the installed skill

From the skill root:

```bash
blender --background /path/to/current-model.blend --python-exit-code 1 --python scripts/extract_native_model.py -- --out /path/to/work/inventory.json
.venv/bin/python scripts/build_native_handoff.py --inventory /path/to/work/inventory.json --config /path/to/work/selection.json --out /path/to/handoff
```

The extractor evaluates native geometry in world-space millimetres, records source filename/hash and custom properties, and reports omissions instead of silently treating missing geometry as complete. Use its include/exclude/budget options for dense scenes. Keep inventories and project-specific selections in the user's project workspace, not inside the distributed skill.

The drawing generator also accepts an inventory without `--config` for an initial model-derived plan. For a useful delivery, define explicit views, selected object patterns, clipping regions, section planes, scales and keyed dimensions in the selection file. Inspect its source/CLI when designing the profile rather than guessing selection behavior.

## Develop useful views

- Cut actual wall geometry for plan linework; a combined object's outer rectangle is not a building outline.
- Select one assembly or one face when a material-batched object contains multiple cabinets. State where clipping was applied.
- Use evaluated triangle/plane intersections for sections and mesh feature edges for projections. This implementation does not perform full hidden-line removal; inspect projection clutter and select a clearer section when necessary.
- Record outer envelope dimensions separately from keyed panel-face or clear-opening dimensions. A verified separation between mesh face planes is model evidence, not an independent site measurement.
- Close dimension stacks and identify panel thickness, usable clear dimensions, lid/door size and operating travel when the source supports them. Do not label a lid's panel depth as certified usable hatch clearance.
- Show section locations and reference each detail to the plan/elevation. Translate titles/notes into the recipient's language and inspect the actual PDF glyphs.

## Review and deliver

The output contains PDF/SVG sheets, selected object/material register, dimension evidence, issues, view selections and a source/file manifest. Inspect every sheet at actual print size, verify source hashes and keyed dimensions, and preserve specific unresolved questions about site sizes, hardware, fixing substrate/loading and services.

Develop required material/component schedules and technical details beyond geometric evidence. The tools help derive and explain model dimensions; issue status for fabrication or construction still depends on actual measurements, selected products and responsible technical review. Read [construction-documents.md](construction-documents.md).
