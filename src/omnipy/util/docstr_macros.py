"""
Docstring macro expansion utilities.

This module provides functionality to expand macros in Python docstrings while preserving
the original docstring (with unexpanded macros) in comment blocks above the docstring.

Authors:
    - Sveinung Gundersen (concept, requirements, review and refactoring)
    - GitHub Copilot w/ Claude Sonnet 4.5 (impl. assistance, January 2026)

Created: January 2026
"""

import re

# Constants
ORIGINAL_DOCSTRING_PREFIX =\
    '%% Original docstring with macros (managed by expand_docstring_macros.py) %%'
ENV_MACRO_PREFIX = 'OMNIPY_MACRO_'


def get_macros_from_env() -> dict[str, str]:
    """
    Load macro definitions from environment variables.

    Environment variables starting with 'OMNIPY_MACRO_' are treated as macro definitions.
    For example:

    ```bash
    OMNIPY_MACRO_COMMON_PARAM='Parameters:\n  param1: desc'
    ```

    defines the macro COMMON_PARAM.

    Returns:
        Dict mapping macro names (with {{...}} delimiters) to their expansion values
    """
    import os
    macros = {}

    for key, value in os.environ.items():
        if key.startswith(ENV_MACRO_PREFIX):
            # Extract macro name from env var name
            # OMNIPY_MACRO_COMMON_PARAM -> COMMON_PARAM
            macro_name = key[len(ENV_MACRO_PREFIX):]
            macros[macro_name] = value

    return macros


def find_macros_in_docstring(docstring: str, macros: dict[str, str]) -> set[str]:
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
        result = result.replace(f'{{{{{macro_name}}}}}', macro_value)
    return result


def _extract_original_docstring_from_comment_block(
    comment_block: str,
    verbose: bool = False,
) -> str:
    """Extract the original unexpanded docstring from comment block."""
    original_lines = []
    for line in comment_block.split('\n'):
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith(f'# {ORIGINAL_DOCSTRING_PREFIX}'):
            original_lines.append(stripped[2:])  # Remove '# ' prefix

    original_docstring = '\n'.join(original_lines)

    if verbose:
        print('  Extracting original docstring from comment block')

    return original_docstring


def _create_docblock_with_expansion(
    matched_docblock: str,
    original_docstring: str,
    indent: str,
    quote: str,
    macros: dict[str, str],
    verbose: bool = False,
) -> tuple[str, bool]:
    """
    Create a new docblock (comment block + docstring) with macros expanded.

    Args:
        matched_docblock: The entire matched text (may include existing comments)
        indent: Indentation string
        original_docstring: The unexpanded docstring text (with macros)
        quote: Quote style (single or double triple quotes)
        macros: Macro definitions
        verbose: Whether to print verbose output

    Returns:
        Tuple of (new_docblock, was_modified)
    """
    # Check if original has macros
    macros_found = find_macros_in_docstring(original_docstring, macros)

    if not macros_found:
        return matched_docblock, False  # No macros, keep as is

    # Expand macros
    expanded_docstring = expand_macros(original_docstring, macros)

    # Check if expansion changed
    if expanded_docstring == original_docstring:
        return matched_docblock, False  # No change needed

    # Build comment block with original docstring (unexpanded)
    comment_block = f'{indent}# {ORIGINAL_DOCSTRING_PREFIX}\n'
    for line in original_docstring.split('\n'):
        comment_block += f'{indent}# {line}\n'

    # Build complete docblock: comment + expanded docstring
    new_docblock = f'{comment_block}{indent}{quote}{expanded_docstring}{quote}'

    if verbose:
        print('  Expanding docstring with macros')

    return new_docblock, True


def process_content(  # noqa: C901
        content: str, macros: dict[str, str], verbose: bool = False) -> tuple[str, bool]:
    """
    Process Python source code, expanding macros in docstrings.

    Preserves complete original docstrings (with unexpanded macros) in
    comment blocks immediately before the expanded docstring.

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
        ^([\ \t]*)                             # Capture indentation at start of line
        (
            \#\ {escaped_prefix}\n             # Marker line
            (?:\1\#\ .*\n)*                    # Multiple comment lines with original docstring
            \1                                 # Same indentation before actual docstring
        )?
        ("""|\'\'\')                           # Opening quotes
        (.*?)                                  # Docstring content (non-greedy)
        \3                                     # Closing quotes (same as opening quotes)
    '''

    modified = False

    def _replace_docblock(match: re.Match[str]) -> str:
        """
        Replace a full docblock (comment + docstring), expanding any macros
        found.
        """
        nonlocal modified

        matched_docblock = match.group(0)  # Entire match (may include comment block)
        indent = match.group(1)  # Indentation (assuming same indentation for entire block)
        comment_block: str | None = match.group(2)  # Comment block if present, else None
        quote = match.group(3)  # Quote style (triple single or double)
        docstring_content = match.group(4)  # Just the docstring content

        if comment_block is not None:
            # Extract the original (unexpanded) docstring from comments
            original_docstring = _extract_original_docstring_from_comment_block(comment_block)
        else:
            # First time - the docstring text is the original
            original_docstring = docstring_content

        new_docblock, was_modified = _create_docblock_with_expansion(
            matched_docblock,
            original_docstring,
            indent,
            quote,
            macros,
            verbose,
        )

        if was_modified:
            modified = True

        return new_docblock

    # Apply the replacement
    new_content = re.sub(
        pattern, _replace_docblock, content, flags=re.VERBOSE | re.DOTALL | re.MULTILINE)

    return new_content, modified
