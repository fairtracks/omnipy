from typing import Annotated

import pytest

from omnipy.data._display.dimensions import AnyDimensions, Dimensions
from omnipy.data._display.frame import (AnyFrame,
                                        empty_frame,
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
    if dims is not None:
        frame = Frame(dims)
    else:
        frame = empty_frame()
        dims = Dimensions(width=None, height=None)

    assert frame.dims is not dims
    assert frame.dims == dims

    assert frame_has_width(frame) is exp_frame_has_width
    assert frame_has_height(frame) is exp_frame_has_height
    assert frame_has_width_and_height(frame) is exp_frame_has_width_and_height

    # Static type checkers SHOULD raise errors here
    try:
        _a: int = frame.dims.width  # type: ignore[assignment]  # noqa: F841
        _b: int = frame.dims.height  # type: ignore[assignment]  # noqa: F841
    except TypeError:
        pass

    # Static type checkers SHOULD NOT raise errors here
    if frame_has_width(frame):
        _c: int = frame.dims.width  # noqa: F841

    if frame_has_height(frame):
        _d: int = frame.dims.height  # noqa: F841

    if frame_has_width_and_height(frame):
        _e: int = frame.dims.width  # noqa: F841
        _f: int = frame.dims.height  # noqa: F841


def test_frame(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    frame: Frame = empty_frame()
    assert frame.dims == Dimensions(width=None, height=None)

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


def test_frame_hashable(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    frame_1 = empty_frame()
    frame_2 = empty_frame()
    frame_3 = Frame(Dimensions(None, 20))
    frame_4 = Frame(Dimensions(10, None))
    frame_5 = Frame(Dimensions(10, 20))

    assert hash(frame_1) == hash(frame_2)
    assert hash(frame_1) != hash(frame_3) != hash(frame_4) != hash(frame_5)

    frame_6 = Frame(Dimensions(10, 20))

    assert hash(frame_5) == hash(frame_6)


# noinspection PyDataclass
def test_fail_frame_no_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    frame = empty_frame()

    with pytest.raises(AttributeError):
        frame.dims = Dimensions(10, 20)  # type: ignore[misc, arg-type]


def test_fail_frame_if_extra_param(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        Frame(Dimensions(), 123)  # type: ignore

    with pytest.raises(TypeError):
        Frame(Dimensions(), extra=30)  # type: ignore
