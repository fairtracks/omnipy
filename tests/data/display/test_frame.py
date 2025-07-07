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
from omnipy.util._pydantic import ValidationError


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


def test_frame() -> None:
    frame: Frame = empty_frame()
    assert frame.dims == Dimensions(width=None, height=None)

    _assert_frame(None, False, False, False)
    _assert_frame(Dimensions(10, None), True, False, False)
    _assert_frame(Dimensions(None, 20), False, True, False)
    _assert_frame(Dimensions(10, 20), True, True, True)


def test_frame_fixed_dims() -> None:
    no_dims_frame: Frame = empty_frame()
    assert no_dims_frame.fixed_width is False
    assert no_dims_frame.fixed_height is False

    width_only_frame = Frame(Dimensions(10, None))
    assert width_only_frame.fixed_width is True
    assert width_only_frame.fixed_height is False

    width_only_frame_not_fixed = Frame(Dimensions(10, None), fixed_width=False)
    assert width_only_frame_not_fixed.fixed_width is False
    assert width_only_frame_not_fixed.fixed_height is False

    height_only_frame = Frame(Dimensions(None, 20))
    assert height_only_frame.fixed_width is False
    assert height_only_frame.fixed_height is True

    height_only_frame_not_fixed = Frame(Dimensions(None, 20), fixed_height=False)
    assert height_only_frame_not_fixed.fixed_width is False
    assert height_only_frame_not_fixed.fixed_height is False

    both_dims_frame = Frame(Dimensions(10, 20))
    assert both_dims_frame.fixed_width is True
    assert both_dims_frame.fixed_height is True

    both_dims_frame_width_not_fixed = Frame(Dimensions(10, 20), fixed_width=False)
    assert both_dims_frame_width_not_fixed.fixed_width is False
    assert both_dims_frame_width_not_fixed.fixed_height is True

    both_dims_frame_width_not_fixed = Frame(Dimensions(10, 20), fixed_height=False)
    assert both_dims_frame_width_not_fixed.fixed_width is True
    assert both_dims_frame_width_not_fixed.fixed_height is False

    both_dims_frame_width_not_fixed = Frame(
        Dimensions(10, 20), fixed_width=False, fixed_height=False)
    assert both_dims_frame_width_not_fixed.fixed_width is False
    assert both_dims_frame_width_not_fixed.fixed_height is False


def test_fail_frame_fixed_dims_if_none() -> None:
    with pytest.raises(ValidationError):
        Frame(Dimensions(None, None), fixed_width=True)

    with pytest.raises(ValidationError):
        Frame(Dimensions(None, None), fixed_height=True)

    with pytest.raises(ValidationError):
        Frame(Dimensions(10, None), fixed_height=True)

    with pytest.raises(ValidationError):
        Frame(Dimensions(None, 20), fixed_width=True)


def test_frame_types() -> None:
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


def test_frame_hashable() -> None:
    frame_1 = empty_frame()
    frame_2 = empty_frame()
    frame_3 = Frame(Dimensions(None, 20))
    frame_4 = Frame(Dimensions(10, None))
    frame_5 = Frame(Dimensions(10, 20))

    assert hash(frame_1) == hash(frame_2)
    assert hash(frame_1) != hash(frame_3) != hash(frame_4) != hash(frame_5)

    frame_6 = Frame(Dimensions(10, 20))

    assert hash(frame_5) == hash(frame_6)

    frame_7 = Frame(Dimensions(10, 20), fixed_width=True, fixed_height=True)
    frame_8 = Frame(Dimensions(10, 20), fixed_width=True, fixed_height=False)
    frame_9 = Frame(Dimensions(10, 20), fixed_width=False, fixed_height=True)
    frame_10 = Frame(Dimensions(10, 20), fixed_width=False, fixed_height=False)

    assert hash(frame_6) == hash(frame_7) != hash(frame_8) != hash(frame_9) != hash(frame_10)


# noinspection PyDataclass
def test_fail_frame_no_assignments() -> None:
    frame = empty_frame()

    with pytest.raises(AttributeError):
        frame.dims = Dimensions(10, 20)  # type: ignore[misc, arg-type]

    with pytest.raises(AttributeError):
        frame.fixed_width = False  # type: ignore[misc]

    with pytest.raises(AttributeError):
        frame.fixed_height = False  # type: ignore[misc]


def test_fail_frame_if_extra_param() -> None:
    with pytest.raises(TypeError):
        Frame(Dimensions(), 123)  # type: ignore

    with pytest.raises(TypeError):
        Frame(Dimensions(), extra=30)  # type: ignore


