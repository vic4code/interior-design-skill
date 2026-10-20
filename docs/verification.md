# Verification

The current integration scope and review findings are recorded in the [product quality audit](reviews/2026-10-20-product-quality-audit.md). Earlier work records preserve the checks performed on prior snapshots; their old helper commands are historical, not current user entry points.

From the repository root:

```bash
skills/interior-design/.venv/bin/python -m unittest discover -s tests -v
npm --prefix skills/interior-design/assets/viewer run build
```

From the installed skill directory:

```bash
.venv/bin/python scripts/interior_design.py demo --out /path/to/demo
```

The single entry should generate four same-space branches, preserve base/result provenance, include matching GLBs and eight-sheet drawing examples, start a loopback-only server and open one browser page. `--no-serve` verifies artifact generation without Node/Blender/browser execution; it does not establish frontend behavior.

Browser acceptance checks must use real generated packages, not only mocked routes. Exercise every style and all five modes, room/view filtering, base comparison, sheet selection/zoom, actual PDF download, responsive widths and rapid 3D style switching. Verify cutaway interior visibility and fit-to-frame drawings without nested scrollbars. Inspect screenshots for exposure/material/readability as well as request/script failures. Confirm a native multi-room package omits unknown area instead of inventing rectangular data, and a drawing-only package opens its available technical sheets.

The automated suite covers validation, geometry evidence, native annotations/schedules, copied-skill independence, same-space source/base consistency, image provenance, package hashes, local serving/isolation/reuse/stop and installation safety. Host file paths do not prove live model behavior in every host; see [compatibility](agent-compatibility.md). Image quality, site dimensions and professional construction approval cannot be established by code tests alone.
