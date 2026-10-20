# Skill package restructuring

## Authorized scope

Restructure the repository around a self-contained `skills/interior-design/` package following the [Anthropic skill-creator guidance](https://github.com/anthropics/skills/tree/main/skills/skill-creator). Provide an English default README and equivalent Traditional Chinese documentation. Reduce preview download sizes while preserving the original images. Remove private project references and identifying information from public files and Git history.

## Acceptance

- The skill contains its instructions, references, scripts and assets; installed copies can run without repository-root resources.
- Both READMEs document installation, local execution, outputs and current limitations with working relative links.
- README previews use lightweight derivatives, link to original images and distinguish AI concepts from model-derived renders.
- Public content and replacement history contain no private project names, source paths, personal data or links to removed commits.
- Validation results distinguish passed, failed and unverified checks.
- Both READMEs show actual generated dimensioned plan/elevation sheets and link the complete A3 PDF, DXF and furniture schedule.

## Implementation notes

Scope approved and implemented on 2026-10-20. Runtime scripts, dependency locks, schema, synthetic example and viewer now live inside the skill. Repository-level files contain documentation, tests and evaluation prompts only.

## Preview optimization

Full-resolution PNG pixels are preserved; JPEG previews only resize and re-encode the same content. Nonessential metadata was removed from the full-resolution Blender PNG without changing its decoded pixels. The original byte counts below describe the starting files. Both READMEs link the previews to the originals. Hashes and source filenames are recorded in `docs/images/concept-provenance.json`.

| Image | Original bytes | Preview bytes | Reduction |
| --- | ---: | ---: | ---: |
| docs/images/fictional-concept.png | 2,642,742 | 152,375 | 94.2% |
| docs/assets/demo-render.png | 3,197,188 | 44,761 | 98.6% |

Combined README image transfer: **5,839,930 bytes → 197,136 bytes**, a **96.6% reduction** (5,642,794 bytes saved).

Documentation is available in English and Traditional Chinese. Private-source mappings and old publication records were replaced with general design patterns, a roadmap and this scoped record.

## Verification — 2026-10-20

Environment: macOS, Python 3.14.6, Node 24.5.0, Blender 5.2.0 LTS, installed headless Chromium.

| Check | Actual result |
| --- | --- |
| Anthropic skill-creator `quick_validate.py` | PASS |
| Anthropic skill-creator `package_skill.py` against a clean copy of tracked skill files | PASS; approximately 54 KiB `.skill` artifact, no caches/dependencies/generated user outputs |
| `bash scripts/setup.sh` from the skill directory | PASS; pinned Python dependencies present, npm clean install completed. Blender was not on the shell PATH; subsequent native execution explicitly added its binary directory. |
| `bash -n scripts/setup.sh` | PASS |
| `skills/interior-design/.venv/bin/python -m unittest discover -s tests -v` | PASS, 8 tests. Includes copying only the skill into a temporary installation, then building/verifying from an unrelated working directory. |
| Native generation using relocated `scripts/project.py` and bundled example | PASS; 17 artifacts plus manifest, revision P01, editable scene, GLB and 1920×1440 Cycles PNG |
| Relocated `scripts/verify_outputs.py` | PASS, 17 checksummed files, consistent revision/IDs, PNG/PDF/SVG/GLB checks |
| `npm --prefix assets/viewer run build` | PASS |
| Real Chromium check of relocated viewer | PASS: render, responsive widths 320/768/1024/1440, plan, PDF download, GLB WebGL, camera/wall controls and updated missing-package instructions; no page errors or failed asset responses on the normal path |
| Local Markdown links and source/preview image SHA-256 | PASS |
| Public filename/content privacy scan, including image bytes | PASS; generated outputs and runtime caches are ignored |
| `git diff --cached --check` | PASS |

Two independent scenario runs exercised missing measurements/product evidence and preservation of browser changes before native rendering. Both produced useful evidence requests and workflows without inventing measurements or claiming room-specific output. A static review viewer was generated with Anthropic's `eval-viewer/generate_review.py`. These are qualitative scenario checks, not an A/B benchmark or proof of separate agent-host compatibility.

## Drawing showcase

Copied actual P01 A101/A202 SVG sheets, five-page PDF, plan DXF and furniture CSV from the verified synthetic output package into `docs/drawings/`, with file/source hashes in `provenance.json`. Both READMEs show the vector sheets before the appearance previews and link the downloadable artifacts. Rendered and visually inspected both sheets in Chromium. Vector previews keep text scalable and require only a few kilobytes; these are actual generator outputs.

## Independent code review

Standards review identified three instruction issues: an old handoff guide path, a missing Windows dependency-install command and own-room commands still pointing at the sample. All were corrected and the standards reviewer confirmed each fix. Spec review found no actionable gaps.

## Publication

The owner explicitly authorized removing identifying information from Git history. Published the reviewed snapshot as one parentless commit using the public account identity and a GitHub noreply email. Replaced remote main using an exact lease, expired local old reflogs and pruned unreachable objects. GitHub independently reported one commit on the public branch. A follow-up amendment records publication results and adds the requested actual drawing previews while preserving a single parentless commit.

## Unverified boundaries

Windows execution, separate Codex/Claude host sessions, arbitrary room reconstruction, site measurements and professional construction approval were not verified. GitHub server caches and existing external clones cannot be removed by rewriting the public branch.
