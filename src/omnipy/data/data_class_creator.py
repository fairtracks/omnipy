from abc import ABCMeta
from typing import Any

from omnipy.api.protocols.private.data import IsDataClassCreator
from omnipy.api.protocols.private.util import IsSnapshotHolder
from omnipy.api.protocols.public.config import IsDataConfig
from omnipy.config.data import DataConfig
from omnipy.util.helpers import SnapshotHolder


class DataClassCreator:
    def __init__(self) -> None:
        self._config: IsDataConfig = DataConfig()
        self._snapshot_holder = SnapshotHolder[object, Any]()

    def set_config(self, config: IsDataConfig) -> None:
        self._config = config

    @property
    def config(self) -> IsDataConfig:
        return self._config

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[object, Any]:
        return self._snapshot_holder


class DataClassBaseMeta(ABCMeta):
    """"""
    _data_class_creator_obj = DataClassCreator()

    @property
    def data_class_creator(self) -> IsDataClassCreator:
        return self._data_class_creator_obj


class DataClassBase(metaclass=DataClassBaseMeta):
    @property
    def _data_class_creator(self) -> IsDataClassCreator:
        return self.__class__.data_class_creator

    @property
    def config(self) -> IsDataConfig:
        return self.__class__.data_class_creator.config

    @property
    def snapshot_holder(self) -> IsSnapshotHolder:
        return self.__class__.data_class_creator.snapshot_holder
