import re
from typing import Annotated, TypedDict

import pytest

from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.draft import DraftOutput, DraftTextOutput, Frame, OutputConfig
from omnipy.data._display.enum import PrettyPrinterLib
from omnipy.data._display.pretty import pretty_repr_of_draft


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
