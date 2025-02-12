import os
import re
from textwrap import dedent
from typing import Annotated

import pytest

from omnipy.data._display import (DefinedDimensions,
                                  Dimensions,
                                  DimensionsFit,
                                  Frame,
                                  OutputConfig,
                                  pretty_repr,
                                  PrettyPrinterLib)
from omnipy.data.model import Model


def _assert_dimensions(dims_cls: type[Dimensions], width: int | None, height: int | None) -> None:
    dims = dims_cls(width, height)
    assert dims.width == width
    assert dims.height == height


def test_dimensions(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_dimensions(Dimensions, None, None)
    _assert_dimensions(Dimensions, 10, None)
    _assert_dimensions(Dimensions, None, 20)
    _assert_dimensions(Dimensions, 10, 20)
    _assert_dimensions(Dimensions, 0, 0)
    _assert_dimensions(Dimensions, 10, 0)
    _assert_dimensions(Dimensions, 0, 20)
    _assert_dimensions(Dimensions, 10, 20)


def test_defined_dimensions(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_dimensions(DefinedDimensions, 10, 20)
    _assert_dimensions(DefinedDimensions, 0, 0)
    _assert_dimensions(DefinedDimensions, 10, 0)
    _assert_dimensions(DefinedDimensions, 0, 20)
    _assert_dimensions(DefinedDimensions, 10, 20)


def test_fail_defined_dimensions_if_none(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(ValueError):
        DefinedDimensions(None, None)

    with pytest.raises(ValueError):
        DefinedDimensions(10, None)

    with pytest.raises(ValueError):
        DefinedDimensions(None, 20)


@pytest.mark.parametrize('dims_cls', [Dimensions, DefinedDimensions])
def test_fail_dimensions_if_negative(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    dims_cls: type[Dimensions],
) -> None:
    with pytest.raises(ValueError):
        dims_cls(-1, None)

    with pytest.raises(ValueError):
        dims_cls(-1, 0)

    with pytest.raises(ValueError):
        dims_cls(None, -1)

    with pytest.raises(ValueError):
        dims_cls(0, -1)

    with pytest.raises(ValueError):
        dims_cls(-1, -1)


@pytest.mark.parametrize('dims_cls', [Dimensions, DefinedDimensions])
def test_fail_dimensions_if_extra_param(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    dims_cls: type[Dimensions],
) -> None:
    with pytest.raises(TypeError):
        dims_cls(10, 20, 30)  # type: ignore

    with pytest.raises(TypeError):
        dims_cls(10, 20, extra=30)  # type: ignore


def _assert_within_frame(width: int | None,
                         height: int | None,
                         frame_width: int | None,
                         frame_height: int | None,
                         fits_width: bool | None,
                         fits_height: bool | None,
                         fits_both: bool | None):
    fit = DimensionsFit(DefinedDimensions(width, height), Dimensions(frame_width, frame_height))
    assert fit.width is fits_width
    assert fit.height is fits_height
    assert fit.both is fits_both


def test_dimensions_fit(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_within_frame(10, 10, None, None, None, None, None)
    _assert_within_frame(10, 10, 10, None, True, None, None)
    _assert_within_frame(10, 10, None, 10, None, True, None)
    _assert_within_frame(10, 10, 10, 10, True, True, True)
    _assert_within_frame(11, 10, 10, 10, False, True, False)
    _assert_within_frame(10, 11, 10, 10, True, False, False)
    _assert_within_frame(11, 11, 10, 10, False, False, False)


def test_dimensions_fit_zeros(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_within_frame(0, 0, None, None, None, None, None)
    _assert_within_frame(0, 0, 0, None, True, None, None)
    _assert_within_frame(0, 0, None, 0, None, True, None)
    _assert_within_frame(0, 0, 0, 0, True, True, True)
    _assert_within_frame(0, 0, 1, None, True, None, None)
    _assert_within_frame(0, 0, None, 1, None, True, None)
    _assert_within_frame(0, 0, 1, 1, True, True, True)


def test_fail_dimensions_fit_direct_init_vals(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    with pytest.raises(ValueError):
        DimensionsFit(width=True, height=True)  # type: ignore

    with pytest.raises(ValueError):
        DimensionsFit(width=True)  # type: ignore

    with pytest.raises(ValueError):
        DimensionsFit(height=True)  # type: ignore

    with pytest.raises(ValueError):
        DimensionsFit(both=True)  # type: ignore


# noinspection PyDataclass
def test_dimensions_fit_immutable_properties(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    fit = DimensionsFit(DefinedDimensions(10, 10), Dimensions(10, 10))

    with pytest.raises(AttributeError):
        fit.width = False  # type: ignore

    with pytest.raises(AttributeError):
        fit.height = False  # type: ignore

    with pytest.raises(AttributeError):
        fit.both = False  # type: ignore


def test_output_config(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    config = OutputConfig(
        indent_tab_size=4, debug_mode=True, pretty_printer=PrettyPrinterLib.DEVTOOLS)
    assert config.indent_tab_size == 4
    assert config.debug_mode is True
    assert config.pretty_printer is PrettyPrinterLib.DEVTOOLS

    config = OutputConfig(
        indent_tab_size=0,
        debug_mode=False,
        pretty_printer='rich',  # type: ignore[arg-type]
    )
    assert config.indent_tab_size == 0
    assert config.debug_mode is False
    assert config.pretty_printer is PrettyPrinterLib.RICH


def test_output_config_mutable_properties(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    config = OutputConfig(indent_tab_size=4, debug_mode=True)

    config.indent_tab_size = 3
    assert config.indent_tab_size == 3

    config.debug_mode = False
    assert config.debug_mode is False

    config.pretty_printer = PrettyPrinterLib.DEVTOOLS
    assert config.pretty_printer is PrettyPrinterLib.DEVTOOLS


def test_fail_output_config_if_invalid_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(ValueError):
        OutputConfig(indent_tab_size=-1)

    with pytest.raises(ValueError):
        OutputConfig(indent_tab_size=None)  # type: ignore

    with pytest.raises(ValueError):
        OutputConfig(debug_mode=None)  # type: ignore

    with pytest.raises(ValueError):
        OutputConfig(pretty_printer=None)  # type: ignore


def test_output_config_default_values(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    config = OutputConfig()
    assert config.indent_tab_size == 2
    assert config.debug_mode is False
    assert config.pretty_printer is PrettyPrinterLib.RICH


def test_fail_output_config_if_extra_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        OutputConfig(indent_tab_size=4, debug_mode=True, extra=2)  # type: ignore


def test_fail_output_config_no_positional_parameters(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        OutputConfig(2, True)  # type: ignore


def test_frame(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    frame = Frame()
    assert frame.dims.width is None
    assert frame.dims.height is None

    dims = Dimensions(10, 20)

    frame = Frame(dims)
    assert frame.dims is dims


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
