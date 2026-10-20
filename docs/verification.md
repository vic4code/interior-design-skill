# Verification

The current restructuring and validation status is recorded in the [skill-package work record](reviews/2026-10-20-skill-package.md). The repackaged skill passed eight tests, isolated-installation generation, native Blender output, artifact verification, viewer build and real-browser checks. Use the commands below to reproduce the checks; see the work record for exact scope and remaining unverified platforms.

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
