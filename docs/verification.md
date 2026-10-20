# Verification

The latest scope and results are recorded in the [style-study work record](reviews/2026-10-20-style-studies.md). The current suite passes 26 tests, covering project validation, copied-skill independence, detailed drawing consistency, native cuts/dimension evidence and host installation safety. Four original Blender style studies and eight-sheet technical drawings are included. The earlier [skill-package record](reviews/2026-10-20-skill-package.md) records the starter pipeline checks. Use the commands below to reproduce the checks; see the work record for exact scope and remaining unverified platforms.

From the repository root:

```bash
cd skills/interior-design
bash scripts/setup.sh
.venv/bin/python scripts/project.py validate assets/example-project.json
.venv/bin/python scripts/project.py build assets/example-project.json --out assets/viewer/public/generated --blender
.venv/bin/python scripts/verify_outputs.py assets/viewer/public/generated
npm --prefix assets/viewer run build
cd ../..
skills/interior-design/.venv/bin/python -m unittest discover -s tests -v
```

Expected full-demo outputs include the model-derived 1920×1440 render, editable scene, GLB, five-page A3 PDF, SVG/DXF drawings and CSV schedules. The artifact verifier checks checksums and package consistency. Blender is required for model/render generation; omitting `--blender` generates the drawing package and a plan-only viewer.

The optional `scripts/browser_smoke.py` needs Python Playwright and Chromium. Report real browser execution separately from build success. Image resizing and link checks do not establish Blender or browser correctness. No site measurement, professional drawing approval or engineering certification is implied by software checks.

## Detailed study checks

```bash
skills/interior-design/.venv/bin/python skills/interior-design/scripts/build_drawing_studies.py --out output/drawing-studies
blender --background --threads 4 --python-exit-code 1 --python skills/interior-design/scripts/render_style_studies.py -- --style all --out output/style-studies
skills/interior-design/.venv/bin/python skills/interior-design/scripts/build_style_review.py --study output/style-studies/mcm --drawings output/drawing-studies --out skills/interior-design/assets/viewer/public/generated
npm --prefix skills/interior-design/assets/viewer run build
```

The detailed eight-sheet pack and original four-style scene pipeline were generated successfully. Chromium tested render/plan/GLB modes, controls, real PDF download and three responsive widths without failed requests or page errors. A live Codex session generated and verified the installed drawing package. Claude Code is installed, but its session test failed at local authentication before generation; Cursor/Copilot live behavior remains unverified. See [agent compatibility](agent-compatibility.md).
