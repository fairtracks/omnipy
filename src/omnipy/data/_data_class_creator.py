"""Shared creator state and base classes for Omnipy's model and dataset types."""

from abc import ABCMeta
from contextlib import contextmanager
from typing import Callable, cast, ContextManager, Generic, Iterator

from omnipy.config.data import DataConfig
from omnipy.data.snapshot import SnapshotHolder
from omnipy.shared.protocols.config import IsDataConfig
from omnipy.shared.protocols.data import (ContentT,
                                          HasContent,
                                          IsDataClassCreator,
                                          IsReactiveObjects,
                                          IsSnapshotHolder)
from omnipy.shared.typedefs import TypeForm
from omnipy.util.decorators import call_super_if_available
from omnipy.util.helpers import is_union
import omnipy.util.pydantic as pyd


class DataClassCreator:
    """Own shared runtime state for a family of Omnipy data classes.

    The data layer keeps configuration, reactive-object tracking, snapshot handling, and deepcopy
    nesting state on a creator object that is shared by related generated classes.
    """
    def __init__(self) -> None:
        self._config: IsDataConfig = cast(IsDataConfig, DataConfig())
        self._reactive_objects: IsReactiveObjects | None = None
        self._snapshot_holder = SnapshotHolder[HasContent, object]()
        self._deepcopy_context_level = 0

    @property
    def config(self) -> IsDataConfig:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISDATACLASSCREATOR_CONFIG_SUMMARY}}
        #
        # {{ISDATACLASSCREATOR_CONFIG_DETAILS}}
        """Return the data configuration shared by the owning data-class family.

        Returns:
            IsDataConfig: Shared configuration object used by related models and datasets.
"""

        return self._config

    def set_config(self, config: IsDataConfig) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISDATACLASSCREATOR_SET_CONFIG_SUMMARY}}
        #
        # {{ISDATACLASSCREATOR_SET_CONFIG_DETAILS}}
        """Replace the shared data configuration for the owning data-class family.

        Args:
            config: Data configuration object to store for related models and datasets.
"""

        self._config = config

    @property
    def reactive_objects(self) -> IsReactiveObjects | None:
        """Return the reactive-object registry currently attached to this creator."""

        return self._reactive_objects

    def set_reactive_objects(self, reactive_objects: IsReactiveObjects) -> None:
        """Attach the reactive-object registry used by the owning data classes."""

        self._reactive_objects = reactive_objects

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[HasContent, object]:
        """Return the snapshot holder shared across related model and dataset instances."""

        return self._snapshot_holder

    def deepcopy_context(
        self,
        top_level_entry_func: Callable[[], None],
        top_level_exit_func: Callable[[], None],
    ) -> ContextManager[int]:
        """Track nested deepcopy operations and run hooks only at the outermost level.

        Args:
            top_level_entry_func: Callback run when entering the first active deepcopy context.
            top_level_exit_func: Callback run when leaving the last active deepcopy context.

        Returns:
            A context manager yielding the current deepcopy nesting depth.
        """
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
    """Metaclass exposing the shared creator object for Omnipy data classes."""

    _data_class_creator_obj: IsDataClassCreator = DataClassCreator()

    @property
    def data_class_creator(self) -> IsDataClassCreator:
        """Return the creator object shared by classes using this metaclass."""

        return self._data_class_creator_obj


class DataClassBase(Generic[ContentT], metaclass=DataClassBaseMeta):
    """Base class that gives Omnipy data classes shared config and snapshot access.

    Model and dataset implementations inherit this class to reach the shared creator state
    managed by ``DataClassCreator`` while keeping instance APIs small.
    """
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
                assert field.key_field.sub_fields is not None
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
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISDATACLASSCREATOR_CONFIG_SUMMARY}}
        #
        # {{ISDATACLASSCREATOR_CONFIG_DETAILS}}
        """Return the data configuration shared by the owning data-class family.

        Returns:
            IsDataConfig: Shared configuration object used by related models and datasets.
"""

        return self.__class__.data_class_creator.config

    @property
    def reactive_objects(self) -> IsReactiveObjects | None:
        """Return the reactive-object registry attached to this data-class family."""

        return self.__class__.data_class_creator.reactive_objects

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[HasContent, ContentT]:
        """Return the snapshot holder coordinating copy-based change tracking."""

        return self.__class__.data_class_creator.snapshot_holder

    def deepcopy_context(
        self,
        top_level_entry_func: Callable[[], None],
        top_level_exit_func: Callable[[], None],
    ) -> ContextManager[int]:
        """Delegate nested deepcopy bookkeeping to the shared data-class creator.

        Args:
            top_level_entry_func: Callback run when entering the outermost deepcopy context.
            top_level_exit_func: Callback run when leaving the outermost deepcopy context.

        Returns:
            A context manager yielding the current deepcopy nesting depth.
        """

        return self.__class__.data_class_creator.deepcopy_context(top_level_entry_func,
                                                                  top_level_exit_func)
