"""Command line for Omnipy: `python -m omnipy --help`."""

import argparse
from collections.abc import Sequence
import sys

COMMANDS = {
    'run': 'Run a job from a job bundle.',
    'skills': 'List and install the agent skills shipped with Omnipy.',
}


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch to the command given as the first argument.

    Args:
        argv: Command line arguments, by default those of the process.

    Returns:
        int: Exit code of the command.
    """
    parser = argparse.ArgumentParser(
        prog='python -m omnipy',
        description='Omnipy command line. See "python -m omnipy <command> --help".',
        epilog='\n'.join(f'{name}: {help_text}' for name, help_text in COMMANDS.items()),
    )
    parser.add_argument('command', choices=COMMANDS)
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments of the command.')
    args = parser.parse_args(argv)

    if args.command == 'skills':
        from omnipy.skills.cli import main as skills_main

        return skills_main(args.args)

    from omnipy.hub.job_bundle import main as run_main

    return run_main(args.args)


if __name__ == '__main__':
    sys.exit(main())
