from abc import ABCMeta
from contextlib import contextmanager
from typing import Callable, ContextManager, Iterator

from omnipy.api.enums import DataReprState
from omnipy.api.protocols.private.data import IsDataClassCreator
from omnipy.api.protocols.private.util import HasContents, IsSnapshotHolder
from omnipy.api.protocols.public.config import IsDataConfig
from omnipy.config.data import DataConfig
from omnipy.util.helpers import SnapshotHolder


class DataClassCreator:
    def __init__(self) -> None:
        self._config: IsDataConfig = DataConfig()
        self._snapshot_holder = SnapshotHolder[HasContents, object]()
        self._deepcopy_context_level = 0
        self._repr_state: DataReprState = DataReprState.UNKNOWN

    @property
    def config(self) -> IsDataConfig:
        return self._config

    def set_config(self, config: IsDataConfig) -> None:
        self._config = config

    @property
    def repr_state(self) -> DataReprState:
        return self._repr_state

    @repr_state.setter
    def repr_state(self, repr_state: DataReprState) -> None:
        self._repr_state = repr_state

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[HasContents, object]:
        return self._snapshot_holder

    def deepcopy_context(
        self,
        top_level_entry_func: Callable[[], None],
        top_level_exit_func: Callable[[], None],
    ) -> ContextManager[int]:
        @contextmanager
        def _call_exit_func_if_top_level(*args, **kwds) -> Iterator[int]:
            if self._deepcopy_context_level == 0:
                top_level_entry_func()

            self._deepcopy_context_level += 1

            try:
                yield self._deepcopy_context_level
            finally:
                self._deepcopy_context_level -= 1

                if self._deepcopy_context_level == 0:
                    top_level_exit_func()

        return _call_exit_func_if_top_level()


class DataClassBaseMeta(ABCMeta):
    """"""
    _data_class_creator_obj: IsDataClassCreator = DataClassCreator()

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
    def repr_state(self) -> DataReprState:
        return self.__class__.data_class_creator.repr_state

    @repr_state.setter
    def repr_state(self, repr_state: DataReprState) -> None:
        self.__class__.data_class_creator.repr_state = repr_state

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[HasContents, object]:
        return self.__class__.data_class_creator.snapshot_holder

    def deepcopy_context(
        self,
        top_level_entry_func: Callable[[], None],
        top_level_exit_func: Callable[[], None],
    ) -> ContextManager[int]:
        return self.__class__.data_class_creator.deepcopy_context(top_level_entry_func,
                                                                  top_level_exit_func)
