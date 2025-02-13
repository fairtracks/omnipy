import os
from textwrap import dedent
from typing import Annotated

import pytest

from data.display.test_draft import _assert_pretty_repr_of_draft
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.draft import DraftMonospacedOutput, DraftOutput, Frame, OutputConfig
from omnipy.data._display.enum import PrettyPrinterLib
from omnipy.data._display.pretty import pretty_repr_of_draft
from omnipy.data.model import Model


def test_pretty_repr_of_draft_init_frame_required(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(ValueError):
        pretty_repr_of_draft(DraftOutput(1))

    out_draft: DraftMonospacedOutput = pretty_repr_of_draft(
        DraftOutput(1, Frame(Dimensions(80, 24))))
    assert out_draft.content == '1'


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
        dedent("""\
        [
          [1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]
        ]"""),
        config=config,
    )
    _assert_pretty_repr_of_draft({1: 2, 3: 4}, '{1: 2, 3: 4}', config=config)
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
        config=config,
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
        config=OutputConfig(indent_tab_size=4, pretty_printer=pretty_printer),
    )


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_in_frame(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer)

    data_1 = [[1, 2], [[3, 4, 5, 6], [7, 8, 9]]]
    _assert_pretty_repr_of_draft(
        data_1,
        dedent("""\
        [
          [1, 2],
          [
            [3, 4, 5, 6],
            [7, 8, 9]
          ]
        ]"""),
        frame=Frame(Dimensions(17, 7)),
        config=config,
    )
    _assert_pretty_repr_of_draft(
        data_1,
        dedent("""\
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
        ]"""),
        frame=Frame(Dimensions(16, 12)),
        config=config,
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


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_of_draft_approximately_in_frame(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    geometry_data: Annotated[list, pytest.fixture],
    geometry_data_thinnest_repr: Annotated[str, pytest.fixture],
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
    )

    _assert_pretty_repr_of_draft(
        geometry_data,
        geometry_data_thinnest_repr,
        frame=Frame(Dimensions(35, 21)),
        config=config,
        within_frame_width=False,
        within_frame_height=True,
    )

    if pretty_printer == PrettyPrinterLib.RICH:
        _assert_pretty_repr_of_draft(
            geometry_data,
            geometry_data_thinnest_repr,
            frame=Frame(Dimensions(10, 10)),
            config=config,
            within_frame_width=False,
            within_frame_height=False,
        )


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""\
        The devtools pretty printer does not work when the required frame is thinner than the
        maximum indentation of the formatter output."""),
)
@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS])
def test_pretty_repr_of_draft_approximately_in_frame_known_issue_devtools(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    geometry_data: Annotated[list, pytest.fixture],
    geometry_data_thinnest_repr: Annotated[str, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    config = OutputConfig(pretty_printer=pretty_printer)

    _assert_pretty_repr_of_draft(
        geometry_data,
        geometry_data_thinnest_repr,
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
        config=OutputConfig(debug_mode=False, pretty_printer=pretty_printer),
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
        config=OutputConfig(debug_mode=True, pretty_printer=pretty_printer),
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
