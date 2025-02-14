from typing import Annotated, TypedDict

import pytest

from omnipy.data._display.dimensions import AnyDimensions, Dimensions
from omnipy.data._display.draft import (AnyFrame,
                                        DraftMonospacedOutput,
                                        DraftOutput,
                                        Frame,
                                        frame_has_height,
                                        frame_has_width,
                                        frame_has_width_and_height,
                                        FrameWithHeight,
                                        FrameWithWidth,
                                        FrameWithWidthAndHeight,
                                        OutputConfig,
                                        UndefinedFrame)
from omnipy.data._display.enum import PrettyPrinterLib


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


def _assert_frame(
    dims: AnyDimensions | None,
    exp_frame_has_width: bool,
    exp_frame_has_height: bool,
    exp_frame_has_width_and_height: bool,
) -> None:
    if dims is None:
        frame = Frame()
        dims = Dimensions()
    else:
        frame = Frame(dims)
        assert frame.dims is dims
    assert frame.dims == dims

    assert frame_has_width(frame) is exp_frame_has_width
    assert frame_has_height(frame) is exp_frame_has_height
    assert frame_has_width_and_height(frame) is exp_frame_has_width_and_height

    # Static type checkers SHOULD raise errors here
    try:
        frame.dims.width += 1  # type: ignore[operator]
        frame.dims.height += 1  # type: ignore[operator]
    except TypeError:
        pass

    # Static type checkers SHOULD NOT raise errors here
    if frame_has_width(frame):
        frame.dims.width += 1

    if frame_has_height(frame):
        frame.dims.height += 1

    if frame_has_width_and_height(frame):
        frame.dims.width += 1
        frame.dims.height += 1


def test_frame(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    frame: Frame = Frame()
    assert frame.dims == Dimensions()

    _assert_frame(None, False, False, False)
    _assert_frame(Dimensions(10, None), True, False, False)
    _assert_frame(Dimensions(None, 20), False, True, False)
    _assert_frame(Dimensions(10, 20), True, True, True)


def test_frame_types(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    def undefined_frame_func(dims: UndefinedFrame) -> None:
        ...

    def frame_with_widths_func(dims: FrameWithWidth) -> None:
        ...

    def frame_with_heights_func(dims: FrameWithHeight) -> None:
        ...

    def frame_with_width_and_height_func(dims: FrameWithWidthAndHeight) -> None:
        ...

    def any_frame_func(dims: AnyFrame) -> None:
        ...

    # Static type checkers SHOULD NOT raise errors here
    undefined_frame_func(Frame(Dimensions(None, None)))
    any_frame_func(Frame(Dimensions(None, None)))

    frame_with_widths_func(Frame(Dimensions(10, None)))
    any_frame_func(Frame(Dimensions(10, None)))

    frame_with_heights_func(Frame(Dimensions(None, 20)))
    any_frame_func(Frame(Dimensions(None, 20)))

    frame_with_widths_func(Frame(Dimensions(10, 20)))
    frame_with_heights_func(Frame(Dimensions(10, 20)))
    frame_with_width_and_height_func(Frame(Dimensions(10, 20)))
    any_frame_func(Frame(Dimensions(10, 20)))

    # Static type checkers SHOULD raise errors here
    frame_with_widths_func(Frame(Dimensions(None, None)))  # type: ignore[arg-type]
    frame_with_heights_func(Frame(Dimensions(None, None)))  # type: ignore[arg-type]
    frame_with_width_and_height_func(Frame(Dimensions(None, None)))  # type: ignore[arg-type]

    undefined_frame_func(Frame(Dimensions(10, None)))  # type: ignore[arg-type]
    frame_with_heights_func(Frame(Dimensions(10, None)))  # type: ignore[arg-type]
    frame_with_width_and_height_func(Frame(Dimensions(10, None)))  # type: ignore[arg-type]

    undefined_frame_func(Frame(Dimensions(None, 20)))  # type: ignore[arg-type]
    frame_with_widths_func(Frame(Dimensions(None, 20)))  # type: ignore[arg-type]
    frame_with_width_and_height_func(Frame(Dimensions(None, 20)))  # type: ignore[arg-type]

    undefined_frame_func(Frame(Dimensions(10, 20)))  # type: ignore[arg-type]


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
    frame: Frame | None,
    config: OutputConfig | None,
) -> None:
    kwargs = _create_draft_output_kwargs(frame, config)
    draft = DraftOutput(content, **kwargs)

    if frame is None:
        frame = Frame()
    else:
        assert draft.frame is frame

    if config is None:
        config = OutputConfig()
    else:
        assert draft.content is content

    assert draft.frame == frame
    assert draft.config == config


def test_draft_output(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_draft_output('Some text', None, None)
    _assert_draft_output([1, 2, 3], Frame(Dimensions(None, None)), None)
    _assert_draft_output([1, 2, 3], Frame(Dimensions(10, None)), None)
    _assert_draft_output([1, 2, 3], Frame(Dimensions(None, 20)), None)
    _assert_draft_output([1, 2, 3], Frame(Dimensions(10, 20)), None)
    _assert_draft_output({'a': 1, 'b': 2}, None, OutputConfig(indent_tab_size=4))
    _assert_draft_output(None, Frame(Dimensions(20, 10)), OutputConfig(indent_tab_size=4))


def _assert_draft_monospaced_output(
    output: str,
    width: int,
    height: int,
    frame_width: int | None = None,
    frame_height: int | None = None,
    fits_width: bool | None = None,
    fits_height: bool | None = None,
    fits_both: bool | None = None,
) -> None:
    draft = DraftMonospacedOutput(output, frame=Frame(Dimensions(frame_width, frame_height)))

    assert draft.dims.width == width
    assert draft.dims.height == height
    assert draft.frame.dims.width == frame_width
    assert draft.frame.dims.height == frame_height

    dims_fit = draft.within_frame
    assert dims_fit.width == fits_width
    assert dims_fit.height == fits_height
    assert dims_fit.both == fits_both


def test_draft_monospaced_output_within_frame(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    out = 'Some output\nAnother line'
    _assert_draft_monospaced_output(
        out, 12, 2, None, None, fits_width=None, fits_height=None, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, 12, None, fits_width=True, fits_height=None, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, None, 2, fits_width=None, fits_height=True, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, 12, 2, fits_width=True, fits_height=True, fits_both=True)
    _assert_draft_monospaced_output(
        out, 12, 2, 11, None, fits_width=False, fits_height=None, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, None, 1, fits_width=None, fits_height=False, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, 12, 1, fits_width=True, fits_height=False, fits_both=False)
    _assert_draft_monospaced_output(
        out, 12, 2, 11, 2, fits_width=False, fits_height=True, fits_both=False)
    _assert_draft_monospaced_output(
        out, 12, 2, 11, 1, fits_width=False, fits_height=False, fits_both=False)


def test_draft_monospaced_output_frame_empty(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_draft_monospaced_output('', 0, 0, None, None, None, None, None)
    _assert_draft_monospaced_output('', 0, 0, 0, None, True, None, None)
    _assert_draft_monospaced_output('', 0, 0, None, 0, None, True, None)
    _assert_draft_monospaced_output('', 0, 0, 0, 0, True, True, True)


def test_draft_monospaced_output_variable_width_chars(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    # Mandarin Chinese characters are double-width
    _assert_draft_monospaced_output('北京', 4, 1)

    # Null character is zero-width
    _assert_draft_monospaced_output('\0北京\n北京', 4, 2)

    # Soft hyphen character is zero-width
    _assert_draft_monospaced_output('hyphe\xad\nnate', 5, 2)
