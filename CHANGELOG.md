# Changelog

## Unreleased

- Add opt-in eye-level forward/back walking in the existing Three.js viewer, with phone step buttons, focused keyboard controls, floor support and conservative obstacle checks, reset and return to overview.
- Reuse materials, full enclosure and lighting with no new runtime dependency or model assets; skip settled and hidden-view rendering.
- Document the single-level preview limits and reproducible resource/navigation acceptance checks.

## 0.1.2 — 2026-10-21

- Route professional and contractor-facing requests through dimensioned drawings, linked specifications, trade interfaces and traceable open decisions.
- Define scoped readiness for coordination, quotation, construction and fabrication; keep assumed dimensions and unverified product/site information explicit.
- Add quotation quantity bases, inclusions/exclusions and decision closure evidence without implying new calculation or viewer capabilities.
- Update Traditional Chinese handoff guidance and add cabinet-coordination and screenshot-only MEP evaluation scenarios.

## 0.1.1 — 2026-10-21

- Ship the four-style demo drawings and production viewer for offline startup with Python 3.11+; no PyPI/npm downloads are needed for the unchanged demo.
- Reuse matching setup dependencies, prefer uv when available, and bound package-download retries. Source fingerprints invalidate stale bundled builds.
- Show furniture names directly on the layout, retaining smaller IDs for drawing references.
- Remove extra drawing-preview mats while preserving proportional 900 × 675 canvases.
- Separate English and Traditional Chinese README layout images.

## 0.1.0 — 2026-10-21

First public release of the portable Interior Design skill.

- One browser review for layout, interactive 3D, image-generated visualizations, MEP coordination and engineering drawings; existing projects use the same interface.
- Four style directions for one synthetic room, consistent image frames, day/night and lamp controls, and an eight-sheet A3 drawing example with PDF, SVG, DXF and schedules.
- A single command entry point, bundled Taste and UI UX Pro Max guidance, and installation paths for Codex, Claude Code, Cursor and GitHub Copilot.
- Output ownership checks protect existing files and source inputs. Installations exclude generated work and local browser sessions.
- Vite patched to 6.4.4 for the release build.

Drawings are dimensioned coordination drafts. Site measurements, product choices, fixing details and discipline review are required before issuing construction or fabrication documents. Image generation and interactive lighting are visual studies; neither certifies dimensions or illumination levels.

See the [release acceptance record](docs/reviews/2026-10-21-v0.1.0-release.md) for verification and host limitations.
