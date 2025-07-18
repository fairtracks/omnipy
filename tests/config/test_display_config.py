import pydantic as pyd
from typing_extensions import ClassVar, override

from omnipy import RecommendedColorStyles
from omnipy.config.data import ColorConfig, DimsModeConfig
from omnipy.shared.enums.colorstyles import DarkHighContrastColorStyles
from omnipy.shared.enums.display import DisplayColorSystem, DisplayDimensionsUpdateMode


class NoSizeDisplayDimsModeConfig(DimsModeConfig):
    @classmethod
    @override
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        return None, None


def test_dims_mode_config_no_display_dims_size_set() -> None:
    no_size_display_config = NoSizeDisplayDimsModeConfig()
    assert no_size_display_config.width == 80
    assert no_size_display_config.height == 24
    assert no_size_display_config.dims_mode is DisplayDimensionsUpdateMode.AUTO

    no_size_display_config.width = 100
    assert no_size_display_config.width == 100

    no_size_display_config.height = 100
    assert no_size_display_config.height == 100

    assert no_size_display_config.dims_mode is DisplayDimensionsUpdateMode.AUTO

    no_size_display_config_auto = NoSizeDisplayDimsModeConfig(width=100, height=100)
    assert no_size_display_config_auto.width == 100
    assert no_size_display_config_auto.height == 100
    assert no_size_display_config_auto.dims_mode is DisplayDimensionsUpdateMode.AUTO

    no_size_display_config_fixed = NoSizeDisplayDimsModeConfig(
        width=100,
        height=100,
        dims_mode=DisplayDimensionsUpdateMode.FIXED,
    )
    assert no_size_display_config_fixed.width == 100
    assert no_size_display_config_fixed.height == 100
    assert no_size_display_config_fixed.dims_mode is DisplayDimensionsUpdateMode.FIXED


class BothSizesdisplayDimsModeConfig(DimsModeConfig):
    display_width: ClassVar[pyd.NonNegativeInt] = 200
    display_height: ClassVar[pyd.NonNegativeInt] = 200

    @classmethod
    @override
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        return cls.display_width, cls.display_height


def test_dims_mode_config_both_display_dims_size_set() -> None:
    both_sizes_display_config = BothSizesdisplayDimsModeConfig()
    assert both_sizes_display_config.width == 200
    assert both_sizes_display_config.height == 200
    assert both_sizes_display_config.dims_mode is DisplayDimensionsUpdateMode.AUTO

    both_sizes_display_config.width = 100
    assert both_sizes_display_config.width == 200

    both_sizes_display_config.height = 100
    assert both_sizes_display_config.height == 200

    assert both_sizes_display_config.dims_mode is DisplayDimensionsUpdateMode.AUTO

    both_sizes_display_config_auto = BothSizesdisplayDimsModeConfig(
        width=100,
        height=100,
    )
    assert both_sizes_display_config_auto.width == 200
    assert both_sizes_display_config_auto.height == 200
    assert both_sizes_display_config_auto.dims_mode is DisplayDimensionsUpdateMode.AUTO

    BothSizesdisplayDimsModeConfig.display_width = 50
    BothSizesdisplayDimsModeConfig.display_height = 50

    assert both_sizes_display_config_auto.width == 50
    assert both_sizes_display_config_auto.height == 50

    both_sizes_display_config_fixed = BothSizesdisplayDimsModeConfig(
        width=100,
        height=100,
        dims_mode=DisplayDimensionsUpdateMode.FIXED,
    )
    assert both_sizes_display_config_fixed.width == 100
    assert both_sizes_display_config_fixed.height == 100
    assert both_sizes_display_config_fixed.dims_mode is DisplayDimensionsUpdateMode.FIXED


class OnlyWidthDisplayDimsModeConfig(DimsModeConfig):
    display_width: ClassVar[pyd.NonNegativeInt] = 200
    display_height: ClassVar[pyd.NonNegativeInt | None] = None

    @classmethod
    @override
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        return cls.display_width, cls.display_height


def test_dims_mode_config_only_width_set() -> None:
    only_width_display_config = OnlyWidthDisplayDimsModeConfig()
    assert only_width_display_config.width == 200
    assert only_width_display_config.height == 24
    assert only_width_display_config.dims_mode is DisplayDimensionsUpdateMode.AUTO

    only_width_display_config.width = 100
    assert only_width_display_config.width == 200

    only_width_display_config.height = 24
    assert only_width_display_config.height == 24

    assert only_width_display_config.dims_mode is DisplayDimensionsUpdateMode.AUTO

    only_width_display_config_auto = OnlyWidthDisplayDimsModeConfig(
        width=100,
        height=100,
    )
    assert only_width_display_config_auto.width == 200
    assert only_width_display_config_auto.height == 100
    assert only_width_display_config_auto.dims_mode is DisplayDimensionsUpdateMode.AUTO

    OnlyWidthDisplayDimsModeConfig.display_width = 50

    assert only_width_display_config_auto.width == 50
    assert only_width_display_config_auto.height == 100

    only_width_display_config_fixed = OnlyWidthDisplayDimsModeConfig(
        width=100,
        height=100,
        dims_mode=DisplayDimensionsUpdateMode.FIXED,
    )
    assert only_width_display_config_fixed.width == 100
    assert only_width_display_config_fixed.height == 100
    assert only_width_display_config_fixed.dims_mode is DisplayDimensionsUpdateMode.FIXED


def test_color_config_auto_style_ansi() -> None:
    color_config = ColorConfig()

    assert color_config.system is DisplayColorSystem.AUTO
    assert color_config.dark_background is False
    assert color_config.solid_background is False
    # ANSI_LIGHT is the default style based on the above defaults
    assert color_config.style is RecommendedColorStyles.ANSI_LIGHT

    color_config.dark_background = True
    assert color_config.style is RecommendedColorStyles.ANSI_DARK

    color_config.system = DisplayColorSystem.ANSI_16
    assert color_config.style is RecommendedColorStyles.ANSI_DARK


def test_color_config_auto_style_more_colors() -> None:
    color_config = ColorConfig(system=DisplayColorSystem.ANSI_256)
    assert color_config.style is RecommendedColorStyles.OMNIPY_SELENIZED_WHITE

    color_config.system = DisplayColorSystem.ANSI_RGB
    assert color_config.style is RecommendedColorStyles.OMNIPY_SELENIZED_WHITE

    color_config.solid_background = True
    assert color_config.style is RecommendedColorStyles.OMNIPY_SELENIZED_LIGHT

    color_config.dark_background = True
    assert color_config.style is RecommendedColorStyles.OMNIPY_SELENIZED_DARK

    color_config.solid_background = False
    assert color_config.style is RecommendedColorStyles.OMNIPY_SELENIZED_BLACK


def test_color_config_specific_not_recommended_style() -> None:
    color_config = ColorConfig(
        system=DisplayColorSystem.ANSI_RGB, style=DarkHighContrastColorStyles.GOTHAM_T16)
    # If a specific style is set, it overrides the automatic style selection.
    assert color_config.style is DarkHighContrastColorStyles.GOTHAM_T16

    color_config.system = DisplayColorSystem.ANSI_16
    color_config.dark_background = False
    color_config.solid_background = True
    assert color_config.style is DarkHighContrastColorStyles.GOTHAM_T16


def test_color_config_specific_style_recommended_style() -> None:
    color_config = ColorConfig(style=RecommendedColorStyles.OMNIPY_SELENIZED_LIGHT)
    # Automatic style selection only applies when style is set to auto or
    # one of the recommended styles.
    assert color_config.style is RecommendedColorStyles.ANSI_LIGHT
