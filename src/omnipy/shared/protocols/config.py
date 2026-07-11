"""Protocols for Omnipy configuration objects and config sections."""

from collections import defaultdict
from io import TextIOBase
from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING

from omnipy.shared.enums.colorstyles import AllColorStyles
from omnipy.shared.enums.data import BackoffStrategy
from omnipy.shared.enums.display import (DisplayColorSystem,
                                         DisplayDimensionsUpdateMode,
                                         HorizontalOverflowMode,
                                         Justify,
                                         MaxTitleHeight,
                                         PanelDesign,
                                         PrettyPrinterLib,
                                         VerticalOverflowMode)
from omnipy.shared.enums.job import (ConfigOutputStorageProtocolOptions,
                                     ConfigPersistOutputsOptions,
                                     ConfigRestoreOutputsOptions,
                                     EngineChoice)
from omnipy.shared.enums.ui import SpecifiedUserInterfaceType, TerminalOutputUserInterfaceType
from omnipy.shared.protocols.util import IsDataPublisher
from omnipy.shared.typedefs import LocaleType
import omnipy.util.pydantic as pyd

if TYPE_CHECKING:
    # To avoid circular import
    from omnipy.shared.protocols.data import IsModel


@runtime_checkable
class IsConfigBase(IsDataPublisher, Protocol):
    """Base protocol for Omnipy configuration objects.

    Config objects publish updates, can be viewed as models, and provide a
    renderer-friendly string representation.
    """
    def as_model(self) -> 'IsModel[Any]':
        ...

    def default_repr_to_terminal_str(
        self,
        ui_type: TerminalOutputUserInterfaceType.Literals,
    ) -> str:
        """Render the config for a terminal-style user interface.

        Args:
            ui_type: Terminal frontend variant requesting the representation.

        Returns:
            str: Terminal-friendly string representation of the config.
        """
        ...

    def __str__(self) -> str:
        ...


# data


@runtime_checkable
class IsColorConfig(IsConfigBase, Protocol):
    """Color settings shared by terminal and HTML-style renderers.

    Attributes:
        system: Available color-system capability for the target renderer.
        style: Named color theme or explicit style identifier.
        dark_background: Whether the target surface uses a dark background.
        solid_background: Whether panels should assume an opaque background.
    """

    system: DisplayColorSystem.Literals
    style: AllColorStyles.Literals | str
    dark_background: bool
    solid_background: bool


@runtime_checkable
class IsUserInterfaceTypeConfig(IsConfigBase, Protocol):
    """Base configuration shared by concrete user-interface frontends.

    Attributes:
        width: Preferred render width in characters or pixels, if known.
        height: Preferred render height in characters or pixels, if known.
        color: Color configuration for this frontend.
    """

    width: pyd.NonNegativeInt | None
    height: pyd.NonNegativeInt | None
    color: IsColorConfig

    def set_width_and_height(
        self,
        width: pyd.NonNegativeInt | None,
        height: pyd.NonNegativeInt | None,
    ) -> None:
        """Update the preferred display dimensions for this frontend.

        Args:
            width: New preferred width, or ``None`` when unknown.
            height: New preferred height, or ``None`` when unknown.
        """


@runtime_checkable
class IsDimsModeMixin(Protocol):
    """Mixin protocol for configs that track dimension refresh behavior.

    Attributes:
        dims_mode: Policy controlling when display dimensions are refreshed.
    """

    dims_mode: DisplayDimensionsUpdateMode.Literals = DisplayDimensionsUpdateMode.AUTO


@runtime_checkable
class IsDimsModeConfig(IsUserInterfaceTypeConfig, IsDimsModeMixin, Protocol):
    """UI config that also exposes display-dimension refresh behavior."""

    ...


@runtime_checkable
class IsTerminalUserInterfaceConfig(IsDimsModeConfig, Protocol):
    """Terminal-specific user-interface configuration."""

    ...


@runtime_checkable
class IsFontConfig(IsConfigBase, Protocol):
    """Font settings for HTML-based Omnipy renderers.

    Attributes:
        families: Ordered list of font-family fallbacks.
        size: Base font size.
        weight: Default font weight.
        line_height: Relative line-height multiplier.
    """

    families: tuple[str, ...]
    size: pyd.NonNegativeFloat
    weight: pyd.NonNegativeInt
    line_height: pyd.NonNegativeFloat


@runtime_checkable
class IsHtmlUserInterfaceConfig(IsUserInterfaceTypeConfig, Protocol):
    """Base configuration for browser- and notebook-style HTML frontends.

    Attributes:
        font: Font settings used by the HTML renderer.
    """

    font: IsFontConfig


