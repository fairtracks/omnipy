"""Command line for the skills shipped with Omnipy: `python -m omnipy skills --help`."""

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

from omnipy.skills import install, skill_names, skill_path

PROJECT_SKILLS_DIR = Path('.agents/skills')
CLAUDE_SKILLS_DIR = Path('.claude/skills')


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == 'list':
        for name in skill_names():
            print(name)
        return 0

    if args.command == 'path':
        print(skill_path(args.name))
        return 0

    return _install(args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='python -m omnipy skills',
        description='The agent skills shipped with Omnipy.',
    )
    commands = parser.add_subparsers(dest='command', required=True)

    commands.add_parser('list', help='List the names of the skills.')

    path_command = commands.add_parser('path', help='Print the directory of a skill.')
    path_command.add_argument('name')

    install_command = commands.add_parser(
        'install',
        help='Install skills for the coding agents of a project.',
        description=(
            'Install the skills into the skills directory of the current project, by default '
            'as symlinks to the skills of the installed Omnipy, so that they follow Omnipy '
            'through upgrades. Into the home directory the skills are copied, as the home '
            'directory is not tied to one Python environment.'
        ),
    )
    install_command.add_argument(
        'names', nargs='*', metavar='name', help='Skills to install. By default, all of them.'
    )
    install_command.add_argument(
        '--claude',
        action='store_true',
        help=f'Install into {CLAUDE_SKILLS_DIR}, read by Claude Code, instead of '
        f'{PROJECT_SKILLS_DIR}, read by most other agents.',
    )
    install_command.add_argument(
        '--home',
        action='store_true',
        help='Install into the skills directory under the home directory, for every project.',
    )
    install_command.add_argument(
        '--dir', type=Path, help='Install into this directory instead (overrides the above).'
    )
    install_command.add_argument(
        '--mode',
        choices=['link', 'copy'],
        help='Link or copy the skills. The default is to copy under --home and to link elsewhere.',
    )
    install_command.add_argument(
        '--force', action='store_true', help='Replace skills already in the directory.'
    )
    return parser


def _install(args: argparse.Namespace) -> int:
    target_dir = _target_dir(args)
    copy = args.mode == 'copy' if args.mode else args.home

    try:
        for name in args.names or skill_names():
            installed = install(name, target_dir, copy=copy, force=args.force)
            how = 'linked' if installed.linked else 'copied'
            print(f'{how} {name} -> {installed.path}')
            if not copy and not installed.linked:
                print(f'  (symlinks are not supported here, so {name} was copied)')
    except FileExistsError as exc:
        print(f'error: {exc} (use --force to replace it)', file=sys.stderr)
        return 1
    except LookupError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    return 0


def _target_dir(args: argparse.Namespace) -> Path:
    if args.dir:
        return args.dir
    skills_dir = CLAUDE_SKILLS_DIR if args.claude else PROJECT_SKILLS_DIR
    return Path.home() / skills_dir if args.home else skills_dir
