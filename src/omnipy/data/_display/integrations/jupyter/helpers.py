from collections import defaultdict
from typing import TypedDict
from uuid import uuid4

import solara

from omnipy.shared.constants import TERMINAL_DEFAULT_HEIGHT, TERMINAL_DEFAULT_WIDTH
from omnipy.shared.protocols.data import IsAvailableDisplayDimsRegistry
import omnipy.util._pydantic as pyd
from omnipy.util.publisher import DataPublisher


class AvailableDisplayDims(TypedDict):
    width: pyd.NonNegativeInt
    height: pyd.NonNegativeInt


class AvailableDisplayDimsRegistry(defaultdict):
    def __init__(self):
        super().__init__(lambda: solara.reactive(
            AvailableDisplayDims(width=TERMINAL_DEFAULT_WIDTH, height=TERMINAL_DEFAULT_HEIGHT)))

    def new_reactive_obj(self) -> solara.Reactive[AvailableDisplayDims]:
        """
        Create a new reactive object with default display dimensions.

        Returns:
            solara.Reactive[AvailableDisplayDims]: A new reactive object with default dimensions.
        """
        return self[uuid4()]

    def remove_reactive_obj(self, reactive_obj: solara.Reactive[AvailableDisplayDims]) -> None:
        """
        Remove a reactive object from the registry.

        Args:
            reactive_obj (solara.Reactive[AvailableDisplayDims]): The reactive object to remove.
        """
        for key, value in self.items():
            if value is reactive_obj:
                del self[key]
                break


class ReactiveObjects(DataPublisher):
    available_display_dims_registry: IsAvailableDisplayDimsRegistry = pyd.Field(
        default_factory=AvailableDisplayDimsRegistry)
