from typing_extensions import assert_never

from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter
from omnipy.data._display.text.pretty_printer.compact_json import CompactJsonPrettyPrinter
from omnipy.data._display.text.pretty_printer.devtools import DevtoolsPrettyPrinter
from omnipy.data._display.text.pretty_printer.rich import RichPrettyPrinter
from omnipy.data._display.text.pretty_printer.text import PlainTextPrettyPrinter
from omnipy.shared.enums.display import PrettyPrinterLib, SyntaxLanguage


def get_pretty_printer_from_config_value(
        pretty_printer: PrettyPrinterLib.Literals) -> PrettyPrinter | None:
    match pretty_printer:
        case PrettyPrinterLib.COMPACT_JSON:
            return CompactJsonPrettyPrinter()
        case PrettyPrinterLib.DEVTOOLS:
            return DevtoolsPrettyPrinter()
        case PrettyPrinterLib.RICH:
            return RichPrettyPrinter()
        case PrettyPrinterLib.TEXT:
            return PlainTextPrettyPrinter()
        case PrettyPrinterLib.AUTO:
            return None


def get_pretty_printer_from_content(draft_panel: DraftPanel) -> PrettyPrinter | None:
    for pretty_printer in [
            CompactJsonPrettyPrinter(),
            PlainTextPrettyPrinter(),
            RichPrettyPrinter(),
            DevtoolsPrettyPrinter(),
    ]:
        if pretty_printer.is_suitable_content(draft_panel):
            return pretty_printer


def get_pretty_printer_from_language(language: SyntaxLanguage.Literals | str) -> PrettyPrinter:

    if SyntaxLanguage.is_syntax_language(language):
        match language:
            case _lang if SyntaxLanguage.is_json_language(_lang):
                return CompactJsonPrettyPrinter()
            case _lang if SyntaxLanguage.is_text_language(_lang):
                return PlainTextPrettyPrinter()
            case _lang if SyntaxLanguage.is_python_language(_lang):
                return RichPrettyPrinter()
            case _ as never:
                assert_never(never)  # pyright: ignore [reportArgumentType]

    # Other language from pygments, not explicitly supported by Omnipy
    return PlainTextPrettyPrinter()
