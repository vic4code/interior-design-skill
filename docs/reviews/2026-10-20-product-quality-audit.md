# Product quality audit and corrections

## Confirmed scope

The owner rejected the shipped frontend and requested an agent-team review. The real product flow must use image generation for presentation, ground it in existing spatial data when available, preserve existing projects and arbitrary geometry, and deliver actual model-derived technical drawings. The procedural rectangular starter is an optional helper, not the skill's primary route or design scope. Private source content must remain local.

## Review baseline

Published snapshot e5b86ca; review diff e20b16f...e5b86ca and inherited runtime entry points. Standards: CONTRIBUTING.md, SKILL.md and the owner's engineering workflow. Spec: preceding style/imagegen work records and the clarified product flow above. Starting worktree clean.

## Findings

### Standards

Four findings: P1 uncalibrated WebGL lighting and inadequate visual acceptance; P1 generic instructions funneling real projects into the restricted starter; P1 viewer requiring single-room starter metadata instead of native sheet registers; P2 missing image-generation/base/provenance support in browser packages.

### Spec

Three findings: P1 image-generation flow exists only in prose/gallery while actual viewer imports procedural render; P1 real/native packages cannot use the viewer; P2 no demonstrated conditioned public/private output. Keep these axes separate; several findings describe the same underlying behavior.

## Acceptance for corrections

- Presentation-first image-generated view with visible source/base relationship and visual-review status. Preserve base and generated files separately.
- Viewer consumes both style-study and native handoff packages with actual sheet IDs, metadata and available artifacts; no synthetic room dimensions forced onto existing projects.
- 3D, when supplied, remains an optional geometry-check view with calibrated light/exposure and a readable default framing.
- Existing source projects are inspected and continued before any optional starter; dimensions retain their evidence basis.
- Actual conditioned image-generation demonstration from a public synthetic base, plus a private local actual-project example. No private names, dimensions or files in the public repo.
- Browser checks verify actual files/modes/downloads and inspect screenshots; functional WebGL checks are not aesthetic approval.

## Implementation / verification

Implementation and installed-browser acceptance passed on 2026-10-20. Publication is recorded below after the release commit is available.

### Additional confirmed acceptance — 2026-10-20

- One browser page has five distinct modes: clean layout, interactive 3D placement, actual image-generated effects, source-backed MEP coordination and engineering drawings. The existing project and public example use the same frontend.
- Layout shows placement and circulation without technical title blocks/tables. Engineering mode exposes dimensioned plans, elevations, sections and details. They must be visibly different rather than opening the same sheet by default.
- View planning uses actual room polygons or supplied areas, activities and design features with a bounded image budget. Each room receives coverage before additional angles. Unknown area remains unknown; planning jobs are not presented as generated images.
- Completed image-generated views retain their own source/base/provenance and can be selected by room and viewpoint. Same-space style alternatives retain equal image framing.
- MEP shows only registered source drawings/proposals with review status. The synthetic A102 is lighting/electrical intent; full circuits, HVAC and plumbing are not implied without the corresponding evidence and trade work.
- **3D starts with the interior visible**, using a view-only cutaway and a control to restore the complete enclosure. Source geometry must remain intact.
- Plan, MEP and engineering content use a consistent viewing area with fit/zoom controls. **No nested vertical scrolling** inside content blocks; desktop and mobile must provide one coherent scrolling experience.
- Experimental changes run in an isolated delivery path and browser URL. Existing source files, active original deliveries and their servers remain intact.
- English and Traditional Chinese README lead with concrete deliverables, show the equal-frame four-style comparison and actual technical-sheet examples, and distinguish host installation support from live workflow validation.

### Acceptance status

| Area | Status |
| --- | --- |
| README, skill workflow and browser-reference updates | Written; relative-link and whitespace checks recorded below. |
| Five-mode package, multi-view gallery and MEP registration | Passed real installed-package acceptance; 22 completed views, 12 sheets and two supplied MEP references in the local multi-room test. |
| Default interior cutaway and single scrolling experience | Passed actual full-model and four-style checks; source model hashes unchanged; fit/zoom/pan checked at 320, 375, 768 and 1440 px. |
| Installed-host run and final team review | Codex workflow passed; Codex and Claude Code installations match all 118 portable source files. Standards: zero blocking violations. Spec: zero open findings. |
| Public publication | Pending release commit/push verification. |

Do not mark screenshot, installed-host, privacy or output checks passed until the actual final files and page have been inspected. Keep live host limitations explicit in the compatibility/verification record.

