# Agent compatibility

One canonical Agent Skills folder is shared by all hosts. No Codex-specific tool names, Claude-only shell interpolation, forced permissions or hard-coded model/provider are required. `agents/openai.yaml` is optional UI metadata; the workflow remains in standard SKILL.md.

| Host | Installation / invocation | Verification status |
| --- | --- | --- |
| Codex CLI / IDE | `.agents/skills/interior-design` in a project, or `~/.agents/skills/interior-design`; `$interior-design` | Official format/location checked; copy layout documented, no separate Codex session evaluation |
| Claude Code | `.claude/skills/interior-design` in a project, or `~/.claude/skills/interior-design`; `/interior-design` | Official format/location checked; copy layout documented, no separate Claude session evaluation |
| Other Agent Skills-compatible hosts | Copy the complete folder to the host's documented skill root or use a supported installer | Standard-format compatibility intended; individual hosts not end-to-end verified |
| Chat-only environments | Read instructions and prepare the brief; export files only if file execution is supported | Local Blender/browser execution depends on the host |

Install by copying the complete `skills/interior-design` folder into the chosen host directory, or use the skills CLI described in README. The complete skill folder includes its executable scripts, schema, example and viewer; follow SKILL.md to locate the installed skill root and run setup there. No per-host installer is added by this documentation update.

Any execution-capable host can run Python and Blender. Web search and image tools depend on host capabilities. If a tool is absent, ask for the relevant source files or explain which operation cannot run. Blender MCP and image APIs are optional, not required for the local core.

Sources checked 2026-10-20: [Agent Skills specification](https://agentskills.io/specification), [Codex skills](https://developers.openai.com/codex/skills/), [Claude Code skills](https://code.claude.com/docs/en/skills).
