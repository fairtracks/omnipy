"""Typed dataset containers and dataset type predicates.

This module defines :class:`Dataset`, the core Omnipy container for named data items that all
share the same model or nested dataset type. It also provides helper predicates for checking
dataset instances and subclasses in a lenient way that works with the library's generic types.
"""

import asyncio
from collections import defaultdict, UserDict
from collections.abc import Iterable, Mapping, MutableMapping
from copy import copy
import functools
import inspect
import json
import os
import tarfile
from textwrap import dedent
from typing import Any, Callable, cast, Generic, Iterator, overload

from typing_extensions import override, Self, TypeIs, TypeVar

from omnipy.data._data_class_creator import DataClassBase, DataClassBaseMeta
from omnipy.data._mixins.display import DatasetDisplayMixin
from omnipy.data._mixins.task import TaskDatasetMixin
from omnipy.data._selector import (create_updated_mapping,
                                   Index2DataItemsType,
                                   Key2DataItemType,
                                   prepare_selected_items_with_iterable_data,
                                   prepare_selected_items_with_mapping_data,
                                   select_keys)
from omnipy.data.helpers import (build_own_module_and_global_namespace_for_forward_refs,
                                 cleanup_name_qualname_and_module)
from omnipy.shared.constants import ASYNC_LOAD_SLEEP_TIME, DATA_KEY
from omnipy.shared.protocols.data import (IsHttpUrlDataset,
                                          IsMultiModelDataset,
                                          IsPathOrUrl,
                                          IsPathsOrUrlsOneOrMoreOrNone)
from omnipy.shared.typedefs import TypeForm
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util._placeholder import F
from omnipy.util.decorators import call_super_if_available
from omnipy.util.helpers import (evaluate_any_forward_refs_if_possible,
                                 get_calling_module_name,
                                 get_default_if_typevar,
                                 get_event_loop_and_check_if_loop_is_running,
                                 is_iterable,
                                 remove_forward_ref_notation,
                                 split_to_union_variants)
from omnipy.util.pydantic import (lenient_isinstance,
                                  lenient_issubclass,
                                  Undefined,
                                  UndefinedType,
                                  ValidationError)
import omnipy.util.pydantic as pyd

if TYPE_CHECKING:
    from omnipy.data._typing.mimic_models import (Model_bool,
                                                  Model_bytes,
                                                  Model_Dataset,
                                                  Model_dict,
                                                  Model_float,
                                                  Model_int,
                                                  Model_list,
                                                  Model_set,
                                                  Model_str,
                                                  Model_tuple_pair,
                                                  Model_tuple_same_type)
    from omnipy.data._typing.typedefs import _KeyT, _ValT, _ValT2
    from omnipy.data.model import Model

_ModelOrDatasetT = TypeVar('_ModelOrDatasetT', bound='Model | Dataset')
_OtherModelOrDatasetT = TypeVar('_OtherModelOrDatasetT', bound='Model | Dataset')
_DatasetT = TypeVar('_DatasetT', bound='Dataset')
_ModelT = TypeVar('_ModelT', bound='Model')
_Model2T = TypeVar('_Model2T', bound='Model')
_Model3T = TypeVar('_Model3T', bound='Model')
_Model4T = TypeVar('_Model4T', bound='Model')
_NewModelT = TypeVar('_NewModelT', bound='Model')

# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()

# TODO: implement copy(), __copy__() and __deepcopy__() for Dataset and Model, making use of
#       pyd.BaseModel.copy()

# Due to overriding the dict method of pydantic GenericModel, we need to
# redefine dict here to be able to use it for typing in Dataset methods.
# Otherwise, python syntax checkers will assume that 'dict' in method signatures
# refers to the method instead of the built-in dict type.

dict_t = dict


class _DatasetMetaclass(DataClassBaseMeta, pyd.ModelMetaclass):
    """Combine Omnipy and Pydantic metaclass behavior for datasets.

    This metaclass lets :class:`Dataset` participate in both Omnipy's data-class creation hooks
    and Pydantic's generic-model machinery when specialized dataset subclasses are created.

    Args:
        None: This metaclass is used implicitly by class creation rather than instantiated
            directly in ordinary code.

    Attributes:
        None: This metaclass defines no public attributes beyond those inherited from its bases.
    """

    ...


