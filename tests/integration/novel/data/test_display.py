from textwrap import dedent
from typing import Any

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.text.pretty import pretty_repr_of_draft_output
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.enums.display import PrettyPrinterLib
from omnipy.shared.enums.ui import UserInterfaceType


def _render_panel_to_plain_terminal(panel: Any) -> str:
    return panel.render_next_stage().render_next_stage().plain.terminal


def _assert_pretty_repr_of_draft(
    data: object,
    exp_plain_output: str,
    frame: Frame,
    config: OutputConfig,
    within_frame_width: bool | None,
    within_frame_height: bool | None,
) -> None:
    in_draft_panel = DraftPanel(data, frame=frame, config=config)
    out_draft_panel: ReflowedTextDraftPanel = pretty_repr_of_draft_output(in_draft_panel)

    assert out_draft_panel.content == exp_plain_output
    assert out_draft_panel.frame == in_draft_panel.frame
    assert out_draft_panel.within_frame.width is within_frame_width
    assert out_draft_panel.within_frame.height is within_frame_height


def test_pretty_repr_of_draft_characterizes_bounded_and_unbounded_viewports() -> None:
    data = [[i, i + 1, i + 2] for i in range(0, 18, 3)]
    config = OutputConfig(printer=PrettyPrinterLib.RICH, freedom=0)

    multiline_output = dedent("""\
        [
          [0, 1, 2],
          [3, 4, 5],
          [6, 7, 8],
          [9, 10, 11],
          [12, 13, 14],
          [15, 16, 17]
        ]""")

    _assert_pretty_repr_of_draft(
        data,
        multiline_output,
        frame=Frame(Dimensions(32, 8), fixed_width=False, fixed_height=False),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        data,
        multiline_output,
        frame=Frame(Dimensions(32, 6), fixed_width=False, fixed_height=False),
        config=config,
        within_frame_width=True,
        within_frame_height=False,
    )

    _assert_pretty_repr_of_draft(
        data,
        '[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14], [15, 16, 17]]',
        frame=Frame(Dimensions(None, 8), fixed_height=False),
        config=config,
        within_frame_width=None,
        within_frame_height=True,
    )


def test_characterize_peek_json_full_viewport_output() -> None:
    model = Model[list[list[int]]]([[i, i + 1, i + 2] for i in range(0, 18, 3)])

    bounded_peek_output = _render_panel_to_plain_terminal(
        model._peek(
            width=32,
            height=8,
            ui=UserInterfaceType.TERMINAL,
        ))
    assert bounded_peek_output == dedent("""\
        ╭────────────────────────╮
        │ Model[list[list[int]]] │
        │                        │
        │ [                      │
        │   [0, 1, 2],           │
        │   [3, 4, 5],           │
        │ …                      │
        ╰────────────────────────╯
        """)

    unbounded_height_peek_output = _render_panel_to_plain_terminal(
        model._peek(
            width=32,
            height=None,
            ui=UserInterfaceType.TERMINAL,
        ))
    assert unbounded_height_peek_output == dedent("""\
        ╭────────────────────────╮
        │ Model[list[list[int]]] │
        │                        │
        │ [                      │
        │   [0, 1, 2],           │
        │   [3, 4, 5],           │
        │   [6, 7, 8],           │
        │   [9, 10, 11],         │
        │   [12, 13, 14],        │
        │   [15, 16, 17]         │
        │ ]                      │
        ╰────────────────────────╯
        """)

    unbounded_width_peek_output = _render_panel_to_plain_terminal(
        model._peek(
            width=None,
            height=8,
            ui=UserInterfaceType.TERMINAL,
        ))
    assert unbounded_width_peek_output == dedent("""\
        ╭────────────────────────────────────────────────────────────────────────────╮
        │                           Model[list[list[int]]]                           │
        │                                                                            │
        │ [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14], [15, 16, 17]] │
        ╰────────────────────────────────────────────────────────────────────────────╯
        """)

    bounded_json_output = _render_panel_to_plain_terminal(
        model._json(
            width=32,
            height=8,
            ui=UserInterfaceType.TERMINAL,
        ))
    assert bounded_json_output == dedent("""\
        ╭───────────────────╮
        │     JsonModel     │
        │                   │
        │ [                 │
        │   [ 0 , 1 , 2  ], │
        │   [ 3 , 4 , 5  ], │
        │ …                 │
        ╰───────────────────╯
        """)

    full_output = _render_panel_to_plain_terminal(
        model._full(
            width=32,
            height=4,
            ui=UserInterfaceType.TERMINAL,
        ))
    assert full_output == unbounded_height_peek_output
    assert '│ …                      │' not in full_output


def test_characterize_dataset_list_framing_and_rows() -> None:
    dataset = Dataset[Model[list[int]]]({f'row_{i}': [i, i + 1] for i in range(12)})

    bounded_list_output = _render_panel_to_plain_terminal(
        dataset._list(
            width=80,
            height=9,
            ui=UserInterfaceType.TERMINAL,
        ))
    assert bounded_list_output == dedent("""\
        ╭───┬────────────────┬──────────────────┬────────┬──────────────────╮
        │ # │ Data file name │       Type       │ Length │ Size (in memory) │
        │   │                │                  │        │                  │
        │ 0 │ row_0          │ Model[list[int]] │      2 │        649 Bytes │
        │ 1 │ row_1          │ Model[list[int]] │      2 │        649 Bytes │
        │ 2 │ row_2          │ Model[list[int]] │      2 │        649 Bytes │
        │ 3 │ row_3          │ Model[list[int]] │      2 │        649 Bytes │
        │ … │ …              │ …                │      … │                … │
        ╰───┴────────────────┴──────────────────┴────────┴──────────────────╯
        """)

    unbounded_height_list_output = _render_panel_to_plain_terminal(
        dataset._list(
            width=80,
            height=None,
            ui=UserInterfaceType.TERMINAL,
        ))
    assert unbounded_height_list_output == dedent("""\
        ╭────┬────────────────┬──────────────────┬────────┬──────────────────╮
        │ #  │ Data file name │       Type       │ Length │ Size (in memory) │
        │    │                │                  │        │                  │
        │ 0  │ row_0          │ Model[list[int]] │      2 │        649 Bytes │
        │ 1  │ row_1          │ Model[list[int]] │      2 │        649 Bytes │
        │ 2  │ row_2          │ Model[list[int]] │      2 │        649 Bytes │
        │ 3  │ row_3          │ Model[list[int]] │      2 │        649 Bytes │
        │ 4  │ row_4          │ Model[list[int]] │      2 │        649 Bytes │
        │ 5  │ row_5          │ Model[list[int]] │      2 │        649 Bytes │
        │ 6  │ row_6          │ Model[list[int]] │      2 │        649 Bytes │
        │ 7  │ row_7          │ Model[list[int]] │      2 │        649 Bytes │
        │ 8  │ row_8          │ Model[list[int]] │      2 │        649 Bytes │
        │ 9  │ row_9          │ Model[list[int]] │      2 │        649 Bytes │
        │ 10 │ row_10         │ Model[list[int]] │      2 │        649 Bytes │
        │ 11 │ row_11         │ Model[list[int]] │      2 │        649 Bytes │
        ╰────┴────────────────┴──────────────────┴────────┴──────────────────╯
        """)
