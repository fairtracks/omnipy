from typing import TypedDict

import pytest

from omnipy.data._display.dimensions import (AnyDimensions,
                                             Dimensions,
                                             DimensionsFit,
                                             DimensionsWithHeight,
                                             DimensionsWithWidth,
                                             DimensionsWithWidthAndHeight,
                                             has_height,
                                             has_width,
                                             has_width_and_height,
                                             Proportionally,
                                             UndefinedDimensions)


class _WidthAndHeightKwargs(TypedDict, total=False):
    width: int | None
    height: int | None


def _assert_dimensions(
    width: int | None,
    height: int | None,
    exp_has_width: bool,
    exp_has_height: bool,
    exp_has_width_and_height: bool,
) -> None:
    kwargs = _WidthAndHeightKwargs()

    kwargs['width'] = width

    kwargs['height'] = height

    dims = Dimensions(**kwargs)

    assert dims.width == width
    assert dims.height == height

    assert has_width(dims) is exp_has_width
    assert has_height(dims) is exp_has_height
    assert has_width_and_height(dims) is exp_has_width_and_height

    # Static type checkers SHOULD raise errors here
    try:
        _a: int = dims.width  # type: ignore[assignment]  # noqa: F841
        _b: int = dims.height  # type: ignore[assignment]  # noqa: F841
    except TypeError:
        pass

    # Static type checkers SHOULD NOT raise errors here
    if has_width(dims):
        _c: int = dims.width  # noqa: F841

    if has_height(dims):
        _d: int = dims.height  # noqa: F841

    if has_width_and_height(dims):
        _e: int = dims.width  # noqa: F841
        _f: int = dims.height  # noqa: F841


def test_dimensions() -> None:
    _assert_dimensions(None, None, False, False, False)
    _assert_dimensions(10, None, True, False, False)
    _assert_dimensions(None, 20, False, True, False)
    _assert_dimensions(10, 20, True, True, True)
    _assert_dimensions(0, 0, True, True, True)
    _assert_dimensions(10, 0, True, True, True)
    _assert_dimensions(0, 20, True, True, True)
    _assert_dimensions(10, 20, True, True, True)


def test_dimension_types() -> None:
    def undefined_dims_func(dims: UndefinedDimensions) -> None:
        ...

    def dims_with_widths_func(dims: DimensionsWithWidth) -> None:
        ...

    def dims_with_heights_func(dims: DimensionsWithHeight) -> None:
        ...

    def dims_with_width_and_height_func(dims: DimensionsWithWidthAndHeight) -> None:
        ...

    def any_dims_func(dims: AnyDimensions) -> None:
        ...

    # Static type checkers SHOULD NOT raise errors here
    undefined_dims_func(Dimensions(None, None))
    any_dims_func(Dimensions(None, None))

    dims_with_widths_func(Dimensions(10, None))
    any_dims_func(Dimensions(10, None))

    dims_with_heights_func(Dimensions(None, 20))
    any_dims_func(Dimensions(None, 20))

    dims_with_widths_func(Dimensions(10, 20))
    dims_with_heights_func(Dimensions(10, 20))
    dims_with_width_and_height_func(Dimensions(10, 20))
    any_dims_func(Dimensions(10, 20))

    # Static type checkers SHOULD raise errors here
    dims_with_widths_func(Dimensions(None, None))  # type: ignore[arg-type]
    dims_with_heights_func(Dimensions(None, None))  # type: ignore[arg-type]
    dims_with_width_and_height_func(Dimensions(None, None))  # type: ignore[arg-type]

    undefined_dims_func(Dimensions(10, None))  # type: ignore[arg-type]
    dims_with_heights_func(Dimensions(10, None))  # type: ignore[arg-type]
    dims_with_width_and_height_func(Dimensions(10, None))  # type: ignore[arg-type]

    undefined_dims_func(Dimensions(None, 20))  # type: ignore[arg-type]
    dims_with_widths_func(Dimensions(None, 20))  # type: ignore[arg-type]
    dims_with_width_and_height_func(Dimensions(None, 20))  # type: ignore[arg-type]

    undefined_dims_func(Dimensions(10, 20))  # type: ignore[arg-type]


