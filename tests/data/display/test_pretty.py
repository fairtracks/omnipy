import os
import re
from textwrap import dedent
from typing import Annotated, TypedDict

import pytest

from omnipy.data._display.config import OutputConfig, PrettyPrinterLib
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.draft import DraftMonospacedOutput, DraftOutput
from omnipy.data._display.frame import Frame
from omnipy.data._display.pretty import pretty_repr_of_draft_output
from omnipy.data.model import Model

DEFAULT_FRAME = Frame(Dimensions(80, 24))


def _harmonize(output: str) -> str:
    return re.sub(r',(\n *[\]\}\)])', '\\1', output)


class _DraftOutputKwArgs(TypedDict, total=False):
    frame: Frame
    config: OutputConfig


def _assert_pretty_repr_of_draft(
    data: object,
    expected_output: str,
    frame: Frame | None = None,
    config: OutputConfig | None = None,
    within_frame_width: bool | None = None,
    within_frame_height: bool | None = None,
) -> None:
    kwargs = _DraftOutputKwArgs()
    if frame is not None:
        kwargs['frame'] = frame
    if config is not None:
        kwargs['config'] = config

    in_draft = DraftOutput(data, **kwargs)

    out_draft: DraftMonospacedOutput = pretty_repr_of_draft_output(in_draft)

    assert _harmonize(out_draft.content) == expected_output
    assert out_draft.within_frame.width is within_frame_width
    assert out_draft.within_frame.height is within_frame_height


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_multi_line_if_nested(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer)

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


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_indent(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:

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
        config=OutputConfig(
            indent_tab_size=4,
            pretty_printer=pretty_printer,
        ),
        within_frame_width=True,
        within_frame_height=True,
    )


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_in_frame(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer)

    data = [[1, 2], [[3, 4, 5, 6], [7, 8, 9]]]

    _assert_pretty_repr_of_draft(
        data,
        '[[1, 2], [[3, 4, 5, 6], [7, 8, 9]]]',
        frame=Frame(Dimensions(None, 7)),
        config=config,
        within_frame_width=None,
        within_frame_height=True,
    )

    excepted_output_width_17 = dedent("""\
        [
          [1, 2],
          [
            [3, 4, 5, 6],
            [7, 8, 9]
          ]
        ]""")

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_width_17,
        frame=Frame(Dimensions(17, None)),
        config=config,
        within_frame_width=True,
        within_frame_height=None,
    )

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_width_17,
        frame=Frame(Dimensions(17, 7)),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    excepted_output_width_13 = dedent("""\
        [
          [1, 2],
          [
            [
              3,
              4,
              5,
              6
            ],
            [7, 8, 9]
          ]
        ]""")

    # Increasing the frame height  adjusts the pretty print layout to make it more proportional to
    # the frame width vs height ratio. This is primarily to avoid long one-liners.
    _assert_pretty_repr_of_draft(
        data,
        excepted_output_width_13,
        frame=Frame(Dimensions(17, 14)),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_width_13,
        frame=Frame(Dimensions(16, None)),
        config=config,
        within_frame_width=True,
        within_frame_height=None,
    )

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_width_13,
        frame=Frame(Dimensions(16, 12)),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        data,
        excepted_output_width_13,
        frame=Frame(Dimensions(16, 11)),
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


