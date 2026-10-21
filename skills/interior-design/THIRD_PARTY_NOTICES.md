# Third-party dependencies

The interior-design skill includes these dependencies inside its own installable folder. Installing separate host-level skills is unnecessary. Their licenses apply to their respective files; the repository MIT license does not replace them.

| Dependency | Pinned upstream source | License | Bundled location |
| --- | --- | --- | --- |
| Taste Skill | [leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill/tree/ccbc15639c97057cbfcf32ecebc38ef716e4bb37/skills/taste-skill), revision `ccbc15639c97057cbfcf32ecebc38ef716e4bb37` | MIT, Copyright (c) 2026 Leonxlnx | `assets/design-guidance/taste/` |
| UI/UX Pro Max | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/56ea9cf174ed86786187daa9de0e6247cb0747e4/.claude/skills/ui-ux-pro-max), revision `56ea9cf174ed86786187daa9de0e6247cb0747e4` | MIT, Copyright (c) 2024 Next Level Builder | `assets/design-guidance/ui-ux-pro-max/` |

Each dependency retains its complete upstream `LICENSE`. [Provenance](assets/design-guidance/provenance.json) records the upstream revision and SHA-256 hashes for the original and bundled files. Taste instructions are unchanged. UI/UX Pro Max command examples replace the host-specific plugin root with `INTERIOR_SKILL_ROOT`; one JavaFX bad-code example replaces an upstream home-directory path with a generic example path. Search implementation and all recommendations otherwise remain unchanged. The bundle intentionally excludes installers, host configuration, caches, tests and personal installation receipts.

UI/UX Pro Max contains font recommendations and license metadata; this bundle distributes no font binaries. Selecting a font, icon library, external image or UI package does not install or redistribute it. Confirm that asset’s own license before embedding it. Source links and credits in dependency instructions and data are retained.

The offline production viewer bundles Three.js 0.180.0 (MIT, Copyright © 2010–2025 three.js authors). Its complete license is retained in `assets/viewer/prebuilt/THREE-LICENSE.txt`; the frontend dependency versions are pinned in `assets/viewer/package-lock.json`. Vite is a build-time dependency and is not distributed as a runtime package.
