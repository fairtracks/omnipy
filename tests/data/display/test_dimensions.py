from typing import Annotated

import pytest

from omnipy.data._display.dimensions import DefinedDimensions, Dimensions, DimensionsFit


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
        DefinedDimensions(None, None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        DefinedDimensions(10, None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        DefinedDimensions(None, 20)  # type: ignore[arg-type]


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


def _assert_within_frame(width: int,
                         height: int,
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
