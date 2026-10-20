# Agent compatibility

Interior Design is one portable [Agent Skills](https://agentskills.io/specification) folder: `skills/interior-design/SKILL.md`, with its scripts, references and assets alongside it. The same workflow supports Codex, Claude Code, Cursor and GitHub Copilot. It does not require host-specific tool names, model providers or permission overrides. `agents/openai.yaml` provides optional Codex UI metadata.

## Install for your agent

From a checkout of this repository, choose an existing project directory and run **one** command:

```bash
python3 skills/interior-design/scripts/install_skill.py --agent codex --project /path/to/project
python3 skills/interior-design/scripts/install_skill.py --agent claude-code --project /path/to/project
python3 skills/interior-design/scripts/install_skill.py --agent cursor --project /path/to/project
python3 skills/interior-design/scripts/install_skill.py --agent copilot --project /path/to/project
```

For personal installation across projects, replace `--project /path/to/project` with `--user`. Use `--list` to show destinations. Python 3 is needed for this copy helper; no Python packages are needed just to install the skill.

| Agent | Project destination | Personal destination | Start using it |
| --- | --- | --- | --- |
| Codex | `.agents/skills/interior-design` | `~/.agents/skills/interior-design` | Select `$interior-design` or ask for an interior design task |
| Claude Code | `.claude/skills/interior-design` | `~/.claude/skills/interior-design` | Invoke `/interior-design` |
| Cursor | `.cursor/skills/interior-design` | `~/.cursor/skills/interior-design` | Ask Agent to use the `interior-design` skill |
| GitHub Copilot | `.github/skills/interior-design` | `~/.copilot/skills/interior-design` | Ask the agent to use the `interior-design` skill |

Paths follow the official [Codex](https://developers.openai.com/codex/skills/), [Claude Code](https://code.claude.com/docs/en/skills), [Cursor](https://cursor.com/docs/skills) and [GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) documentation, checked 2026-10-20. Restart or reload the host if its skill list does not refresh. For cloud sessions, commit a project installation or follow the host's remote skill distribution instructions; a personal installation stays on the local machine.

The helper copies the complete source folder and refuses existing installations and symbolic-link destinations. Source symlinks, dependency folders, caches, generated output and `.env` files are skipped. It does not run the skill, install dependencies or change agent settings. To update an existing installation, review and replace it yourself; the helper has no overwrite mode. You can also copy the complete folder manually into your host's documented skill directory.

## What has been verified

| Check | Result |
| --- | --- |
| Standard `SKILL.md` layout and documented host paths | Checked against the official sources linked above |
| Installation in project and personal directories for all four hosts | Tested in temporary directories; SKILL.md, license, scripts, references, schema/example and viewer resources retained |
| Existing files, symbolic-link destinations, source links, private runtime artifacts | Installer safety tests passed |
| Installed helper executed independently of the repository working directory | Passed for all four host layouts |
| Live Codex CLI session using the personal installation | Passed: read installed skill, generated eight sheets and checked all 17 output hashes plus four source hashes |
| Live Claude Code session | Installed; session test blocked by local OAuth authentication failure before model execution. Not claimed as a passed generation test |
| Live Cursor and Copilot sessions | Not evaluated; file-installation checks do not establish model behavior |

To repeat the installation checks from the repository root:

```bash
python3 -m unittest discover -s tests -p test_install_skill.py -v
```

The installed skill includes its own setup instructions and runtime dependencies. Drawing generation needs Python packages, Blender rendering needs Blender, and the interactive viewer needs Node.js and a browser. Those tools run locally under the selected host's normal permissions. Hosts without file execution can help prepare a brief but cannot export these deliverables on their own. Web browsing and optional image tools use the capabilities available in the host; do not assume every host includes them.
