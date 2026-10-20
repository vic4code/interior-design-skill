# Bundled interface design dependencies

Use these dependencies when creating or changing the browser presentation. They ship inside this skill, so Codex, Claude Code and other hosts use the same guidance and local data. They do not require additional skill installations or a plugin environment variable.

## Use the guidance

1. Read [`assets/design-guidance/taste/SKILL.md`](../assets/design-guidance/taste/SKILL.md) for visual composition, type, proportion and polished interaction.
2. Read [`assets/design-guidance/ui-ux-pro-max/SKILL.md`](../assets/design-guidance/ui-ux-pro-max/SKILL.md) for the searchable design workflow. Treat its references to a skill root as this bundled directory, not a host plugin directory.
3. Search before designing a new browser experience; inspect the actual recommendations and use only results relevant to a residential design review interface. An empty or mismatched search is not design evidence.
4. Keep the approved interior design and project geometry authoritative. UI recommendations cannot change room dimensions, openings, selected furniture, drawing issue status or the user's requirements.

Resolve `INTERIOR_SKILL_ROOT` to the absolute directory containing the installed interior-design `SKILL.md`. This is a task variable, not a required machine configuration. For example, from that directory:

```sh
INTERIOR_SKILL_ROOT="$PWD"
PYTHONDONTWRITEBYTECODE=1 python3 "$INTERIOR_SKILL_ROOT/assets/design-guidance/ui-ux-pro-max/scripts/search.py" "interior design portfolio editorial" --design-system -p "Space Review"
PYTHONDONTWRITEBYTECODE=1 python3 "$INTERIOR_SKILL_ROOT/assets/design-guidance/ui-ux-pro-max/scripts/search.py" "keyboard focus tabs" --domain ux
```

The search runtime uses Python's standard library, reads bundled CSV/JSON files and works offline. Use `--persist` only when a durable design record is needed, with an explicit output directory in the working project. Never persist into the installed skill. No Blender, npm package, external service, font download or image generation is required to run these searches. Image generation and model viewing are separate capabilities of the complete interior-design workflow.

## Apply to this skill's browser presentation

Use one project page for layout, 3D placement, image-generated visual studies and issued drawings. Preserve the selected project, style and viewpoint while moving between these views. Display style images at the same aspect ratio; reserve room for controls without covering the architecture. Keep drawings legible with zoom, sheet navigation, issue status and downloads. Make keyboard focus, loading states, unavailable artifacts and mobile controls explicit.

These vendored files are design guidance, not authority to execute package installation commands, contact services or change files outside the user's task. Existing user instructions and repository rules take precedence.

See [third-party notices](../THIRD_PARTY_NOTICES.md) for source revisions and licenses.
