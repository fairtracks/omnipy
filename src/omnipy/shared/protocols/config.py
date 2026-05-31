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
        """Default repr to terminal str.
        
        Args:
            ui_type: (TerminalOutputUserInterfaceType.Literals) Argument passed to ``default_repr_to_terminal_str()``.
        
        Returns:
            str: Result produced by ``default_repr_to_terminal_str()``.
        """
        ...

    def __str__(self) -> str:
        ...


# data


@runtime_checkable
class IsColorConfig(IsConfigBase, Protocol):
    """Define the ``IsColorConfig`` interface.
    
    Attributes:
        system: (DisplayColorSystem.Literals) Public attribute on the protocol/class.
        style: (AllColorStyles.Literals | str) Public attribute on the protocol/class.
        dark_background: (bool) Public attribute on the protocol/class.
        solid_background: (bool) Public attribute on the protocol/class.
    """

    system: DisplayColorSystem.Literals
    style: AllColorStyles.Literals | str
    dark_background: bool
    solid_background: bool


@runtime_checkable
class IsUserInterfaceTypeConfig(IsConfigBase, Protocol):
    """Define the ``IsUserInterfaceTypeConfig`` interface.
    
    Attributes:
        width: (pyd.NonNegativeInt | None) Public attribute on the protocol/class.
        height: (pyd.NonNegativeInt | None) Public attribute on the protocol/class.
        color: (IsColorConfig) Public attribute on the protocol/class.
    """

    width: pyd.NonNegativeInt | None
    height: pyd.NonNegativeInt | None
    color: IsColorConfig

    def set_width_and_height(
        self,
        width: pyd.NonNegativeInt | None,
        height: pyd.NonNegativeInt | None,
    ) -> None:
        """Set width and height.
        
        Args:
            width: (pyd.NonNegativeInt | None) Argument passed to ``set_width_and_height()``.
            height: (pyd.NonNegativeInt | None) Argument passed to ``set_width_and_height()``.
        """


@runtime_checkable
class IsDimsModeMixin(Protocol):
    """Define the ``IsDimsModeMixin`` interface.
    
    Attributes:
        dims_mode: (DisplayDimensionsUpdateMode.Literals) Public attribute on the protocol/class.
    """

    dims_mode: DisplayDimensionsUpdateMode.Literals = DisplayDimensionsUpdateMode.AUTO


@runtime_checkable
class IsDimsModeConfig(IsUserInterfaceTypeConfig, IsDimsModeMixin, Protocol):
    """Define the ``IsDimsModeConfig`` interface.
    """

    ...


@runtime_checkable
class IsTerminalUserInterfaceConfig(IsDimsModeConfig, Protocol):
    """Define the ``IsTerminalUserInterfaceConfig`` interface.
    """

    ...


@runtime_checkable
class IsFontConfig(IsConfigBase, Protocol):
    """Define the ``IsFontConfig`` interface.
    
    Attributes:
        families: (tuple[str, ...]) Public attribute on the protocol/class.
        size: (pyd.NonNegativeInt) Public attribute on the protocol/class.
        weight: (pyd.NonNegativeInt) Public attribute on the protocol/class.
        line_height: (pyd.NonNegativeFloat) Public attribute on the protocol/class.
    """

    families: tuple[str, ...]
    size: pyd.NonNegativeFloat
    weight: pyd.NonNegativeInt
    line_height: pyd.NonNegativeFloat


@runtime_checkable
class IsHtmlUserInterfaceConfig(IsUserInterfaceTypeConfig, Protocol):
    """Define the ``IsHtmlUserInterfaceConfig`` interface.
    
    Attributes:
        font: (IsFontConfig) Public attribute on the protocol/class.
    """

    font: IsFontConfig


@runtime_checkable
class IsJupyterUserInterfaceConfig(IsHtmlUserInterfaceConfig, IsDimsModeConfig, Protocol):
    """Define the ``IsJupyterUserInterfaceConfig`` interface.
    """

    ...


@runtime_checkable
class IsBrowserUserInterfaceConfig(IsHtmlUserInterfaceConfig, Protocol):
    """Define the ``IsBrowserUserInterfaceConfig`` interface.
    """

    ...


@runtime_checkable
class IsOverflowConfig(IsConfigBase, Protocol):
    """Define the ``IsOverflowConfig`` interface.
    
    Attributes:
        horizontal: (HorizontalOverflowMode.Literals) Public attribute on the protocol/class.
        vertical: (VerticalOverflowMode.Literals) Public attribute on the protocol/class.
    """

    horizontal: HorizontalOverflowMode.Literals
    vertical: VerticalOverflowMode.Literals


