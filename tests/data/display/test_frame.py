from typing import Annotated

import pytest

from omnipy.data._display.dimensions import AnyDimensions, Dimensions
from omnipy.data._display.frame import (AnyFrame,
                                        Frame,
                                        frame_has_height,
                                        frame_has_width,
                                        frame_has_width_and_height,
                                        FrameWithHeight,
                                        FrameWithWidth,
                                        FrameWithWidthAndHeight,
                                        UndefinedFrame)


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

    assert frame.dims is not dims
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
