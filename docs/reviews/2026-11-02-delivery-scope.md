# Reference-driven delivery scope verification

The skill now routes full residential packages, supplied professional drawing examples and acceptance requests to a delivery scope reference and an 18-category catalog. Private example drawings were reviewed locally; the repository contains only generalized requirements and synthetic tests.

The scope distinguishes design layout, setting-out, ceiling, HVAC, flooring, power/data, fixture placement, lighting control, elevation indexing, room elevations and internal/section details. Input revision, floor/ceiling datum, room coverage and critical holds are explicit. Smaller commissions retain a justified custom scope.

The new `acceptance` entry checks declared coverage, safe artifact paths, drawing/image/record types, SHA-256, revision, evidence locators and recorded findings. It has no geometry parser or professional approval authority. Its best result is `ready_for_review`; incomplete or held work returns exit 2. It preserves unrelated output files and source artifacts.

Verification on 2026-11-02:

- Full Python suite: 108 tests passed using the existing Python 3.12 skill environment.
- New behavior tests cover changed/missing/wrong-revision evidence, a text file substituted for a drawing, pending/missing checks, held work, per-room coverage, unjustified exclusions, duplicate IDs, path traversal/symlinks, site-package-free CLI operation and preservation of unrelated files.
- Official skill frontmatter validator passed.
- An independently copied portable skill ran its actual bundled demo with Python site packages disabled, without installing Python/npm packages.
- A real inventory of the generated demo correctly returned `incomplete` for full residential scope, including absent ceiling, HVAC, floor, control and elevation-key categories. A limited inventory/layout profile returned `ready_for_review`; no construction approval was claimed.
- Private reference file moves were verified against pre-move SHA-256; existing design launchers and runtime compatibility paths were preserved.

The initial source checkout was sparse and omitted LICENSE.txt; installation tests failed until the complete required package files were included. One pre-existing detached-server startup test also failed once; the complete corrected-checkout run passed. These were recorded rather than weakening those tests.

Current actual-site dimensions, structure, products and technical reviews remain outside what synthetic fixtures can establish. The scope does not claim that a whole apartment's drawing set has been generated.