def test_fail_dimensions_if_negative() -> None:
    with pytest.raises(ValueError):
        Dimensions(-1, None)

    with pytest.raises(ValueError):
        Dimensions(-1, 0)

    with pytest.raises(ValueError):
        Dimensions(None, -1)

    with pytest.raises(ValueError):
        Dimensions(0, -1)

    with pytest.raises(ValueError):
        Dimensions(-1, -1)


def test_dimensions_hashable() -> None:
    dims_1 = Dimensions(None, None)
    dims_2 = Dimensions(None, None)
    dims_3 = Dimensions(10, None)
    dims_4 = Dimensions(None, 20)
    dims_5 = Dimensions(10, 20)

    assert hash(dims_1) == hash(dims_2)
    assert hash(dims_1) != hash(dims_3) != hash(dims_4) != hash(dims_5)

    dims_6 = Dimensions(10, 20)

    assert hash(dims_5) == hash(dims_6)


# noinspection PyDataclass
def test_fail_dimensions_no_assignments() -> None:
    dims: Dimensions = Dimensions(width=None, height=10)

    with pytest.raises(AttributeError):
        # TODO: Check why dims is type narrowed to `Dimensions[None, int]` here in Pyright
        dims.width = 10  # type: ignore[misc]

    with pytest.raises(AttributeError):
        dims.height = None  # type: ignore[misc]


def test_fail_dimensions_if_extra_param() -> None:
    with pytest.raises(TypeError):
        Dimensions(10, 20, 30)  # type: ignore

    with pytest.raises(TypeError):
        Dimensions(10, 20, extra=30)  # type: ignore


def _assert_within_frame(width: int,
                         height: int,
                         frame_width: int | None,
                         frame_height: int | None,
                         fits_width: bool | None,
                         fits_height: bool | None,
                         fits_both: bool | None):
    fit = DimensionsFit(Dimensions(width, height), Dimensions(frame_width, frame_height))
    assert fit.width is fits_width
    assert fit.height is fits_height
    assert fit.both is fits_both


def test_dimensions_fit() -> None:
    _assert_within_frame(10, 10, None, None, None, None, None)
    _assert_within_frame(10, 10, 10, None, True, None, None)
    _assert_within_frame(10, 10, None, 10, None, True, None)
    _assert_within_frame(10, 10, 10, 10, True, True, True)
    _assert_within_frame(11, 10, 10, 10, False, True, False)
    _assert_within_frame(10, 11, 10, 10, True, False, False)
    _assert_within_frame(11, 11, 10, 10, False, False, False)


def test_dimensions_fit_zeros() -> None:
    _assert_within_frame(0, 0, None, None, None, None, None)
    _assert_within_frame(0, 0, 0, None, True, None, None)
    _assert_within_frame(0, 0, None, 0, None, True, None)
    _assert_within_frame(0, 0, 0, 0, True, True, True)
    _assert_within_frame(0, 0, 1, None, True, None, None)
    _assert_within_frame(0, 0, None, 1, None, True, None)
    _assert_within_frame(0, 0, 1, 1, True, True, True)


# noinspection PyDataclass
def test_dimensions_fit_immutable_properties() -> None:
    fit = DimensionsFit(Dimensions(10, 10), Dimensions(10, 10))

    with pytest.raises(AttributeError):
        fit.width = False  # type: ignore

    with pytest.raises(AttributeError):
        fit.height = False  # type: ignore

    with pytest.raises(AttributeError):
        fit.both = False  # type: ignore


def test_dimensions_fit_proportionality_basic() -> None:
    Dims = Dimensions

    assert DimensionsFit(Dims(10, 10), Dims(20, 20)).proportionality is Proportionally.SAME
    assert DimensionsFit(Dims(10, 11), Dims(20, 20)).proportionality is Proportionally.THINNER
    assert DimensionsFit(Dims(11, 10), Dims(20, 20)).proportionality is Proportionally.WIDER
    assert DimensionsFit(Dims(11, 10), Dims(21, 20)).proportionality is Proportionally.WIDER
    assert DimensionsFit(Dims(11, 10), Dims(22, 20)).proportionality is Proportionally.SAME
    assert DimensionsFit(Dims(11, 10), Dims(22, 19)).proportionality is Proportionally.THINNER

    assert DimensionsFit(Dims(10, 10), Dims(None, None)).proportionality is None
    assert DimensionsFit(Dims(10, 10), Dims(None, 20)).proportionality is None
    assert DimensionsFit(Dims(10, 10), Dims(10, None)).proportionality is None


