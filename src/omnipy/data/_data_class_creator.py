from abc import ABCMeta
from contextlib import contextmanager
from typing import Callable, ContextManager, Iterator

from omnipy.config.data import DataConfig
from omnipy.shared.protocols.config import IsDataConfig
from omnipy.shared.protocols.data import IsDataClassCreator
from omnipy.shared.protocols.util import HasContents, IsSnapshotHolder
from omnipy.shared.typedefs import TypeForm
import omnipy.util._pydantic as pyd
from omnipy.util.decorators import call_super_if_available
from omnipy.util.helpers import is_union, SnapshotHolder


class DataClassCreator:
    def __init__(self) -> None:
        self._config: IsDataConfig = DataConfig()
        self._snapshot_holder = SnapshotHolder[HasContents, object]()
        self._deepcopy_context_level = 0

    @property
    def config(self) -> IsDataConfig:
        return self._config

    def set_config(self, config: IsDataConfig) -> None:
        self._config = config

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
    @call_super_if_available(call_super_before_method=False)
    @classmethod
    def _prepare_params(cls, params: TypeForm) -> TypeForm:
        # This line is needed for interoperability with pydantic GenericModel, which internally
        # stores the model as a len(1) tuple
        return params[0] if isinstance(params, tuple) and len(params) == 1 else params

    @classmethod
    def _recursively_set_allow_none(cls, field: pyd.ModelField) -> None:
        if field.sub_fields:
            if is_union(field.outer_type_):
                if any(_.allow_none for _ in field.sub_fields):
                    field.allow_none = True

            for sub_field in field.sub_fields:
                cls._recursively_set_allow_none(sub_field)
        if field.key_field:
            if is_union(field.key_field.outer_type_):
                if any(_.allow_none for _ in field.key_field.sub_fields):
                    field.key_field.allow_none = True

            if field.key_field.sub_fields:
                for sub_field in field.key_field.sub_fields:
                    cls._recursively_set_allow_none(sub_field)

    @property
    def _data_class_creator(self) -> IsDataClassCreator:
        return self.__class__.data_class_creator

    @property
    def config(self) -> IsDataConfig:
        return self.__class__.data_class_creator.config

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
