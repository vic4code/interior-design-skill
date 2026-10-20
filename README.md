# Interior Design Skill

**Turn the space you imagine into an editable model, a convincing visual study and drawings your designer or builder can work through.**

English · [繁體中文](README.zh-TW.md)

A portable Agent Skill for **Codex, Claude Code, Cursor and GitHub Copilot**. Bring plans, references and product links; work through layout, materials, furniture, lighting and technical details with Blender and a browser frontend. The core runs locally without a required paid generation API.

## Four styles, actual Blender output

The same original fictional living/work room, developed through four distinct furniture and material languages. These are **model-derived Blender renders**, with editable scene generation, GLB exports, cameras and source hashes.

| Mid-century Modern | Japandi |
| --- | --- |
| [![MCM — timber frames, olive upholstery and warm selected objects](docs/showcase/mcm/hero-preview.jpg)](docs/showcase/mcm/hero.jpg) | [![Japandi — low oak forms, natural textile and quiet light](docs/showcase/japandi/hero-preview.jpg)](docs/showcase/japandi/hero.jpg) |
| Exposed timber, tapered legs, olive and rust, composed vintage character. | Low platforms, pale oak, linen, mineral surfaces and soft light. |
| **Contemporary** | **Bauhaus** |
| [![Contemporary — rounded forms, stone and layered neutrals](docs/showcase/contemporary/hero-preview.jpg)](docs/showcase/contemporary/hero.jpg) | [![Bauhaus — tubular chrome, crisp cushions and geometric accents](docs/showcase/bauhaus/hero-preview.jpg)](docs/showcase/bauhaus/hero.jpg) |
| Rounded upholstery, monolithic surfaces and restrained contrast. | Chrome, black upholstery and disciplined primary-color accents. |

