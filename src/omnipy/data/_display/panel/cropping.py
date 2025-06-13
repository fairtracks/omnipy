import rich.console

from omnipy.data._display.config import HorizontalOverflowMode, OutputConfig, VerticalOverflowMode
from omnipy.data._display.dimensions import has_width
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.helpers import UnicodeCharWidthMap
from omnipy.data._display.panel.draft.monospaced import _calc_line_stats
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import extract_newline, strip_and_split_newline


def rich_overflow_method(
        horizontal_overflow_mode: HorizontalOverflowMode) -> rich.console.OverflowMethod | None:
    match horizontal_overflow_mode:
        case HorizontalOverflowMode.ELLIPSIS:
            return 'ellipsis'
        case HorizontalOverflowMode.CROP:
            return 'crop'
        case HorizontalOverflowMode.WORD_WRAP:
            return None


def crop_content_lines_vertically_for_resizing(
    content_lines: list[str],
    frame: AnyFrame,
    vertical_overflow_mode: VerticalOverflowMode,
) -> list[str]:
    # If both frame dimensions are specified, the frame height is less
    # than the number of lines, and the frame width is defined as flexible
    # (fixed_width=False), then we need to crop the content to fit the frame
    # so that the width of the panel can be reduced to fit only what is in
    # the frame. Otherwise (and the default) is that the panel is wide
    # enough to support the maximum width over all lines, also those out of
    # frame.
    #
    # TODO: Add support for scrolling of text content, not just
    #       cropping from bottom

    if has_width(frame.dims) and frame.dims.width == 0 or frame.fixed_width is True:
        return content_lines

    return crop_content_lines_vertically(
        content_lines,
        frame.dims.height,
        vertical_overflow_mode,
    )


def crop_content_lines_vertically(
        content_lines: list[str],
        frame_height: pyd.NonNegativeInt | None,
        vertical_overflow_mode: VerticalOverflowMode,  # linesep: str | None,
) -> list[str]:
    if frame_height is None or len(content_lines) <= frame_height:
        return content_lines

    if frame_height == 0:
        return []

    match vertical_overflow_mode:
        case VerticalOverflowMode.CROP_BOTTOM:
            return content_lines[:frame_height]
        case VerticalOverflowMode.CROP_TOP:
            return content_lines[-frame_height:]
        case VerticalOverflowMode.ELLIPSIS_BOTTOM:
            uncropped_lines = content_lines[:frame_height - 1]
            first_cropped_line = content_lines[frame_height - 1]
            newline = extract_newline(first_cropped_line)
            return uncropped_lines + ['…' + newline]
        case VerticalOverflowMode.ELLIPSIS_TOP:
            uncropped_lines = content_lines[-frame_height + 1:]
            first_cropped_line = content_lines[-frame_height + 1]
            newline = extract_newline(first_cropped_line)
            return ['…' + newline] + uncropped_lines
        case _:
            raise ValueError(f'Unknown vertical overflow mode: {vertical_overflow_mode}')


def crop_content_line_horizontally(
    content_line: str,
    frame_width: pyd.NonNegativeInt | None,
    horizontal_overflow_mode: HorizontalOverflowMode,
) -> str:
    if frame_width is None or len(content_line) <= frame_width:
        return content_line

    match horizontal_overflow_mode:
        case HorizontalOverflowMode.ELLIPSIS:
            if frame_width > 1:
                return content_line[:frame_width - 1] + '…'
            else:
                return '…'
        case HorizontalOverflowMode.CROP:
            return content_line[:frame_width]
        case HorizontalOverflowMode.WORD_WRAP:
            return content_line
        case _:
            raise ValueError(f'Unknown horizontal overflow mode: {horizontal_overflow_mode}')


def crop_content_with_extra_wide_chars(
    all_content_lines: list[str],
    frame: AnyFrame,
    config: OutputConfig,
    char_width_map: UnicodeCharWidthMap,
) -> list[str]:
    if has_width(frame.dims) \
            and frame.fixed_width is False \
            and frame.dims.width > 0:

        ellipsis_if_overflow = config.horizontal_overflow_mode == HorizontalOverflowMode.ELLIPSIS

        for i, (line, newline) in enumerate(strip_and_split_newline(_) for _ in all_content_lines):

            stats = _calc_line_stats(
                line,
                config.tab_size,
                char_width_map,
                width_limit=frame.dims.width,
            )

            cropped_line = line[:stats.char_count]

            if stats.overflow and ellipsis_if_overflow:
                if stats.line_width == frame.dims.width > 0:
                    # Exactly at the limit, must remove the last character
                    # to have space for the ellipsis
                    cropped_line = cropped_line[:-1]
                cropped_line += '…'

            cropped_line = cropped_line.rstrip('\t')

            all_content_lines[i] = cropped_line + newline

    return all_content_lines