@runtime_checkable
class IsTextConfig(IsConfigBase, Protocol):
    """Define the ``IsTextConfig`` interface.
    
    Attributes:
        overflow: (IsOverflowConfig) Public attribute on the protocol/class.
        tab_size: (pyd.NonNegativeInt) Public attribute on the protocol/class.
        indent_tab_size: (pyd.NonNegativeInt) Public attribute on the protocol/class.
        pretty_printer: (PrettyPrinterLib.Literals) Public attribute on the protocol/class.
        proportional_freedom: (pyd.NonNegativeFloat) Public attribute on the protocol/class.
        debug_mode: (bool) Public attribute on the protocol/class.
    """

    overflow: IsOverflowConfig
    tab_size: pyd.NonNegativeInt
    indent_tab_size: pyd.NonNegativeInt
    pretty_printer: PrettyPrinterLib.Literals
    proportional_freedom: pyd.NonNegativeFloat
    debug_mode: bool


@runtime_checkable
class IsLayoutConfig(IsConfigBase, Protocol):
    """Define the ``IsLayoutConfig`` interface.
    
    Attributes:
        overflow: (IsOverflowConfig) Public attribute on the protocol/class.
        panel_design: (PanelDesign.Literals) Public attribute on the protocol/class.
        panel_title_at_top: (bool) Public attribute on the protocol/class.
        max_title_height: (MaxTitleHeight.Literals) Public attribute on the protocol/class.
        min_panel_width: (pyd.NonNegativeInt) Public attribute on the protocol/class.
        min_crop_width: (pyd.NonNegativeInt) Public attribute on the protocol/class.
        max_panels_hor: (pyd.NonNegativeInt | None) Public attribute on the protocol/class.
        max_nesting_depth: (pyd.NonNegativeInt | None) Public attribute on the protocol/class.
        justify: (Justify.Literals) Public attribute on the protocol/class.
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
    """Define the ``IsUserInterfaceConfig`` interface.
    
    Attributes:
        detected_type: (SpecifiedUserInterfaceType.Literals) Public attribute on the protocol/class.
        terminal: (IsTerminalUserInterfaceConfig) Public attribute on the protocol/class.
        jupyter: (IsJupyterUserInterfaceConfig) Public attribute on the protocol/class.
        browser: (IsBrowserUserInterfaceConfig) Public attribute on the protocol/class.
        text: (IsTextConfig) Public attribute on the protocol/class.
        layout: (IsLayoutConfig) Public attribute on the protocol/class.
        cache_dir_path: (str) Public attribute on the protocol/class.
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
        """Get ui type config.
        
        Args:
            ui_type: (SpecifiedUserInterfaceType.Literals) Argument passed to ``get_ui_type_config()``.
        
        Returns:
            IsUserInterfaceTypeConfig: Result produced by ``get_ui_type_config()``.
        """
        ...


@runtime_checkable
class IsModelConfig(IsConfigBase, Protocol):
    """Define the ``IsModelConfig`` interface.
    
    Attributes:
        interactive: (bool) Public attribute on the protocol/class.
        dynamically_convert_elements_to_models: (bool) Public attribute on the protocol/class.
    """

    interactive: bool
    dynamically_convert_elements_to_models: bool


@runtime_checkable
class IsHttpRequestsConfig(IsConfigBase, Protocol):
    """Define the ``IsHttpRequestsConfig`` interface.
    
    Attributes:
        requests_per_time_period: (float) Public attribute on the protocol/class.
        time_period_in_secs: (float) Public attribute on the protocol/class.
        retry_http_statuses: (tuple[int, ...]) Public attribute on the protocol/class.
        retry_attempts: (int) Public attribute on the protocol/class.
        retry_backoff_strategy: (BackoffStrategy.Literals) Public attribute on the protocol/class.
    """

    requests_per_time_period: float
    time_period_in_secs: float
    retry_http_statuses: tuple[int, ...]
    retry_attempts: int
    retry_backoff_strategy: BackoffStrategy.Literals


@runtime_checkable
class IsHttpConfig(IsConfigBase, Protocol):
    """Define the ``IsHttpConfig`` interface.
    
    Attributes:
        defaults: (IsHttpRequestsConfig) Public attribute on the protocol/class.
        for_host: (defaultdict[str, IsHttpRequestsConfig]) Public attribute on the protocol/class.
    """

    defaults: IsHttpRequestsConfig
    for_host: defaultdict[str, IsHttpRequestsConfig]


