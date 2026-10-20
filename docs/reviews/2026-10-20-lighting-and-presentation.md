# Lighting and presentation consistency

## Authorized scope and acceptance

The owner requested correction of washed-out 3D materials, designed default lighting, daylight and lights-off effects, equal image sizes with explicit generation prompts, and visible examples of all five deliverables in both READMEs.

- Diagnose material/export and lighting causes separately. Preserve the existing source model and original project; test corrected exports in a separate local delivery.
- Provide day/night and indoor-light on/off controls, with a readable day-plus-lights default. Daylight with indoor lights off must retain daylight. Lighting previews do not certify illuminance or electrical design.
- Generate actual same-room, same-camera lighting examples using the host image tool, with prompts locking 4:3 framing, level camera, verticals, openings and furniture placement. Keep originals, prompts, hashes and visual-review notes.
- Deliver image derivatives with identical 900×675 frames; never stretch geometry to force a ratio. Verify actual README display sizes and top alignment, as file dimensions alone do not control table layout.
- Show five distinct real artifacts directly in English and Traditional Chinese README: clean layout, interactive-model preview, image-gen result, available MEP proposal and engineering detail. Include daylight/lights-off comparisons.
- Use one frontend for public examples and existing local projects. Synchronize installed skill sources, test actual browser controls and screenshots, review Standards and Spec separately, scan public files/history, and push the authorized public changes.

## Starting snapshot

`38e82ab`; clean worktree. Continue the existing portable runtime and `scripts/interior_design.py` entry. Private runtime assets remain outside Git. Original project paths and account identifiers are excluded from this record.

## Implementation and verification

Implementation, final installed-browser acceptance and publication passed on 2026-10-21.

### Actual changes

- Added independent day/night and indoor-light on/off controls, defaulting to daylight with warm interior light. State survives asynchronous model loading and style/mode changes. The bounded preview rig keeps authored colors and uses available emitter/fixture geometry; its fallback is explicitly a visual preview.
- Diagnosed lost source texture multipliers in an imported native GLB. A separate private export restored 35 authored factors while retaining identical geometry, textures, nodes/accessors and binary payload. No private source or corrected native artifact was published.
- Full-house screenshots exposed excessive lighting that the single-room example had not revealed. Replaced whole-model quadratic light scaling with fixed preview power and local falloff, and lowered indirect fill. Actual model pixels retained their material contrast rather than washing out. Daylight/off stayed unchanged; nighttime/on gained local warm zones.
- Real-GPU screenshots also exposed floor/rug z-fighting from an excessively small camera near plane. A scale-aware near plane removed the triangular artifacts while preserving geometry and shadows. Before/after screenshots were inspected; final installed screenshots match the accepted frames.
- English and Traditional Chinese README show five actual deliverables, four real WebGL lighting states, four same-space styles and three separately labelled image-gen lighting studies. Fixed HTML cell widths and shared image rows control rendered alignment.
- New image-generation prompts lock camera, lens, horizon/vanishing points, 4:3 canvas, crop, openings and furniture, then vary only the requested illumination. Three generated originals are all 1448×1086; previews and actual model captures are all 900×675. Prompts are requests, not dimensional certification.

### Passed checks — 2026-10-21

- `.venv/bin/python -m unittest discover -s tests -q`: **65 tests passed**, including a copied-skill demo that decodes all three lighting images and verifies common base/provenance hashes and identical output dimensions.
- `npm run build` with an isolated output directory: passed. Lighting state/disposal checks and real Chromium controls, delayed-load selection, style persistence, keyboard focus and responsive layouts passed.
- The installed Codex single entry built and automatically opened a separate existing-project review. Codex and Claude Code installations match **130 portable files** byte-for-byte; their older active frontend builds were retained.
- Final installed browser acceptance: **166 checks** for the multi-room review and **257 checks** for the public four-style demo, **423 total**. All five modes, four responsive widths, layout/detail separation, MEP, fit/zoom/pan, cutaway and downloads passed with zero JavaScript, HTTP or transport errors.
- Five real browser PDF downloads matched registered SHA-256 hashes. The served native and synthetic GLBs matched their package manifests. Eight final installed lighting screenshots matched the visually accepted source-test frames pixel-for-pixel; whole-house and close-up images were inspected separately.
- Actual GitHub sanitizer/native CSS checks passed both READMEs at 1440 and 375 px. Each has 16 images in four tables; each group has equal rendered image dimensions, aligned row tops, 4:3 frames and no table overflow. The final five 3D captures were refreshed after the camera fix; hashes and exact 900×675 frames passed.
- Team review kept Standards and Spec separate: **zero blocking findings on either axis**. Final installed/browser evidence closes the previously pending release checks.

### Public audit and portable package

- Scanned **280 tracked files**, public archive contents, GLB JSON and **386 reachable Git objects / six pre-release commits**: zero private-identifier findings. Public author/committer identities and the sole GitHub contributor match the intended account.
- **146** source/image/viewer/artifact hashes, **50** bundled dependency hashes and **78** README links passed. Twenty-three historical raw-source records refer to bytes not bundled in the public repository; the package audit does not claim those originals were rehashed.
- Official `quick_validate.py` and `package_skill.py` passed from a clean tracked-only stage: **130 files**, no virtual environments, node_modules, generated project data or build caches. Every archived file matches the portable source stage.
- Private installable audit archive: **6,508,408 bytes**, SHA-256 `bcf8630e10087256e81f4d3fe5803b0f2c1f26ac0f5e139bbb643e494a2a365f`. No private review artifacts are in the public package.

### Remaining limits

Interactive light is qualitative, with a bounded number of unshadowed practical preview lights and a directional shadow map; it is not a photometric or electrical calculation. Image-gen results remain visual simulations. Live Claude Code generation remains unverified because authentication failed in the earlier host test; the portable installation itself is verified. The separate Temporal installation is not integrated into this workflow.

## Publication — 2026-10-21

[Implementation commit 6b88b52](https://github.com/vic4code/interior-design-skill/commit/6b88b5245920c8732b4890b358d8a024ddd4035b) was pushed to `main`; `git ls-remote origin refs/heads/main` matched that local commit. Private source models, corrected native exports, browser packages and QA evidence remain outside the public repository. The two installed hosts match all 130 released portable files.
