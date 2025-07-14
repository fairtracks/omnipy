import os
import re
from textwrap import dedent
from typing import Annotated

import pytest

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.text.pretty import pretty_repr_of_draft_output
from omnipy.data.model import Model
from omnipy.shared.enums.display import PrettyPrinterLib, SyntaxLanguage

from ..panel.helpers.panel_assert import DraftPanelKwArgs

DEFAULT_FRAME = Frame(Dimensions(80, 24), fixed_width=False, fixed_height=False)


def _remove_training_commas(output: str) -> str:
    return re.sub(r',(\n *[\]\}\)])', '\\1', output)


def _hackish_convert_json_to_python_syntax(output: str) -> str:
    # Revert stringified number keys to plain numbers
    output = re.sub(r'"(\d+)":', '\\1:', output)

    # Double quotes to single quotes
    output = re.sub(r'"', "'", output)

    # Convert empty lists to tuples (just since the tests expect it)
    output = re.sub(r'\[\]', '()', output)

    # Remove padding within brackets. Double application to remove padding
    # with more than two sequential brackets.
    output = re.sub(r'([\[{]) (\S)', '\\1\\2', output)
    output = re.sub(r'([\[{]) (\S)', '\\1\\2', output)
    output = re.sub(r'(\S) ([\]}])', '\\1\\2', output)
    output = re.sub(r'(\S) ([\]}])', '\\1\\2', output)

    # Remove spaces before commas
    output = re.sub(r'(\S) +,', '\\1,', output)

    return output


def _assert_pretty_repr_of_draft(
    data: object,
    exp_plain_output: str,
    frame: Frame | None = None,
    config: OutputConfig | None = None,
    within_frame_width: bool | None = None,
    within_frame_height: bool | None = None,
) -> None:
    kwargs = DraftPanelKwArgs()
    if frame is not None:
        kwargs['frame'] = frame
    if config is not None:
        kwargs['config'] = config

    in_draft_panel = DraftPanel(data, **kwargs)

    out_draft_panel: ReflowedTextDraftPanel = pretty_repr_of_draft_output(in_draft_panel)
    output = out_draft_panel.content

    if config:
        if config.pretty_printer is PrettyPrinterLib.DEVTOOLS:
            output = _remove_training_commas(output)
        if config.language == SyntaxLanguage.JSON:
            output = _hackish_convert_json_to_python_syntax(output)

    assert output == exp_plain_output
    assert out_draft_panel.frame == in_draft_panel.frame
    assert out_draft_panel.within_frame.width is within_frame_width
    assert out_draft_panel.within_frame.height is within_frame_height


@pytest.mark.parametrize('pretty_printer, language',
                         [(PrettyPrinterLib.DEVTOOLS, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.JSON)])