@runtime_checkable
class IsJupyterUserInterfaceConfig(IsHtmlUserInterfaceConfig, IsDimsModeConfig, Protocol):
    """HTML UI configuration specialized for Jupyter environments."""

    ...


@runtime_checkable
class IsBrowserUserInterfaceConfig(IsHtmlUserInterfaceConfig, Protocol):
    """HTML UI configuration specialized for browser rendering."""

    ...


@runtime_checkable
class IsOverflowConfig(IsConfigBase, Protocol):
    """Overflow behavior for horizontally and vertically constrained output.

    Attributes:
        horizontal: Horizontal overflow handling policy.
        vertical: Vertical overflow handling policy.
    """

    horizontal: HorizontalOverflowMode.Literals
    vertical: VerticalOverflowMode.Literals


@runtime_checkable
class IsTextConfig(IsConfigBase, Protocol):
    """Text-formatting settings used by Omnipy renderers.

    Attributes:
        overflow: Overflow behavior for text output.
        tab_size: Number of spaces represented by a tab.
        indent_tab_size: Tab width used when indenting structured output.
        pretty_printer: Pretty-printing backend to use.
        proportional_freedom: Tuning value for proportional line breaking.
        debug_mode: Whether extra rendering diagnostics should be shown.
    """

    overflow: IsOverflowConfig
    tab_size: pyd.NonNegativeInt
    indent_tab_size: pyd.NonNegativeInt
    pretty_printer: PrettyPrinterLib.Literals
    proportional_freedom: pyd.NonNegativeFloat
    debug_mode: bool


@runtime_checkable
class IsLayoutConfig(IsConfigBase, Protocol):
    """Panel and layout settings for structured output rendering.

    Attributes:
        overflow: Overflow behavior used by panels and layouts.
        panel_design: Visual panel style.
        panel_title_at_top: Whether panel titles should be rendered above content.
        max_title_height: Maximum title height policy.
        min_panel_width: Minimum panel width before collapsing layout.
        min_crop_width: Minimum width before content is cropped.
        max_panels_hor: Maximum number of side-by-side panels, if limited.
        max_nesting_depth: Maximum nested panel depth, if limited.
        justify: Default content justification inside panels.
    """

    overflow: IsOverflowConfig
    panel_design: PanelDesign.Literals
    panel_title_at_top: bool
    max_title_height: MaxTitleHeight.Literals
    min_panel_width: pyd.NonNegativeInt
    min_crop_width: pyd.NonNegativeInt
    max_panels_hor: pyd.NonNegativeInt | None
    max_nesting_depth: pyd.NonNegativeInt | None
    justify: Justify.Literals


@runtime_checkable
class IsUserInterfaceConfig(IsConfigBase, Protocol):
    """Top-level bundle of frontend-specific UI configuration sections.

    Attributes:
        detected_type: Frontend type currently in use.
        terminal: Terminal-specific UI settings.
        jupyter: Jupyter-specific UI settings.
        browser: Browser-specific UI settings.
        text: Shared text-rendering settings.
        layout: Shared layout-rendering settings.
        cache_dir_path: Directory used for UI-related cache files.
    """

    detected_type: SpecifiedUserInterfaceType.Literals
    terminal: IsTerminalUserInterfaceConfig
    jupyter: IsJupyterUserInterfaceConfig
    browser: IsBrowserUserInterfaceConfig
    text: IsTextConfig
    layout: IsLayoutConfig
    cache_dir_path: str

    def get_ui_type_config(
        self,
        ui_type: SpecifiedUserInterfaceType.Literals,
    ) -> IsUserInterfaceTypeConfig:
        """Return the config section matching a concrete frontend type.

        Args:
            ui_type: Frontend type whose config section should be returned.

        Returns:
            IsUserInterfaceTypeConfig: Config section for the requested frontend.
        """
        ...


@runtime_checkable
class IsModelConfig(IsConfigBase, Protocol):
    """Configuration controlling model behavior and conversions.

    Attributes:
        interactive: Whether models favor interactive display behavior.
        dynamically_convert_elements_to_models: Whether nested elements are converted lazily.
    """

    interactive: bool
    dynamically_convert_elements_to_models: bool


@runtime_checkable
class IsHttpRequestsConfig(IsConfigBase, Protocol):
    """HTTP retry and throttling policy for one request profile.

    Attributes:
        requests_per_time_period: Maximum requests allowed per time window.
        time_period_in_secs: Length of the throttling window in seconds.
        retry_http_statuses: HTTP status codes that should trigger retries.
        retry_attempts: Maximum number of retry attempts.
        retry_backoff_strategy: Backoff strategy used between retries.
    """

    requests_per_time_period: float
    time_period_in_secs: float
    retry_http_statuses: tuple[int, ...]
    retry_attempts: int
    retry_backoff_strategy: BackoffStrategy.Literals


