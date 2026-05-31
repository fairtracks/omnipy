"""Registry helpers that pick a pretty-printer from config, content, or syntax."""

from typing import Literal, overload

from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter
from omnipy.data._display.text.pretty_printer.bytes import HexdumpPrettyPrinter
from omnipy.data._display.text.pretty_printer.column import ColumnPrettyPrinter
from omnipy.data._display.text.pretty_printer.compact_json import CompactJsonPrettyPrinter
from omnipy.data._display.text.pretty_printer.devtools import DevtoolsPrettyPrinter
from omnipy.data._display.text.pretty_printer.rich import RichPrettyPrinter
from omnipy.data._display.text.pretty_printer.text import CodePrettyPrinter, PlainTextPrettyPrinter
from omnipy.shared.enums.display import PrettyPrinterLib, SyntaxLanguageSpec
from omnipy.shared.exceptions import ShouldNotOccurException


def get_pretty_printer_from_config_value(
        pretty_printer: PrettyPrinterLib.Literals) -> PrettyPrinter | None:
    """Return an explicit pretty-printer selected by configuration."""

    match pretty_printer:
        case PrettyPrinterLib.COMPACT_JSON:
            return CompactJsonPrettyPrinter()
        case PrettyPrinterLib.DEVTOOLS:
            return DevtoolsPrettyPrinter()
        case PrettyPrinterLib.RICH:
            return RichPrettyPrinter()
        case PrettyPrinterLib.COLUMN:
            return ColumnPrettyPrinter()
        case PrettyPrinterLib.TEXT:
            return PlainTextPrettyPrinter()
        case PrettyPrinterLib.CODE:
            return CodePrettyPrinter()
        case PrettyPrinterLib.HEXDUMP:
            return HexdumpPrettyPrinter()
        case PrettyPrinterLib.AUTO:
            return None


def get_debug_pretty_printer_if_debug_mode(debug_mode: bool) -> PrettyPrinter | None:
    """Return the debug pretty-printer when debug mode is enabled."""

    if debug_mode:
        return RichPrettyPrinter()
    else:
        return None


@overload
def get_pretty_printer_from_content(
    draft_panel: DraftPanel,
    default: Literal[False],
) -> PrettyPrinter | None:
    """Choose a content-based pretty-printer without requiring a fallback."""

    ...


@overload
def get_pretty_printer_from_content(
    draft_panel: DraftPanel,
    default: Literal[True],
) -> PrettyPrinter:
    """Choose a content-based pretty-printer and require a fallback match."""

    ...


def get_pretty_printer_from_content(draft_panel: DraftPanel, default: bool) -> PrettyPrinter | None:
    """Choose a pretty-printer based on the panel content type."""

    for pretty_printer in [
            CompactJsonPrettyPrinter(),
            ColumnPrettyPrinter(),
            HexdumpPrettyPrinter(),
            CodePrettyPrinter(),
            RichPrettyPrinter(),
            DevtoolsPrettyPrinter(),
            PlainTextPrettyPrinter(),
    ]:
        if pretty_printer.is_suitable_content(draft_panel, default=default):
            return pretty_printer

    if default:
        raise ShouldNotOccurException('No pretty printer found for content, even with '
                                      'default=True. This should not happen, as a default '
                                      'pretty printer should be defined for any content.')
    else:
        return None


def get_pretty_printer_from_syntax(
        syntax: SyntaxLanguageSpec.Literals | str) -> PrettyPrinter | None:
    """Choose a pretty-printer based on the requested syntax language."""

    # Note: Python syntax is explicitly not checked for here, as this
    # allows get_pretty_printer_from_content(default=True) to select
    # between CodePrettyPrinter (which displays strings without quotes)
    # and e.g. RichPrettyPrinter (which displays strings as objects, with
    # quotes) based on the type of content.
    match syntax:
        case _syntax if SyntaxLanguageSpec.is_json_syntax(_syntax):
            return CompactJsonPrettyPrinter()
        case _syntax if SyntaxLanguageSpec.is_text_syntax(_syntax):
            return PlainTextPrettyPrinter()
        case _syntax if SyntaxLanguageSpec.is_hexdump_syntax(_syntax):
            return HexdumpPrettyPrinter()
        case _:
            return None
