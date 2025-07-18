from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter
from omnipy.data.typechecks import is_model_instance


class PlainTextPrettyPrinter(PrettyPrinter[str]):
    def is_suitable_content(self, draft_panel: DraftPanel[object, FrameT]) -> bool:
        from omnipy.components.raw.models import StrModel

        content = draft_panel.content
        if isinstance(content, str):
            return True

        if is_model_instance(content):
            return content.outer_type() is str or isinstance(content, StrModel)

        return False

    def format_draft(
        self,
        draft_panel: DraftPanel[str, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        return ReflowedTextDraftPanel.create_from_draft_panel(draft_panel)

    def prepare_draft_panel(self, draft_panel: DraftPanel[object,
                                                          FrameT]) -> DraftPanel[str, FrameT]:
        if is_model_instance(draft_panel.content):
            raw_content = draft_panel.content.content
        else:
            raw_content = draft_panel.content

        if not isinstance(raw_content, str):
            raw_content = repr(raw_content)
        return DraftPanel[str, FrameT].create_copy_with_other_content(
            draft_panel,
            other_content=raw_content,
        )