def test_dimensions_fit_proportionality_large_deviations() -> None:
    Dims = Dimensions

    # Large deviations of proportionality give much wider or much thinner
    assert DimensionsFit(Dims(10, 30), Dims(20, 20)).proportionality is Proportionally.MUCH_THINNER
    assert DimensionsFit(Dims(30, 10), Dims(20, 20)).proportionality is Proportionally.MUCH_WIDER

    # Proportionality is thinner or wider if the deviation is not too large
    assert DimensionsFit(Dims(10, 30), Dims(20, 40)).proportionality is Proportionally.THINNER
    assert DimensionsFit(Dims(30, 10), Dims(40, 20)).proportionality is Proportionally.WIDER

    # Threshold for large deviations in proportionality is related to the relative size of the frame
    assert DimensionsFit(Dims(10, 30), Dims(40, 40)).proportionality is Proportionally.THINNER
    assert DimensionsFit(Dims(30, 10), Dims(40, 40)).proportionality is Proportionally.WIDER

    # Threshold for large deviations in proportionality can be adjusted with proportional_freedom
    assert DimensionsFit(Dims(10, 30), Dims(40, 40), proportional_freedom=1.4).proportionality \
           is Proportionally.MUCH_THINNER
    assert DimensionsFit(Dims(30, 10), Dims(40, 40), proportional_freedom=1.4).proportionality \
           is Proportionally.MUCH_WIDER

    # Proportional_freedom adjustment have less effect on larger relative frame sizes
    assert DimensionsFit(Dims(10, 30), Dims(200, 200)).proportionality is Proportionally.THINNER
    assert DimensionsFit(Dims(30, 10), Dims(200, 200)).proportionality is Proportionally.WIDER

    assert DimensionsFit(Dims(10, 30), Dims(200, 200), proportional_freedom=1.4).proportionality \
           is Proportionally.THINNER
    assert DimensionsFit(Dims(30, 10), Dims(200, 200), proportional_freedom=1.4).proportionality \
           is Proportionally.WIDER


def test_dimensions_fit_repr() -> None:
    # Test basic case with all properties defined
    fit = DimensionsFit(Dimensions(10, 10), Dimensions(20, 20))
    assert repr(fit) == \
        'DimensionsFit(width=True, height=True, both=True, proportionality=Proportionally.SAME)'

    # Test case where dimensions don't fit
    fit = DimensionsFit(Dimensions(25, 15), Dimensions(20, 20))
    assert repr(fit) == \
        'DimensionsFit(width=False, height=True, both=False, proportionality=Proportionally.WIDER)'

    # Test case with None frame width
    fit = DimensionsFit(Dimensions(10, 10), Dimensions(None, 20))
    assert repr(fit) == 'DimensionsFit(width=None, height=True, both=None, proportionality=None)'
    # Test case with None frame height
    fit = DimensionsFit(Dimensions(10, 10), Dimensions(20, None))
    assert repr(fit) == 'DimensionsFit(width=True, height=None, both=None, proportionality=None)'

    # Test case with both frame dimensions None
    fit = DimensionsFit(Dimensions(10, 10), Dimensions(None, None))
    assert repr(fit) == 'DimensionsFit(width=None, height=None, both=None, proportionality=None)'

    # Test case with zero dimensions
    fit = DimensionsFit(Dimensions(0, 0), Dimensions(10, 10))
    assert repr(fit) == 'DimensionsFit(width=True, height=True, both=True, proportionality=None)'

    # Test thinner proportionality
    fit = DimensionsFit(Dimensions(10, 15), Dimensions(20, 20))
    assert repr(fit) == \
        'DimensionsFit(width=True, height=True, both=True, proportionality=Proportionally.THINNER)'
