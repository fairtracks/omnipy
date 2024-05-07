from abc import ABCMeta

from omnipy.api.protocols.private.data import IsDataConfigHolder
from omnipy.api.protocols.public.config import IsDataConfig
from omnipy.config.data import DataConfig


class DataClassCreator:
    def __init__(self) -> None:
        self._config: IsDataConfig = DataConfig()

    def set_config(self, config: IsDataConfig) -> None:
        self._config = config

    @property
    def config(self) -> IsDataConfig:
        return self._config


class DataClassBaseMeta(ABCMeta):
    """"""
    _data_class_creator_obj = DataClassCreator()

    @property
    def data_class_creator(self) -> IsDataConfigHolder:
        return self._data_class_creator_obj


class DataClassBase(metaclass=DataClassBaseMeta):
    @property
    def _data_class_creator(self) -> IsDataConfigHolder:
        return self.__class__.data_class_creator

    @property
    def config(self) -> IsDataConfig:
        return self.__class__.data_class_creator.config