def test_frame_modified_copy() -> None:
    frame = Frame(Dimensions(10, 20), fixed_width=False, fixed_height=True)

    # Exact copy
    frame_copy = frame.modified_copy()
    assert frame_copy.dims == Dimensions(10, 20)
    assert frame_copy.fixed_width is False
    assert frame_copy.fixed_height is True

    # Copy with edits
    new_frame_only_width = frame.modified_copy(width=30, height=None, fixed_width=True)

    assert new_frame_only_width.dims == Dimensions(30, None)
    assert new_frame_only_width.fixed_width is True
    # Automatically set fixed_height to False as height is None
    assert new_frame_only_width.fixed_height is False

    # Copy with modified width
    new_frame_new_height = frame.modified_copy(height=10, fixed_height=False)

    assert new_frame_new_height.dims == Dimensions(10, 10)
    assert new_frame_new_height.fixed_width is False
    assert new_frame_new_height.fixed_height is False

    # Original frame should remain unchanged
    assert frame.dims == Dimensions(10, 20)
    assert frame.fixed_width is False
    assert frame.fixed_height is True


def test_cropped_dims() -> None:
    # No dimensions defined
    frame: AnyFrame = Frame(Dimensions(None, None), fixed_width=False, fixed_height=False)

    assert frame.crop_width(11) == 11
    assert frame.crop_width(10) == 10
    assert frame.crop_width(9) == 9

    assert frame.crop_height(21) == 21
    assert frame.crop_height(20) == 20
    assert frame.crop_height(19) == 19

    assert frame.crop_dims(Dimensions(11, 21)) == Dimensions(11, 21)
    assert frame.crop_dims(Dimensions(10, 20)) == Dimensions(10, 20)
    assert frame.crop_dims(Dimensions(9, 19)) == Dimensions(9, 19)

    # Both dimensions defined
    frame = Frame(Dimensions(10, 20), fixed_width=False, fixed_height=False)

    assert frame.crop_width(11) == 10
    assert frame.crop_width(10) == 10
    assert frame.crop_width(9) == 9

    assert frame.crop_height(21) == 20
    assert frame.crop_height(20) == 20
    assert frame.crop_height(19) == 19

    assert frame.crop_dims(Dimensions(11, 21)) == Dimensions(10, 20)
    assert frame.crop_dims(Dimensions(10, 20)) == Dimensions(10, 20)
    assert frame.crop_dims(Dimensions(9, 19)) == Dimensions(9, 19)

    # Fixed width
    frame = Frame(Dimensions(10, None), fixed_width=True, fixed_height=False)

    assert frame.crop_width(11) == 10
    assert frame.crop_width(11, ignore_fixed_dims=True) == 10
    assert frame.crop_width(10) == 10
    assert frame.crop_width(10, ignore_fixed_dims=True) == 10
    assert frame.crop_width(9) == 10
    assert frame.crop_width(9, ignore_fixed_dims=True) == 9

    assert frame.crop_height(21) == 21
    assert frame.crop_height(21, ignore_fixed_dims=True) == 21
    assert frame.crop_height(20) == 20
    assert frame.crop_height(20, ignore_fixed_dims=True) == 20
    assert frame.crop_height(19) == 19
    assert frame.crop_height(19, ignore_fixed_dims=True) == 19

    assert frame.crop_dims(Dimensions(11, 21)) == Dimensions(10, 21)
    assert frame.crop_dims(Dimensions(11, 21), ignore_fixed_dims=True) == Dimensions(10, 21)
    assert frame.crop_dims(Dimensions(10, 20)) == Dimensions(10, 20)
    assert frame.crop_dims(Dimensions(10, 20), ignore_fixed_dims=True) == Dimensions(10, 20)
    assert frame.crop_dims(Dimensions(9, 19)) == Dimensions(10, 19)
    assert frame.crop_dims(Dimensions(9, 19), ignore_fixed_dims=True) == Dimensions(9, 19)

    # Fixed height
    frame = Frame(Dimensions(None, 20), fixed_width=False, fixed_height=True)

    assert frame.crop_width(11) == 11
    assert frame.crop_width(11, ignore_fixed_dims=True) == 11
    assert frame.crop_width(10) == 10
    assert frame.crop_width(10, ignore_fixed_dims=True) == 10
    assert frame.crop_width(9) == 9
    assert frame.crop_width(9, ignore_fixed_dims=True) == 9

    assert frame.crop_height(21) == 20
    assert frame.crop_height(21, ignore_fixed_dims=True) == 20
    assert frame.crop_height(20) == 20
    assert frame.crop_height(20, ignore_fixed_dims=True) == 20
    assert frame.crop_height(19) == 20
    assert frame.crop_height(19, ignore_fixed_dims=True) == 19

    assert frame.crop_dims(Dimensions(11, 21)) == Dimensions(11, 20)
    assert frame.crop_dims(Dimensions(11, 21), ignore_fixed_dims=True) == Dimensions(11, 20)
    assert frame.crop_dims(Dimensions(10, 20)) == Dimensions(10, 20)
    assert frame.crop_dims(Dimensions(10, 20), ignore_fixed_dims=True) == Dimensions(10, 20)
    assert frame.crop_dims(Dimensions(9, 19)) == Dimensions(9, 20)
    assert frame.crop_dims(Dimensions(9, 19), ignore_fixed_dims=True) == Dimensions(9, 19)
