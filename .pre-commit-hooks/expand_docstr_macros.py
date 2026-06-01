#!/usr/bin/env python3
"""
Pre-commit hook to expand macros in docstrings.

Preserves macro references in comments immediately before docstrings.
Macros are defined via environment variables starting with 'OMNIPY_MACRO_'.

Authors:
    - Sveinung Gundersen (concept, requirements, review and refactoring)
    - GitHub Copilot w/ Claude Sonnet 4.5 (impl. assistance, January 2026)

Created: January 2026
"""

import importlib
from pathlib import Path
import sys
import traceback

from omnipy.util.docstr_macros import get_macros_from_env, process_content


def load_macros() -> dict[str, str]:
    """
    Load macros after importing omnipy to trigger macro env-var registration.

    Returns:
        Dict of macro definitions read from the process environment
    """
    importlib.import_module('omnipy')
    return get_macros_from_env()


def process_file(filepath: Path, macros: dict[str, str], verbose: bool = False) -> bool:
    """
    Process a file, expanding macros in docstrings.

    Args:
        filepath: Path to the Python file to process
        macros: Dict of macro definitions
        verbose: Whether to print verbose output

    Returns:
        True if file was modified
    """
    if verbose:
        print(f'\nProcessing {filepath}:')

    content = filepath.read_text()
    new_content, modified = process_content(content, macros, verbose=verbose)

    if modified:
        filepath.write_text(new_content)
        print(f'Expanded macros in {filepath}')

    return modified


def main():
    """Main entry point."""
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    files = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

    if not files:
        print('Usage: expand_docstr_macros.py [--verbose] <file1.py> <file2.py> ...')
        sys.exit(0)

    # Load macros from environment variables
    macros = load_macros()

    if verbose:
        print(f'Loaded {len(macros)} macros from environment variables:')
        for macro_name in sorted(macros.keys()):
            print(f'  {macro_name}')

    if not macros:
        print('Warning: No macros defined. Set environment variables like OMNIPY_MACRO_NAME=value')
        sys.exit(0)

    modified_any = False

    for filepath_str in files:
        filepath = Path(filepath_str)
        if filepath.suffix == '.py':
            try:
                if process_file(filepath, macros, verbose=verbose):
                    modified_any = True
            except Exception as e:
                print(f'Error processing {filepath}: {e}')
                traceback.print_exc()
                sys.exit(1)

    sys.exit(1 if modified_any else 0)


if __name__ == '__main__':
    main()