Click a preview for the full image. The studies use original procedural furniture, materials and artwork. See [style decisions, references and reproduction](skills/interior-design/references/style-studies.md). [Lo-Fi House](https://lofi-house.com/cases/) and [Dan Retro](https://www.danretro.com/products) informed the reference/selection workflow; their case photographs and commercial models are not bundled.

## What a drawing delivery looks like

A coordinated **eight-sheet A3 set** from the same room and cabinetry dimensions: setting-out, openings, lighting/power proposals, interior elevations, cabinet arrangements, sections, finish schedules and an issue register.

| Dimensioned layout · A101 | Cabinet arrangement · J301 |
| --- | --- |
| [![Detailed plan with dimension chains, door swing, furniture IDs and cabinet setting-out](docs/showcase/drawings/A101.svg)](docs/showcase/drawings/A101.svg) | [![Cabinet front, plan and side views with panel and opening dimensions](docs/showcase/drawings/J301.svg)](docs/showcase/drawings/J301.svg) |
| **Cabinet section & interfaces · J401** | **Lighting & power proposals · A102** |
| [![Section and construction interfaces with panel thickness, clear dimensions, shelf levels and fixing questions](docs/showcase/drawings/J401.svg)](docs/showcase/drawings/J401.svg) | [![Ceiling and power coordination plan with fixture IDs, mounting heights and legends](docs/showcase/drawings/A102.svg)](docs/showcase/drawings/A102.svg) |

**Download:** [Complete A3 PDF](docs/showcase/drawings/design-coordination.pdf) · [Full delivery ZIP](docs/showcase/design-development-S01.zip) · [Plan DXF](docs/showcase/drawings/plan.dxf) · [Joinery dimensions](docs/showcase/drawings/joinery.csv) · [Furniture schedule](docs/showcase/drawings/furniture.csv) · [Open decisions](docs/showcase/drawings/issues.csv).

These are actual generated sheets, not decorative mockups. The cabinet's width, depth, panel thicknesses, shelf levels and internal clear sizes close against the shared source. Site measurements, material samples, selected hardware and fixing conditions determine the real project's construction release status. The fictional sample explicitly records those assumptions and interfaces.

## Install for your agent

```bash
npx skills add vic4code/interior-design-skill --skill interior-design
```

Or, from a checkout, use the local installer:

```bash
python3 skills/interior-design/scripts/install_skill.py --agent codex --user
python3 skills/interior-design/scripts/install_skill.py --agent claude-code --user
```

Use `--project /path/to/project` instead of `--user` for a project installation. Existing installations are never overwritten.

| Agent | Project skill folder | Start with |
| --- | --- | --- |
| Codex | `.agents/skills/interior-design` | `$interior-design` |
| Claude Code | `.claude/skills/interior-design` | `/interior-design` |
| Cursor | `.cursor/skills/interior-design` | Ask the agent to use the skill |
| GitHub Copilot | `.github/skills/interior-design` | Ask the agent to use the skill |

The complete folder contains its scripts, dependency locks, example data, schema and viewer. [Compatibility and actual verification](docs/agent-compatibility.md).

> Use the interior-design skill. Help me develop this plan and these references into a MCM living room, an editable Blender scene and a detailed drawing package. Check furniture use, cabinet internal dimensions and installation interfaces. Show the actual files and the questions that still need site or product confirmation.

## Get your first drawing package

Python 3.11+ is required. The optional browser frontend needs Node.js 20.19+ or 22.12+; editable 3D and offline renders need Blender 4.3+ on PATH. From the installed skill directory, or a checkout:

```bash
git clone https://github.com/vic4code/interior-design-skill.git
cd interior-design-skill/skills/interior-design
bash scripts/setup.sh
.venv/bin/python scripts/build_drawing_studies.py --out output/my-first-drawing-set
```

Open `output/my-first-drawing-set/design-coordination.pdf`. It contains the eight sheets shown above. For the native MCM scene and images:

```bash
blender --background --threads 4 --python-exit-code 1 --python scripts/render_style_studies.py -- --style mcm --out output/mcm-study
```

Choose `japandi`, `contemporary`, `bauhaus` or `all` for other studies. CPU is the portable default; the renderer exposes an optional device selection. See its `--help` and [workflow reference](skills/interior-design/references/style-studies.md).

Windows: create `.venv` with `py -m venv .venv`, install using `.venv\Scripts\python -m pip install -r scripts/requirements.lock.txt`, and substitute `.venv\Scripts\python` in the commands. Install frontend dependencies with `npm --prefix assets/viewer ci --ignore-scripts`.

## Design real spaces

The skill is not limited to the small rectangular-room starter. Use project-specific Blender geometry and data for multiple rooms, irregular walls, rotated furniture, detailed assemblies and daily operations. Inspect the actual plan/model, preserve stable IDs and derive drawings from the same revision. [Advanced spaces](skills/interior-design/references/advanced-spaces.md) explains that route.

The included `project.py` remains a small reproducible quick-start generator with its own schema limits. Those limits do not define the skill's design scope. Its [format reference](skills/interior-design/references/project-format.md) documents them. Photos alone cannot establish reliable dimensions; the agent needs calibrated plans, measurements and product evidence.

A professional drawing workflow develops overall and chained dimensions, elevations, sections, component sizes, finish/hardware schedules and trade interfaces. Read [construction documents](skills/interior-design/references/construction-documents.md). Selected products should come from opened manufacturer sources; distinguish exact models from measured approximations.

## Browser review and verification

For the quick-start browser review, from the skill folder:

```bash
.venv/bin/python scripts/project.py build assets/example-project.json --out assets/viewer/public/generated --blender
npm --prefix assets/viewer run dev
```
To review the detailed MCM study instead, build a matching drawing set and combine it with the rendered study:

```bash
.venv/bin/python scripts/build_drawing_studies.py --out output/drawing-study
.venv/bin/python scripts/build_style_review.py --study output/mcm-study --drawings output/drawing-study --out assets/viewer/public/generated
```


It supports render/plan/GLB inspection and downloads. Drag editing, automatic scene-state recovery and complete MEP design are separate extensions, not hidden features. Keep private projects local and preserve model-faithful renders if you optionally generate AI appearance simulations.

Repository checks:

```bash
skills/interior-design/.venv/bin/python -m unittest discover -s tests -v
npm --prefix skills/interior-design/assets/viewer run build
```

The skill follows the [Anthropic skill-creator structure](https://github.com/anthropics/skills/tree/main/skills/skill-creator): focused `SKILL.md`, progressively loaded references, executable scripts and reusable assets. See [verification](docs/verification.md), [research and attribution](docs/research.md), [roadmap](docs/implementation-roadmap.md) and [contributing](CONTRIBUTING.md).

Original code and synthetic assets use [MIT](LICENSE). Third-party product models and images need their own documented permissions. Your agent/LLM may have separate costs; the local core does not require a paid image API.
