from typing import Annotated, TypedDict

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
        dims.width += 1  # type: ignore[operator]
        dims.height += 1  # type: ignore[operator]
    except TypeError:
        pass

    # Static type checkers SHOULD NOT raise errors here
    if has_width(dims):
        dims.width += 1

    if has_height(dims):
        dims.height += 1

    if has_width_and_height(dims):
        dims.width += 1
        dims.height += 1


def test_dimensions(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_dimensions(None, None, False, False, False)
    _assert_dimensions(10, None, True, False, False)
    _assert_dimensions(None, 20, False, True, False)
    _assert_dimensions(10, 20, True, True, True)
    _assert_dimensions(0, 0, True, True, True)
    _assert_dimensions(10, 0, True, True, True)
    _assert_dimensions(0, 20, True, True, True)
    _assert_dimensions(10, 20, True, True, True)


def test_dimension_types(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
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


def test_fail_dimensions_if_negative(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
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


def test_dimensions_validate_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    dims: Dimensions = Dimensions(width=None, height=10)

    # TODO: Check why dims is type narrowed to `Dimensions[None, int]` here in Pyright
    dims.width = 10  # pyright: ignore [reportAttributeAccessIssue]

    with pytest.raises(ValueError):
        dims.width = -1  # pyright: ignore [reportAttributeAccessIssue]

    dims.height = None  # pyright: ignore [reportAttributeAccessIssue]

    with pytest.raises(ValueError):
        dims.height = 'None'  # type: ignore[assignment]


def test_fail_dimensions_if_extra_param(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
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


# noinspection PyDataclass
def test_dimensions_fit_immutable_properties(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    fit = DimensionsFit(Dimensions(10, 10), Dimensions(10, 10))

    with pytest.raises(AttributeError):
        fit.width = False  # type: ignore

    with pytest.raises(AttributeError):
        fit.height = False  # type: ignore

    with pytest.raises(AttributeError):
        fit.both = False  # type: ignore


def test_dimensions_fit_proportionality(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    def proportionally_wider(a, frame):
        return a.height * frame.width / frame.height < a.width

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
