# Lightweight walkthrough acceptance — 2026-10-22

Implemented in the **shared, installed-skill viewer**, with a reusable `src/walkthrough.js`, updated SKILL/reference guidance and rebuilt offline viewer. All generated review packages use this renderer, including actual project GLBs; this is not a demo-only camera script. Published metadata remains v0.1.2; the change is unreleased. No tag, release, package or extra issue is part of this change. GitHub delivery proceeds only after the later explicit user authorization and successful local review.

## Reference evidence and design decision

The supplied [Threads share](https://www.threads.com/share/BAX-waDSYi/) resolves to [anthonymaniquis / @a.maniquis's post](https://www.threads.com/@a.maniquis/post/DewZtExAtAb). The separate source researcher reported directly reading the author's claim: “3d render by claude ai opus, updated with lighting scenario and Unreal Engine for cinematic walk through”. A dark-background cutaway/dollhouse room was visible. A login overlay prevented further video interaction; no login or bypass was attempted.

That evidence supports **an author claim of a cinematic walkthrough**, not verified free navigation, an Unreal runtime in the browser, Gaussian splatting or reconstruction with a large model. The requested controllable forward/back movement comes from the user's explicit requirement. The eye-level camera, conservative floor/obstacle checks and existing Three.js lighting are **our own lightweight implementation choices**. No reference footage, code or assets were downloaded or incorporated.

## Inspected baseline

- Clean working tree at `41b3c29`; no AGENTS.md at repository, workspace or filesystem root, and none found below the workspace. Skill v0.1.2; private viewer package v0.1.0.
- Three.js **0.180.0**, OrbitControls, GLTFLoader and RoomEnvironment; Vite **6.4.4**. No dependency or lockfile version change.
- Model/Three.js deferred until selecting 3D. Existing ACES tone mapping, authored PBR materials, DPR cap 1.75, cached 2048² directional shadow and at most eight unshadowed warm preview lights. No new light/shadow/postprocessing pass.
- Existing camera was an orbiting cutaway overview with dolly/zoom and pan; static active views still rendered on every animation callback. Existing Python unit tests and production/offline bundle fingerprints were inspected before implementation.

## Result and limits

Overview is preserved. Entering **走入空間** restores enclosure, places the eye 1.6 m above supported floor geometry, sets a 65° vertical FOV once and allows drag look. Phone buttons step 0.35 m; focused canvas keys support forward/back, strafe and yaw. Reset restores the entry pose, and returning to overview restores its previous enclosure selection. Camera movement preserves projection, eye height and source geometry. Buttons remain outside the scene with at least 44 px touch targets. Keyboard events outside the canvas are untouched; blur, mode exit and visibility events clear held movement.

Support is derived from actual named floor triangles, with a 20 cm footprint sampled at its center/four extremities. Expanded mesh AABBs overlapping body height provide conservative obstacle checks, including walls hidden in overview. At most 8 cm substeps prevent jumping over thin obstacles. Unsupported models show an unavailable explanation and retain overview. This is a single-level preview: complex combined meshes may over-block; stairs, stacked floors, dynamic obstacles and arbitrary import naming need authored navigation data. It is not complete physical collision, a certified accessible route or photorealistic reconstruction.

The animation callback remains for interaction, but a settled view issues no redraw. Existing damping/rotation, resize, lighting and movement trigger rendering; non-3D/hidden views skip it. No model, image, material or lighting asset changed.

## Independent local review and fixes

Review base: `41b3c2949937b49a6c974573cb9937b0be22f612`. A separate read-only reviewer examined event cleanup, mode/camera handoff, rendering lifecycle, conservative boundaries and touch controls. Two required lifecycle findings were fixed:

1. **Settled context restoration did not redraw.** Independently reproduced with `WEBGL_lose_context`: the context restored but emitted zero draws. The viewer now recreates GPU-only PMREM environment targets, requests cached-shadow refresh and marks the frame dirty on restoration. Visibility changes also invalidate the frame. Recheck: **507 recovery draws, then 0 idle draws**; the actual walk scene before and after restoration is byte-identical, SHA256 `725c210f361213818b3be3bd8f080e5cfe928068d8e7ceacf804f54f779677a6`.
2. **Superseded pending canvases could retain OrbitControls document listeners.** Canvas attachment and controls/listener construction now occur only after GLB loading and current-version validation. Empty geometry uses unified disposal; visibility/context listeners are removed through an AbortController. The browser regression deliberately delays one model while switching to a newer one and checks for exactly one current document key interceptor.

The optional repeated `aria-live` mutation was also removed: movement status only writes when the message changes. Camera and collision behavior remain as documented. The independent final review found no remaining blocking issue. Regression checks include actual context loss/recovery and idle re-settling, not only synthetic events.

## Measured resource and interaction cost

Production file totals, before at `41b3c29` and after rebuilt bundle; decimal bytes. Gzip is summed per file using Python `gzip.compress(..., mtime=0)`, not HTTP transfer sizes (the local server serves uncompressed assets).

| Measurement | Before | After | Change |
| --- | ---: | ---: | ---: |
| All production JavaScript | 623,043 B | 629,607 B | +6,564 B / 1.05% |
| JavaScript gzip | 162,846 B | 165,541 B | +2,695 B / 1.65% |
| HTML + CSS + JS | 642,332 B | 650,004 B | +7,672 B |
| HTML + CSS + JS gzip | 168,436 B | 171,345 B | +2,909 B |
| MCM GLB | 2,559,312 B | 2,559,312 B | unchanged |
| Settled 3D, two-second sampled draw calls | 262 | 0 | no idle drawing |
| GLB requests before opening 3D | 0 | 0 | deferred load retained |
| Added runtime packages / model assets | — | 0 / 0 | no new downloads |

All four GLBs remain byte-for-byte identical to HEAD: Bauhaus 2,464,692 B; Contemporary 2,501,796 B; Japandi 2,745,996 B; MCM 2,559,312 B. Source textures/images and existing demo drawings are unchanged. Screenshots below are documentation evidence outside the installed skill and are not loaded by the viewer.

Browser: Chromium 154.0.8037.57, Linux, headless SwiftShader software WebGL; desktop viewport 1280 × 900, canvas 853 × 640 at DPR 1. Draw calls were counted by instrumenting WebGL drawElements/drawArrays after loading/settling. The baseline and first after sample used the same environment; the acceptance script repeats the zero-idle check on the shipped after bundle. These are draw counts, **not FPS, GPU time, energy or physical-phone benchmarks**. No phone performance number is claimed. The change meets the +10 KB raw JS / +5 KB gzip change budget. A physical target phone's p95 frame-time target of 33 ms during a defined walk remains unmeasured.

WebGL view/projection matrices from the actual shipped renderer show a 0.350000035 m translation for one forward step, eye height unchanged within floating-point tolerance, identical projection and changed near/far reprojection separation. Before eye position: `(3, 1.605000003, -0.615000019)`; after: `(3, 1.605000053, -0.965000054)`. The model's floor is about 0.005 m above its origin; the camera is 1.6 m above that surface. The browser test observes uniforms without shipping debug camera globals.

## Verification and reproduction

- **99/99 Python tests passed**, including copied-skill independence, source/artifact fingerprints and the standard-library demo with Node/npm absent from PATH.
- **5/5 Node navigation tests passed**: camera displacement/FOV/reset; thin wall and floor edge; no floor fallback; capped key movement, blur/inactive cleanup/disposal; real floor hole inside an overall bounding box.
- Production build and `scripts/build_quickstart.py` passed; all four unchanged drawing bundles and the production viewer/checksums/fingerprints were synchronized through the existing build path.
- `python3 -S …/interior_design.py demo --out /tmp/interior-final-offline --no-serve` passed without package downloads.
- Browser acceptance uses an actual generated four-style package and shipped prebuilt viewer. It checks all five modes, image decode, sheet selection/zoom, actual PDF download, all style model loads, rapid switching with a single remaining canvas, fixed projection and translation/parallax/reset, drag/key movement, selectors retaining keyboard behavior, lighting control state, inactive and idle draws, 320/390/768/1024/1440 px page fit and 44 px controls.
- Mobile context: touch-enabled Chromium 390 × 844, actual CDP touch pointer events and button taps; scene pixels change after a touch drag. This establishes browser touch handling, not physical iOS/Android device performance. Hidden-tab guard uses a simulated `document.hidden` predicate/event because headless tab visibility is platform dependent.
- No script errors or HTTP failures in the final browser acceptance. Screenshots were inspected for scene framing, material appearance, mobile control placement and contrast; a low-contrast active-mode button found during inspection was fixed before the final run.

```bash
python3 -m unittest discover -s tests -q
npm --prefix skills/interior-design/assets/viewer test
python3 scripts/build_quickstart.py
python3 -S skills/interior-design/scripts/interior_design.py demo --out /tmp/interior-check --no-open
# Use the localhost URL printed above:
PLAYWRIGHT_MODULE=/path/to/playwright CHROME_BIN=/usr/bin/chromium \
  node scripts/test_walkthrough.cjs http://127.0.0.1:PORT/ /tmp/interior-walk-evidence
```

The first npm install could not write its default cache; setting `--cache /tmp/interior-npm-cache` resolved it without changing credentials, permissions or package versions. No denied or uncertain external action remains. Physical-device frame rates, arbitrary native model navigation and unobservable reference-video interaction remain outside the verified scope; none blocks this conservative preview.

[Machine-readable acceptance](lightweight-walkthrough/results.json) · [Independent review](lightweight-walkthrough/local-review.json) · [Baseline draw/resource sample](lightweight-walkthrough/baseline-metrics.json)

[Before forward step](lightweight-walkthrough/walk-before.png) · [After forward step](lightweight-walkthrough/walk-after.png) · [Mobile touch view](lightweight-walkthrough/mobile-touch.png) · [Recovered WebGL scene](lightweight-walkthrough/context-restored.png)