@pytest.fixture
def geometry_data_thinnest_repr() -> str:
    return dedent("""\
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


@pytest.fixture
def geometry_data_thinnest_devtools_repr() -> str:
    return dedent("""\
        [
          {
            'geometry': {
              'location': {
                'lng': 77.2295097,
                'lat': 28.612912
              },
              'viewport': {
                'northeast': {
                  'lng': (
                    7
                    7
                    .
                    2
                    3
                    0
                    8
                    5
                    8
                    6
                    8
                    0
                    2
                    9
                    1
                    5
                  ),
                  'lat': (
                    2
                    8
                    .
                    6
                    1
                    4
                    2
                    6
                    0
                    9
                    8
                    0
                    2
                    9
                    1
                    5
                  )
                },
                'southwest': {
                  'lng': (
                    7
                    7
                    .
                    2
                    2
                    8
                    1
                    6
                    0
                    7
                    1
                    9
                    7
                    0
                    8
                    4
                    8
                  ),
                  'lat': (
                    2
                    8
                    .
                    6
                    1
                    1
                    5
                    6
                    3
                    0
                    1
                    9
                    7
                    0
                    8
                    5
                  )
                }
              },
              (
                'lo'
                'ca'
                'ti'
                'on'
                '_t'
                'yp'
                'e'
              ): (
                'AP'
                'PR'
                'OX'
                'IM'
                'AT'
                'E'
              )
            }
          }
        ]""")


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_approximately_in_frame(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    geometry_data: Annotated[list, pytest.fixture],
    geometry_data_thinnest_repr: Annotated[str, pytest.fixture],
    geometry_data_thinnest_devtools_repr: Annotated[str, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer)

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
        frame=Frame(Dimensions(150, 9)),
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
        frame=Frame(Dimensions(149, 9)),
        config=config,
        within_frame_width=True,
        within_frame_height=False,
    )

    _assert_pretty_repr_of_draft(
        geometry_data,
        geometry_data_thinnest_repr,
        frame=Frame(Dimensions(37, 21)),
        config=config,
        within_frame_width=True,
        within_frame_height=True,
    )

    _assert_pretty_repr_of_draft(
        geometry_data,
        geometry_data_thinnest_repr,
        frame=Frame(Dimensions(35, 21)),
        config=config,
        within_frame_width=False,
        within_frame_height=True,
    )

    match (pretty_printer):
        case (PrettyPrinterLib.RICH):
            _assert_pretty_repr_of_draft(
                geometry_data,
                geometry_data_thinnest_repr,
                frame=Frame(Dimensions(10, 10)),
                config=config,
                within_frame_width=False,
                within_frame_height=False,
            )
        case (PrettyPrinterLib.DEVTOOLS):
            _assert_pretty_repr_of_draft(
                geometry_data,
                geometry_data_thinnest_devtools_repr,
                frame=Frame(Dimensions(10, 10)),
                config=config,
                within_frame_width=False,
                within_frame_height=False,
            )


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_models(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    class ListOfIntsModel(Model[list[int]]):
        ...

    class ListOfListsOfIntsModel(Model[list[ListOfIntsModel]]):
        ...

    _assert_pretty_repr_of_draft(
        ListOfListsOfIntsModel([[1, 2, 3], [4, 5, 6]]),
        dedent("""\
        [
          [1, 2, 3],
          [4, 5, 6]
        ]"""),
        frame=DEFAULT_FRAME,
        config=OutputConfig(debug_mode=False, pretty_printer=pretty_printer),
        within_frame_width=True,
        within_frame_height=True,
    )

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
        config=OutputConfig(debug_mode=True, pretty_printer=pretty_printer),
        within_frame_width=True,
        within_frame_height=True,
    )


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_variable_char_weight(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:

    _assert_pretty_repr_of_draft(
        ['北京', '€450'],
        "['北京', '€450']",
        frame=Frame(Dimensions(16, 1)),
        config=OutputConfig(pretty_printer=pretty_printer),
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
        frame=Frame(Dimensions(15, 4)),
        config=OutputConfig(pretty_printer=pretty_printer),
        within_frame_width=True,
        within_frame_height=True,
    )


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""\
        The implementation of multi-line adjustment of pretty_repr detects whether the data
        representation is nested by counting abbreviations of nested containers by the rich library.
        If such abbreviation strings ('(...)', '[...]', or '{...}') are present in the input data,
        the adjustment algorithm gets confused."""),
)
@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_multi_line_if_nested_known_issue(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer)
    _assert_pretty_repr_of_draft([1, 2, '[...]'], "[1, 2, '[...]']", config=config)
