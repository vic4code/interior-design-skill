# Contributing

Help people turn room ideas into editable models and dimensioned coordination drawings. Preserve one dimensional source, explicit assumptions and reproducible outputs.

Keep runtime resources inside `skills/interior-design/` so an installed skill works independently of the repository checkout. Follow the [Anthropic skill-creator structure](https://github.com/anthropics/skills/tree/main/skills/skill-creator): concise instructions, progressively loaded references, reusable scripts and bundled assets. Keep both READMEs aligned.

Before a pull request, run the unit tests from the repository root:

```bash
skills/interior-design/.venv/bin/python -m unittest discover -s tests -v
```

Then, from `skills/interior-design/`, try the complete portable example and build the viewer:

```bash
.venv/bin/python scripts/interior_design.py demo --out /path/to/demo --no-serve
npm --prefix assets/viewer run build
```

After changing drawing generators, sample data or viewer sources, rebuild the shipped offline assets from the repository root with `skills/interior-design/.venv/bin/python scripts/build_quickstart.py`. This refreshes four synthetic drawing sets, the production viewer, input fingerprints and artifact checksums. Keep `assets/viewer/public/generated/` empty of private runtime output. The runtime validates source fingerprints and falls back to a source build when a shipped bundle is stale. `tests/test_quickstart.py` verifies the demo with Python site packages disabled and no Node/npm on PATH.

Technical README previews use white 900 × 675 canvases with proportional fit and no added mat. Run `node scripts/render_showcase.cjs` with Playwright and Chrome installed (or set `PLAYWRIGHT_MODULE` to an existing module path) to regenerate the JPEGs and source/image hashes.

For a real browser acceptance run, omit `--no-serve`; the browser should open automatically. Check all four styles and layout/3D/image/MEP/drawing views, room/view selection, a base comparison, sheet selection/zoom and a real PDF download. Verify default interior visibility and fit-to-frame drawings without nested scrollbars. Missing MEP inputs must remain explicit. Inspect desktop and mobile screenshots; rendering a canvas is not proof of visual quality. Keep internal Python helpers under `scripts/_internal/`; expose product workflows through the single entry point. Verify bundled dependency licenses/hashes when changing vendored resources.

Report platform limitations and distinguish passed checks from unverified paths. Keep the core free of required paid API calls. Publish synthetic fixtures and assets cleared for redistribution; document third-party source, author, licence and permitted use. Keep private project content and generated user projects out of Git. Describe unreviewed drawings as coordination drafts.

Report mm/metre conversions and mark breaking schema changes. Improve validation errors rather than relaxing checks merely to make a failing input pass. Use `docs/reviews/` for scoped work records containing acceptance criteria and dated verification results without personal runtime data.
