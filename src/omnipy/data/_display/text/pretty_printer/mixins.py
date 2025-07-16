from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data.typechecks import is_model_instance


class PythonWidthReducingPrettyPrinterMixin:
    def prepare_draft_panel(
        self,
        draft_panel: DraftPanel[object, FrameT],
    ) -> DraftPanel[object, FrameT]:
        if is_model_instance(draft_panel.content) and not draft_panel.config.debug_mode:
            content: object = draft_panel.content.to_data()
        else:
            content = draft_panel.content
        return DraftPanel[object, FrameT].create_copy_with_other_content(
            draft_panel,
            other_content=content,
        )


class JsonWidthReducingPrettyPrinterMixin:
    def prepare_draft_panel(
        self,
        draft_panel: DraftPanel[object, FrameT],
    ) -> DraftPanel[object, FrameT]:
        if is_model_instance(draft_panel.content):
            content: object = draft_panel.content.to_data()
        else:
            content = draft_panel.content
        return DraftPanel[object, FrameT].create_copy_with_other_content(
            draft_panel,
            other_content=content,
        )
