from collections import defaultdict
from io import TextIOBase
from typing import Protocol, runtime_checkable

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
import omnipy.util._pydantic as pyd


@runtime_checkable
class IsConfigBase(IsDataPublisher, Protocol):
    """"""
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
    """"""
    system: DisplayColorSystem.Literals
    style: AllColorStyles.Literals | str
    dark_background: bool
    solid_background: bool


@runtime_checkable
class IsUserInterfaceTypeConfig(IsConfigBase, Protocol):
    """"""
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
    """"""
    dims_mode: DisplayDimensionsUpdateMode.Literals = DisplayDimensionsUpdateMode.AUTO


@runtime_checkable
class IsDimsModeConfig(IsUserInterfaceTypeConfig, IsDimsModeMixin, Protocol):
    """"""
    ...


@runtime_checkable
class IsTerminalUserInterfaceConfig(IsDimsModeConfig, Protocol):
    """"""
    ...


@runtime_checkable
class IsFontConfig(IsConfigBase, Protocol):
    """"""
    families: tuple[str, ...]
    size: pyd.NonNegativeInt
    weight: pyd.NonNegativeInt
    line_height: pyd.NonNegativeFloat


@runtime_checkable
class IsHtmlUserInterfaceConfig(IsUserInterfaceTypeConfig, Protocol):
    """"""
    font: IsFontConfig


@runtime_checkable
class IsJupyterUserInterfaceConfig(IsHtmlUserInterfaceConfig, IsDimsModeConfig, Protocol):
    """"""
    ...


@runtime_checkable
class IsBrowserUserInterfaceConfig(IsHtmlUserInterfaceConfig, Protocol):
    """"""
    ...


@runtime_checkable
class IsOverflowConfig(IsConfigBase, Protocol):
    """"""
    horizontal: HorizontalOverflowMode.Literals
    vertical: VerticalOverflowMode.Literals


@runtime_checkable
class IsTextConfig(IsConfigBase, Protocol):
    """"""
    overflow: IsOverflowConfig
    tab_size: pyd.NonNegativeInt
    indent_tab_size: pyd.NonNegativeInt
    pretty_printer: PrettyPrinterLib.Literals
    proportional_freedom: pyd.NonNegativeFloat
    debug_mode: bool


@runtime_checkable
class IsLayoutConfig(IsConfigBase, Protocol):
    """"""
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
    """"""
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
    """"""
    interactive: bool
    dynamically_convert_elements_to_models: bool


@runtime_checkable
class IsHttpRequestsConfig(IsConfigBase, Protocol):
    """"""
    requests_per_time_period: float
    time_period_in_secs: float
    retry_http_statuses: tuple[int, ...]
    retry_attempts: int
    retry_backoff_strategy: BackoffStrategy.Literals


@runtime_checkable
class IsHttpConfig(IsConfigBase, Protocol):
    """"""
    defaults: IsHttpRequestsConfig
    for_host: defaultdict[str, IsHttpRequestsConfig]


@runtime_checkable
class IsDataConfig(IsConfigBase, Protocol):
    """"""
    ui: IsUserInterfaceConfig
    model: IsModelConfig
    http: IsHttpConfig


# engine


@runtime_checkable
class IsJobRunnerConfig(IsConfigBase, Protocol):
    """"""
    ...


@runtime_checkable
class IsLocalRunnerConfig(IsJobRunnerConfig, Protocol):
    """"""
    ...


@runtime_checkable
class IsPrefectEngineConfig(IsJobRunnerConfig, Protocol):
    """"""
    use_cached_results: bool = False


@runtime_checkable
class IsEngineConfig(IsConfigBase, Protocol):
    """"""
    choice: EngineChoice.Literals
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    ...


# job


@runtime_checkable
class IsOutputStorageConfigBase(IsConfigBase, Protocol):
    """"""
    persist_data_dir_path: str


@runtime_checkable
class IsLocalOutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    """"""


@runtime_checkable
class IsS3OutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    """"""
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str


@runtime_checkable
class IsOutputStorageConfig(IsConfigBase, Protocol):
    """"""
    persist_outputs: ConfigPersistOutputsOptions.Literals
    restore_outputs: ConfigRestoreOutputsOptions.Literals
    protocol: ConfigOutputStorageProtocolOptions.Literals
    local: IsLocalOutputStorageConfig
    s3: IsS3OutputStorageConfig


@runtime_checkable
class IsJobConfig(IsConfigBase, Protocol):
    """"""
    output_storage: IsOutputStorageConfig


# root_log


@runtime_checkable
class IsRootLogConfig(IsConfigBase, Protocol):
    """"""
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