@runtime_checkable
class IsHttpConfig(IsConfigBase, Protocol):
    """HTTP configuration with default and per-host request policies.

    Attributes:
        defaults: Fallback request policy used when no host-specific override exists.
        for_host: Request-policy overrides keyed by host name.
    """

    defaults: IsHttpRequestsConfig
    for_host: defaultdict[str, IsHttpRequestsConfig]


@runtime_checkable
class IsDataConfig(IsConfigBase, Protocol):
    """Top-level configuration bundle for data, models, and HTTP access.

    Attributes:
        ui: User-interface and rendering settings.
        model: Model conversion and interaction settings.
        http: HTTP retry and throttling settings.
    """

    ui: IsUserInterfaceConfig
    model: IsModelConfig
    http: IsHttpConfig


# engine


@runtime_checkable
class IsJobRunnerConfig(IsConfigBase, Protocol):
    """Base protocol for engine-specific job-runner configuration sections."""

    ...


@runtime_checkable
class IsLocalRunnerConfig(IsJobRunnerConfig, Protocol):
    """Runner configuration for the local execution backend."""

    ...


@runtime_checkable
class IsPrefectEngineConfig(IsJobRunnerConfig, Protocol):
    """Runner configuration for the Prefect execution backend.

    Attributes:
        use_cached_results: Whether Prefect should reuse cached task results.
    """

    use_cached_results: bool = False


@runtime_checkable
class IsEngineConfig(IsConfigBase, Protocol):
    """Top-level engine selection and per-engine configuration bundle.

    Attributes:
        choice: Engine backend currently selected for execution.
        local: Configuration for the local backend.
        prefect: Configuration for the Prefect backend.
    """

    choice: EngineChoice.Literals
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    ...


# job


@runtime_checkable
class IsOutputStorageConfigBase(IsConfigBase, Protocol):
    """Base protocol for persisted-output storage backends.

    Attributes:
        persist_data_dir_path: Root path used for persisted job outputs.
    """

    persist_data_dir_path: str


@runtime_checkable
class IsLocalOutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    """Filesystem-backed settings for persisted job outputs."""


@runtime_checkable
class IsS3OutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    """S3-compatible settings for persisted job outputs.

    Attributes:
        endpoint_url: S3 API endpoint URL.
        access_key: Access key used for authentication.
        secret_key: Secret key used for authentication.
        bucket_name: Bucket that stores persisted outputs.
    """

    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str


@runtime_checkable
class IsOutputStorageConfig(IsConfigBase, Protocol):
    """Persisted-output policy and backend selection.

    Attributes:
        persist_outputs: Default policy for persisting job outputs.
        restore_outputs: Default policy for restoring persisted outputs.
        protocol: Storage backend selected for persisted outputs.
        local: Local-backend settings.
        s3: S3-backend settings.
    """

    persist_outputs: ConfigPersistOutputsOptions.Literals
    restore_outputs: ConfigRestoreOutputsOptions.Literals
    protocol: ConfigOutputStorageProtocolOptions.Literals
    local: IsLocalOutputStorageConfig
    s3: IsS3OutputStorageConfig


@runtime_checkable
class IsJobConfig(IsConfigBase, Protocol):
    """Job execution configuration shared across tasks and flows.

    Attributes:
        output_storage: Settings controlling persisted job outputs.
    """

    output_storage: IsOutputStorageConfig


# root_log


@runtime_checkable
class IsRootLogConfig(IsConfigBase, Protocol):
    """Root logging configuration for Omnipy runtime objects.

    Attributes:
        log_format_str: Format string used by root log handlers.
        locale: Locale used for formatting and localization-sensitive output.
        log_to_stdout: Whether logging to standard output is enabled.
        log_to_stderr: Whether logging to standard error is enabled.
        log_to_file: Whether file logging is enabled.
        stdout: Stream used for standard-output logging.
        stderr: Stream used for standard-error logging.
        stdout_log_min_level: Minimum level sent to standard output.
        stderr_log_min_level: Minimum level sent to standard error.
        file_log_min_level: Minimum level written to the log file.
        file_log_path: Destination path for file logging.
    """

    log_format_str: str
    locale: LocaleType
    log_to_stdout: bool
    log_to_stderr: bool
    log_to_file: bool
    stdout: TextIOBase
    stderr: TextIOBase
    stdout_log_min_level: int
    stderr_log_min_level: int
    file_log_min_level: int
    file_log_path: str
