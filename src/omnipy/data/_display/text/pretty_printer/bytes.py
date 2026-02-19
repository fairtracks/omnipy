from typing_extensions import override

from omnipy import SyntaxLanguageSpec
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter
from omnipy.data.typechecks import is_model_instance


class HexdumpPrettyPrinter(PrettyPrinter[str]):
    @override
    @classmethod
    def is_suitable_content(cls, draft_panel: DraftPanel[object, AnyFrame]) -> bool:
        from omnipy.components.raw.models import BytesModel

        content = draft_panel.content

        if is_model_instance(content):
            return isinstance(content, BytesModel)

        return False

    @override
    @classmethod
    def get_default_syntax_language(cls) -> SyntaxLanguageSpec.Literals:
        return SyntaxLanguageSpec.HEXDUMP

    @override
    def format_prepared_draft(
        self,
        draft_panel: DraftPanel[str, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        return ReflowedTextDraftPanel.create_from_draft_panel(draft_panel)

    @override
    @classmethod
    def _get_content_for_draft_panel(cls, draft_panel: DraftPanel[object, AnyFrame]) -> str:
        from hexdump import hexdump
        if is_model_instance(draft_panel.content):
            raw_content = draft_panel.content.content
        else:
            raw_content = draft_panel.content

        if not isinstance(raw_content, bytes):
            raw_content = repr(raw_content).encode()

        return str(hexdump(raw_content))
