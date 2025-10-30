from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
import shutil
from typing import Any, TypedDict

from pydantic import BaseModel
from typing_extensions import override

from omnipy.config import ConfigBase
from omnipy.hub.ui import detect_display_color_system
from omnipy.shared.constants import (BROWSER_DEFAULT_HEIGHT,
                                     BROWSER_DEFAULT_WIDTH,
                                     JUPYTER_DEFAULT_HEIGHT,
                                     JUPYTER_DEFAULT_WIDTH,
                                     MIN_CROP_WIDTH,
                                     MIN_PANEL_WIDTH,
                                     TERMINAL_DEFAULT_HEIGHT,
                                     TERMINAL_DEFAULT_WIDTH)
from omnipy.shared.enums.colorstyles import AllColorStyles, RecommendedColorStyles
from omnipy.shared.enums.data import BackoffStrategy
from omnipy.shared.enums.display import (DisplayColorSystem,
                                         DisplayDimensionsUpdateMode,
                                         HorizontalOverflowMode,
                                         Justify,
                                         MaxTitleHeight,
                                         PanelDesign,
                                         PrettyPrinterLib,
                                         VerticalOverflowMode)
from omnipy.shared.enums.ui import SpecifiedUserInterfaceType, UserInterfaceType
from omnipy.shared.protocols.config import (IsBrowserUserInterfaceConfig,
                                            IsColorConfig,
                                            IsFontConfig,
                                            IsHttpConfig,
                                            IsHttpRequestsConfig,
                                            IsJupyterUserInterfaceConfig,
                                            IsLayoutConfig,
                                            IsModelConfig,
                                            IsOverflowConfig,
                                            IsTerminalUserInterfaceConfig,
                                            IsTextConfig,
                                            IsUserInterfaceConfig,
                                            IsUserInterfaceTypeConfig)
import omnipy.util._pydantic as pyd


class _ColorConfigTypedDict(TypedDict):
    system: DisplayColorSystem.Literals
    style: AllColorStyles.Literals | str
    dark_background: bool
    solid_background: bool


class ColorConfig(ConfigBase):
    """
    Configuration for color output.
    """
    system: DisplayColorSystem.Literals = DisplayColorSystem.AUTO
    style: AllColorStyles.Literals | str = RecommendedColorStyles.AUTO
    dark_background: bool = False
    solid_background: bool = False

    @pyd.root_validator()
    def default_style(cls, values: _ColorConfigTypedDict) -> _ColorConfigTypedDict:
        if values['style'] in RecommendedColorStyles:
            values['style'] = RecommendedColorStyles.get_default_style(
                values['system'],
                values['dark_background'],
                values['solid_background'],
            )
        return values

    # Override __getattribute__ to dynamically update default style
    def __getattribute__(self, attr):
        if (attr in ['style'] and object.__getattribute__(self, 'style') in RecommendedColorStyles):
            setattr(self, 'style', RecommendedColorStyles.AUTO)
        return object.__getattribute__(self, attr)


class UserInterfaceTypeConfig(ConfigBase):
    width: pyd.NonNegativeInt | None = TERMINAL_DEFAULT_WIDTH
    height: pyd.NonNegativeInt | None = TERMINAL_DEFAULT_HEIGHT
    color: IsColorConfig = pyd.Field(default_factory=ColorConfig)

    def set_width_and_height(
        self,
        width: pyd.NonNegativeInt | None,
        height: pyd.NonNegativeInt | None,
    ) -> None:
        """
        Sets width and height, and notifies subscribers of the change. Only
        notifies self-subscribers once after both attributes have been
        updated.
        """
        for (dim_name, dim_value) in (('width', width), ('height', height)):
            object.__setattr__(self, dim_name, dim_value)
            self._call_subscribers(dim_name, dim_value)
        self._call_self_subscribers()


class DimsModeMixin(BaseModel):
    dims_mode: DisplayDimensionsUpdateMode.Literals = DisplayDimensionsUpdateMode.AUTO


class DimsModeConfig(UserInterfaceTypeConfig, DimsModeMixin, ABC):
    class Config:  # pyright: ignore [reportIncompatibleVariableOverride]
        validate_all = True
        validate_assignment = True

    @classmethod
    @abstractmethod
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        ...

    @pyd.validator('width', always=True)
    def check_and_set_auto_width(
        cls,
        value: pyd.NonNegativeInt,
        values: dict[str, Any],
    ) -> pyd.NonNegativeInt:
        return cls._get_available_display_dim_if_auto_dims_mode(value, values, index=0)

    @pyd.validator('height', always=True)
    def check_and_set_auto_height(
        cls,
        value: pyd.NonNegativeInt,
        values: dict[str, Any],
    ) -> pyd.NonNegativeInt:
        return cls._get_available_display_dim_if_auto_dims_mode(value, values, index=1)

    @classmethod
    def _get_available_display_dim_if_auto_dims_mode(
        cls,
        value: pyd.NonNegativeInt,
        values: dict[str, Any],
        index: int,
    ):
        if values.get('dims_mode') is DisplayDimensionsUpdateMode.AUTO:
            fetched_val = cls._get_available_display_dims()[index]
            if fetched_val:
                return fetched_val
        return value

    # Override __getattribute__ to dynamically update width and height
    # if dims_mode is AUTO and the display size is available.
    def __getattribute__(self, attr):
        if (attr in ['width', 'height']
                and object.__getattribute__(self, 'dims_mode') is DisplayDimensionsUpdateMode.AUTO):
            width, height = object.__getattribute__(self, '_get_available_display_dims')()
            if width is not None:
                setattr(self, 'width', width)
            if height is not None:
                setattr(self, 'height', height)
        return object.__getattribute__(self, attr)


