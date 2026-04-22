from omnipy.components.tables.models import ColumnWiseTableWithColNamesModel
from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel.draft.base import DraftPanel

from ..helpers.panel_assert import assert_draft_panel_subcls


def test_table_draft_panel_init() -> None:
    simple_table = ColumnWiseTableWithColNamesModel(a=[1, 2], b=['x', 'y'])
    assert_draft_panel_subcls(DraftPanel, simple_table)

    assert_draft_panel_subcls(
        DraftPanel,
        simple_table,
        title='My Simple Table',
        frame=Frame(Dimensions(20, 10)),
        constraints=Constraints(max_inline_container_width_incl=10),
        config=OutputConfig())
