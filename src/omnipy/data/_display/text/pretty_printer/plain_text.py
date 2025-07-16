from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter


class PlainTextPrettyPrinter(PrettyPrinter[str]):
    def format_draft(
        self,
        draft_panel: DraftPanel[str, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        return ReflowedTextDraftPanel.create_from_draft_panel(draft_panel)

    def prepare_draft_panel(self, draft_panel: DraftPanel[object,
                                                          FrameT]) -> DraftPanel[str, FrameT]:
        if isinstance(draft_panel.content, str):
            content = draft_panel.content
        else:
            content = repr(draft_panel.content)
        return DraftPanel[str, FrameT].create_copy_with_other_content(
            draft_panel,
            other_content=content,
        )