class TerminalUserInterfaceConfig(DimsModeConfig):
    @classmethod
    @override
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        width, height = shutil.get_terminal_size(fallback=(0, 0))
        return None if width == 0 else width, None if height == 0 else height


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


class HtmlUserInterfaceConfig(UserInterfaceTypeConfig):
    font: IsFontConfig = pyd.Field(default_factory=FontConfig)


class JupyterUserInterfaceConfig(HtmlUserInterfaceConfig, DimsModeConfig):
    @classmethod
    @override
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        # For now, Jupyter width is pushed, not fetched. Hence, we return None.
        return None, None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.width = JUPYTER_DEFAULT_WIDTH
        self.height = JUPYTER_DEFAULT_HEIGHT
        self.color.system = detect_display_color_system(UserInterfaceType.JUPYTER)
        self.color.dark_background = False


class BrowserUserInterfaceConfig(HtmlUserInterfaceConfig):
    """
    Configuration for browser user interface type.
    """
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.width = BROWSER_DEFAULT_WIDTH
        self.height = BROWSER_DEFAULT_HEIGHT
        self.color.system = detect_display_color_system(UserInterfaceType.BROWSER_PAGE)
        self.color.dark_background = False


class OverflowConfig(ConfigBase):
    """
    Configuration for overflow handling.
    """
    horizontal: HorizontalOverflowMode.Literals = HorizontalOverflowMode.ELLIPSIS
    vertical: VerticalOverflowMode.Literals = VerticalOverflowMode.ELLIPSIS_BOTTOM


class TextConfig(ConfigBase):
    overflow: IsOverflowConfig = pyd.Field(default_factory=OverflowConfig)
    tab_size: pyd.NonNegativeInt = 4
    indent_tab_size: pyd.NonNegativeInt = 2
    pretty_printer: PrettyPrinterLib.Literals = PrettyPrinterLib.AUTO
    proportional_freedom: pyd.NonNegativeFloat = 2.5
    debug_mode: bool = False


class LayoutConfig(ConfigBase):
    overflow: IsOverflowConfig = pyd.Field(default_factory=OverflowConfig)
    panel_design: PanelDesign.Literals = PanelDesign.TABLE
    panel_title_at_top: bool = True
    max_title_height: MaxTitleHeight.Literals = MaxTitleHeight.AUTO
    min_panel_width: pyd.NonNegativeInt = MIN_PANEL_WIDTH
    min_crop_width: pyd.NonNegativeInt = MIN_CROP_WIDTH
    justify: Justify.Literals = Justify.LEFT


def _get_cache_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('_cache')))


class UserInterfaceConfig(ConfigBase):
    """
    Configuration for the user interface, including inputs and output
    devices.
    """
    detected_type: SpecifiedUserInterfaceType.Literals = UserInterfaceType.UNKNOWN
    terminal: IsTerminalUserInterfaceConfig = pyd.Field(default_factory=TerminalUserInterfaceConfig)
    jupyter: IsJupyterUserInterfaceConfig = pyd.Field(default_factory=JupyterUserInterfaceConfig)
    browser: IsBrowserUserInterfaceConfig = pyd.Field(default_factory=BrowserUserInterfaceConfig)
    text: IsTextConfig = pyd.Field(default_factory=TextConfig)
    layout: IsLayoutConfig = pyd.Field(default_factory=LayoutConfig)
    cache_dir_path: str = pyd.Field(default_factory=_get_cache_dir_path)

    def get_ui_type_config(
        self,
        ui_type: SpecifiedUserInterfaceType.Literals,
    ) -> IsUserInterfaceTypeConfig:  # pyright: ignore [reportReturnType]
        match ui_type:
            case x if UserInterfaceType.is_terminal(x):
                return self.terminal
            case x if UserInterfaceType.is_jupyter(x):
                return self.jupyter
            case x if UserInterfaceType.is_browser(x):
                return self.browser


class ModelConfig(ConfigBase):
    """
    Configuration for behavior of the Model class.
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
    retry_backoff_strategy: BackoffStrategy.Literals = BackoffStrategy.EXPONENTIAL


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
    ui: IsUserInterfaceConfig = pyd.Field(default_factory=lambda: UserInterfaceConfig())
    model: IsModelConfig = pyd.Field(default_factory=lambda: ModelConfig())
    http: IsHttpConfig = pyd.Field(default_factory=HttpConfig)
