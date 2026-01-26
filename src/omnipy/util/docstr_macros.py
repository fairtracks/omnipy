"""
Docstring macro expansion utilities.

This module provides functionality to expand macros in Python docstrings while preserving
the original docstring (with unexpanded macros) in comment blocks above the docstring.
"""

import re
from typing import Set

# Constants
ORIGINAL_DOCSTRING_PREFIX = '%% Original docstring with macros (managed by copy_docstrings.py) %%'


def get_macros_from_env() -> dict[str, str]:
    """
    Load macro definitions from environment variables.

    Environment variables starting with 'OMNIPY_MACRO_' are treated as macro definitions.
    For example, OMNIPY_MACRO_COMMON_PARAM='Parameters:\n  param1: desc' defines
    the macro {{COMMON_PARAM}}.

    Returns:
        Dict mapping macro names (with {{...}} delimiters) to their expansion values
    """
    import os
    macros = {}

    for key, value in os.environ.items():
        if key.startswith('OMNIPY_MACRO_'):
            # Extract macro name from env var name
            # OMNIPY_MACRO_COMMON_PARAM -> COMMON_PARAM
            macro_name = key[len('OMNIPY_MACRO_'):]
            # Add delimiters
            macro_key = f'{{{{{macro_name}}}}}'
            macros[macro_key] = value

    return macros


def find_macros_in_docstring(docstring: str, macros: dict[str, str]) -> Set[str]:
    """Find all macro references in a docstring."""
    macros_found = set()
    for macro_name in macros.keys():
        if macro_name in docstring:
            macros_found.add(macro_name)
    return macros_found


def expand_macros(text: str, macros: dict[str, str]) -> str:
    """Expand all macros in text."""
    result = text
    for macro_name, macro_value in macros.items():
        result = result.replace(macro_name, macro_value)
    return result


def process_content(content: str,
                    macros: dict[str, str],
                    verbose: bool = False) -> tuple[str, bool]:
    """
    Process Python source code, expanding macros in docstrings.

    Preserves complete original docstrings (with unexpanded macros) in comment blocks
    immediately before the expanded docstring.

    Args:
        content: Python source code as a string
        macros: Dict mapping macro names to their expansion values
        verbose: Whether to print verbose output

    Returns:
        Tuple of (processed_content, was_modified)
    """
    if verbose:
        print(f'Processing content with {len(macros)} macros available')

    # Pattern to match docstrings with optional preceding ORIGINAL_DOCSTRING comment block
    # Build the pattern with the marker prefix escaped properly
    escaped_prefix = re.escape(ORIGINAL_DOCSTRING_PREFIX)
    pattern = rf'''
        ^([\ \t]*)                              # Capture indentation at start of line
        (?:
            \#\ {escaped_prefix}\n             # Marker line
            (?:\1\#\ .*\n)*                    # Multiple comment lines with original docstring
            \1                                 # Same indentation before actual docstring
        )?
        (                                      # Capture the quote style and docstring
            (?:r)?                             # Optional 'r' prefix
            ("""|\'\'\')                       # Opening quotes
            .*?                                # Docstring content (non-greedy)
            \3                                 # Closing quotes (same as opening quotes)
        )
    '''

    modified = False

    def replace_docstring(match):
        nonlocal modified
        indent = match.group(1)
        full_match = match.group(0)
        docstring_part = match.group(2)

        # Check if this already has an ORIGINAL_DOCSTRING marker
        has_marker = f'# {ORIGINAL_DOCSTRING_PREFIX}' in full_match

        # Extract the actual docstring content
        if '"""' in docstring_part:
            quote = '"""'
        else:
            quote = "'''"

        is_raw = docstring_part.startswith('r')
        if is_raw:
            start_idx = docstring_part.index(quote) + 3
        else:
            start_idx = len(quote)

        end_idx = docstring_part.rindex(quote)
        docstring_content = docstring_part[start_idx:end_idx]

        if has_marker:
            # Extract original docstring from comment
            original_lines = []
            for line in full_match.split('\n'):
                stripped = line.strip()
                if stripped.startswith(
                        '# ') and not stripped.startswith(f'# {ORIGINAL_DOCSTRING_PREFIX}'):
                    original_lines.append(stripped[2:])  # Remove '# ' prefix

            original_docstring = '\n'.join(original_lines)

            # Check if original has macros
            macros_found = find_macros_in_docstring(original_docstring, macros)

            if not macros_found:
                return match.group(0)  # No macros, keep as is

            # Re-expand from original
            expanded_content = expand_macros(original_docstring, macros)

            # Check if expansion changed
            if expanded_content == docstring_content:
                return match.group(0)  # No change needed

            # Build comment block with original
            comment_block = f'{indent}# {ORIGINAL_DOCSTRING_PREFIX}\n'
            for line in original_docstring.split('\n'):
                comment_block += f'{indent}# {line}\n'

            # Rebuild docstring
            prefix = 'r' if is_raw else ''
            new_docstring = f'{comment_block}{indent}{prefix}{quote}{expanded_content}{quote}'

            if verbose:
                print(f'  Re-expanding docstring with macros')

            modified = True
            return new_docstring
        else:
            # First time - check for macros
            macros_found = find_macros_in_docstring(docstring_content, macros)

            if not macros_found:
                return match.group(0)  # No macros, return unchanged

            # Store original docstring in comment block
            comment_block = f'{indent}# {ORIGINAL_DOCSTRING_PREFIX}\n'
            for line in docstring_content.split('\n'):
                comment_block += f'{indent}# {line}\n'

            # Expand macros
            expanded_content = expand_macros(docstring_content, macros)

            # Rebuild docstring
            prefix = 'r' if is_raw else ''
            new_docstring = f'{comment_block}{indent}{prefix}{quote}{expanded_content}{quote}'

            if verbose:
                print(f'  Expanding docstring with macros')

            modified = True
            return new_docstring

    # Apply the replacement
    new_content = re.sub(
        pattern, replace_docstring, content, flags=re.VERBOSE | re.DOTALL | re.MULTILINE)

    return new_content, modified
