from typing_extensions import override

from omnipy import SyntaxLanguageSpec
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.enums.display import PrettyPrinterLib


class PlainTextPrettyPrinter(PrettyPrinter[str]):
    @override
    @classmethod
    def get_pretty_printer_lib(cls) -> PrettyPrinterLib.Literals:
        return PrettyPrinterLib.TEXT

    @override
    @classmethod
    def is_suitable_content(
        cls,
        draft_panel: DraftPanel[object, AnyFrame],
        default: bool = False,
    ) -> bool:
        from omnipy.components.raw.models import StrModel

        content = draft_panel.content

        if default:
            if is_model_instance(content):
                return content.outer_type() is str
        else:
            if is_model_instance(content):
                return isinstance(content, StrModel)

        return False

    @override
    @classmethod
    def get_default_syntax_language(cls) -> SyntaxLanguageSpec.Literals:
        # By default, we use TEXT syntax to avoid incorrect highlighting
        # or non-Python string content, such as Markdown, being
        # highlighted as Python code. For plain str content, such as e.g.
        # in Dataset.list() output, CodePrettyPrinter is automatically
        # selected, which by default uses SyntaxLanguageSpec.PYTHON instead.
        return SyntaxLanguageSpec.TEXT

    @override
    def format_prepared_draft(
        self,
        draft_panel: DraftPanel[str, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        return ReflowedTextDraftPanel.create_from_draft_panel(draft_panel)

    @override
    @classmethod
    def _get_content_for_draft_panel(cls, draft_panel: DraftPanel[object, AnyFrame]) -> str:
        if is_model_instance(draft_panel.content):
            raw_content = draft_panel.content.content
        else:
            raw_content = draft_panel.content

        if not isinstance(raw_content, str):
            raw_content = repr(raw_content)

        return raw_content


class CodePrettyPrinter(PlainTextPrettyPrinter):
    @override
    @classmethod
    def get_pretty_printer_lib(cls) -> PrettyPrinterLib.Literals:
        return PrettyPrinterLib.CODE

    @override
    @classmethod
    def is_suitable_content(
        cls,
        draft_panel: DraftPanel[object, AnyFrame],
        default: bool = False,
    ) -> bool:
        # To allow plain str content, such as e.g. in Dataset.list() output,
        # to be automatically highlighted as Python code.
        if default and isinstance(draft_panel.content, str):
            return True

        return False

    @override
    @classmethod
    def get_default_syntax_language(cls) -> SyntaxLanguageSpec.Literals:
        # Python syntax is provided as default. This is among others used
        # to support highlighting of numbers, types etc. in tables and
        # elsewhere, such as Dataset.list() output. For str-based Models,
        # PlainTextPrettyPrinter is automatically selected, which uses
        # SyntaxLanguageSpec.TEXT instead.
        return SyntaxLanguageSpec.PYTHON
