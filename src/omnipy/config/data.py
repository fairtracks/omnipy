"""Configuration models for data display, UI, and HTTP behavior."""

from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
import shutil
from typing import Any, TypedDict

from typing_extensions import override

from omnipy.config import ConfigBase
from omnipy.hub.ui import detect_display_color_system
from omnipy.shared.constants import (BROWSER_DEFAULT_HEIGHT,
                                     BROWSER_DEFAULT_WIDTH,
                                     DEFAULT_DARK_BACKGROUND,
                                     JUPYTER_DEFAULT_HEIGHT,
                                     JUPYTER_DEFAULT_WIDTH,
                                     MAX_PANEL_NESTING_DEPTH,
                                     MAX_PANELS_HORIZONTALLY,
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
import omnipy.util.pydantic as pyd


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
    dark_background: bool = DEFAULT_DARK_BACKGROUND
    solid_background: bool = False

    @pyd.root_validator()
    def default_style(cls, values: _ColorConfigTypedDict) -> _ColorConfigTypedDict:
        """Resolve recommended style presets to concrete color style names.

        Args:
            values: Parsed configuration values for color rendering.

        Returns:
            _ColorConfigTypedDict: Updated values where ``style`` is replaced with
                a concrete style when a recommended preset is used.

        Raises:
            None: This validator does not raise exceptions directly.

        Example:
            >>> ColorConfig.default_style({
            ...     'system': DisplayColorSystem.TRUECOLOR,
            ...     'style': RecommendedColorStyles.AUTO,
            ...     'dark_background': True,
            ...     'solid_background': False,
            ... })
            {'system': ..., 'style': ..., 'dark_background': True, 'solid_background': False}
        """
        if values['style'] in RecommendedColorStyles:
            values['style'] = RecommendedColorStyles.get_default_style(
                values['system'],
                values['dark_background'],
                values['solid_background'],
            )
        return values


class UserInterfaceTypeConfig(ConfigBase):
    """Shared width, height, and color settings for one UI target."""

    width: pyd.NonNegativeInt | None = TERMINAL_DEFAULT_WIDTH
    height: pyd.NonNegativeInt | None = TERMINAL_DEFAULT_HEIGHT
    color: IsColorConfig = pyd.Field(default_factory=ColorConfig)

    def set_width_and_height(
        self,
        width: pyd.NonNegativeInt | None,
        height: pyd.NonNegativeInt | None,
    ) -> None:
        """Set width and height and notify subscribers about the updates.

        Args:
            width: New UI width in character or pixel units, depending on
                renderer.
            height: New UI height in character or pixel units, depending on
                renderer.

        Returns:
            None: This method mutates the instance and emits subscriber events.

        Raises:
            None: This method does not raise exceptions directly.

        Example:
            >>> ui_cfg = UserInterfaceTypeConfig()
            >>> ui_cfg.set_width_and_height(120, 40)
        """
        for (dim_name, dim_value) in (('width', width), ('height', height)):
            object.__setattr__(self, dim_name, dim_value)
            self._call_subscribers(dim_name, dim_value)
        self._call_self_subscribers()


class DimsModeMixin(pyd.BaseModel):
    """Mixin that adds automatic display-dimension update mode selection."""

    dims_mode: DisplayDimensionsUpdateMode.Literals = DisplayDimensionsUpdateMode.AUTO


class DimsModeConfig(UserInterfaceTypeConfig, DimsModeMixin, ABC):
    """Base config that can refresh width and height from the active display."""
    class Config:  # pyright: ignore [reportIncompatibleVariableOverride]
        """Pydantic model configuration: validates all fields and validates on assignment."""
        validate_all = True
        validate_assignment = True

    @classmethod
    @abstractmethod
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        """Fetch currently available display dimensions for a UI target.

        Args:
            cls: The configuration class querying display capabilities.

        Returns:
            tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]: Width
                and height where unavailable dimensions are ``None``.

        Raises:
            NotImplementedError: Implementations in subclasses provide concrete
                behavior.

        Example:
            >>> TerminalUserInterfaceConfig._get_available_display_dims()
            (120, 40)
        """
        ...

    @pyd.validator('width', always=True)
    def check_and_set_auto_width(
        cls,
        value: pyd.NonNegativeInt,
        values: dict[str, Any],
    ) -> pyd.NonNegativeInt:
        """Resolve width automatically when dimension mode is ``AUTO``.

        Args:
            value: Candidate width from parsed model input.
            values: Additional parsed field values available to the validator.

        Returns:
            pyd.NonNegativeInt: Auto-detected width when available, otherwise
                the provided ``value``.

        Raises:
            None: This validator does not raise exceptions directly.

        Example:
            >>> DimsModeConfig.check_and_set_auto_width(80, {'dims_mode': DisplayDimensionsUpdateMode.AUTO})
            80
        """
        return cls._get_available_display_dim_if_auto_dims_mode(value, values, index=0)

    @pyd.validator('height', always=True)
    def check_and_set_auto_height(
        cls,
        value: pyd.NonNegativeInt,
        values: dict[str, Any],
    ) -> pyd.NonNegativeInt:
        """Resolve height automatically when dimension mode is ``AUTO``.

        Args:
            value: Candidate height from parsed model input.
            values: Additional parsed field values available to the validator.

        Returns:
            pyd.NonNegativeInt: Auto-detected height when available, otherwise
                the provided ``value``.

        Raises:
            None: This validator does not raise exceptions directly.

        Example:
            >>> DimsModeConfig.check_and_set_auto_height(24, {'dims_mode': DisplayDimensionsUpdateMode.AUTO})
            24
        """
        return cls._get_available_display_dim_if_auto_dims_mode(value, values, index=1)

    @classmethod
    def _get_available_display_dim_if_auto_dims_mode(
        cls,
        value: pyd.NonNegativeInt,
        values: dict[str, Any],
        index: int,
    ):
        """Resolve one display dimension from environment when in auto mode.

        Args:
            value: Fallback parsed value when auto-detection is disabled or
                unavailable.
            values: Parsed model field map containing ``dims_mode``.
            index: Dimension index where ``0`` is width and ``1`` is height.

        Returns:
            pyd.NonNegativeInt: Auto-detected dimension value when available,
                otherwise the provided ``value``.

        Raises:
            None: This helper does not raise exceptions directly.

        Example:
            >>> DimsModeConfig._get_available_display_dim_if_auto_dims_mode(
            ...     80,
            ...     {'dims_mode': DisplayDimensionsUpdateMode.AUTO},
            ...     0,
            ... )
            80
        """
        if values.get('dims_mode') is DisplayDimensionsUpdateMode.AUTO:
            fetched_val = cls._get_available_display_dims()[index]
            if fetched_val:
                return fetched_val
        return value

    # Override __getattribute__ to dynamically update width and height
    # if dims_mode is AUTO and the display size is available.
    def __getattribute__(self, attr):
        """Read attributes and refresh dimensions when auto mode is enabled.

        Args:
            attr: Name of the requested attribute.

        Returns:
            Any: Value of the requested attribute.

        Raises:
            AttributeError: If ``attr`` does not exist on the instance.

        Example:
            >>> cfg = TerminalUserInterfaceConfig()
            >>> cfg.width
            120
        """
        if (attr in ['width', 'height']
                and object.__getattribute__(self, 'dims_mode') is DisplayDimensionsUpdateMode.AUTO):
            width, height = object.__getattribute__(self, '_get_available_display_dims')()
            if width is not None:
                setattr(self, 'width', width)
            if height is not None:
                setattr(self, 'height', height)
        return object.__getattribute__(self, attr)


class TerminalUserInterfaceConfig(DimsModeConfig):
    """Terminal-specific UI configuration with live terminal size detection."""
    @classmethod
    @override
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        """Fetch terminal width and height from the current shell session.

        Args:
            cls: The terminal UI configuration class.

        Returns:
            tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
                Terminal width and height, or ``None`` for unavailable values.

        Raises:
            None: This method does not raise exceptions directly.

        Example:
            >>> TerminalUserInterfaceConfig._get_available_display_dims()
            (120, 40)
        """
        width, height = shutil.get_terminal_size(fallback=(0, 0))
        return None if width == 0 else width, None if height == 0 else height


class FontConfig(ConfigBase):
    """Font settings for HTML-based display integrations."""

    families: tuple[str, ...] = (
        'Menlo',
        'DejaVu Sans Mono',
        'Consolas',
        'Courier New',
        'monospace',
    )
    size: pyd.NonNegativeFloat = 14
    weight: pyd.NonNegativeInt = 400
    line_height: pyd.NonNegativeFloat = 1.25


class HtmlUserInterfaceConfig(UserInterfaceTypeConfig):
    """Common configuration for browser-like HTML render targets."""

    font: IsFontConfig = pyd.Field(default_factory=FontConfig)


class JupyterUserInterfaceConfig(HtmlUserInterfaceConfig, DimsModeConfig):
    """Jupyter-specific UI configuration with notebook defaults."""
    @classmethod
    @override
    def _get_available_display_dims(
            cls) -> tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
        """Return notebook display dimensions when they can be queried.

        Args:
            cls: The Jupyter UI configuration class.

        Returns:
            tuple[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]:
                ``(None, None)`` because dimensions are currently pushed from
                Jupyter frontend code.

        Raises:
            None: This method does not raise exceptions directly.

        Example:
            >>> JupyterUserInterfaceConfig._get_available_display_dims()
            (None, None)
        """
        # For now, Jupyter width is pushed, not fetched. Hence, we return None.
        return None, None

    def __init__(self, **data: Any) -> None:
        """Initialize Jupyter defaults for dimensions and color settings.

        Args:
            **data: Optional pydantic field values passed to the parent model
                initializer.

        Returns:
            None: Initializes the instance in place.

        Raises:
            pyd.ValidationError: If provided ``data`` does not satisfy model
                validation constraints.

        Example:
            >>> cfg = JupyterUserInterfaceConfig()
            >>> (cfg.width, cfg.height)
            (JUPYTER_DEFAULT_WIDTH, JUPYTER_DEFAULT_HEIGHT)
        """
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
        """Initialize browser defaults for dimensions and color settings.

        Args:
            **data: Optional pydantic field values passed to the parent model
                initializer.

        Returns:
            None: Initializes the instance in place.

        Raises:
            pyd.ValidationError: If provided ``data`` does not satisfy model
                validation constraints.

        Example:
            >>> cfg = BrowserUserInterfaceConfig()
            >>> (cfg.width, cfg.height)
            (BROWSER_DEFAULT_WIDTH, BROWSER_DEFAULT_HEIGHT)
        """
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
    """Text-formatting configuration shared by display renderers."""

    overflow: IsOverflowConfig = pyd.Field(default_factory=OverflowConfig)
    tab_size: pyd.NonNegativeInt = 4
    indent_tab_size: pyd.NonNegativeInt = 2
    pretty_printer: PrettyPrinterLib.Literals = PrettyPrinterLib.AUTO
    proportional_freedom: pyd.NonNegativeFloat = 2.5
    debug_mode: bool = False


class LayoutConfig(ConfigBase):
    """Layout-panel configuration for multi-panel display composition."""

    overflow: IsOverflowConfig = pyd.Field(default_factory=OverflowConfig)
    panel_design: PanelDesign.Literals = PanelDesign.TABLE
    panel_title_at_top: bool = True
    max_title_height: MaxTitleHeight.Literals = MaxTitleHeight.AUTO
    min_panel_width: pyd.NonNegativeInt = MIN_PANEL_WIDTH
    min_crop_width: pyd.NonNegativeInt = MIN_CROP_WIDTH
    max_panels_hor: pyd.NonNegativeInt | None = MAX_PANELS_HORIZONTALLY
    max_nesting_depth: pyd.NonNegativeInt | None = MAX_PANEL_NESTING_DEPTH
    justify: Justify.Literals = Justify.LEFT


def _get_cache_dir_path() -> str:
    """Build the default cache directory path beneath the working directory.

    Returns:
        str: Absolute path to the ``_cache`` directory in the current working
            directory.

    Example:
        >>> _get_cache_dir_path().endswith('/_cache')
        True
    """
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
        """Return UI-specific configuration for a supported UI type.

        Args:
            ui_type: UI type discriminator used to select terminal, Jupyter,
                or browser settings.

        Returns:
            IsUserInterfaceTypeConfig: Matching configuration model when
                ``ui_type`` is recognized as terminal, Jupyter, or browser.
            ``None``: Returned implicitly when ``ui_type`` is unsupported.

        Example:
            >>> cfg = UserInterfaceConfig()
            >>> cfg.get_ui_type_config(UserInterfaceType.TERMINAL)
            TerminalUserInterfaceConfig(...)
        """
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
    """HTTP request defaults together with per-host overrides."""

    defaults: IsHttpRequestsConfig = pyd.Field(default_factory=HttpRequestsConfig)
    for_host: defaultdict[str, IsHttpRequestsConfig] = pyd.Field(
        default_factory=lambda: defaultdict(HttpRequestsConfig))

    @pyd.validator('for_host', always=True)
    def update_http_defaults(cls,
                             _for_host: defaultdict[str, HttpRequestsConfig],
                             values: dict[str, Any]) -> defaultdict[str, HttpRequestsConfig]:
        """Create a host map that clones current HTTP defaults per new key.

        Args:
            cls: The HTTP config model class.
            _for_host: Parsed ``for_host`` value from pydantic input.
            values: Other parsed field values, including ``defaults``.

        Returns:
            defaultdict[str, HttpRequestsConfig]: Mapping that returns a copy
                of ``defaults`` for unknown hosts.

        Raises:
            KeyError: If ``defaults`` is missing from ``values`` during
                validation.

        Example:
            >>> cfg = HttpConfig()
            >>> cfg.for_host['example.org'].retry_attempts
            5
        """
        return defaultdict(lambda: values['defaults'].copy())


class DataConfig(ConfigBase):
    """
    Configuration for data module.
    """
    ui: IsUserInterfaceConfig = pyd.Field(default_factory=lambda: UserInterfaceConfig())
    model: IsModelConfig = pyd.Field(default_factory=lambda: ModelConfig())
    http: IsHttpConfig = pyd.Field(default_factory=HttpConfig)