def test_pretty_repr_of_draft_multi_line_if_nested(
    pretty_printer: PrettyPrinterLib.Literals,
    language: SyntaxLanguage.Literals,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer, language=language, proportional_freedom=0)

    _assert_pretty_repr_of_draft(1, '1', config=config)

    _assert_pretty_repr_of_draft([1, 2, 3], '[1, 2, 3]', config=config)

    _assert_pretty_repr_of_draft(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        '[[1, 2, 3], [4, 5, 6], [7, 8, 9]]',
        config=config,
    )

    _assert_pretty_repr_of_draft(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        dedent("""\
        [
          [1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]
        ]"""),
        frame=DEFAULT_FRAME,
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft({1: 2, 3: 4}, '{1: 2, 3: 4}', config=config)

    _assert_pretty_repr_of_draft([{1: 2, 3: 4}], '[{1: 2, 3: 4}]', config=config)

    _assert_pretty_repr_of_draft(
        [{
            1: 2, 3: 4
        }],
        dedent("""\
        [
          {
            1: 2,
            3: 4
          }
        ]"""),
        frame=DEFAULT_FRAME,
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    if language == SyntaxLanguage.JSON:
        # CompactJson configured to smax include 2 nested levels in one line
        _assert_pretty_repr_of_draft(
            [[1, 2, 3], [()], [[4, 5, 6], [7, 8, 9]]],
            dedent("""\
            [
              [1, 2, 3],
              [()],
              [[4, 5, 6], [7, 8, 9]]
            ]"""),
            config=config,
        )
    else:
        _assert_pretty_repr_of_draft(
            [[1, 2, 3], [()], [[4, 5, 6], [7, 8, 9]]],
            '[[1, 2, 3], [()], [[4, 5, 6], [7, 8, 9]]]',
            config=config,
        )

    _assert_pretty_repr_of_draft(
        [[1, 2, 3], [()], [[4, 5, 6], [7, 8, 9]]],
        dedent("""\
        [
          [1, 2, 3],
          [()],
          [
            [4, 5, 6],
            [7, 8, 9]
          ]
        ]"""),
        frame=DEFAULT_FRAME,
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )


@pytest.mark.parametrize('pretty_printer, language',
                         [(PrettyPrinterLib.DEVTOOLS, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.JSON)])
def test_pretty_repr_of_draft_indent(
    pretty_printer: PrettyPrinterLib.Literals,
    language: SyntaxLanguage.Literals,
) -> None:
    config = OutputConfig(
        pretty_printer=pretty_printer,
        language=language,
        proportional_freedom=0,
        indent_tab_size=4,
    )

    _assert_pretty_repr_of_draft(
        [[1, 2, 3], [[4, 5, 6], [7, 8, 9]]],
        dedent("""\
        [
            [1, 2, 3],
            [
                [4, 5, 6],
                [7, 8, 9]
            ]
        ]"""),
        frame=DEFAULT_FRAME,
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )


@pytest.mark.parametrize('pretty_printer, language',
                         [(PrettyPrinterLib.DEVTOOLS, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.JSON)])
def test_pretty_repr_of_draft_in_frame(
    pretty_printer: PrettyPrinterLib.Literals,
    language: SyntaxLanguage.Literals,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer, language=language, proportional_freedom=0)

    data = [[0, 1, 2], [[3, 4, 5, 6], [7, 8, 9]]]

    if language == SyntaxLanguage.JSON:
        # CompactJson configured to max include 2 nested levels in one line
        _assert_pretty_repr_of_draft(
            data,
            dedent("""\
            [
              [0, 1, 2],
              [[3, 4, 5, 6], [7, 8, 9]]
            ]"""),
            frame=Frame(Dimensions(None, 7)),
            config=config,
            within_frame_width=None,
            within_frame_height=True,
        )
    else:  # PYTHON
        _assert_pretty_repr_of_draft(
            data,
            '[[0, 1, 2], [[3, 4, 5, 6], [7, 8, 9]]]',
            frame=Frame(Dimensions(None, 7)),
            config=config,
            within_frame_width=None,
            within_frame_height=True,
        )

    if language == SyntaxLanguage.JSON:
        # CompactJson supports a more compact representation
        excepted_output_slimmer = dedent("""\
            [
              [0, 1, 2],
              [
                [
                  3, 4, 5, 6
                ],
                [7, 8, 9]
              ]
            ]""")
        output_height = 9
    else:  # PYTHON
        excepted_output_slimmer = dedent("""\
            [
              [0, 1, 2],
              [
                [3, 4, 5, 6],
                [7, 8, 9]
              ]
            ]""")
        output_height = 7

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_slimmer,
        frame=Frame(Dimensions(17, None), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=None,
    )

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_slimmer,
        frame=Frame(Dimensions(17, output_height), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    if language == SyntaxLanguage.JSON:
        # CompactJson supports a slightly more compact representation
        excepted_output_high_and_slim = dedent("""\
            [
              [
                0,
                1,
                2
              ],
              [
                [
                  3,
                  4,
                  5,
                  6
                ], [
                  7,
                  8,
                  9
                ]
              ]
            ]""")
    else:  # PYTHON
        excepted_output_high_and_slim = dedent("""\
            [
              [
                0,
                1,
                2
              ],
              [
                [
                  3,
                  4,
                  5,
                  6
                ],
                [
                  7,
                  8,
                  9
                ]
              ]
            ]""")

    # Increasing the frame height  adjusts the pretty print layout to make it more proportional to
    # the frame width vs height ratio. This is primarily to avoid long one-liners.
    _assert_pretty_repr_of_draft(
        data,
        excepted_output_high_and_slim,
        frame=Frame(Dimensions(17, 24), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_high_and_slim,
        frame=Frame(Dimensions(8, None), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=None,
    )

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_high_and_slim,
        frame=Frame(Dimensions(8, 20), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_high_and_slim,
        frame=Frame(Dimensions(8, 18), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=False,
    )


@pytest.fixture
def geometry_data() -> list:
    return [{
        'geometry': {
            'location': {
                'lng': 77.2295097, 'lat': 28.612912
            },
            'viewport': {
                'northeast': {
                    'lng': 77.2308586802915, 'lat': 28.6142609802915
                },
                'southwest': {
                    'lng': 77.22816071970848, 'lat': 28.6115630197085
                }
            },
            'location_type': 'APPROXIMATE',
        }
    }]


@pytest.mark.parametrize('pretty_printer, language',
                         [(PrettyPrinterLib.DEVTOOLS, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.JSON)])
def test_pretty_repr_of_draft_approximately_in_frame(
    geometry_data: Annotated[list, pytest.fixture],
    pretty_printer: PrettyPrinterLib.Literals,
    language: SyntaxLanguage.Literals,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer, language=language, proportional_freedom=0)

    _assert_pretty_repr_of_draft(
        geometry_data,
        dedent("""\
        [
          {
            'geometry': {
              'location': {'lng': 77.2295097, 'lat': 28.612912},
              'viewport': {'northeast': {'lng': 77.2308586802915, 'lat': 28.6142609802915}, \
'southwest': {'lng': 77.22816071970848, 'lat': 28.6115630197085}},
              'location_type': 'APPROXIMATE'
            }
          }
        ]"""),
        frame=Frame(Dimensions(160, 9), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        geometry_data,
        dedent("""\
        [
          {
            'geometry': {
              'location': {'lng': 77.2295097, 'lat': 28.612912},
              'viewport': {
                'northeast': {'lng': 77.2308586802915, 'lat': 28.6142609802915},
                'southwest': {'lng': 77.22816071970848, 'lat': 28.6115630197085}
              },
              'location_type': 'APPROXIMATE'
            }
          }
        ]"""),
        frame=Frame(Dimensions(149, 12), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    geometry_data_thinnest_repr = dedent("""\
        [
          {
            'geometry': {
              'location': {
                'lng': 77.2295097,
                'lat': 28.612912
              },
              'viewport': {
                'northeast': {
                  'lng': 77.2308586802915,
                  'lat': 28.6142609802915
                },
                'southwest': {
                  'lng': 77.22816071970848,
                  'lat': 28.6115630197085
                }
              },
              'location_type': 'APPROXIMATE'
            }
          }
        ]""")

    _assert_pretty_repr_of_draft(
        geometry_data,
        geometry_data_thinnest_repr,
        frame=Frame(Dimensions(37, 21), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        geometry_data,
        geometry_data_thinnest_repr,
        frame=Frame(Dimensions(35, 21), fixed_width=False),
        config=config,
        within_frame_width=False,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        geometry_data,
        geometry_data_thinnest_repr,
        frame=Frame(Dimensions(10, 10), fixed_width=False),
        config=config,
        within_frame_width=False,
        within_frame_height=False,
    )


@pytest.mark.parametrize(
    'pretty_printer, language',
    # Devtools actually shortens the long line to fit the frame,
    # which is not what we want to test here.
    [  # (PrettyPrinterLib.DEVTOOLS, SyntaxLanguage.PYTHON),
        (PrettyPrinterLib.RICH, SyntaxLanguage.PYTHON),
        (PrettyPrinterLib.RICH, SyntaxLanguage.JSON),
    ])
def test_pretty_repr_of_draft_one_line_wider_than_frame(
    pretty_printer: PrettyPrinterLib.Literals,
    language: SyntaxLanguage.Literals,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer, language=language, proportional_freedom=0)
    # This is a test for the case where one line is wider than the frame
    # width. The pretty printer should not fit the short lines into a singe
    # line even though this single line will not be wider than the widest
    # line. The result would in that case be two lines that are both wider
    # than the frame width and need to be cropped, which is worse than
    # having one line that is too wide for the frame.

    _assert_pretty_repr_of_draft(
        {
            'nested': {
                'short_key_1': 'short_value', 'short_key_2': 'short_value_2'
            },
            'long_key': 'This is a very long value that will be too long for the frame',
        },
        dedent("""\
        {
          'nested': {
            'short_key_1': 'short_value',
            'short_key_2': 'short_value_2'
          },
          'long_key': 'This is a very long value that will be too long for the frame'
        }"""),
        frame=Frame(Dimensions(40, 7), fixed_width=True),
        config=config,
        within_frame_width=False,
        within_frame_height=True,
    )


@pytest.mark.parametrize('pretty_printer, language',
                         [(PrettyPrinterLib.DEVTOOLS, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.JSON)])
def test_pretty_repr_of_draft_models(
    pretty_printer: PrettyPrinterLib.Literals,
    language: SyntaxLanguage.Literals,
) -> None:
    class ListOfIntsModel(Model[list[int]]):
        ...

    class ListOfListsOfIntsModel(Model[list[ListOfIntsModel]]):
        ...

    _assert_pretty_repr_of_draft(
        ListOfListsOfIntsModel([[1, 2], [3, 4]]),
        dedent("""\
        [
          [1, 2],
          [3, 4]
        ]"""),
        frame=DEFAULT_FRAME,
        config=OutputConfig(
            debug_mode=False,
            pretty_printer=pretty_printer,
            language=language,
            proportional_freedom=0,
        ),
        within_frame_width=True,
        within_frame_height=True,
    )

    def _debug_mode_test():
        _assert_pretty_repr_of_draft(
            ListOfListsOfIntsModel([[1, 2, 3], [4, 5, 6]]),
            dedent("""\
            ListOfListsOfIntsModel(
              [
                ListOfIntsModel(
                  [1, 2, 3]
                ),
                ListOfIntsModel(
                  [4, 5, 6]
                )
              ]
            )"""),
            frame=DEFAULT_FRAME,
            config=OutputConfig(
                debug_mode=True,
                pretty_printer=pretty_printer,
                language=language,
                proportional_freedom=0,
            ),
            within_frame_width=True,
            within_frame_height=True,
        )

    if language == SyntaxLanguage.PYTHON:
        # Debug mode is only supported for Python syntax
        _debug_mode_test()
    else:
        with pytest.raises(TypeError):
            _debug_mode_test()


@pytest.mark.parametrize('pretty_printer, language',
                         [(PrettyPrinterLib.DEVTOOLS, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.PYTHON),
                          (PrettyPrinterLib.RICH, SyntaxLanguage.JSON)])
def test_pretty_repr_of_draft_variable_char_weight(
    pretty_printer: PrettyPrinterLib.Literals,
    language: SyntaxLanguage.Literals,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer, language=language, proportional_freedom=0)

    _assert_pretty_repr_of_draft(
        ['北京', '€450'],
        "['北京', '€450']",
        frame=Frame(Dimensions(18, 1), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        ['北京', '€450'],
        dedent("""\
        [
          '北京',
          '€450'
        ]"""),
        frame=Frame(Dimensions(15, 4), fixed_width=False),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""\
        The implementation of multi-line adjustment of pretty_repr detects whether the data
        representation is nested by counting abbreviations of nested containers by the rich library.
        If such abbreviation strings ('(...)', '[...]', or '{...}') are present in the input data,
        the adjustment algorithm gets confused.

        Since the content here is not really nested, it should have been printed as a single line.
        """),
)
@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_multi_line_if_nested_known_issue(
        pretty_printer: PrettyPrinterLib.Literals) -> None:
    config = OutputConfig(pretty_printer=pretty_printer, proportional_freedom=0)
    _assert_pretty_repr_of_draft(
        [1, 2, '[...]'],
        "[1, 2, '[...]']",
        frame=DEFAULT_FRAME,
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )
