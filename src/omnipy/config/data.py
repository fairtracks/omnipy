from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
import shutil
from typing import Any

from pydantic import BaseModel
from typing_extensions import override

from omnipy.config import ConfigBase
from omnipy.data._display.config import TERMINAL_DEFAULT_HEIGHT, TERMINAL_DEFAULT_WIDTH
from omnipy.shared.enums import (BackoffStrategy,
                                 ColorStyles,
                                 ConsoleColorSystem,
                                 ConsoleDimensionsMode,
                                 HorizontalOverflowMode,
                                 PanelDesign,
                                 PrettyPrinterLib,
                                 RecommendedColorStyles,
                                 VerticalOverflowMode)
from omnipy.shared.protocols.config import (IsBrowserConsoleConfig,
                                            IsColorConfig,
                                            IsDisplayConfig,
                                            IsFontConfig,
                                            IsHttpConfig,
                                            IsHttpRequestsConfig,
                                            IsJupyterConsoleDimsModeConfig,
                                            IsLayoutConfig,
                                            IsModelConfig,
                                            IsOverflowConfig,
                                            IsTerminalConsoleConfig,
                                            IsTextConfig)
import omnipy.util._pydantic as pyd


class ColorConfig(ConfigBase):
    """
    Configuration for color output.
    """
    system: ConsoleColorSystem = ConsoleColorSystem.AUTO
    style: ColorStyles | str = RecommendedColorStyles.ANSI_DARK
    transparent_background: bool = True


class ConsoleConfig(ConfigBase):
    width: pyd.NonNegativeInt | None = TERMINAL_DEFAULT_WIDTH
    height: pyd.NonNegativeInt | None = TERMINAL_DEFAULT_HEIGHT
    color: IsColorConfig = pyd.Field(default_factory=ColorConfig)


class DimsModeMixin(BaseModel):
    dims_mode: ConsoleDimensionsMode = ConsoleDimensionsMode.AUTO


class DimsModeConfig(ConsoleConfig, DimsModeMixin, ABC):
    class Config:  # pyright: ignore [reportIncompatibleVariableOverride]
        validate_all = True
        validate_assignment = True

    @classmethod
    @abstractmethod
    def _get_console_size(cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        ...

    @pyd.validator('width', always=True)
    def check_and_set_auto_width(
        cls,
        value: pyd.NonNegativeInt,
        values: dict[str, Any],
    ) -> pyd.NonNegativeInt:
        return cls._get_console_size_if_auto_dims_mode(value, values, index=0)

    @pyd.validator('height', always=True)
    def check_and_set_auto_height(
        cls,
        value: pyd.NonNegativeInt,
        values: dict[str, Any],
    ) -> pyd.NonNegativeInt:
        return cls._get_console_size_if_auto_dims_mode(value, values, index=1)

    @classmethod
    def _get_console_size_if_auto_dims_mode(
        cls,
        value: pyd.NonNegativeInt,
        values: dict[str, Any],
        index: int,
    ):
        if values.get('dims_mode') is ConsoleDimensionsMode.AUTO:
            fetched_val = cls._get_console_size()[index]
            if fetched_val:
                return fetched_val
        return value

    # Override __getattribute__ to dynamically update width and height
    # if dims_mode is AUTO and the console size is available.
    def __getattribute__(self, attr):
        if (attr in ['width', 'height']
                and object.__getattribute__(self, 'dims_mode') is ConsoleDimensionsMode.AUTO):
            width, height = object.__getattribute__(self, '_get_console_size')()
            if width is not None:
                setattr(self, 'width', width)
            if height is not None:
                setattr(self, 'height', height)
        return object.__getattribute__(self, attr)


class TerminalConsoleConfig(DimsModeConfig):
    @classmethod
    @override
    def _get_console_size(cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        width, height = shutil.get_terminal_size(fallback=(-1, -1))
        return None if width == -1 else width, None if height == -1 else height


class FontConfig(ConfigBase):
    families: tuple[str, ...] = (
        'Menlo',
        'DejaVu Sans Mono',
        'Consolas',
        'Courier New',
        'monospace',
    )
    size: pyd.NonNegativeInt = 14
    weight: pyd.NonNegativeInt = 400
    line_height: pyd.NonNegativeFloat = 1.25


class HtmlConsoleConfig(ConsoleConfig):
    font: IsFontConfig = pyd.Field(default_factory=FontConfig)


class JupyterConsoleDimsModeConfig(HtmlConsoleConfig, DimsModeConfig):
    @classmethod
    @override
    def _get_console_size(cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        # For now, Jupyter width is pushed, not fetched. Hence, we return None.
        return None, None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.width = 120
        self.height = 50
        self.color.system = ConsoleColorSystem.ANSI_RGB
        self.color.style = RecommendedColorStyles.OMNIPY_SELENIZED_WHITE
        self.color.transparent_background = True


class BrowserConsoleConfig(HtmlConsoleConfig):
    """
    Configuration for browser console output.
    """
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.width = 160
        self.height = None
        self.color.system = ConsoleColorSystem.ANSI_RGB
        self.color.style = RecommendedColorStyles.OMNIPY_SELENIZED_WHITE
        self.color.transparent_background = False


class OverflowConfig(ConfigBase):
    """
    Configuration for overflow handling.
    """
    horizontal: HorizontalOverflowMode = HorizontalOverflowMode.ELLIPSIS
    vertical: VerticalOverflowMode = VerticalOverflowMode.ELLIPSIS_BOTTOM


class TextConfig(ConfigBase):
    overflow: IsOverflowConfig = pyd.Field(default_factory=OverflowConfig)
    tab_size: pyd.NonNegativeInt = 4
    indent_tab_size: pyd.NonNegativeInt = 2
    pretty_printer: PrettyPrinterLib = PrettyPrinterLib.RICH
    debug_mode: bool = False


class LayoutConfig(ConfigBase):
    overflow: IsOverflowConfig = pyd.Field(default_factory=OverflowConfig)
    panel_design: PanelDesign = PanelDesign.TABLE_GRID
    panel_title_at_top: bool = True


def _get_cache_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('_cache')))


class DisplayConfig(ConfigBase):
    """
    Configuration for display output.
    """
    terminal: IsTerminalConsoleConfig = pyd.Field(default_factory=TerminalConsoleConfig)
    jupyter: IsJupyterConsoleDimsModeConfig = pyd.Field(
        default_factory=JupyterConsoleDimsModeConfig)
    browser: IsBrowserConsoleConfig = pyd.Field(default_factory=BrowserConsoleConfig)
    text: IsTextConfig = pyd.Field(default_factory=TextConfig)
    layout: IsLayoutConfig = pyd.Field(default_factory=LayoutConfig)
    cache_dir_path: str = pyd.Field(default_factory=_get_cache_dir_path)


class ModelConfig(ConfigBase):
    """
    Configuration for model module.
    """
    interactive: bool = True
    dynamically_convert_elements_to_models: bool = False


class HttpRequestsConfig(ConfigBase):
    """
    Configuration for HTTP requests.
    """
    # For RateLimitingClientSession helper class
    requests_per_time_period: float = 60
    time_period_in_secs: float = 60

    # For get_*_from_api_endpoint tasks
    retry_http_statuses: tuple[int, ...] = (408, 425, 429, 500, 502, 503, 504)
    retry_attempts: int = 5
    retry_backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL


class HttpConfig(ConfigBase):
    defaults: IsHttpRequestsConfig = pyd.Field(default_factory=HttpRequestsConfig)
    for_host: defaultdict[str, IsHttpRequestsConfig] = pyd.Field(
        default_factory=lambda: defaultdict(HttpRequestsConfig))

    @pyd.validator('for_host', always=True)
    def update_http_defaults(cls,
                             _for_host: defaultdict[str, HttpRequestsConfig],
                             values: dict[str, Any]) -> defaultdict[str, HttpRequestsConfig]:
        return defaultdict(lambda: values['defaults'].copy())


class DataConfig(ConfigBase):
    """
    Configuration for data module.
    """
    display: IsDisplayConfig = pyd.Field(default_factory=lambda: DisplayConfig())
    model: IsModelConfig = pyd.Field(default_factory=lambda: ModelConfig())
    http: IsHttpConfig = pyd.Field(default_factory=HttpConfig)