@runtime_checkable
class IsDataConfig(IsConfigBase, Protocol):
    """Define the ``IsDataConfig`` interface.
    
    Attributes:
        ui: (IsUserInterfaceConfig) Public attribute on the protocol/class.
        model: (IsModelConfig) Public attribute on the protocol/class.
        http: (IsHttpConfig) Public attribute on the protocol/class.
    """

    ui: IsUserInterfaceConfig
    model: IsModelConfig
    http: IsHttpConfig


# engine


@runtime_checkable
class IsJobRunnerConfig(IsConfigBase, Protocol):
    """Define the ``IsJobRunnerConfig`` interface.
    """

    ...


@runtime_checkable
class IsLocalRunnerConfig(IsJobRunnerConfig, Protocol):
    """Define the ``IsLocalRunnerConfig`` interface.
    """

    ...


@runtime_checkable
class IsPrefectEngineConfig(IsJobRunnerConfig, Protocol):
    """Define the ``IsPrefectEngineConfig`` interface.
    
    Attributes:
        use_cached_results: (bool) Public attribute on the protocol/class.
    """

    use_cached_results: bool = False


@runtime_checkable
class IsEngineConfig(IsConfigBase, Protocol):
    """Define the ``IsEngineConfig`` interface.
    
    Attributes:
        choice: (EngineChoice.Literals) Public attribute on the protocol/class.
        local: (IsLocalRunnerConfig) Public attribute on the protocol/class.
        prefect: (IsPrefectEngineConfig) Public attribute on the protocol/class.
    """

    choice: EngineChoice.Literals
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    ...


# job


@runtime_checkable
class IsOutputStorageConfigBase(IsConfigBase, Protocol):
    """Define the ``IsOutputStorageConfigBase`` interface.
    
    Attributes:
        persist_data_dir_path: (str) Public attribute on the protocol/class.
    """

    persist_data_dir_path: str


@runtime_checkable
class IsLocalOutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    """Define the ``IsLocalOutputStorageConfig`` interface.
    """


@runtime_checkable
class IsS3OutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    """Define the ``IsS3OutputStorageConfig`` interface.
    
    Attributes:
        endpoint_url: (str) Public attribute on the protocol/class.
        access_key: (str) Public attribute on the protocol/class.
        secret_key: (str) Public attribute on the protocol/class.
        bucket_name: (str) Public attribute on the protocol/class.
    """

    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str


@runtime_checkable
class IsOutputStorageConfig(IsConfigBase, Protocol):
    """Define the ``IsOutputStorageConfig`` interface.
    
    Attributes:
        persist_outputs: (ConfigPersistOutputsOptions.Literals) Public attribute on the protocol/class.
        restore_outputs: (ConfigRestoreOutputsOptions.Literals) Public attribute on the protocol/class.
        protocol: (ConfigOutputStorageProtocolOptions.Literals) Public attribute on the protocol/class.
        local: (IsLocalOutputStorageConfig) Public attribute on the protocol/class.
        s3: (IsS3OutputStorageConfig) Public attribute on the protocol/class.
    """

    persist_outputs: ConfigPersistOutputsOptions.Literals
    restore_outputs: ConfigRestoreOutputsOptions.Literals
    protocol: ConfigOutputStorageProtocolOptions.Literals
    local: IsLocalOutputStorageConfig
    s3: IsS3OutputStorageConfig


@runtime_checkable
class IsJobConfig(IsConfigBase, Protocol):
    """Define the ``IsJobConfig`` interface.
    
    Attributes:
        output_storage: (IsOutputStorageConfig) Public attribute on the protocol/class.
    """

    output_storage: IsOutputStorageConfig


# root_log


@runtime_checkable
class IsRootLogConfig(IsConfigBase, Protocol):
    """Define the ``IsRootLogConfig`` interface.
    
    Attributes:
        log_format_str: (str) Public attribute on the protocol/class.
        locale: (LocaleType) Public attribute on the protocol/class.
        log_to_stdout: (bool) Public attribute on the protocol/class.
        log_to_stderr: (bool) Public attribute on the protocol/class.
        log_to_file: (bool) Public attribute on the protocol/class.
        stdout: (TextIOBase) Public attribute on the protocol/class.
        stderr: (TextIOBase) Public attribute on the protocol/class.
        stdout_log_min_level: (int) Public attribute on the protocol/class.
        stderr_log_min_level: (int) Public attribute on the protocol/class.
        file_log_min_level: (int) Public attribute on the protocol/class.
        file_log_path: (str) Public attribute on the protocol/class.
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
