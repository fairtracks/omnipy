import os
import re
from textwrap import dedent
from typing import Annotated

import pytest

from omnipy.data._display import pretty_repr, PrettyPrinterLib
from omnipy.data.model import Model


def _harmonize(output: str) -> str:
    return re.sub(r',(\n *[\]\}\)])', '\\1', output)


def _assert_pretty_repr(
    pretty_printer: PrettyPrinterLib,
    data: object,
    expected_output: str,
    **kwargs,
) -> None:
    assert _harmonize(pretty_repr(data, pretty_printer=pretty_printer, **kwargs)) == expected_output


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_multi_line_if_nested(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    _assert_pretty_repr(pretty_printer, 1, '1')
    _assert_pretty_repr(pretty_printer, [1, 2, 3], '[1, 2, 3]')
    _assert_pretty_repr(
        pretty_printer,
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        dedent("""\
        [
          [1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]
        ]"""),
    )
    _assert_pretty_repr(pretty_printer, {1: 2, 3: 4}, '{1: 2, 3: 4}')
    _assert_pretty_repr(
        pretty_printer,
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
    )
    _assert_pretty_repr(
        pretty_printer,
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
    )


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_indent(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:

    _assert_pretty_repr(
        pretty_printer,
        [[1, 2, 3], [[4, 5, 6], [7, 8, 9]]],
        dedent("""\
        [
            [1, 2, 3],
            [
                [4, 5, 6],
                [7, 8, 9]
            ]
        ]"""),
        indent_tab_size=4,
    )


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_max_width(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:

    data_1 = [[1, 2], [[3, 4, 5, 6], [7, 8, 9]]]
    _assert_pretty_repr(
        pretty_printer,
        data_1,
        dedent("""\
        [
          [1, 2],
          [
            [3, 4, 5, 6],
            [7, 8, 9]
          ]
        ]"""),
        max_width=17,
        height=7,
    )
    _assert_pretty_repr(
        pretty_printer,
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
        max_width=16,
        height=12,
    )

    data_2 = [{
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

    _assert_pretty_repr(
        pretty_printer,
        data_2,
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
        max_width=150,
        height=9,
    )
    _assert_pretty_repr(
        pretty_printer,
        data_2,
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
        max_width=149,
        height=9,
    )

    _assert_pretty_repr(
        pretty_printer,
        data_2,
        dedent("""\
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
        ]"""),
        max_width=37,
        height=21,
    )


@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_models(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    class ListOfIntsModel(Model[list[int]]):
        ...

    class ListOfListsOfIntsModel(Model[list[ListOfIntsModel]]):
        ...

    _assert_pretty_repr(
        pretty_printer,
        ListOfListsOfIntsModel([[1, 2, 3], [4, 5, 6]]),
        dedent("""\
        [
          [1, 2, 3],
          [4, 5, 6]
        ]"""),
        debug_mode=False,
    )

    _assert_pretty_repr(
        pretty_printer,
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
        debug_mode=True,
    )


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
The implementation of multi-line adjustment of pretty_repr detects whether the data representation
is nested by counting abbreviations of nested containers by the rich library. If such abbreviation
strings ('(...)', '[...]', or '{...}') are present in the input data, the adjustment algorithm gets
confused.
""")
@pytest.mark.parametrize('pretty_printer', [PrettyPrinterLib.DEVTOOLS, PrettyPrinterLib.RICH])
def test_pretty_repr_multi_line_if_nested_known_issue(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    pretty_printer: PrettyPrinterLib,
) -> None:
    _assert_pretty_repr(pretty_printer, [1, 2, '[...]'], "[1, 2, '[...]']")
