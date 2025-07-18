from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter
from omnipy.data.typechecks import is_model_instance


class HexdumpPrettyPrinter(PrettyPrinter[str]):
    def is_suitable_content(self, draft_panel: DraftPanel[object, FrameT]) -> bool:
        from omnipy.components.raw.models import BytesModel

        content = draft_panel.content
        if isinstance(content, bytes):
            return True

        if is_model_instance(content):
            return content.outer_type() is bytes or isinstance(content, BytesModel)

        return False

    def format_draft(
        self,
        draft_panel: DraftPanel[str, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        return ReflowedTextDraftPanel.create_from_draft_panel(draft_panel)

    def prepare_draft_panel(self, draft_panel: DraftPanel[object,
                                                          FrameT]) -> DraftPanel[str, FrameT]:
        from hexdump import hexdump
        if is_model_instance(draft_panel.content):
            raw_content = draft_panel.content.content
        else:
            raw_content = draft_panel.content

        if not isinstance(raw_content, bytes):
            raw_content = repr(raw_content).encode()

        return DraftPanel[bytes, FrameT].create_copy_with_other_content(
            draft_panel,
            other_content=str(hexdump(raw_content)),
        )
