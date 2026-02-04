from typing import cast

from typing_extensions import override

from omnipy import SyntaxLanguageSpec
from omnipy.components.json.typedefs import JsonScalar
from omnipy.components.tables.models import ColumnModel, PrintableTable
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import PrettyPrinter


class ColumnPrettyPrinter(PrettyPrinter[list[JsonScalar]]):
    @override
    @classmethod
    def is_suitable_content(cls, draft_panel: DraftPanel[object, AnyFrame]) -> bool:
        from omnipy.components.tables.models import ColumnModel
        return isinstance(draft_panel.content, (ColumnModel, PrintableTable))

    @override
    @classmethod
    def get_default_syntax_language(cls) -> SyntaxLanguageSpec.Literals:
        return SyntaxLanguageSpec.TEXT

    @override
    @classmethod
    def _get_content_for_draft_panel(cls, draft_panel: DraftPanel[object,
                                                                  AnyFrame]) -> list[JsonScalar]:
        if not isinstance(draft_panel.content, ColumnModel):
            column_model = ColumnModel(draft_panel.content)
        else:
            column_model = draft_panel.content

        return cast(list[JsonScalar], column_model.to_data())

    @override
    def format_prepared_draft(
        self,
        draft_panel: DraftPanel[list[JsonScalar], FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        output = '\n'.join(str(item) for item in draft_panel.content)
        return ReflowedTextDraftPanel.create_from_draft_panel(draft_panel, other_content=output)
