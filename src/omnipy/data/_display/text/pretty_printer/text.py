from typing_extensions import override

from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter
from omnipy.data.typechecks import is_model_instance


class PlainTextPrettyPrinter(PrettyPrinter[str]):
    @override
    @classmethod
    def is_suitable_content(cls, draft_panel: DraftPanel[object, AnyFrame]) -> bool:
        from omnipy.components.raw.models import StrModel

        content = draft_panel.content
        if isinstance(content, str):
            return True

        if is_model_instance(content):
            return content.outer_type() is str or isinstance(content, StrModel)

        return False

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
