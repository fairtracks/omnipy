"""Pretty printers for plain text and code-highlighted string content."""

from typing_extensions import override

from omnipy.components.raw.models import StrModel
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter
from omnipy.data.model import is_model_instance
from omnipy.shared.enums.display import PrettyPrinterLib, SyntaxLanguageSpec


class PlainTextPrettyPrinter(PrettyPrinter[str]):
    """Format string-like content as plain text.

    This printer favors text-safe defaults to avoid accidental syntax
    highlighting when content originates from generic string models.
    """
    @override
    @classmethod
    def get_pretty_printer_lib(cls) -> PrettyPrinterLib.Literals:
        """Return the enum value identifying this pretty-printer backend.

        Returns:
            ``PrettyPrinterLib.TEXT``.
        """
        return PrettyPrinterLib.TEXT

    @override
    @classmethod
    def is_suitable_content(
        cls,
        draft_panel: DraftPanel[object, AnyFrame],
        default: bool = False,
    ) -> bool:
        """Return whether the panel content should use plain-text formatting.

        Args:
            draft_panel: Draft panel whose content type is evaluated.
            default: Whether selection runs as default fallback logic.

        Returns:
            ``True`` if this printer is the best match for the content.
        """

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
        """Return the default syntax language used by this printer.

        Returns:
            ``SyntaxLanguageSpec.TEXT`` to avoid incorrect code highlighting.
        """
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
        """Wrap prepared text content in a reflowed draft panel.

        Args:
            draft_panel: Prepared draft panel containing string content.

        Returns:
            Reflowed text draft panel preserving frame, constraints, and config.
        """
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
    """Format generic string content as code-highlighted text.

    This printer primarily acts as a default for plain ``str`` content when a
    richer syntax-highlighted representation is preferred.
    """
    @override
    @classmethod
    def get_pretty_printer_lib(cls) -> PrettyPrinterLib.Literals:
        """Return the enum value identifying this pretty-printer backend.

        Returns:
            ``PrettyPrinterLib.CODE``.
        """
        return PrettyPrinterLib.CODE

    @override
    @classmethod
    def is_suitable_content(
        cls,
        draft_panel: DraftPanel[object, AnyFrame],
        default: bool = False,
    ) -> bool:
        """Return whether the panel should be treated as code-like text.

        Args:
            draft_panel: Draft panel whose content is evaluated.
            default: Whether selection runs in fallback/default mode.

        Returns:
            ``True`` for default handling of plain ``str`` content.
        """
        # To allow plain str content, such as e.g. in Dataset.list() output,
        # to be automatically highlighted as Python code.
        if default and isinstance(draft_panel.content, str):
            return True

        return False

    @override
    @classmethod
    def get_default_syntax_language(cls) -> SyntaxLanguageSpec.Literals:
        """Return the default syntax language used by this printer.

        Returns:
            ``SyntaxLanguageSpec.PYTHON`` for code-oriented highlighting.
        """
        # Python syntax is provided as default. This is among others used
        # to support highlighting of numbers, types etc. in tables and
        # elsewhere, such as Dataset.list() output. For str-based Models,
        # PlainTextPrettyPrinter is automatically selected, which uses
        # SyntaxLanguageSpec.TEXT instead.
        return SyntaxLanguageSpec.PYTHON
