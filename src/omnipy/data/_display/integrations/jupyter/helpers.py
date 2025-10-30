from typing import Generic

import solara
from solara.toestand import ValueBase
from typing_extensions import TypeVar

from omnipy.config.data import JupyterUserInterfaceConfig, LayoutConfig, TextConfig
from omnipy.shared.protocols.config import (IsJupyterUserInterfaceConfig,
                                            IsLayoutConfig,
                                            IsTextConfig)
from omnipy.shared.protocols.data import AvailableDisplayDims
from omnipy.util import _pydantic as pyd
from omnipy.util.publisher import DataPublisher

ConfigBaseT = TypeVar('ConfigBaseT')


class ReactiveConfigCopy(solara.Reactive[ConfigBaseT], Generic[ConfigBaseT]):
    """
    A `solara.Reactive` wrapper for a `ConfigBase` object that ensures deep
    copies are made at initialization and when setting values. This is part
    of a workaround of the lack for support in `solara.Reactive` for
    detecting changes in nested mutable objects (see "Mutation pitfalls" in
    the Solara documentation:
    https://solara.dev/documentation/getting_started/fundamentals/state-management).
    """
    def __init__(self, default_value: ConfigBaseT | ValueBase[ConfigBaseT], key=None, equals=None):
        if not isinstance(default_value, ValueBase):
            super().__init__(default_value.deepcopy(), key=key, equals=equals)
        else:
            super().__init__(default_value, key=key, equals=equals)

    def set(self, value: ConfigBaseT) -> None:
        super().set(value.deepcopy())


class ReactiveObjects(DataPublisher):
    """
    Holds reactive objects used throughout the Omnipy library.

    JupyterUserInterfaceConfig contains nested mutable objects that are
    all instances of misc. Config classes. Changes to those nested objects
    will not be detected by solara.Reactive (see "Mutation pitfalls" in
    the Solara documentation:
    https://solara.dev/documentation/getting_started/fundamentals/state-management).
    However, all Config classes inherit from DataPublisher, which makes
    sure that any changes to the config will automatically be published to
    all subscribers, including subscribers to parent objects. Therefore,
    to circumvent the solara.Reactive limitation, we wrap the
    JupyterUserInterfaceConfig in a ReactiveConfigCopy, which ensures that
    deep copies are made when setting new value. Also, we register
    jupyter_ui_config.set() as a subscriber to the main jupyter config (in
    hub/runtime.py:Runtime.reset_subscriptions()). With this, all changes
    to the main Jupyter config will propagate to the reactive
    `jupyter_ui_config` object contained in the ReactiveObjects instance,
    allowing solara to detect changes and propagate the update to all
    reactive components that read from `jupyter_ui_config`. Similarly, we
    wrap the TextConfig and LayoutConfig in ReactiveConfigCopy instances to
    ensure that changes to those configs are also detected.
    """
    jupyter_ui_config: solara.Reactive[IsJupyterUserInterfaceConfig] = pyd.Field(
        default_factory=lambda: ReactiveConfigCopy(JupyterUserInterfaceConfig()))
    text_config: solara.Reactive[IsTextConfig] = pyd.Field(
        default_factory=lambda: ReactiveConfigCopy(TextConfig()))
    layout_config: solara.Reactive[IsLayoutConfig] = pyd.Field(
        default_factory=lambda: ReactiveConfigCopy(LayoutConfig()))
    available_display_dims_in_px: solara.Reactive[AvailableDisplayDims] = pyd.Field(
        default_factory=lambda: solara.Reactive(AvailableDisplayDims(width=0, height=0)))

    def __eq__(self, other) -> bool:
        if not isinstance(other, ReactiveObjects):
            return False
        return all(
            getattr(self, field.name).value == getattr(other, field.name).value
            for field in self.__class__.__fields__.values())
