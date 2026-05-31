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
    """"""
    def as_model(self) -> 'IsModel[Any]':
        ...

    def default_repr_to_terminal_str(
        self,
        ui_type: TerminalOutputUserInterfaceType.Literals,
    ) -> str:
        ...

    def __str__(self) -> str:
        ...


# data


@runtime_checkable
class IsColorConfig(IsConfigBase, Protocol):
    """Protocol for UI color configuration."""

    system: DisplayColorSystem.Literals
    style: AllColorStyles.Literals | str
    dark_background: bool
    solid_background: bool


@runtime_checkable
class IsUserInterfaceTypeConfig(IsConfigBase, Protocol):
    """Protocol for size-aware user-interface configuration."""

    width: pyd.NonNegativeInt | None
    height: pyd.NonNegativeInt | None
    color: IsColorConfig

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


@runtime_checkable
class IsDimsModeMixin(Protocol):
    """Protocol for configs that expose a display-dimensions update mode."""

    dims_mode: DisplayDimensionsUpdateMode.Literals = DisplayDimensionsUpdateMode.AUTO


@runtime_checkable
class IsDimsModeConfig(IsUserInterfaceTypeConfig, IsDimsModeMixin, Protocol):
    """Protocol for UI configs with dimension update mode support."""

    ...


@runtime_checkable
class IsTerminalUserInterfaceConfig(IsDimsModeConfig, Protocol):
    """Protocol for terminal UI configuration."""

    ...


@runtime_checkable
class IsFontConfig(IsConfigBase, Protocol):
    """Protocol for font configuration used by HTML-based UIs."""

    families: tuple[str, ...]
    size: pyd.NonNegativeFloat
    weight: pyd.NonNegativeInt
    line_height: pyd.NonNegativeFloat


@runtime_checkable
class IsHtmlUserInterfaceConfig(IsUserInterfaceTypeConfig, Protocol):
    """Protocol for HTML-based user-interface configuration."""

    font: IsFontConfig


@runtime_checkable
class IsJupyterUserInterfaceConfig(IsHtmlUserInterfaceConfig, IsDimsModeConfig, Protocol):
    """Protocol for Jupyter user-interface configuration."""

    ...


@runtime_checkable
class IsBrowserUserInterfaceConfig(IsHtmlUserInterfaceConfig, Protocol):
    """Protocol for browser user-interface configuration."""

    ...


@runtime_checkable
class IsOverflowConfig(IsConfigBase, Protocol):
    """Protocol for text and layout overflow configuration."""

    horizontal: HorizontalOverflowMode.Literals
    vertical: VerticalOverflowMode.Literals


@runtime_checkable
class IsTextConfig(IsConfigBase, Protocol):
    """Protocol for text rendering configuration."""

    overflow: IsOverflowConfig
    tab_size: pyd.NonNegativeInt
    indent_tab_size: pyd.NonNegativeInt
    pretty_printer: PrettyPrinterLib.Literals
    proportional_freedom: pyd.NonNegativeFloat
    debug_mode: bool


@runtime_checkable
class IsLayoutConfig(IsConfigBase, Protocol):
    """Protocol for panel and layout rendering configuration."""

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
    """Protocol for the complete user-interface configuration tree."""

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
        ...


@runtime_checkable
class IsModelConfig(IsConfigBase, Protocol):
    """Protocol for model-behavior configuration."""

    interactive: bool
    dynamically_convert_elements_to_models: bool


@runtime_checkable
class IsHttpRequestsConfig(IsConfigBase, Protocol):
    """Protocol for HTTP request throttling and retry configuration."""

    requests_per_time_period: float
    time_period_in_secs: float
    retry_http_statuses: tuple[int, ...]
    retry_attempts: int
    retry_backoff_strategy: BackoffStrategy.Literals


@runtime_checkable
class IsHttpConfig(IsConfigBase, Protocol):
    """Protocol for HTTP configuration grouped by host defaults."""

    defaults: IsHttpRequestsConfig
    for_host: defaultdict[str, IsHttpRequestsConfig]


@runtime_checkable
class IsDataConfig(IsConfigBase, Protocol):
    """Protocol for the top-level data configuration."""

    ui: IsUserInterfaceConfig
    model: IsModelConfig
    http: IsHttpConfig


# engine


@runtime_checkable
class IsJobRunnerConfig(IsConfigBase, Protocol):
    """Protocol for engine-specific job runner configuration."""

    ...


@runtime_checkable
class IsLocalRunnerConfig(IsJobRunnerConfig, Protocol):
    """Protocol for local job runner configuration."""

    ...


@runtime_checkable
class IsPrefectEngineConfig(IsJobRunnerConfig, Protocol):
    """Protocol for Prefect engine configuration."""

    use_cached_results: bool = False


@runtime_checkable
class IsEngineConfig(IsConfigBase, Protocol):
    """Protocol for selecting and configuring execution engines."""

    choice: EngineChoice.Literals
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    ...


# job


@runtime_checkable
class IsOutputStorageConfigBase(IsConfigBase, Protocol):
    """Protocol for output-storage configuration with a persistence directory."""

    persist_data_dir_path: str


@runtime_checkable
class IsLocalOutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    """Protocol for local output-storage configuration."""


@runtime_checkable
class IsS3OutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    """Protocol for S3 output-storage configuration."""

    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str


@runtime_checkable
class IsOutputStorageConfig(IsConfigBase, Protocol):
    """Protocol for job output persistence and restore configuration."""

    persist_outputs: ConfigPersistOutputsOptions.Literals
    restore_outputs: ConfigRestoreOutputsOptions.Literals
    protocol: ConfigOutputStorageProtocolOptions.Literals
    local: IsLocalOutputStorageConfig
    s3: IsS3OutputStorageConfig


@runtime_checkable
class IsJobConfig(IsConfigBase, Protocol):
    """Protocol for top-level job configuration."""

    output_storage: IsOutputStorageConfig


# root_log


@runtime_checkable
class IsRootLogConfig(IsConfigBase, Protocol):
    """Protocol for root logging configuration."""

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
