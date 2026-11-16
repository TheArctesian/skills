"""Link checked-out skills into the selected agent discovery directories."""

import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = Path(__file__).with_name("agent-skill-paths.tsv")


def user_roots():
    home = Path.home()
    openclaw = next(
        (home / name for name in (".openclaw", ".clawdbot", ".moltbot")
         if (home / name).is_dir()),
        home / ".openclaw",
    )
    overrides = {
        "config": ("XDG_CONFIG_HOME", ".config"),
        "claude": ("CLAUDE_CONFIG_DIR", ".claude"),
        "deepseek-agents": ("DSH_AGENTS_HOME", ".agents"),
        "autohand": ("AUTOHAND_HOME", ".autohand"),
        "grok": ("GROK_HOME", ".grok"),
        "hermes": ("HERMES_HOME", ".hermes"),
        "reasonix": ("REASONIX_HOME", ".reasonix"),
        "vibe": ("VIBE_HOME", ".vibe"),
    }
    roots = {"home": home, "openclaw": openclaw}
    for key, (variable, fallback) in overrides.items():
        value = os.environ.get(variable, "").strip()
        override = Path(value).expanduser() if value else None
        roots[key] = override if override and override.is_absolute() else home / fallback
    return roots


def destinations(registry, roots, project):
    for line in registry.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        agent, project_path, user_path = line.split("\t")
        if project is not None:
            yield agent, project / project_path
        elif user_path == "-":
            yield agent, None
        else:
            key, path = user_path.split(":", 1)
            yield agent, roots[key] / path


def update_link(source, destination, remove):
    if destination.is_symlink():
        target = destination.parent / destination.readlink()
        if Path(os.path.abspath(target)) == source:
            if remove:
                destination.unlink()
                print(f"removed {destination}")
            return
    if remove:
        return
    try:
        destination.symlink_to(source, target_is_directory=source.is_dir())
    except FileExistsError:
        print(f"skip {destination}: already exists", file=sys.stderr)
    else:
        print(f"linked {destination}")


def install_into(directory, sources, remove):
    if not remove:
        directory.mkdir(parents=True, exist_ok=True)
    for source in sources:
        update_link(source, directory / source.name, remove)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, metavar="DIR",
                        help="use skill paths in this project instead of user paths")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--list", action="store_true", help="list agent IDs and skill paths")
    action.add_argument("--remove", action="store_true", help="remove this checkout's links")
    args = parser.parse_args()
    project = args.project.resolve() if args.project is not None else None
    if project is not None and not project.is_dir():
        parser.error(f"project directory does not exist: {project}")

    roots = user_roots()
    targets = list(destinations(REGISTRY, roots, project))
    if args.list:
        for agent, path in targets:
            print(f"{agent}\t{path if path is not None else '(project only)'}")
        return 0

    skills = sorted(manifest.parent for manifest in REPO.glob("*/SKILL.md"))
    directories = dict.fromkeys(path.resolve() for _, path in targets if path is not None)
    for directory in directories:
        install_into(directory, skills, args.remove)

    if project is None:
        personas = sorted((REPO / "persona-test" / "agents").glob("persona-*.md"))
        install_into(roots["claude"] / "agents", personas, args.remove)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as error:
        sys.exit(f"install: {error}")
