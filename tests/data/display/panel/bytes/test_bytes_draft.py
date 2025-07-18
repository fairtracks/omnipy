from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel.draft.bytes import BytesDraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.shared.enums.display import SyntaxLanguage

from ..helpers.panel_assert import assert_draft_panel_subcls, assert_next_stage_panel


def test_bytes_draft_panel_init() -> None:
    assert_draft_panel_subcls(BytesDraftPanel, b'\xc3\xa6\xc3\xb8\xc3\xa5')

    assert_draft_panel_subcls(
        BytesDraftPanel,
        b'\xc3\xa6\xc3\xb8\xc3\xa5',
        title='My JSON file',
        frame=Frame(Dimensions(20, 10)),
        constraints=Constraints(max_inline_container_width_incl=10),
        config=OutputConfig(lang=SyntaxLanguage.JSON),
    )


def test_bytes_draft_panel_render_next_stage_simple() -> None:
    text_draft_panel = BytesDraftPanel(b'\xc3\xa6\xc3\xb8\xc3\xa5')
    assert_next_stage_panel(
        this_panel=text_draft_panel,
        next_stage=text_draft_panel.render_next_stage(),
        next_stage_panel_cls=ReflowedTextDraftPanel,
        exp_content="b'\\xc3\\xa6\\xc3\\xb8\\xc3\\xa5'",
    )


def test_bytes_draft_panel_render_next_stage_with_repr_complex() -> None:
    draft_panel_complex = BytesDraftPanel(
        b'\xc3\xa6\xc3\xb8\xc3\xa5',
        title='My repr panel',
        frame=Frame(Dimensions(18, 2)),
        constraints=Constraints(max_inline_container_width_incl=10),
        config=OutputConfig(indent=1, lang=SyntaxLanguage.PYTHON),
    )
    assert_next_stage_panel(
        this_panel=draft_panel_complex,
        next_stage=draft_panel_complex.render_next_stage(),
        next_stage_panel_cls=ReflowedTextDraftPanel,
        exp_content="b'\\xc3\\xa6\\xc3\\xb8\\xc3\\xa5'",
    )
