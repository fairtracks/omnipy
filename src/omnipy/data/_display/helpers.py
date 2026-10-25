from rich.cells import get_character_cell_size


def char_cell_width(char: str) -> int:
    """Return the display cell width (0, 1 or 2) of a character used by panel layout.

    Widths are taken from rich, so that panel layout agrees with rich's rendering.
    """
    return get_character_cell_size(char)


def only_single_width_chars(line: str) -> bool:
    # All printable ASCII characters are one cell wide (tab is not printable)
    return line.isascii() and line.isprintable()


def soft_wrap_words(words: list[str], max_width: int) -> list[str]:
    """Wrap words into lines that don't exceed max_width.

    Distributes words across multiple lines ensuring that each line doesn't
    exceed the specified maximum width. Single words longer than max_width
    are not split and will appear on their own line.

    Args:
        words: List of words to be wrapped
        max_width: Maximum width (in characters) for each line

    Returns:
        List of strings, where each string is a wrapped line of text
    """
    lines: list[list[str]] = []
    current_line: list[str] = []
    current_width = 0

    for word in words:
        # Add word to current line
        space_width = 1 if current_line else 0
        current_width += len(word) + space_width
        current_line.append(word)

        # If line has more than one word and exceeds max_width,
        # move last word to new line
        if len(current_line) > 1 and current_width > max_width:
            lines.append(current_line[:-1])
            current_line = [word]
            current_width = len(word)

    # Add the final line
    if current_line:
        lines.append(current_line)

    # Add spaces and return
    return [' '.join(line) for line in lines]
