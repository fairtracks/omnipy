import pydantic as pyd
from typing_extensions import ClassVar, override

from omnipy.config.data import DimsModeConfig
from omnipy.shared.enums import ConsoleDimensionsMode


class NoSizeConsoleDimsModeConfig(DimsModeConfig):
    @classmethod
    @override
    def _get_console_size(cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        return None, None


def test_dims_mode_config_no_console_dims_size_set():
    no_size_console_config = NoSizeConsoleDimsModeConfig()
    assert no_size_console_config.width == 80
    assert no_size_console_config.height == 24
    assert no_size_console_config.dims_mode is ConsoleDimensionsMode.AUTO

    no_size_console_config.width = 100
    assert no_size_console_config.width == 100

    no_size_console_config.height = 100
    assert no_size_console_config.height == 100

    assert no_size_console_config.dims_mode is ConsoleDimensionsMode.AUTO

    no_size_console_config_auto = NoSizeConsoleDimsModeConfig(width=100, height=100)
    assert no_size_console_config_auto.width == 100
    assert no_size_console_config_auto.height == 100
    assert no_size_console_config_auto.dims_mode is ConsoleDimensionsMode.AUTO

    no_size_console_config_fixed = NoSizeConsoleDimsModeConfig(
        width=100,
        height=100,
        dims_mode=ConsoleDimensionsMode.FIXED,
    )
    assert no_size_console_config_fixed.width == 100
    assert no_size_console_config_fixed.height == 100
    assert no_size_console_config_fixed.dims_mode is ConsoleDimensionsMode.FIXED


class BothSizesConsoleDimsModeConfig(DimsModeConfig):
    console_width: ClassVar[pyd.NonNegativeInt] = 200
    console_height: ClassVar[pyd.NonNegativeInt] = 200

    @classmethod
    @override
    def _get_console_size(cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        return cls.console_width, cls.console_height


def test_dims_mode_config_both_console_dims_size_set():
    both_sizes_console_config = BothSizesConsoleDimsModeConfig()
    assert both_sizes_console_config.width == 200
    assert both_sizes_console_config.height == 200
    assert both_sizes_console_config.dims_mode is ConsoleDimensionsMode.AUTO

    both_sizes_console_config.width = 100
    assert both_sizes_console_config.width == 200

    both_sizes_console_config.height = 100
    assert both_sizes_console_config.height == 200

    assert both_sizes_console_config.dims_mode is ConsoleDimensionsMode.AUTO

    both_sizes_console_config_auto = BothSizesConsoleDimsModeConfig(
        width=100,
        height=100,
    )
    assert both_sizes_console_config_auto.width == 200
    assert both_sizes_console_config_auto.height == 200
    assert both_sizes_console_config_auto.dims_mode is ConsoleDimensionsMode.AUTO

    BothSizesConsoleDimsModeConfig.console_width = 50
    BothSizesConsoleDimsModeConfig.console_height = 50

    assert both_sizes_console_config_auto.width == 50
    assert both_sizes_console_config_auto.height == 50

    both_sizes_console_config_fixed = BothSizesConsoleDimsModeConfig(
        width=100,
        height=100,
        dims_mode=ConsoleDimensionsMode.FIXED,
    )
    assert both_sizes_console_config_fixed.width == 100
    assert both_sizes_console_config_fixed.height == 100
    assert both_sizes_console_config_fixed.dims_mode is ConsoleDimensionsMode.FIXED


class OnlyWidthConsoleDimsModeConfig(DimsModeConfig):
    console_width: ClassVar[pyd.NonNegativeInt] = 200
    console_height: ClassVar[pyd.NonNegativeInt | None] = None

    @classmethod
    @override
    def _get_console_size(cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        return cls.console_width, cls.console_height


def test_dims_mode_config_only_width_set():
    only_width_console_config = OnlyWidthConsoleDimsModeConfig()
    assert only_width_console_config.width == 200
    assert only_width_console_config.height == 24
    assert only_width_console_config.dims_mode is ConsoleDimensionsMode.AUTO

    only_width_console_config.width = 100
    assert only_width_console_config.width == 200

    only_width_console_config.height = 24
    assert only_width_console_config.height == 24

    assert only_width_console_config.dims_mode is ConsoleDimensionsMode.AUTO

    only_width_console_config_auto = OnlyWidthConsoleDimsModeConfig(
        width=100,
        height=100,
    )
    assert only_width_console_config_auto.width == 200
    assert only_width_console_config_auto.height == 100
    assert only_width_console_config_auto.dims_mode is ConsoleDimensionsMode.AUTO

    OnlyWidthConsoleDimsModeConfig.console_width = 50

    assert only_width_console_config_auto.width == 50
    assert only_width_console_config_auto.height == 100

    only_width_console_config_fixed = OnlyWidthConsoleDimsModeConfig(
        width=100,
        height=100,
        dims_mode=ConsoleDimensionsMode.FIXED,
    )
    assert only_width_console_config_fixed.width == 100
    assert only_width_console_config_fixed.height == 100
    assert only_width_console_config_fixed.dims_mode is ConsoleDimensionsMode.FIXED