class Dataset(
        DatasetDisplayMixin,
        TaskDatasetMixin,
        DataClassBase,
        pyd.GenericModel,
        UserDict[str, _ModelOrDatasetT],
        Generic[_ModelOrDatasetT],
        metaclass=_DatasetMetaclass):
    """Store named, typed data items in a dict-like container.

    ``Dataset`` is Omnipy's core container for collections of data items that all conform to the
    same model type, or to the same nested dataset type. The class must be specialized before use,
    for example as ``Dataset[Model[list[int]]]`` or ``Dataset[MyModel]``.

    Instances behave much like mutable dictionaries whose keys are data-file names and whose values
    are validated model or dataset objects. The validated backing contents live in :attr:`data`,
    while convenience methods such as :meth:`from_data`, :meth:`to_data`, :meth:`to_json`, and
    :meth:`load` expose plain-Python, JSON, and serialized representations.

    Item access supports both ordinary dictionary-style keys and dataset-specific selectors such as
    integer positions, slices, and iterables of keys or positions. Singular selection returns one
    validated item; plural selection returns a new dataset of the same specialized class.

    Attributes:
        data: Mapping from data-file names to validated model or nested dataset instances.

    """
    class Config:
        """Configure Pydantic behavior for dataset instances.

        The nested config enables assignment-time validation and permits arbitrary runtime types
        needed by Omnipy's dataset internals.

        Attributes:
            validate_assignment: Re-validate fields whenever attributes are reassigned.
            arbitrary_types_allowed: Permit non-Pydantic helper types in the model definition.
        """
        validate_assignment = True
        arbitrary_types_allowed = True

        # TODO: Use json serializer package from the pydantic config instead of 'json'

        # json_loads = orjson.loads
        # json_dumps = orjson_dumps

    if TYPE_CHECKING:
        data: dict_t[str, _ModelOrDatasetT] = pyd.Field(default={})

    else:

        # TODO: For pydantic v2, remove hack in Dataset to stop e.g.
        #       [{'a': 'b', 'c': 'd'}] to be coerced into {'a': 'c'} (remove
        #       first part of the union below, and edit get_type() and to_json_schema())
        data: list[dict_t[str, _ModelOrDatasetT]] | dict_t[str, _ModelOrDatasetT] = pyd.Field(
            default={})

    # data: dict[str, _ModelOrDatasetT] = pyd.Field(default={})

    def __class_getitem__(  # type: ignore[override]
        cls,
        params: type[_ModelOrDatasetT] | tuple[type[_ModelOrDatasetT]]
        | tuple[type[_ModelOrDatasetT], Any] | TypeVar
        | tuple[TypeVar, ...],
    ) -> Self:
        """Specialize the dataset class with a concrete model or nested dataset type.

        Args:
            params: The model type, dataset type, union of such types, or type variable used to
                parameterize the dataset.

        Returns:
            A specialized ``Dataset`` subclass bound to the supplied item type.

        Raises:
            TypeError: If the supplied type argument is not a supported model or dataset type.
        """
        # TODO: change model type to params: Type[Any] | tuple[Type[Any], ...]
        #       as in GenericModel.

        _params = cls._prepare_params(params)
        orig_params = cls._clean_type(_params)

        if cls == Dataset:
            for type_variant in split_to_union_variants(orig_params):
                from omnipy.data.model import is_model_subclass

                if (not isinstance(type_variant,
                                   (TypeVar, str)) and not is_model_subclass(type_variant)
                        and not is_dataset_subclass(type_variant)):
                    cls._raise_type_exception(f'Invalid model: {orig_params} ')
        else:
            if isinstance(orig_params, TypeVar):
                _params = get_default_if_typevar(orig_params)

        created_dataset = super().__class_getitem__(_params)
        cls._recursively_set_allow_none(created_dataset._get_data_field())
        cleanup_name_qualname_and_module(cls, created_dataset, orig_params)

        return cast(Self, created_dataset)

    @call_super_if_available(call_super_before_method=True)
    @classmethod
    def _clean_type(cls, _type: TypeForm) -> TypeForm:
        """Normalize a dataset item type before it is cached or exposed.

        Subclasses can override this hook to rewrite forward references or other type forms before
        the dataset stores them as its effective item type.

        Args:
            _type: Candidate model or dataset type form.

        Returns:
            The normalized type form.
        """
        return _type

    def __init__(  # noqa: C901
        self,
        value: Mapping[str, object] | Iterable[tuple[str, object]] | UndefinedType = Undefined,
        *,
        data: Mapping[str, object] | UndefinedType = Undefined,
        **kwargs: object,
    ) -> None:
        from omnipy.data.model import is_model_instance, is_pure_pydantic_model

        # TODO: Error message when forgetting parenthesis when creating Dataset should be improved.
        #       Unclear where this can be done, if anywhere? E.g.:
        #           a = Dataset[Model[int]]
        #           a['adsfas'] = 2
        #           Traceback (most recent call last):
        #             ...
        #           TypeError: 'ModelMetaclass' object does not support item assignment
        #
        # TODO: Disallow e.g.:
        #       Dataset[Model[str]](Model[int](5)) ==  Dataset[Model[str]](data=Model[int](5))
        #       == Dataset[Model[str]](data={'__root__': Model[str]('5')})

        super_kwargs = {}

        assert DATA_KEY not in kwargs, \
            ('Not allowed with "data" as kwargs key. Not sure how you managed this? Are you trying '
             'to break Dataset init on purpose?')

        if value != Undefined:
            assert data == Undefined, \
                'Not allowed to combine positional and "data" keyword argument'
            assert len(kwargs) == 0, \
                'Not allowed to combine positional and keyword arguments'
            super_kwargs[DATA_KEY] = value

        if data != Undefined:
            assert len(kwargs) == 0, \
                f"Not allowed to combine '{DATA_KEY}' with other keyword arguments"
            super_kwargs[DATA_KEY] = data

        if kwargs:
            if DATA_KEY not in super_kwargs:
                super_kwargs[DATA_KEY] = kwargs
                kwargs = {}

        _type = self.get_type()
        if _type == _ModelOrDatasetT:  # type: ignore[misc]
            self._raise_type_exception()

        def _validate_any_models_or_datasets(
                iterable_data: Iterable[tuple[str, object]]) -> tuple[dict, bool]:
            """Validate model or dataset instances found in iterable input data.

            Args:
                iterable_data: Iterable of ``(key, value)`` pairs supplied to dataset
                    initialization.

            Returns:
                A tuple containing the prepared mapping and a flag indicating whether any input
                values were already model or dataset instances.
            """

            prepared_data = {}
            _model_or_dataset_as_input: bool = False

            for key, val in iterable_data:
                if is_model_instance(val):
                    _model_or_dataset_as_input = True
                    prepared_data[key] = self._validate_value_for_data_file(key, val)
                else:
                    prepared_data[key] = val
            return prepared_data, _model_or_dataset_as_input

        model_or_dataset_as_input = False
        if DATA_KEY in super_kwargs:
            input_data = super_kwargs[DATA_KEY]
            for_type_check = input_data.content if is_model_instance(input_data) else input_data
            match for_type_check:
                case Dataset():
                    model_or_dataset_as_input = True
                    super_kwargs[DATA_KEY] = cast(Dataset, input_data).to_data()
                case _input_data if is_pure_pydantic_model(_input_data):
                    super_kwargs[DATA_KEY], model_or_dataset_as_input = (
                        _validate_any_models_or_datasets(_input_data.dict().items()))
                case Mapping():
                    super_kwargs[DATA_KEY], model_or_dataset_as_input = (
                        _validate_any_models_or_datasets(cast(Mapping, input_data).items()))
                case Iterable():
                    try:
                        super_kwargs[DATA_KEY], model_or_dataset_as_input = (
                            _validate_any_models_or_datasets(self._check_iterable(input_data)))
                    except (TypeError, ValueError) as e:
                        raise TypeError(
                            'Data object must be a mapping or an iterable of '
                            '(key, val) pairs',
                            self.__class__) from e

                case _:
                    ...

        self._init(super_kwargs, **kwargs)

        try:
            self._primary_validation(super_kwargs)
        except ValidationError:
            if model_or_dataset_as_input:
                self._secondary_validation_from_data(super_kwargs)
            else:
                raise

        if not self.__doc__:
            self._set_standard_field_description()

    def _primary_validation(self, super_kwargs):
        """Run the primary Pydantic validation pass for dataset initialization.

        Args:
            super_kwargs: Keyword arguments prepared for ``pydantic.GenericModel.__init__()``.

        Returns:
            ``None``.

        Raises:
            ValidationError: If the prepared dataset payload does not validate.
        """
        # Pydantic validation of super_kwargs
        super().__init__(**super_kwargs)

    def _secondary_validation_from_data(self, super_kwargs):
        """Retry initialization by parsing the prepared payload via ``from_data()``.

        Args:
            super_kwargs: Keyword arguments containing the prepared dataset payload.

        Raises:
            ValidationError: If parsing the prepared payload still fails validation.
        """
        super().__init__()
        self.from_data(super_kwargs[DATA_KEY])

    def _init(self, super_kwargs: dict_t[str, Any], **kwargs: Any) -> None:
        """Provide a subclass hook that runs before dataset validation.

        The base implementation is intentionally empty. Specialized datasets can override this hook
        to adjust initialization arguments before the primary validation pass runs.

        Args:
            super_kwargs: Keyword arguments prepared for the base Pydantic initializer.
            **kwargs: Remaining keyword arguments passed to dataset construction.

        """
        ...

    # TODO: Revise with pydantic v2: __deepcopy__ is not defined for Dataset and Model, as it is not
    #       supported by pydantic v1. BaseModel.copy(deep=True) does not support a deepcopy memo.
    #       So we instead make use of the builtin support for deepcopy, which seems to work fine.
    #       However, __deepcopy__ in pydantic v2 is probably more efficient due to the memo and
    #       the Rust backend.

    def __copy__(self):
        """Return a shallow copy of the dataset.

        The copied dataset receives a new top-level mapping while reusing the same validated item
        objects.

        Returns:
            A new dataset instance with a shallow copy of the backing mapping.
        """
        return self.copy(deep=False)

    def copy(self, *, deep: bool = False, **kwargs) -> Self:
        """Copy the dataset.

        Args:
            deep: Whether to deep-copy nested values as well as the dataset object.
            **kwargs: Additional keyword arguments forwarded to Pydantic's ``copy()``.

        Returns:
            A copied dataset instance of the same specialized class.
        """
        pydantic_copy = pyd.GenericModel.copy(self, deep=deep, **kwargs)
        if not deep:
            object.__setattr__(pydantic_copy, DATA_KEY, pydantic_copy.__dict__[DATA_KEY].copy())

        return pydantic_copy  # pyright: ignore [reportReturnType]

    @classmethod
    def clone_dataset_cls(cls,
                          new_dataset_cls_name: str,
                          model_cls: type[_NewModelT] | None = None) -> type[Self]:
        """Create a new dataset subclass based on this dataset class.

        Args:
            new_dataset_cls_name: Name of the generated dataset subclass.
            model_cls: Optional replacement item model for the generated subclass.

        Returns:
            A newly created dataset subclass.
        """
        if model_cls:
            generic_dataset_cls = cls.__bases__[0]
            new_base_cls = generic_dataset_cls[model_cls]  # type: ignore[index]
        else:
            new_base_cls = cls

        new_dataset_cls = type(new_dataset_cls_name, (new_base_cls,), {})
        return new_dataset_cls

    @classmethod
    def _get_data_field(cls) -> pyd.ModelField:
        """Return the Pydantic field object that stores dataset contents.

        Returns:
            The Pydantic model field representing the ``data`` attribute.
        """
        return cast(pyd.ModelField, cls.__fields__.get(DATA_KEY))

    @classmethod
    @functools.cache
    def get_type(cls) -> type[_ModelOrDatasetT]:
        """Return the concrete item type stored by this dataset class.

        Returns:
            The specialized model or nested dataset class used for every item in the dataset.
        """
        # Part of pydantic v1 hack to stop coercing of e.g.
        # [{'a': 'b', 'c': 'd'}] to {'a': 'c'}
        return cls._clean_type(cls._get_data_field().sub_fields[1].type_)  # type: ignore[index]
        # return cls._clean_type(cls._get_data_field().type_)

    @classmethod
    def _clean_type_caches(cls):
        cls.get_type.cache_clear()

    @staticmethod
    def _raise_type_exception(prefix_msg: str = '') -> None:
        """Raise the standard error for unspecialized dataset classes.

        Args:
            prefix_msg: Optional message prepended before the standard guidance text.

        Raises:
            TypeError: Always raised to explain how a dataset must be specialized.
        """
        msg = dedent("""\
            The Dataset class requires a concrete type (e.g. a Model class
            or a subclass) to be specified as a type hierarchy within
            brackets either directly, e.g.:

              model = Dataset[Model[list[int]]]()

            or indirectly in a subclass definition, e.g.:

              class MyNumberListDataset(Dataset[Model[list[int]]]): ...

            For anything other than the simplest cases, the definition of
            Model and Dataset subclasses is encouraged , e.g.:

              class MyNumberListModel(Model[list[int]]): ...
              class MyDataset(Dataset[MyNumberListModel]): ...

            Alternatively, a dataset can nest another dataset instead of a
            model, e.g.:

              class MyNestedDataset(Dataset[Dataset[Model[list[int]]]]): ...

            Note that at the bottom of the dataset nesting hierarchy, a
            Model class must always be specified.

            Unions of Model or Dataset classes are also supported, e.g.:

              model = Dataset[Model[int] | StrModel]()""")
        if prefix_msg:
            msg = prefix_msg + '\n\n' + msg
        raise TypeError(msg)

    def _set_standard_field_description(self) -> None:
        self.__fields__[DATA_KEY].field_info.description = self._get_standard_field_description()

    @classmethod
    def _get_standard_field_description(cls) -> str:
        """Return the default description text used for the dataset ``data`` field.

        Returns:
            The standard descriptive text for the dataset backing field.
        """
        return ('This class represents a dataset in the `omnipy` Python package and contains '
                'a set of named data items that follows the same data model. '
                'It is a statically typed specialization of the Dataset class according to a '
                'particular specialization of the Model class. Both main classes are wrapping '
                'the excellent Python package named `pydantic`.')

    if TYPE_CHECKING:  # noqa: C901

        # The code below is a hack needed because of a fundamental limitation of the current Python
        # typing syntax. There is no way (that we know of) to tell the type checkers that Model
        # objects can mimic the functionality of their type arguments, say that a Model[list] can
        # mimic a list. What we were aiming to do as a lesser hack was to tell to the type checkers
        # that the Model objects can be considered as inheriting from both the Model class
        # and the type argument class, e.g. Model[list] and list, but in a general way, using type
        # variables. As a workaround, we have to overload the Model.__new__ and Dataset.__getitem__
        # methods for the most important types.

        @overload
        def __getitem__(
            self: 'Dataset[Model[float]]',
            selector: str | int,
        ) -> Model_float:
            """Describe float-model item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[float]`` item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[int]]',
            selector: str | int,
        ) -> Model_int:
            """Describe int-model item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[int]`` item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[bool]]',
            selector: str | int,
        ) -> Model_bool:
            """Describe bool-model item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[bool]`` item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[str]]',
            selector: str | int,
        ) -> Model_str:
            """Describe string-model item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[str]`` item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[bytes]]',
            selector: str | int,
        ) -> Model_bytes:
            """Describe bytes-model item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[bytes]`` item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[set[_ValT]]]',
            selector: str | int,
        ) -> Model_set[_ValT]:
            """Describe set-model item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[set[_ValT]]`` item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[list[_ValT]]]',
            selector: str | int,
        ) -> Model_list[_ValT]:
            """Describe list-model item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[list[_ValT]]`` item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[tuple[_ValT, ...]]]',
            selector: str | int,
        ) -> Model_tuple_same_type[_ValT]:
            """Describe homogeneous-tuple item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[tuple[_ValT, ...]]`` item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[tuple[_ValT, _ValT2]]]',
            selector: str | int,
        ) -> Model_tuple_pair[_ValT, _ValT2]:
            """Describe pair-tuple item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[tuple[_ValT, _ValT2]]`` item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[dict_t[_KeyT, _ValT]]]',
            selector: str | int,
        ) -> Model_dict[_KeyT, _ValT]:
            """Describe dict-model item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected ``Model[dict[_KeyT, _ValT]]`` item.
            """
            ...

        # For better typing of NestedDataset and similar. Will always type
        # as if a nested Dataset is returned, thus will be wrong for the
        # terminal Model case (only when multiple __getitem__ are chained,
        # e.g.:
        #   nested_dataset = Dataset[Dataset[Model[list[int]]]](...)
        #   nested_dataset['a'][0] = 5  # <- here the type checker will
        #                               #    think nested_dataset['a'] is a
        #                               #    Dataset, not a Model[list[int]]

        @overload
        def __getitem__(
            self: 'Dataset[Model[Dataset[_ModelT]]]',
            selector: str | int,
        ) -> Model_Dataset[_ModelT]:
            """Describe nested-dataset model access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected nested dataset model item.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[_DatasetT | _ModelT ]',
            selector: str | int,
        ) -> _DatasetT:
            """Describe union item access that narrows to a nested dataset.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected nested dataset instance.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[_DatasetT | _ModelT | _Model2T]',
            selector: str | int,
        ) -> _DatasetT:
            """Describe three-way union item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected nested dataset instance.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[_DatasetT | _ModelT | _Model2T | _Model3T]',
            selector: str | int,
        ) -> _DatasetT:
            """Describe four-way union item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected nested dataset instance.
            """
            ...

        @overload
        def __getitem__(
            self: 'Dataset[_DatasetT | _ModelT | _Model2T | _Model3T | _Model4T]',
            selector: str | int,
        ) -> _DatasetT:
            """Describe five-way union item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected nested dataset instance.
            """
            ...

        # Even though these two overloads overlap, they are needed in this
        # order to solve typing for both nested and regular Dataset cases.

        @overload
        def __getitem__(  # type: ignore[overload-overlap]
            self: 'Dataset[_ModelOrDatasetT]',
            selector: str | int,
        ) -> _ModelOrDatasetT:
            """Describe general singular item access for static type checkers.

            Args:
                selector: Data-file key or positional index selecting one item.

            Returns:
                The selected validated dataset item.
            """
            ...

        # The only thing that should really be needed – if Python type hints would have able to
        # describe that Model objects can dynamically inherit from their type arguments. This would
        # at least go some way towards what we really want, which is a way to describe exactly the
        # way Model objects mimic the functionality of their type arguments.
        #
        # @overload
        # def __getitem__(self, selector: str | int) -> _ModelOrDatasetT:
        #     ...

        @overload
        def __getitem__(self, selector: slice | Iterable[str | int]) -> Self:
            """Describe plural item selection for static type checkers.

            Args:
                selector: Slice or iterable selecting multiple items.

            Returns:
                A dataset of the same specialized class containing the selected items.
            """
            ...

    def __getitem__(
        self,
        selector: str | int | slice | Iterable[str | int],
    ) -> '_DatasetT | _ModelOrDatasetT | Model | Self':
        """Return one item or a selected subset of the dataset.

        Args:
            selector: A data-file key, positional index, slice, or iterable of keys and/or
                indices.

        Returns:
            The selected validated item for singular selection, or a new dataset containing the
            selected items for plural selection.
        """
        selected_keys = select_keys(selector, self.data)

        if selected_keys.singular:
            value: _ModelOrDatasetT | Self = self.data[selected_keys.keys[0]]
        else:
            value = self.__class__({key: self.data[key] for key in selected_keys.keys})

        return self._check_value(value)

    @call_super_if_available(call_super_before_method=True)
    def _check_value(self, value: Any) -> Any:
        """Post-process a selected value before returning it.

        Subclasses can override this hook to unwrap or adapt validated values returned from the
        dataset API.

        Args:
            value: Selected validated item or dataset subset.

        Returns:
            The value to expose to the caller.
        """
        return value

    def __delitem__(self, selector: str | int | slice | Iterable[str | int]) -> None:
        """Delete one or more items selected from the dataset.

        Args:
            selector: A data-file key, positional index, slice, or iterable of keys and/or
                indices.
        """
        selected_keys = select_keys(selector, self.data)

        if selected_keys.singular:
            del self.data[selected_keys.keys[0]]
        else:
            prev_data = copy(self.data)

            try:
                for key in selected_keys.keys:
                    del self.data[key]
            except Exception:
                self.data = prev_data
                raise

    @overload
    def __setitem__(self, selector: str | int, data_obj: object) -> None:
        """Describe singular assignment for static type checkers.

        Args:
            selector: Data-file key or positional index selecting one item.
            data_obj: Single value assigned to the selected item.

        """
        ...

    @overload
    def __setitem__(self,
                    selector: slice | Iterable[str | int],
                    data_obj: Mapping[str, object] | Iterable[object]) -> None:
        """Describe plural assignment for static type checkers.

        Args:
            selector: Slice or iterable selecting multiple items.
            data_obj: Mapping or iterable providing replacement values.

        """
        ...

    def __setitem__(
        self,
        selector: str | int | slice | Iterable[str | int],
        data_obj: object | Mapping[str, object] | Iterable[object],
    ) -> None:
        """Assign one or more items and validate them against the dataset type.

        Args:
            selector: A data-file key, positional index, slice, or iterable of keys and/or
                indices.
            data_obj: A single replacement item for singular selection, or mapping/iterable data
                for plural selection.

        Raises:
            TypeError: If plural assignment receives a value that is neither a mapping nor an
                iterable.
            ValidationError: If any assigned item fails dataset validation.
        """
        selected_keys = select_keys(selector, self.data)

        if selected_keys.singular:
            self._set_data_file_and_validate(selected_keys.keys[0],
                                             cast(_ModelOrDatasetT, data_obj))
        else:
            key_2_data_item: Key2DataItemType[object]
            index_2_data_items: Index2DataItemsType[object]

            if isinstance(data_obj, MutableMapping):
                key_2_data_item, index_2_data_items = \
                    prepare_selected_items_with_mapping_data(
                        selected_keys.keys, selected_keys.last_index,
                        cast(Mapping[str, object], data_obj),
                    )

            elif is_iterable(data_obj) and not isinstance(data_obj, (str, bytes)):
                key_2_data_item, index_2_data_items = \
                    prepare_selected_items_with_iterable_data(
                        selected_keys.keys, selected_keys.last_index, tuple(data_obj),
                        cast(Mapping[str, object], self.data),
                    )

            else:
                raise TypeError('Data object must be a mapping or an iterable')

            self._update_selected_items_with_data_items(key_2_data_item, index_2_data_items)

    def _update_selected_items_with_data_items(
        self,
        key_2_data_item: Key2DataItemType[object],
        index_2_data_item: Index2DataItemsType[object],
    ) -> None:
        """Apply prepared replacement values to the currently selected dataset items.

        Args:
            key_2_data_item: Replacement values keyed directly by data-file name.
            index_2_data_item: Replacement values keyed by positional index.

        Raises:
            ValidationError: If the updated dataset contents fail validation.
        """

        updated_mapping = create_updated_mapping(
            cast(MutableMapping[str, object], self.data), key_2_data_item,
            index_2_data_item)  # pyright: ignore [reportUndefinedVariable]
        self._replace_data_with_mapping(updated_mapping)

    def _replace_data_with_mapping(self, updated_mapping: MutableMapping[str, object]) -> None:
        """Replace the dataset contents atomically using a prepared mapping.

        Args:
            updated_mapping: Candidate full mapping to validate and install.

        Raises:
            ValidationError: If the replacement mapping does not validate for this dataset type.
        """
        prev_data = self.data
        try:
            self.absorb_and_replace(self.__class__(updated_mapping))
        except Exception:
            self.data = prev_data
            raise

    def _set_data_file_and_validate(self, key: str, val: _ModelOrDatasetT) -> None:
        """Assign one dataset item and roll back if validation fails.

        Args:
            key: Data-file name to insert or replace.
            val: Candidate validated or raw item value.

        Raises:
            ValidationError: If the inserted value does not validate for this dataset type.
        """
        has_prev_value = key in self.data
        if has_prev_value:
            prev_value = self.data[key]

        try:
            self.data[key] = val
            self._validate_data_file(key)
        except Exception:
            if has_prev_value:
                self.data[key] = prev_value
            else:
                del self.data[key]
            raise

    @classmethod
    def _check_iterable(cls, iterable: Iterable[Any]) -> Iterable[Any]:
        """Normalize iterable input into an iterator of ``(key, value)`` pairs.

        Args:
            iterable: Candidate outer iterable supplied as dataset input.

        Returns:
            An iterator yielding normalized ``(key, value)`` pairs.

        Raises:
            TypeError: If the iterable shape is incompatible with dataset initialization.
        """
        if isinstance(iterable, (str, bytes)):
            raise TypeError(
                'Outer data iterables cannot be strings or, '
                'bytes, got: {type(value)}', cls)

        def check_iterable_elements(iterable: Iterable) -> Iterator:
            """Validate and normalize each element of an outer dataset iterable.

            Args:
                iterable: Iterable whose elements should each describe one ``(key, value)`` pair.

            Returns:
                An iterator over normalized ``(key, value)`` pairs.

            Raises:
                TypeError: If any element is not a list-like or tuple-like key-value pair.
            """
            for el in iterable:
                if not isinstance(el, (tuple, list)):
                    raise TypeError(
                        'Inner data iterable elements must be '
                        '(key, val) pairs, as tuples or lists, '
                        f'not: {type(el)}',
                        cls)
                if isinstance(el, Mapping):
                    yield from el.items()
                else:
                    yield el

        return check_iterable_elements(iterable)

    @classmethod
    def validate(cls, value: Any) -> Self:
        """Validate arbitrary input as an instance of this dataset class.

        This method is primarily part of the Pydantic integration layer and preserves dataset
        validation behavior when iterables are accepted as input.

        Args:
            value: The value to validate.

        Returns:
            A validated dataset instance.
        """
        # TODO: Doublecheck if validate() method is still needed for pydantic v2

        # validate_cls_counts[cls.__name__] += 1
        if is_iterable(value) and not isinstance(value, Mapping):
            value = cls._check_iterable(value)

        return super().validate({'data': value})

    # TODO: Improve DRY of Model.update_forward_refs() and Dataset.update_forward_refs()
    @classmethod
    def update_forward_refs(
        cls,
        calling_module: str | None = None,
        prev_visited_classes: set[type] | None = None,
        **localns: Any,
    ) -> None:
        """
        Try to update ForwardRefs on fields based on this Model, globalns and localns.
        """

        from omnipy.data.model import is_model_subclass

        if prev_visited_classes is None:
            prev_visited_classes = set()
        elif cls in prev_visited_classes:
            return

        # Merge the namespaces of the Datasets's own module and the
        # calling module to the local namespace for evaluation of forward
        # references, which is necessary for cases where the Dataset is
        # defined in a different module than where it is used, e.g. when
        # the Dataset is defined in a library and used by a user in their
        # own code.
        if calling_module is None:
            calling_module = get_calling_module_name()
        own_module_ns, globalns = \
            build_own_module_and_global_namespace_for_forward_refs(cls, calling_module, **localns)

        prev_type = cls._get_data_field().type_

        super().update_forward_refs(**globalns)

        cls._get_data_field().type_ = evaluate_any_forward_refs_if_possible(prev_type, **globalns)
        if DATA_KEY in cls.__annotations__:
            cls.__annotations__[DATA_KEY] = evaluate_any_forward_refs_if_possible(
                cls.__annotations__[DATA_KEY], **globalns)

        cls._clean_type_caches()

        prev_visited_classes.add(cls)

        # Merge the Dataset's own module namespace into
        # localns before propagating. This is to allow Model classes and
        # pydantic-generated parametrized base classes (which have
        # __module__='omnipy.data.dataset' rather than the defining
        # module) to still resolve forward refs that only exist
        # in the defining module's namespace.

        extra_ns: dict[str, Any] = {}
        extra_ns.update(own_module_ns)
        extra_ns.update(localns)

        # Propagate update_forward_refs to parent Dataset classes but
        # retaining the same calling module. This is needed to ensure the
        # correct context is used to resolve forward references in complex
        # inheritance hierarchies.
        #
        # We explicitly call `update_forward_refs` on immediate parent
        # classes (`__bases__`) instead of relying solely on
        # `super().update_forward_refs()`. This is because `super()`
        # inside this classmethod resolves relative to `Dataset` in the MRO,
        # silently bypassing custom logic on any intermediate `Dataset`
        # subclasses. Explicitly propagating through `__bases__` ensures
        # that class-level setups are correctly applied to all parents
        # exactly once, efficiently preventing redundant updates.
        for base in cls.__bases__:
            if is_dataset_subclass(base) and base is not Dataset:
                base.update_forward_refs(
                    calling_module=calling_module,
                    prev_visited_classes=prev_visited_classes,
                    **extra_ns,
                )

        # As above, but now propagate update_forward_refs to the types of
        # the Dataset (e.g. the Model).
        for type_variant in split_to_union_variants(cls.get_type()):
            if is_dataset_subclass(type_variant) or is_model_subclass(type_variant):
                type_variant.update_forward_refs(
                    calling_module=calling_module,
                    prev_visited_classes=prev_visited_classes,
                    **extra_ns,
                )

        cls.__name__ = remove_forward_ref_notation(cls.__name__)
        cls.__qualname__ = remove_forward_ref_notation(cls.__qualname__)

    def _validate_data_file(self, data_file: str) -> None:
        """Validate one stored dataset item in place.

        Args:
            data_file: Key of the item that should be revalidated.

        Raises:
            ValidationError: If the stored item does not validate for this dataset type.
        """
        from omnipy.data.model import is_model_instance

        val = self.data[data_file]
        if is_model_instance(val):
            self.data[data_file] = self._validate_value_for_data_file(data_file, val)
        else:
            self._force_full_validation()

    @staticmethod
    def _basic_validation_func(type_variant: 'type[Model | Dataset]',
                               value: UndefinedType | object) -> _ModelOrDatasetT:
        """Construct one candidate model or dataset during validation.

        Args:
            type_variant: Candidate model or dataset class to instantiate.
            value: Raw value passed to the candidate class constructor.

        Returns:
            The validated model or dataset instance.

        Raises:
            ValidationError: If construction of the candidate type fails validation.
            TypeError: If the candidate type cannot be constructed from ``value``.
            ValueError: If the candidate type rejects ``value`` semantically.
        """
        return cast(_ModelOrDatasetT, type_variant(value))  # type: ignore[arg-type]

    @classmethod
    def _validate_value_for_data_file(
        cls,
        data_file: str,
        value: UndefinedType | object,
        validation_func: (
            'Callable[[type[Model | Dataset], UndefinedType | object], _ModelOrDatasetT]'
        ) = _basic_validation_func,
    ) -> _ModelOrDatasetT:
        """Validate one data-file value against all allowed dataset item variants.

        Args:
            data_file: Key associated with the candidate item.
            value: Raw value to validate.
            validation_func: Callable used to try construction for each allowed type variant.

        Returns:
            The first validated model or dataset instance accepted by the allowed type variants.

        Raises:
            ValidationError: If all candidate type variants reject the value.
        """
        errors = []
        for type_variant in split_to_union_variants(cls.get_type()):
            try:
                return validation_func(cast('type[Model | Dataset]', type_variant), value)
            except (ValidationError, ValueError, TypeError) as exp:
                errors.append(exp)
        assert errors
        raise ValidationError([pyd.ErrorWrapper(exc, loc=data_file) for exc in errors], cls)

    def _force_full_validation(self):
        """Trigger assignment-based validation for the full dataset mapping.

        Raises:
            ValidationError: If any stored item fails full dataset validation.
        """
        self.data = self.data  # Triggers pydantic validation, as validate_assignment=True

    @override
    def __iter__(self) -> Iterator[str]:  # type: ignore[override]
        """Iterate over dataset keys.

        Returns:
            An iterator over data-file names in the backing mapping.
        """
        return UserDict.__iter__(self)

    def __setattr__(self, attr: str, value: Any) -> None:
        """Restrict attribute assignment to declared dataset fields and properties.

        Args:
            attr: Attribute name being assigned.
            value: Value to store on the dataset instance.

        Raises:
            RuntimeError: If assignment targets an undeclared extra attribute.
        """
        if attr in self.__dict__ or attr == DATA_KEY or attr.startswith('__'):
            super().__setattr__(attr, value)
        elif attr == 'repr_state':
            prop = getattr(self.__class__, attr)
            prop.__set__(self, value)
        else:
            raise RuntimeError('Dataset does not allow setting of extra attributes')

    @pyd.root_validator
    def _parse_root_object(
        cls,
        root_obj: dict_t[str, dict_t[str, _ModelOrDatasetT]],
    ) -> Any:  # noqa
        """Pre-validate the root dataset object before normal field parsing.

        Args:
            cls: Dataset class performing validation.
            root_obj: Root object containing the ``data`` field to normalize.

        Returns:
            A root object whose ``data`` field has normalized values.

        Raises:
            AssertionError: If the root object does not contain the ``data`` field.
            ValidationError: If ``None`` values cannot be parsed by any allowed item type.
        """
        assert DATA_KEY in root_obj
        data_dict = root_obj[DATA_KEY]
        for data_file, val in data_dict.items():
            if val is None:

                def validation_by_parse_obj(
                    type_variant: 'type[Model | Dataset]',
                    value: UndefinedType | object,
                ) -> _ModelOrDatasetT:
                    """Parse a raw value with ``parse_obj()`` for one candidate type.

                    Args:
                        type_variant: Candidate model or dataset class to parse with.
                        value: Raw value to parse.

                    Returns:
                        The parsed model or dataset instance.
                    """
                    return cast(_ModelOrDatasetT, type_variant.parse_obj(value))

                data_dict[data_file] = cls._validate_value_for_data_file(
                    data_file,
                    val,
                    validation_by_parse_obj,
                )

        return {DATA_KEY: data_dict}

    def to(self, model_or_dataset_cls: type[_OtherModelOrDatasetT]) -> '_OtherModelOrDatasetT':
        """Convert this dataset to another model or dataset class.

        Args:
            model_or_dataset_cls: Target model or dataset class that can be constructed from this
                dataset.

        Returns:
            An instance of the requested target class.
        """
        return model_or_dataset_cls(self)

    def do(self, placeholder: F) -> 'Dataset[_ModelOrDatasetT]':
        """Apply a callable placeholder to each item and collect the results in a new dataset.

        Args:
            placeholder: Callable wrapper used to transform each validated dataset item.

        Returns:
            A new dataset of the same class containing the transformed items.
        """
        new_dataset = self.__class__()
        for data_file, val in self.items():
            new_dataset[data_file] = placeholder(val)
        return new_dataset

    def to_data(self) -> dict_t[str, Any]:
        """Return the dataset as plain Python contents.

        Returns:
            A mapping from data-file name to plain Python data extracted from each validated item.
        """
        return {key: self._check_value(val) for key, val in self.dict(by_alias=True).items()}

    def dict(self, **kwargs) -> dict_t[str, Any]:
        """Return the dataset backing mapping as a plain dictionary.

        Args:
            **kwargs: Keyword arguments forwarded to Pydantic's ``dict()`` implementation.

        Returns:
            The serialized value of the dataset's ``data`` field.
        """
        return super().dict(**kwargs)[DATA_KEY]

    def from_data(self,
                  data: Mapping[str, Any] | Iterable[tuple[str, Any]],
                  update: bool = True) -> None:
        """Populate the dataset from plain Python contents.

        Args:
            data: Mapping or iterable of ``(key, value)`` pairs to parse into validated items.
            update: Whether to merge into existing contents instead of replacing them first.
        """
        def callback_func(type_variant: 'Model | Dataset', content: Any):
            """Populate one item instance from plain Python content.

            Args:
                type_variant: Newly created model or dataset instance to populate.
                content: Plain Python content to load into the instance.

            """
            type_variant.from_data(content)

        self._from_dict_with_callback(data, update, callback_func)

    def _from_dict_with_callback(self,
                                 data: Mapping[str, Any] | Iterable[tuple[str, Any]],
                                 update: bool,
                                 callback_func: 'Callable[[Model | Dataset, Any], None]'):
        """Populate the dataset by applying a callback to fresh item instances.

        Args:
            data: Mapping or iterable of ``(key, value)`` pairs to ingest.
            update: Whether to merge with current contents instead of clearing first.
            callback_func: Callback that populates one newly created item instance from raw input.

        Raises:
            ValidationError: If any generated item fails dataset validation.
        """
        if isinstance(data, dict):
            data_as_dict: dict[str, Any] = data  # pyright: ignore [reportAssignmentType]
        else:
            data_as_dict = dict(data)

        if not update:
            self.clear()

        for data_file, content in data_as_dict.items():
            # TODO: Redefine from_data() also as classmethods on Model and
            #       Dataset. Here, we could then do
            #       type_variant.from_data(content) instead of creating a
            #       new instance and then calling from_data() on it.
            #       Instance-level from_data() should however also be kept,
            #       as it is useful in many cases. Note: Classmethod
            #       from_data() should still first create an empty instance
            #       and then call instance-level from_data() on it, to avoid
            #       issues with __init__ arguments (when e.g. 'self', 'value',
            #       'data' is used as keys in the data).

            def validation_by_callback_func(
                type_variant: 'type[Model | Dataset]',
                value: UndefinedType | object,
            ) -> _ModelOrDatasetT:
                """Create one validated item by invoking the provided callback.

                Args:
                    type_variant: Candidate model or dataset class to instantiate.
                    value: Raw value to hand to the callback.

                Returns:
                    A populated item instance accepted by the dataset type.
                """
                new_instance = type_variant()
                callback_func(new_instance, value)
                return cast(_ModelOrDatasetT, new_instance)

            self.data[data_file] = self._validate_value_for_data_file(
                data_file,
                content,
                validation_by_callback_func,
            )

    def absorb(self, other: 'Dataset'):
        """Merge another dataset's contents into this dataset.

        Args:
            other: Dataset whose plain-Python contents should be added or overwrite matching keys.
        """
        self.from_data(other.to_data(), update=True)

    def absorb_and_replace(self, other: 'Dataset'):
        """Replace this dataset's contents with another dataset's contents.

        Args:
            other: Dataset whose contents should replace the current contents.
        """
        self.from_data(other.to_data(), update=False)

    def to_json(self, pretty=True) -> dict_t[str, str]:
        """Serialize each dataset item to JSON.

        Args:
            pretty: Whether to pretty-print the JSON for each item.

        Returns:
            A mapping from data-file name to JSON string.
        """
        result = {}

        for key, val in self.data.items():
            result[key] = val.to_json(pretty=pretty)

        return result

    def from_json(self,
                  data: Mapping[str, str] | Iterable[tuple[str, str]],
                  update: bool = True) -> None:
        """Populate the dataset from per-item JSON strings.

        Args:
            data: Mapping or iterable of ``(key, json_string)`` pairs.
            update: Whether to merge into existing contents instead of replacing them first.
        """
        def callback_func(type_variant: 'Model | Dataset', content: Any):
            """Populate one item instance from a JSON string.

            Args:
                type_variant: Newly created model or dataset instance to populate.
                content: JSON content to load into the instance.

            """
            type_variant.from_json(content)

        self._from_dict_with_callback(data, update, callback_func)

    # @classmethod
    # def get_type_args(cls):
    #     return cls.__fields__.get(DATA_KEY).type_
    #
    #
    # @classmethod
    # def create_from_json(cls, data: str, tuple[str]]):
    #     if isinstance(data, tuple):
    #         data = data[0]
    #
    #     obj = cls()
    #     obj.from_json(data, update=False)
    #     return obj
    #
    # def __reduce__(self):
    #     return self.__class__.create_from_json, (self.to_json(),)

    @classmethod
    def to_json_schema(cls, pretty: bool = True) -> str | dict_t[str, str]:
        """Return a JSON schema for the dataset's serialized contents.

        Args:
            pretty: Whether to return pretty-printed JSON text instead of compact JSON text.

        Returns:
            A JSON schema string describing the dataset contents.
        """
        result = {}
        clean_dataset = super(Dataset, Dataset).__class_getitem__(cls.get_type())
        schema = clean_dataset.schema()
        for key, val in schema['properties'][DATA_KEY].items():
            # Remove the first part of the type definition of 'data', added
            # as a hack to stop coercing of e.g. [{'a': 'b', 'c': 'd'}]
            # to {'a': 'c'}
            if key == 'anyOf':
                result['type'] = 'object'
                result['additionalProperties'] = {
                    '$ref': '#/definitions/' + pyd.normalize_name(clean_dataset.get_type().__name__)
                }
            else:
                result[key] = val

        result['title'] = clean_dataset.__name__
        result['definitions'] = schema['definitions']

        for model_desc in result['definitions'].values():
            if 'orig_model' in model_desc:
                del model_desc['orig_model']

        if pretty:
            return cls._pretty_print_json(result)
        else:
            return json.dumps(result)

    @staticmethod
    def _pretty_print_json(json_content: Any) -> str:
        """Render JSON-serializable content as indented JSON text.

        Args:
            json_content: JSON-serializable object to pretty-print.

        Returns:
            Indented JSON text.
        """
        return json.dumps(json_content, indent=2)

    def save(self, path: str):
        """Serialize the dataset to a ``.tar.gz`` archive and extract a directory copy.

        Args:
            path: Destination path with or without the ``.tar.gz`` suffix.
        """
        serializer_registry = self._get_serializer_registry()

        parsed_dataset, serializer = serializer_registry.auto_detect_tar_file_serializer(self)

        if serializer is None:
            print(f'Unable to find a serializer for dataset with data type "{type(self)}". '
                  f'Will abort saving...')
        else:
            if not path.endswith('.tar.gz'):
                out_tar_gz_path = f'{path}.tar.gz'

            print(f'Writing dataset as a gzipped tarpack to "{os.path.abspath(out_tar_gz_path)}"')

            with open(out_tar_gz_path, 'wb') as out_tar_gz_file:
                out_tar_gz_file.write(serializer.serialize(parsed_dataset))

            directory = os.path.abspath(out_tar_gz_path[:-7])
            if not os.path.exists(directory):
                os.makedirs(directory)

            tar = tarfile.open(out_tar_gz_path)
            print(f'Extracting content to directory "{os.path.abspath(out_tar_gz_path[:-7])}"')
            tar.extractall(path=directory)
            tar.close()

    @classmethod
    def load(
        cls,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        """Create a dataset and load serialized contents into it.

        Args:
            paths_or_urls: Path, URL, iterable of paths or URLs, or dataset/model of HTTP URLs to
                load from.
            by_file_suffix: Whether serializer lookup should prefer file-suffix detection.
            as_mime_type: Optional MIME type hint for HTTP loading.
            **kwargs: Alternate keyed path or URL arguments when ``paths_or_urls`` is omitted.

        Returns:
            A loaded dataset, or an ``asyncio.Task`` when called inside a running event loop.
        """
        dataset = cls()
        return dataset.load_into(
            paths_or_urls, by_file_suffix=by_file_suffix, as_mime_type=as_mime_type, **kwargs)

    def load_into(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        """Load serialized contents into this dataset instance.

        Args:
            paths_or_urls: Path, URL, iterable of paths or URLs, or dataset/model of HTTP URLs to
                load from.
            by_file_suffix: Whether serializer lookup should prefer file-suffix detection.
            as_mime_type: Optional MIME type hint for HTTP loading.
            **kwargs: Alternate keyed path or URL arguments when ``paths_or_urls`` is omitted.

        Returns:
            This dataset instance after loading, or an ``asyncio.Task`` when called inside a
            running event loop.

        Raises:
            AssertionError: If the input forms are combined incorrectly.
            TypeError: If ``paths_or_urls`` has an unsupported type.
            NotImplementedError: If keyed local-path loading is requested.
        """
        from omnipy.components.remote.datasets import HttpUrlDataset
        from omnipy.components.remote.models import HttpUrlModel

        if paths_or_urls is None:
            assert len(kwargs) > 0, 'No paths or urls specified'
            paths_or_urls = kwargs
        else:
            assert len(kwargs) == 0, 'No keyword arguments allowed when paths_or_urls is specified'

        match paths_or_urls:
            case HttpUrlDataset():
                return self._load_http_urls(paths_or_urls, as_mime_type=as_mime_type)

            case HttpUrlModel():
                return self._load_http_urls(
                    HttpUrlDataset({str(paths_or_urls): paths_or_urls}),
                    as_mime_type=as_mime_type,
                )

            case str():
                try:
                    http_url_dataset = HttpUrlDataset({paths_or_urls: paths_or_urls})
                except ValidationError:
                    return self._load_paths([paths_or_urls], by_file_suffix)
                return self._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)

            case Mapping():
                try:
                    http_url_dataset = HttpUrlDataset(paths_or_urls)
                except ValidationError as exp:
                    raise NotImplementedError(
                        'Loading files with specified keys is not yet '
                        'implemented, as only tar.gz file import is '
                        'supported until serializers have been refactored.') from exp
                return self._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)

            case Iterable():
                path_or_url_iterable = paths_or_urls
                try:
                    http_url_dataset = HttpUrlDataset(
                        zip(path_or_url_iterable, path_or_url_iterable))
                except ValidationError:
                    return self._load_paths(path_or_url_iterable, by_file_suffix)
                return self._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)
            case _:
                raise TypeError(f'"paths_or_urls" argument is of incorrect type. Type '
                                f'{type(paths_or_urls)} is not supported.')

    def _load_http_urls(
        self,
        http_url_dataset: IsHttpUrlDataset,
        as_mime_type: None | str = None,
    ) -> Self | asyncio.Task[Self]:
        """Load dataset contents from one or more HTTP URLs.

        Args:
            http_url_dataset: Dataset of HTTP URLs keyed by data-file name.
            as_mime_type: Optional MIME type hint passed to the remote loading task.

        Returns:
            This dataset instance after loading, or an ``asyncio.Task`` in an active event loop.
        """
        from omnipy.components.remote.helpers import RateLimitingClientSession
        from omnipy.components.remote.tasks import get_auto_from_api_endpoint, get_retry_client

        hosts: defaultdict[str, list[int]] = defaultdict(list)
        for i, url in enumerate(http_url_dataset.values()):
            hosts[url.host].append(i)

        async def load_all(as_mime_type: None | str = None) -> 'Dataset[_ModelOrDatasetT]':
            """Fetch all grouped HTTP URLs asynchronously.

            Args:
                as_mime_type: Optional MIME type hint forwarded to the remote fetch task.

            Returns:
                This dataset instance after all remote loads complete.
            """
            tasks = []

            # TODO: Manage ClientConnectionResetError in Dataset._load_http_urls
            for host in hosts:
                host_config = self.config.http.for_host[host]
                async with RateLimitingClientSession(
                        host_config.requests_per_time_period,
                        host_config.time_period_in_secs) as client_session:
                    async with get_retry_client(
                            client_session=client_session,
                            retry_http_statuses=host_config.retry_http_statuses,
                            retry_attempts=host_config.retry_attempts,
                            retry_backoff_strategy=host_config.retry_backoff_strategy
                    ) as retry_client:
                        indices = hosts[host]
                        # fetch_task = get_auto_from_api_endpoint
                        # if as_mime_type:
                        #     match as_mime_type:
                        #         case 'application/json':
                        #             fetch_task = get_json_from_api_endpoint
                        #         case 'text/plain':
                        #             fetch_task = get_str_from_api_endpoint
                        #         case 'application/octet-stream' | _:
                        #             fetch_task = get_bytes_from_api_endpoint

                        ret = get_auto_from_api_endpoint.refine(
                            output_dataset_param='output_dataset').run(
                                http_url_dataset[indices],
                                retry_client=retry_client,
                                output_dataset=self,
                                as_mime_type=as_mime_type)

                        if not isinstance(ret, asyncio.Task):
                            assert inspect.iscoroutine(ret)
                            task = asyncio.create_task(ret)
                        else:
                            task = ret

                        tasks.append(task)

                        while not task.done():
                            await asyncio.sleep(ASYNC_LOAD_SLEEP_TIME)

            await asyncio.gather(*tasks)
            return self

        loop, loop_is_running = get_event_loop_and_check_if_loop_is_running()

        if loop and loop_is_running:
            return loop.create_task(load_all(as_mime_type=as_mime_type))
        else:
            return asyncio.run(load_all(as_mime_type=as_mime_type))

    def _load_paths(self, path_or_urls: Iterable[str], by_file_suffix: bool) -> Self:
        """Load dataset contents from local tar files or directories.

        Args:
            path_or_urls: Iterable of local filesystem paths to load from.
            by_file_suffix: Whether serializer selection should use file-suffix detection.

        Returns:
            This dataset instance after all paths have been loaded.

        Raises:
            RuntimeError: If no serializer can load one of the provided paths.
        """
        for path_or_url in path_or_urls:
            serializer_registry = self._get_serializer_registry()
            tar_gz_file_path = self._ensure_tar_gz_file(path_or_url)

            if by_file_suffix:
                loaded_dataset = \
                    serializer_registry.load_from_tar_file_path_based_on_file_suffix(
                        self, tar_gz_file_path, self)
            else:
                loaded_dataset = \
                    serializer_registry.load_from_tar_file_path_based_on_dataset_cls(
                        self, tar_gz_file_path, self, any_file_suffix=True)
            if loaded_dataset is not None:
                self.absorb(loaded_dataset)
                continue
            else:
                raise RuntimeError('Unable to load from serializer')
        return self

    @staticmethod
    def _ensure_tar_gz_file(path: str):
        """Return a ``.tar.gz`` path, creating an archive when needed.

        Args:
            path: Existing file or directory path, optionally already ending in ``.tar.gz``.

        Returns:
            Path to an existing or newly created ``.tar.gz`` archive.

        Raises:
            AssertionError: If the provided path does not exist.
        """
        assert os.path.exists(path), f'No file or directory at {path}'

        if not path.endswith('.tar.gz'):
            tar_gz_file_path = path + '.tar.gz'
            if not os.path.isfile(tar_gz_file_path):
                print(f'Creating compressed file {os.path.abspath(tar_gz_file_path)} from '
                      f'the content of "{os.path.abspath(path)}"')

                with tarfile.open(tar_gz_file_path, 'w:gz') as tar:
                    if os.path.isdir(path):
                        for fn in sorted(os.listdir(path)):
                            p = os.path.join(path, fn)
                            tar.add(p, arcname=fn)
                    elif os.path.isfile(path):
                        tar.add(path, arcname=os.path.basename(path))
            return tar_gz_file_path

        return path

    @staticmethod
    def _get_serializer_registry():
        """Return the global serializer registry used for dataset I/O.

        Returns:
            The serializer registry singleton from :mod:`omnipy.components`.
        """
        from omnipy.components import get_serializer_registry
        return get_serializer_registry()

    def as_multi_model_dataset(self) -> 'IsMultiModelDataset[_ModelOrDatasetT]':
        """Return a multi-model view of this dataset.

        Returns:
            A ``MultiModelDataset`` initialized with the same item type and current contents.
        """
        from omnipy.data.multi import MultiModelDataset

        multi_model_dataset = MultiModelDataset[self.get_type()]()
        for data_file in self:
            multi_model_dataset.data[data_file] = self.data[data_file]
        return multi_model_dataset

    def __eq__(self, other: object) -> bool:
        """Compare datasets by specialized class and contents.

        Args:
            other: Object to compare against.

        Returns:
            ``True`` when both objects are datasets of the same specialized class with equal
            validated contents.
        """
        # return self.__class__ == other.__class__ and super().__eq__(other)
        return isinstance(other, Dataset) \
            and self.__class__ == other.__class__ \
            and self.data == other.data \
            and self.to_data() == other.to_data()  # last is probably unnecessary, but just in case

    def __repr_args__(self):
        """Return key-value pairs used by Pydantic when building ``repr()`` output.

        Returns:
            A list of ``(key, value)`` pairs formatted for concise dataset representation.
        """
        from omnipy.data.model import is_model_instance

        return [(k, v.content) if is_model_instance(v) else (k, v) for k, v in self.data.items()]


def is_dataset_instance(__obj: object) -> 'TypeIs[Dataset]':
    """Return whether an object is a dataset instance.

    Args:
        __obj: Object to test.

    Returns:
        ``True`` if the object is recognized as a ``Dataset`` instance.
    """
    return lenient_isinstance(__obj, Dataset)


@functools.cache
def is_dataset_subclass(__cls: TypeForm) -> 'TypeIs[type[Dataset]]':
    """Return whether a type form is a dataset subclass.

    Args:
        __cls: Type or type-like form to test.

    Returns:
        ``True`` if the argument is recognized as a ``Dataset`` subclass.
    """
    return lenient_issubclass(__cls, Dataset)
