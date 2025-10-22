from abc import ABC

from typing_extensions import override

from omnipy.components.json.models import is_json_model_instance_hack
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter
from omnipy.data.typechecks import is_model_instance


class PythonStatsTighteningPrettyPrinter(PrettyPrinter[object], ABC):
    @override
    @classmethod
    def is_suitable_content(cls, draft_panel: DraftPanel[object, AnyFrame]) -> bool:
        # To first allow for syntax-based selection, and PYTHON is the default syntax
        return False

    @override
    @classmethod
    def _get_content_for_draft_panel(cls, draft_panel: DraftPanel[object, AnyFrame]) -> object:
        if is_model_instance(draft_panel.content) and not draft_panel.config.debug:
            return draft_panel.content.to_data()
        else:
            return draft_panel.content


class JsonStatsTighteningPrettyPrinterMixin(PrettyPrinter[object], ABC):
    @override
    @classmethod
    def is_suitable_content(cls, draft_panel: DraftPanel[object, AnyFrame]) -> bool:
        return is_json_model_instance_hack(draft_panel.content)

    @override
    @classmethod
    def _get_content_for_draft_panel(cls, draft_panel: DraftPanel[object, AnyFrame]) -> object:
        if is_model_instance(draft_panel.content):
            return draft_panel.content.to_data()
        else:
            return draft_panel.content
