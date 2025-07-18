from omnipy.components.json.models import is_json_model_instance_hack
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data.typechecks import is_model_instance


class PythonWidthReducingPrettyPrinterMixin:
    def is_suitable_content(self, draft_panel: DraftPanel[object, FrameT]) -> bool:
        # To first allow for language-based selection, and PYTHON is the default language
        return False

    def prepare_draft_panel(
        self,
        draft_panel: DraftPanel[object, FrameT],
    ) -> DraftPanel[object, FrameT]:
        if is_model_instance(draft_panel.content) and not draft_panel.config.debug:
            content: object = draft_panel.content.to_data()
        else:
            content = draft_panel.content
        return DraftPanel[object, FrameT].create_copy_with_other_content(
            draft_panel,
            other_content=content,
        )


class JsonWidthReducingPrettyPrinterMixin:
    def is_suitable_content(self, draft_panel: DraftPanel[object, FrameT]) -> bool:
        return is_json_model_instance_hack(draft_panel.content)

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
