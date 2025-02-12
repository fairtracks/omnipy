import os
import re
from textwrap import dedent
from typing import Annotated, TypedDict

import pytest

from omnipy.data._display import (DefinedDimensions,
                                  Dimensions,
                                  DimensionsFit,
                                  DraftOutput,
                                  DraftTextOutput,
                                  Frame,
                                  OutputConfig,
                                  pretty_repr_of_draft,
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


class _DraftOutputKwArgs(TypedDict, total=False):
    frame: Frame
    config: OutputConfig


def _create_draft_output_kwargs(
    frame: Frame | None = None,
    config: OutputConfig | None = None,
) -> _DraftOutputKwArgs:
    kwargs = _DraftOutputKwArgs()

    if frame is not None:
        kwargs['frame'] = frame

    if config is not None:
        kwargs['config'] = config

    return kwargs


def _assert_draft_output(
    content: object,
    frame: Frame | None = None,
    config: OutputConfig | None = None,
) -> None:
    kwargs = _create_draft_output_kwargs(frame, config)

    draft = DraftOutput(content, **kwargs)

    assert draft.content is content

    if frame is not None:
        assert draft.frame is frame
    else:
        assert draft.frame == Frame()

    if config is not None:
        assert draft.config is config
    else:
        assert draft.config == OutputConfig()


def test_draft_output(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_draft_output([1, 2, 3])
    _assert_draft_output([1, 2, 3], frame=Frame(Dimensions(10, 20)))
    _assert_draft_output([1, 2, 3], config=OutputConfig(indent_tab_size=4))
    _assert_draft_output([1, 2, 3],
                         frame=Frame(Dimensions(10, 20)),
                         config=OutputConfig(indent_tab_size=4))

    _assert_draft_output('Some text')
    _assert_draft_output({'a': 1, 'b': 2})
    _assert_draft_output(None)


def _assert_draft_text_output(
    output: str,
    width: int,
    height: int,
    frame_width: int | None = None,
    frame_height: int | None = None,
    fits_width: bool | None = None,
    fits_height: bool | None = None,
    fits_both: bool | None = None,
) -> None:
    draft = DraftTextOutput(output, frame=Frame(Dimensions(frame_width, frame_height)))
    assert draft.dims.width == width
    assert draft.dims.height == height
    assert draft.frame.dims.width == frame_width
    assert draft.frame.dims.height == frame_height

    dims_fit = draft.within_frame
    assert dims_fit.width == fits_width
    assert dims_fit.height == fits_height
    assert dims_fit.both == fits_both


def test_draft_text_output_within_frame(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    out = 'Some output\nAnother line'
    _assert_draft_text_output(
        out, 12, 2, None, None, fits_width=None, fits_height=None, fits_both=None)
    _assert_draft_text_output(
        out, 12, 2, 12, None, fits_width=True, fits_height=None, fits_both=None)
    _assert_draft_text_output(
        out, 12, 2, None, 2, fits_width=None, fits_height=True, fits_both=None)
    _assert_draft_text_output(out, 12, 2, 12, 2, fits_width=True, fits_height=True, fits_both=True)
    _assert_draft_text_output(
        out, 12, 2, 11, None, fits_width=False, fits_height=None, fits_both=None)
    _assert_draft_text_output(
        out, 12, 2, None, 1, fits_width=None, fits_height=False, fits_both=None)
    _assert_draft_text_output(
        out, 12, 2, 12, 1, fits_width=True, fits_height=False, fits_both=False)
    _assert_draft_text_output(
        out, 12, 2, 11, 2, fits_width=False, fits_height=True, fits_both=False)
    _assert_draft_text_output(
        out, 12, 2, 11, 1, fits_width=False, fits_height=False, fits_both=False)


def test_draft_text_output_frame_empty(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_draft_text_output('', 0, 0, None, None, None, None, None)
    _assert_draft_text_output('', 0, 0, 0, None, True, None, None)
    _assert_draft_text_output('', 0, 0, None, 0, None, True, None)
    _assert_draft_text_output('', 0, 0, 0, 0, True, True, True)


def _harmonize(output: str) -> str:
    return re.sub(r',(\n *[\]\}\)])', '\\1', output)


def _assert_pretty_repr_of_draft(
    data: object,
    expected_output: str,
    frame: Frame | None = None,
    config: OutputConfig | None = None,
    within_frame_width: bool = True,
    within_frame_height: bool = True,
) -> None:
    if frame is None:
        frame = Frame(Dimensions(width=80, height=24))

    kwargs = _create_draft_output_kwargs(frame, config)
    in_draft = DraftOutput(data, **kwargs)

    out_draft: DraftTextOutput = pretty_repr_of_draft(in_draft)

    assert _harmonize(out_draft.content) == expected_output
    assert out_draft.within_frame.width is within_frame_width
    assert out_draft.within_frame.height is within_frame_height


def test_pretty_repr_of_draft_init_frame_required(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(ValueError):
        pretty_repr_of_draft(DraftOutput(1))

    out_draft: DraftTextOutput = pretty_repr_of_draft(DraftOutput(1, Frame(Dimensions(80, 24))))
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
