import pydantic as pyd
from typing_extensions import ClassVar, override

from omnipy.config.data import DimsModeConfig
from omnipy.shared.enums import DisplayDimensionsUpdateMode


class NoSizeDisplayDimsModeConfig(DimsModeConfig):
    @classmethod
    @override
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        return None, None


def test_dims_mode_config_no_display_dims_size_set():
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


def test_dims_mode_config_both_display_dims_size_set():
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


class OnlyWidthdisplayDimsModeConfig(DimsModeConfig):
    display_width: ClassVar[pyd.NonNegativeInt] = 200
    display_height: ClassVar[pyd.NonNegativeInt | None] = None

    @classmethod
    @override
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        return cls.display_width, cls.display_height


def test_dims_mode_config_only_width_set():
    only_width_display_config = OnlyWidthdisplayDimsModeConfig()
    assert only_width_display_config.width == 200
    assert only_width_display_config.height == 24
    assert only_width_display_config.dims_mode is DisplayDimensionsUpdateMode.AUTO

    only_width_display_config.width = 100
    assert only_width_display_config.width == 200

    only_width_display_config.height = 24
    assert only_width_display_config.height == 24

    assert only_width_display_config.dims_mode is DisplayDimensionsUpdateMode.AUTO

    only_width_display_config_auto = OnlyWidthdisplayDimsModeConfig(
        width=100,
        height=100,
    )
    assert only_width_display_config_auto.width == 200
    assert only_width_display_config_auto.height == 100
    assert only_width_display_config_auto.dims_mode is DisplayDimensionsUpdateMode.AUTO

    OnlyWidthdisplayDimsModeConfig.display_width = 50

    assert only_width_display_config_auto.width == 50
    assert only_width_display_config_auto.height == 100

    only_width_display_config_fixed = OnlyWidthdisplayDimsModeConfig(
        width=100,
        height=100,
        dims_mode=DisplayDimensionsUpdateMode.FIXED,
    )
    assert only_width_display_config_fixed.width == 100
    assert only_width_display_config_fixed.height == 100
    assert only_width_display_config_fixed.dims_mode is DisplayDimensionsUpdateMode.FIXED