Documentation checks on 2026-10-20: `git diff --check -- README.md README.zh-TW.md skills/interior-design/SKILL.md skills/interior-design/references/browser-review.md docs/reviews/2026-10-20-product-quality-audit.md` passed. A local standard-library link check passed for all 81 relative Markdown links across those five files and confirmed final newlines. These checks do not cover runtime browser behavior.

## Confirmed refactor scope and task dependencies

- Review package contract (ready): native/style/starter input, actual sheet IDs, separate base/imagegen/provenance, checksummed files.
- Presentation-first frontend and automatic local browser launcher (depend on review contract): image/base comparison, drawing selector/downloads, optional 3D, unknown dimensions omitted, isolated local serving.
- Detailed native drawing correction (completed): real labels, internal dimensions, opening/detail registers and region evidence instead of outer envelopes alone.
- Unified installed-skill entry (depends on package+launcher, coordinate drawing source move): one scripts/interior_design.py; implementation helpers under scripts/_internal; demo/review/native/install workflows; structured outputs, no user-facing collection of helper scripts.
- Integration acceptance (depends on all above): run from installed copy, auto-open actual private project review with image-generated effect and completed drawing package; inspect browser screenshots and download, re-review and publish only synthetic data.

The existing project is preserved. Runtime helpers now live under the portable skill's internal directory. Image generation runs through the host tool rather than an unconfigured Python API wrapper.

## Final integration results — 2026-10-20

- `.venv/bin/python -m unittest discover -s tests -q`: **65 tests passed**. `npm --prefix skills/interior-design/assets/viewer run build`: passed.
- The installed Codex entry packaged the existing multi-room delivery in a separate working directory and opened its browser automatically. All **93 registered artifacts** were present and matched their SHA-256 hashes. The existing project's six selected baseline source files remained unchanged.
- Real browser acceptance passed **166 checks for the local multi-room package** and **240 checks for the public four-style package**, running concurrently. No JavaScript errors, HTTP errors or transport failures occurred. Checks included actual image/base decoding, room/view selection, distinct layout/engineering modes, source-backed MEP, PDF downloads, responsive fit/zoom/pan and interior/full-enclosure switching. Desktop/mobile and image-gen/model screenshots were visually inspected.
- A separate installed-workflow regression passed for a section-only package without presentation/model, a real two-page MEP PDF, original-PDF download hashes and selecting the engineering booklet rather than a services reference. PDF previews retain filled forms and annotations, preserve original downloads and reject unsupported XFA or excessive resource usage explicitly.
- Team review found and resolved PDF-as-image display, drawing-only startup and MEP-PDF book-selection defects. Standards and Spec were reviewed separately; no blocking findings remain. A nonblocking suggestion to deduplicate provenance validation is deferred.
- A parallel-browser test initially exposed transient gallery connection resets; the local server backlog was increased and final concurrent acceptance passed. Another test found a previously registered local layout file absent after the original package build; its removal cause was not established. The complete package was regenerated and verified, and reopening now validates registered file hashes before opening the browser. Missing/changed-file regressions pass.
- Claude Code's portable installation and dependencies are present; its live model-session test remains unverified because local authentication failed before generation. Cursor/Copilot support has installation tests, not live model-session acceptance. Site measurements, trade decisions and construction-release approval remain project work, not outcomes certified by these software tests.

## Public privacy and package audit — 2026-10-20

Passed against the final staged source snapshot before publication:

- Scanned all 243 tracked worktree files, the contents of the public delivery ZIP, JSON metadata in eight GLBs, and 221 reachable Git objects. No private project/account identifiers, private title, local account paths or known private source-model hash were found. Generic upstream examples and API routes were reviewed separately from private paths.
- All 85 relative README file/anchor links resolve. All 105 registered artifact/image/base/export hashes and all 50 bundled dependency file hashes match their actual bytes. Seventeen historical original-image/native-source hash records refer to sources not distributed in this repository; those original bytes were not independently rehashed by this portable-package audit.
- All four currently reachable commits use the expected public author and committer identity. GitHub reports only the intended public contributor account.
- A clean portable stage was assembled exclusively from Git-tracked skill files. Anthropic's official `quick_validate.py` and `package_skill.py` both passed using Python 3.12. The resulting private audit artifact contains **118 files, 4,466,323 bytes**, and has SHA-256 `4b6b95cdb0605d5dea2e8e649f3bfc532f583a628814518a80e869cb643e842b`.
- Every packaged file matches its portable-stage bytes. The package's four GLB JSON chunks parse, and private-identifier checks pass. No Git metadata, virtual environment, node_modules, build output or runtime cache directories are packaged.

These results cover public privacy, registered file integrity and portable packaging. Installed-host/browser integration, final review and publication are tracked separately and remain subject to their actual acceptance results.
