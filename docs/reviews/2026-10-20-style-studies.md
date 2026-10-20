# Style studies and detailed drawing showcase

## Authorized scope

Improve the skill beyond the scope of its bundled starter generator. Produce original MCM, Japandi, Contemporary and Bauhaus studies informed by the supplied Lo-Fi House cases and Dan Retro selection references. Show actual Blender renders, several coordinated drawing deliverables and downloads in both READMEs. Preserve a host-neutral standard skill with Codex, Claude Code and other mainstream installation guidance. Keep private source names/data out of public files and Git metadata.

## Acceptance

- Explain the difference between general agent-led design workflows and the starter generator's input limits. No arbitrary dimension/furniture limits on the overall skill.
- Four materially and geometrically distinct Blender studies, with reproducible scene source and image provenance. No third-party case/product images or models are redistributed.
- Shared synthetic dimensions/IDs across studies and drawing package; professional sheet hierarchy, dimension chains, opening/finish schedules and cabinetry sections/details. Technical assumptions, unresolved equipment/hardware and issue status remain explicit.
- README leads with actual render and drawing deliverables, links the package, and keeps previews small.
- Host installation paths are checked against official documentation, with tested versus documented compatibility accurately labeled.
- Run appropriate schema, geometry, artifact, native render and installation checks, then independent standards/spec reviews.

## Contract

`assets/style-studies/project.json` retains the starter v1.0 schema for a fictional 6000×4800×2800 mm room. F01 sofa, F02 coffee table, F03 desk, F04 chair, F05 custom low sideboard. F05 bounds: x3400,y250,W2200,D450,H750 mm. Door/window positions and stable IDs are shared with all sheets. `styles.json` stores four visual directions. Detailed/procedural geometry is generated from the same outer bounds; product identity and engineering approval are not inferred.

## Results

2026-10-20: Four 1600×1200 hero renders and four 1280×960 detail renders completed in Blender Cycles. The public derivatives include original GLB geometry and source/provenance hashes; four inline hero JPEGs total 188,442 bytes. Eight A3 sheets, PDF, DXF and schedules were generated from shared synthetic dimensions.

Personal installations were performed for Codex and Claude Code, with pinned Python dependencies. A real Codex CLI session read the installed skill and generated all eight sheets, verifying 17 output and four source hashes. Claude Code attempted a live session but local OAuth authentication failed before model execution; generation is unverified there. Cursor/Copilot installation layouts are tested, live sessions unverified. A separate installed-skill native extraction and nine-sheet delivery ran on a private local model; content and exact runtime paths are excluded from this repository.

The first full run passed 24 unit tests and the viewer production build. Review found two distinct geometry-evidence/assembly issues plus one source-hash omission. Corrections and final verification are in progress; no construction approval is inferred from software checks.

## Independent review corrections

### Standards

Two P2 findings: native dimension evidence accepted isolated coordinate matches rather than faces; style bridge omitted the styles.json source hash. The native verifier now requires nondegenerate axis-aligned planar triangles at each measured station, records face evidence and supports explicit bounded evidence regions. It distinguishes plane stations from functional opening approval. A sloped-triangle rejection and region-selection tests cover the regression. The bridge now checks all three shared input hashes; a changed-palette rejection test covers the regression.

### Spec

Two P2 findings: the same dimension-evidence issue, plus renderer shelf/plinth positions differing from J401. Shelf and plinth geometry were corrected against the drawing section, then all four style outputs regenerated.

The two review axes were assessed separately. Final verification below supersedes the preliminary run.

## Final checks

- Anthropic skill-creator quick_validate: passed.
- Style browser bridge: produced 23 checksummed files; Chromium loaded the actual GLB, image and plan, exercised controls and PDF download at 320/768/1440 widths, with no page errors or failed requests.
- Public-file and ZIP-content scan: no private source names, personal identifiers or local home paths; README relative links resolved and showcase derivatives matched provenance hashes.
- GitHub contributor/commit metadata checked: only the repository owner handle and its noreply address.

Final unit suite: 26 tests passed, including the sloped-face and palette-source regression checks.

- Official Anthropic package_skill passed on a clean tracked-file staging copy; archive contains only 42 distributable skill files, no runtimes or generated projects. An initial invocation lacked the creator package import path; rerun with its package root on PYTHONPATH passed.
- Starter drawings-only generation and 13-artifact verifier passed. The new study manifest uses a different contract; passing a render-only intermediate folder to the starter verifier first failed for missing manifest, then the complete starter output was generated and verified.
- Targeted standards re-review confirmed both source/evidence findings resolved, with no residual issues.

Final Blender assembly check: actual native world-space shelf bounds start beyond the 9 mm back panel, with 420 mm shelf depth; the plinth has 60 mm rear setback and 339 mm depth, matching J401. All four styles were rerendered from the corrected source; published provenance was refreshed.

Publication target: [main](https://github.com/vic4code/interior-design-skill/tree/main), using only the public owner identity in commit metadata. Private nine-sheet delivery remains local.
