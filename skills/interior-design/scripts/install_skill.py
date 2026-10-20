#!/usr/bin/env python3
"""Copy this portable skill to an explicitly selected agent and installation scope."""
import argparse
import fnmatch
from pathlib import Path
import shutil
import sys

SKILL_NAME = "interior-design"
HOSTS = {
    "codex": (".agents/skills", ".agents/skills"),
    "claude-code": (".claude/skills", ".claude/skills"),
    "cursor": (".cursor/skills", ".cursor/skills"),
    "copilot": (".github/skills", ".copilot/skills"),
}
IGNORE = (
    ".git", ".venv", "venv", ".cache", ".pytest_cache", ".mypy_cache",
    "node_modules", "dist", "generated", "__pycache__", ".DS_Store",
    "*.pyc", "*.pyo", ".env", ".env.*",
)


def ignore_runtime(directory, names):
    """Do not redistribute runtime output, secrets or links outside the package."""
    return [name for name in names if
            (Path(directory) / name).is_symlink() or
            any(fnmatch.fnmatch(name, pattern) for pattern in IGNORE)]


def install(agent, *, project=None, user=False, source=None):
    """Return the new destination; never update an existing installation."""
    if (project is None) == (not user):
        raise ValueError("Choose exactly one scope: --project PATH or --user")
    source = Path(source or Path(__file__).resolve().parents[1]).resolve()
    if not (source / "SKILL.md").is_file():
        raise ValueError("Source must be the complete skill folder containing SKILL.md")
    base = Path.home() if user else Path(project).expanduser()
    if not base.is_dir():
        raise ValueError("Installation scope must be an existing directory")
    base = base.resolve()
    relative = HOSTS[agent][1 if user else 0]
    destination = base / relative / SKILL_NAME
    if destination == source or source in destination.parents:
        raise ValueError("Installation destination cannot be inside the source skill")
    current = base
    for part in Path(relative).parts + (SKILL_NAME,):
        current = current / part
        if current.is_symlink():
            raise FileExistsError(f"Refusing a symbolic-link destination: {current}")
    if destination.exists():
        raise FileExistsError(f"Installation already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=ignore_runtime)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=HOSTS)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--project", type=Path, metavar="PATH")
    scope.add_argument("--user", action="store_true", help="Install for the current user")
    parser.add_argument("--list", action="store_true", help="List supported destinations")
    args = parser.parse_args()
    if args.list:
        for host, (project, user) in HOSTS.items():
            print(f"{host}: project {project}/{SKILL_NAME}; user ~/{user}/{SKILL_NAME}")
        return 0
    if args.agent is None or (args.project is None and not args.user):
        parser.error("--agent and an explicit --project PATH or --user are required")
    try:
        destination = install(args.agent, project=args.project, user=args.user)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Installation failed: {error}\n")
    print(f"Installed {SKILL_NAME} for {args.agent}: {destination}")
    print("No dependencies installed or scripts executed. Open the project in your agent to use the skill.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
