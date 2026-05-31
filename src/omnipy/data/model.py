"""Pydantic-backed Omnipy models and model inspection helpers.

This module defines :class:`Model`, Omnipy's central typed container for a single
validated root value, together with helper predicates for recognizing Omnipy
models, plain pydantic models, and related class relationships.
"""

from collections.abc import Callable, Iterable, Mapping, MutableSequence
from contextlib import contextmanager
from copy import copy, deepcopy
import functools
import inspect
from itertools import chain
import json
from types import GenericAlias, NoneType, UnionType
from typing import (Annotated,
                    Any,
                    cast,
                    ContextManager,
                    ForwardRef,
                    Generator,
                    Generic,
                    get_args,
                    get_origin,
                    Iterator,
                    Literal,
                    Optional,
                    overload,
                    Union)

from typing_extensions import get_original_bases, override, Self, TypeIs, TypeVar

from omnipy.data._data_class_creator import DataClassBase, DataClassBaseMeta
from omnipy.data._mixins.display import ModelDisplayMixin
from omnipy.data._typing.typedefs import _KeyT, _ValT, _ValT2
from omnipy.data.dataset import Dataset, is_dataset_instance
from omnipy.data.helpers import (build_own_module_and_global_namespace_for_forward_refs,
                                 cleanup_name_qualname_and_module,
                                 MethodInfo,
                                 ResetSolutionTuple,
                                 SPECIAL_METHODS_INFO_DICT,
                                 validate_cls_counts,
                                 YesNoMaybe)
from omnipy.shared.constants import ROOT_KEY
from omnipy.shared.exceptions import OmnipyNoneIsNotAllowedError
from omnipy.shared.protocols.data import IsModel, IsSnapshotWrapper
from omnipy.shared.typedefs import TypeForm
from omnipy.shared.typing import TYPE_CHECKER, TYPE_CHECKING
from omnipy.util._placeholder import F
from omnipy.util.contexts import (hold_and_reset_prev_attrib_value,
                                  LastErrorHolder,
                                  nothing,
                                  setup_and_teardown_callback_context)
from omnipy.util.decorators import add_callback_after_call, no_context
from omnipy.util.helpers import (all_equals,
                                 all_type_variants,
                                 ensure_plain_type,
                                 evaluate_any_forward_refs_if_possible,
                                 get_calling_module_name,
                                 get_default_if_typevar,
                                 is_literal_type,
                                 is_non_str_byte_iterable,
                                 is_optional,
                                 is_type_specialization,
                                 is_union,
                                 remove_forward_ref_notation,
                                 split_to_union_variants)
from omnipy.util.pydantic import (is_none_type,
                                  lenient_isinstance,
                                  lenient_issubclass,
                                  Undefined,
                                  UndefinedType,
                                  ValidationError)
# from orjson import orjson
import omnipy.util.pydantic as pyd
from omnipy.util.setdeque import SetDeque

_ReturnT = TypeVar('_ReturnT')
_RootT = TypeVar('_RootT')
_ModelT = TypeVar('_ModelT', bound='Model')
_DatasetT = TypeVar('_DatasetT', bound='Dataset')
_OtherModelT = TypeVar('_OtherModelT', bound='Model')
_ClassOrTupleT = TypeVar('_ClassOrTupleT')

# TODO: Refactor Dataset and Model using mixins (including below functions)

# Due to overriding the dict method of pydantic GenericModel, we need to
# redefine dict here to be able to use it for typing in Dataset methods.
# Otherwise, python syntax checkers will assume that 'dict' in method signatures
# refers to the method instead of the built-in dict type.

dict_t = dict


class ModelMetaclass(DataClassBaseMeta, pyd.ModelMetaclass):
    """Metaclass for :class:`Model` with relaxed ``None`` handling.

    Omnipy uses this metaclass as a workaround for a pydantic v1 bug affecting
    nested root models. During certain validation paths, pydantic may check
    ``None`` against the model class too early. Treating ``None`` as a temporary
    instance match lets Omnipy defer the actual ``None`` decision to the model's
    declared type.
    """

    # Hack to overcome bug in pydantic/fields.py (v1.10.13), lines 636-641:
    #
    # if origin is None or origin is CollectionsHashable:
    #     # field is not "typing" object eg. Union, dict, list etc.
    #     # allow None for virtual superclasses of NoneType, e.g. Hashable
    #     if isinstance(self.type_, type) and isinstance(None, self.type_):
    #         self.allow_none = True
    #     return
    #
    # This hinders models (including pure pydantic BaseModels) to be properly considered as
    # subfields, e.g. in `list[MyModel]` as `get_origin(MyModel) is None`. Here, we want allow_none
    # to be set to True so that Model is allowed to validate a None value.
    #
    # TODO: Revisit the need for _ModelMetaclass hack in pydantic v2
    def __instancecheck__(self, instance: Any) -> bool:
        """Report ``None`` as temporarily instance-compatible.

        Args:
            instance: Object being checked against the model class.

        Returns:
            ``True`` when ``instance`` is ``None`` or when the normal metaclass
            instance check succeeds.
        """
        if instance is None:
            return True
        return super().__instancecheck__(instance)


undefined_default_factory: Callable[[], Any] = lambda: Undefined


class Model(  # type: ignore[misc]
        ModelDisplayMixin,
        DataClassBase[_RootT],
        pyd.GenericModel,
        Generic[_RootT],
        metaclass=ModelMetaclass,
):
    """Typed pydantic-backed container for a single validated value.

    ``Model[T]`` is Omnipy's central data container. Each concrete
    specialization wraps one root value of type ``T``, validates incoming data
    with pydantic, and exposes the parsed value through :attr:`content`. Models
    also proxy many operations on the wrapped object so they can often be used
    like the underlying value while still preserving Omnipy validation,
    conversion helpers, and interactive snapshot semantics.

    Concrete models are created either as type aliases such as
    ``Model[list[int]]`` or by subclassing an already-specialized model class.
    """
    @classmethod
    def _get_special_methods_info_dict(cls) -> dict_t[str, MethodInfo]:
        return SPECIAL_METHODS_INFO_DICT

    __root__: _RootT = pyd.Field(default_factory=undefined_default_factory)

    # TODO: Pydantic v2, see if slots=True can be used for Model and Dataset to reduce memory usage

    class Config:
        """Pydantic model configuration: allows arbitrary types and validates all fields by default."""
        arbitrary_types_allowed = True
        validate_all = True
        # validate_assignment = True
        smart_union = True
        # json_loads = orjson.loads
        # json_dumps = orjson_dumps
        use_enum_values = True

    def _get_default_factory(self) -> Callable[[], _RootT]:
        try:
            fixed_default_val = self._get_default_value()
            return lambda: fixed_default_val
        except (ValidationError, TypeError, ValueError):
            return lambda: self._get_default_value()

    @classmethod
    def _get_default_value_from_model(  # noqa: C901
            cls,
            model: type[_RootT] | TypeForm | TypeVar,
    ) -> _RootT:
        model = get_default_if_typevar(model)
        origin_type = get_origin(model)
        args = get_args(model)

        if origin_type is Annotated:
            model = args[0]
            origin_type = get_origin(model)
            args = get_args(model)

        if origin_type in (None, ()):
            origin_type = model

        if origin_type is None:
            origin_type = NoneType

        if origin_type in [Union, UnionType]:
            if any(is_none_type(arg) for arg in args):
                return cast(_RootT, None)

            last_error_holder = LastErrorHolder()
            for arg in args:
                if callable(arg) or isinstance(arg, TypeVar):
                    with last_error_holder:
                        return cls._get_default_value_from_model(arg)
            last_error_holder.raise_derived(TypeError(f'Cannot instantiate model "{model}".'))

        if origin_type is tuple and args and Ellipsis not in args:
            return cast(_RootT, tuple(cls._get_default_value_from_model(arg) for arg in args))

        if origin_type is Literal:
            return args[0]

        if origin_type is Callable:
            return cast(_RootT, lambda: None)

        if origin_type is ForwardRef or type(origin_type) is ForwardRef:
            raise TypeError(f'Cannot instantiate model "{model}". ')

        return cast(_RootT, origin_type())  # type: ignore[misc]

    @classmethod
    def _prepare_cls_members_to_mimic_model(  # noqa: C901
            cls,
            created_model: 'type[Model[_RootT]]',
    ) -> None:
        from omnipy.data._typing.helpers import all_model_type_variants

        outer_types = all_model_type_variants(created_model)

        def _type_supports_method(_type: type | GenericAlias, _method_name: str) -> bool:
            if is_literal_type(_type):
                # Literal types should be considered to support the same
                # methods as their underlying type, e.g. int for Literal[3]
                _type = get_args(_type)[0].__class__
            elif get_args(_type):
                # If type is a specialization of a generic type, e.g.
                # MyList[int], we want to check the methods of the
                # underlying generic type, e.g. MyList, as the
                # specialization of non-builtin types typically does not
                # have any special methods.
                _type = cast(type, get_origin(_type))

            method: Callable | None = getattr(_type, _method_name, None)
            if method is None:
                return False

            # We need to check for e.g. object.__or__, which was added
            # in Python 3.10 for e.g 'str | int' and is supported by
            # all types, but should not be considered as a supported
            # method for the model.

            ALWAYS_SUPPORTED_METHODS = ('__delattr__', '__hash__')

            if (_type is object or is_type_specialization(_type)
                    or _method_name in ALWAYS_SUPPORTED_METHODS):
                return True

            # __objclass__ exists for slot_wrappers (built-ins)
            objclass = getattr(method, '__objclass__', None)
            if objclass is not None:
                # Check if the method is defined on the type itself or
                # inherited from a parent class other than object or type
                return objclass not in (type, object)

            return True

        if any(lenient_isinstance(_type, TypeVar) for _type in outer_types):
            return

        for name, method_info in created_model._get_special_methods_info_dict().items():
            method_defined_before_model = False
            for base in created_model.__mro__:
                if base is Model:
                    break
                if name in base.__dict__:
                    if name == '__hash__' and base.__dict__[name] is None:
                        continue
                    method_defined_before_model = True
                    break

            if method_defined_before_model:
                continue

            names_to_check = (name, '__add__') if name in ('__iadd__', '__radd__') else (name,)
            for type_to_support in outer_types:
                if any(_type_supports_method(type_to_support, _) for _ in names_to_check):
                    setattr(created_model,
                            name,
                            functools.partialmethod(cls._special_method, name, method_info))
                    break

    @override
    def __class_getitem__(  # type: ignore[override]
        cls,
        params: type[_RootT] | tuple[type[_RootT]] | TypeVar | tuple[TypeVar],
    ) -> 'type[Model[_RootT]]':
        """Create a concrete ``Model[T]`` specialization.

        Args:
            params: Type expression describing the wrapped root value.

        Returns:
            A concrete :class:`Model` subclass bound to ``params``.
        """

        model = cls._prepare_params(params)

        orig_model: type[_RootT] | TypeVar = model

        # Populating the root field at runtime instead of providing a __root__ Field explicitly
        # is needed due to the inability of typing/pydantic to provide a dynamic default based on
        # the actual type. The following issue in mypy seems relevant:
        # https://github.com/python/mypy/issues/3737 (as well as linked issues)

        created_model = cast(
            type[Model],
            super().__class_getitem__(model if cls is Model else params),  # type: ignore
        )

        created_model._get_root_field().field_info = deepcopy(
            created_model._get_root_field().field_info)

        if cls is Model and orig_model is not _RootT:  # type: ignore[misc]
            created_model._get_root_field().field_info.extra = {'orig_model': orig_model}

        created_model._inherit_first_orig_model_in_bases_if_missing()

        cls._recursively_set_allow_none(created_model._get_root_field())

        # As long as models are not created concurrently, setting the class members temporarily
        # should not have averse effects
        # TODO: Check if we can move to explicit definition of __root__ field at the object
        #       level in pydantic 2.0 (when it is released)

        if created_model is not cls:
            cleanup_name_qualname_and_module(cls, created_model, orig_model)

        cls._prepare_cls_members_to_mimic_model(created_model)

        return created_model

    @classmethod
    def _inherit_first_orig_model_in_bases_if_missing(cls):
        if cls is not Model:
            for orig_base in get_original_bases(cls):
                if isinstance(orig_base, ModelMetaclass):
                    model_base = cast(type[Model], orig_base)
                    if model_base.__concrete__:
                        model_base._inherit_first_orig_model_in_bases_if_missing()
                        orig_model = model_base.get_orig_model()
                        if orig_model is not Undefined:
                            cls.set_orig_model(orig_model)
                            break

            cls._clean_type_caches()

    if TYPE_CHECKING and TYPE_CHECKER != 'mypy':  # noqa: C901

        # mypy currently does not support overloads of __new__()

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

        @overload
        def __new__(
            cls: 'type[Model[float]]' | 'type[Model[Model[float]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_float:
            ...

        @overload
        def __new__(
            cls: 'type[Model[int]]' | 'type[Model[Model[int]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_int:
            ...

        @overload
        def __new__(
            cls: 'type[Model[bool]]' | 'type[Model[Model[bool]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_bool:
            ...

        @overload
        def __new__(
            cls: 'type[Model[str]]' | 'type[Model[Model[str]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_str:
            ...

        @overload
        def __new__(
            cls: 'type[Model[bytes]]' | 'type[Model[Model[bytes]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_bytes:
            ...

        @overload
        def __new__(
            cls: 'type[Model[set[_ValT]]]| type[Model[Model[set[_ValT]]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_set[_ValT]:
            ...

        @overload
        def __new__(
            cls: 'type[Model[list[_ValT]]]| type[Model[Model[list[_ValT]]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_list[_ValT]:
            ...

        @overload
        def __new__(  # pyright: ignore[reportOverlappingOverload]
            cls: 'type[Model[tuple[_ValT, _ValT2]]] | type[Model[Model[tuple[_ValT, _ValT2]]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_tuple_pair[_ValT, _ValT2]:
            ...

        @overload
        def __new__(
            cls: 'type[Model[tuple[_ValT, ...]]] | type[Model[Model[tuple[_ValT, ...]]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_tuple_same_type[_ValT]:
            ...

        @overload
        def __new__(
            cls: 'type[Model[dict_t[_KeyT, _ValT]]] | type[Model[Model[dict_t[_KeyT, _ValT]]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_dict[_KeyT, _ValT]:
            ...

        @overload
        def __new__(
            cls: 'type[Model[Dataset[_OtherModelT]]]',
            *args: Any,
            **kwargs: Any,
        ) -> 'Model_Dataset[_OtherModelT]':
            ...

        @overload
        def __new__(
            cls: 'type[Model[Dataset[_DatasetT | _OtherModelT]]]',
            *args: Any,
            **kwargs: Any,
        ) -> 'Model_Dataset[_DatasetT]':
            ...

        @overload
        def __new__(
            cls: 'type[_ModelT]',
            *args: Any,
            **kwargs: Any,
        ) -> '_ModelT':
            ...

        def __new__(
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> 'Model | _ModelT':
            ...
    else:

        def __new__(  # type: ignore[no-redef]
                cls,
                *args: Any,
                **kwargs: Any,
        ) -> Self:
            """Create an instance only for concrete ``Model[T]`` specializations.

            Args:
                *args: Positional arguments forwarded to instance creation.
                **kwargs: Keyword arguments forwarded to instance creation.

            Returns:
                A new instance of the concrete model class.

            Raises:
                TypeError: If ``Model`` is instantiated without first binding a
                    concrete root type.
            """
            model_not_specified = ROOT_KEY not in cls.__fields__
            if model_not_specified:
                cls._raise_no_model_exception()

            return super().__new__(cls)

    @classmethod
    def get_orig_model(cls) -> type[_RootT] | UndefinedType:
        """Return the original declared model type before internal normalization.

        Returns:
            The original type expression supplied for this model specialization,
            or :data:`Undefined` when no original type has been recorded.
        """
        if cls.__fields__[ROOT_KEY].field_info and cls.__fields__[ROOT_KEY].field_info.extra:
            return cls.__fields__[ROOT_KEY].field_info.extra.get('orig_model', Undefined)
        return Undefined

    @classmethod
    def set_orig_model(cls, orig_model: TypeForm) -> None:
        """Store the original declared model type on the root field metadata.

        Args:
            orig_model: Original type expression to associate with the model.
        """
        cls.__fields__[ROOT_KEY].field_info.extra['orig_model'] = orig_model

    def __init__(  # noqa: C901
        self,
        value: _RootT | object | UndefinedType = Undefined,
        *,
        __root__: _RootT | object | UndefinedType = Undefined,
        **kwargs: _RootT | object,
    ) -> None:
        """Parse input into the concrete model's root value.

        The constructor accepts either a direct root value, the pydantic-style
        ``__root__`` keyword, or keyword pairs for dict-like models. Omnipy also
        accepts datasets, other models, and plain pydantic models as input and
        converts them to raw data before validation.

        Args:
            value: Root value to parse.
            __root__: Alternative explicit root value.
            **kwargs: Mapping-style root content for dict-like models.

        Raises:
            AssertionError: If root data is supplied through more than one input
                path.
            ValidationError: If the provided data cannot be parsed as this
                model's declared type.
        """
        super_kwargs: dict[str, _RootT] = {}
        num_root_vals = 0

        if value is not Undefined:
            super_kwargs[ROOT_KEY] = cast(_RootT, value)
            num_root_vals += 1

        if __root__ is not Undefined:
            super_kwargs[ROOT_KEY] = cast(_RootT, __root__)
            num_root_vals += 1

        if kwargs:
            super_kwargs[ROOT_KEY] = cast(_RootT, kwargs)
            kwargs = {}
            num_root_vals += 1

        assert num_root_vals <= 1, 'Not allowed to provide root data in more than one argument'

        if self._get_root_field().default_factory is undefined_default_factory:
            self._get_root_field().default_factory = self._get_default_factory()

        dataset_or_model_as_input = False
        if ROOT_KEY in super_kwargs:
            try:
                dataset_or_model_as_input, value = \
                    prepare_value_for_validation_if_dataset_or_model(super_kwargs[ROOT_KEY])
            except Exception as exc:
                val_exc = ValueError(f'Failed to prepare value for validation: {exc}')
                raise ValidationError(
                    [pyd.ErrorWrapper(exc, loc=ROOT_KEY), pyd.ErrorWrapper(val_exc, loc=ROOT_KEY)],
                    self.__class__)
            if dataset_or_model_as_input:
                super_kwargs[ROOT_KEY] = cast(_RootT, value)

        self._init(super_kwargs, **kwargs)

        try:
            self._primary_validation(super_kwargs)
        except ValidationError:
            if dataset_or_model_as_input:
                self._secondary_validation_from_data(super_kwargs)
            else:
                raise

        if not self.__class__.__doc__:
            self._set_standard_field_description()

    def _get_default_value(self) -> _RootT:
        return self.__class__._get_default_value_from_model(self.full_type())

    def _primary_validation(self, super_kwargs):
        # Pydantic validation of super_kwargs
        validate_cls_counts[self.__class__.__name__] += 1
        super().__init__(**super_kwargs)

    def _secondary_validation_from_data(self, super_kwargs):
        super().__init__()
        self.from_data(super_kwargs[ROOT_KEY])

    def _init(self, super_kwargs: dict_t[str, Any], **kwargs: Any) -> None:
        ...

    def __del__(self):
        content_id = id(self.content)
        self.snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id)

    def __copy__(self) -> Self:
        """Return a shallow copy using Omnipy's custom copy semantics.

        Returns:
            A shallow-copied model instance whose mutable content is not shared
            with the original.
        """
        return self.copy(deep=False)

    if TYPE_CHECKING:

        @override
        def __iter__(self) -> Iterator:  # type: ignore[override]
            ...

    def copy(self, *, deep: bool = False, **kwargs) -> Self:
        """Copy the model while avoiding shared mutable content by default.

        Omnipy overrides pydantic's copy semantics so a shallow copy still gets
        a shallow-copied root value instead of sharing the same mutable object.

        Args:
            deep: When ``True``, perform a deep copy.
            **kwargs: Additional keyword arguments forwarded to pydantic's
                ``copy()`` implementation.

        Returns:
            A copied model instance.
        """
        pydantic_copy = pyd.GenericModel.copy(self, deep=deep, **kwargs)
        if not deep:
            # Shallow copying of the model should not share the same
            # content, as this can lead to unintentional side effects when
            # the content is mutable.
            pydantic_copy.content = copy(pydantic_copy.__dict__[ROOT_KEY])
        return pydantic_copy  # pyright: ignore[reportReturnType]

    @classmethod
    def clone_model_cls(cls, new_model_cls_name: str) -> type[Self]:
        """Create a subclass clone of this concrete model class.

        Args:
            new_model_cls_name: Name to assign to the cloned class.

        Returns:
            A new subclass with the same behavior and type binding.
        """
        new_model_cls = type(new_model_cls_name, (cls,), {})
        return cast(type[Self], new_model_cls)

    @staticmethod
    def _raise_no_model_exception() -> None:
        raise TypeError('Note: The Model class requires a concrete model to be specified as '
                        'a type hierarchy within brackets either directly, e.g.:\n\n'
                        '\tmodel = Model[list[int]]([1,2,3])\n\n'
                        'or indirectly in a subclass definition, e.g.:\n\n'
                        '\tclass MyNumberList(Model[list[int]]): ...\n\n')

    def _set_standard_field_description(self) -> None:
        self.__fields__[ROOT_KEY].field_info.description = self._get_standard_field_description()

    @classmethod
    def _get_standard_field_description(cls) -> str:
        return ('This class represents a concrete model for data items in the `omnipy` Python '
                'package. It is a statically typed specialization of the Model class, '
                'which is itself wrapping the excellent Python package named `pydantic`.')

    @classmethod
    def validate(cls: type['Model'], value: Any) -> 'Model':
        """Validate a value while preserving Omnipy iterator overrides.

        This method is primarily an internal compatibility shim for pydantic's
        validation API. Omnipy temporarily restores pydantic's original
        ``__iter__`` behavior when validating model instances so custom iterator
        proxying does not interfere with validation.

        Args:
            value: Value to validate as an instance of ``cls``.

        Returns:
            A validated model instance.
        """
        # TODO: Doublecheck if validate() method is still needed for pydantic v2

        validate_cls_counts[cls.__name__] += 1
        if is_model_instance(value):

            @contextmanager
            def temporary_set_value_iter_to_pydantic_method() -> Iterator[None]:
                prev_iter = value.__class__.__iter__
                value.__class__.__iter__ = pyd.GenericModel.__iter__  # type: ignore[method-assign]

                try:
                    yield
                finally:
                    value.__class__.__iter__ = prev_iter  # type: ignore[method-assign]

            with temporary_set_value_iter_to_pydantic_method():
                return super().validate(value)
        else:
            return super().validate(value)

    @classmethod
    def update_forward_refs(
        cls,
        calling_module: str | None = None,
        prev_visited_classes: set[type] | None = None,
        **localns: Any,
    ) -> None:
        """Resolve forward references for this model and related model bases.

        Omnipy extends pydantic's behavior by merging namespaces from both the
        defining module and the calling module, then propagating the same context
        through parent model classes. This keeps forward references working when
        specialized models are defined in one module and used from another.

        Args:
            calling_module: Module name to use as the caller context. When not
                provided, Omnipy infers it from the call stack.
            prev_visited_classes: Set used internally to avoid revisiting model
                classes during recursive propagation.
            **localns: Additional local names available while resolving forward
                references.
        """
        if prev_visited_classes is None:
            prev_visited_classes = set()
        elif cls in prev_visited_classes:
            return

        # Merge the namespaces of the Model's own module and the calling
        # module to the local namespace for evaluation of forward
        # references, which is necessary for cases where the Model is
        # defined in a different module than where it is used, e.g. when
        # the Model is defined in a library and used by a user in their
        # own code.
        if calling_module is None:
            calling_module = get_calling_module_name()
        own_module_ns, globalns = \
            build_own_module_and_global_namespace_for_forward_refs(cls, calling_module, **localns)

        prev_outer_type = cls._get_root_field().outer_type_
        prev_type = cls._get_root_field().type_

        super().update_forward_refs(**globalns)

        cls._get_root_field().outer_type_ = evaluate_any_forward_refs_if_possible(
            prev_outer_type, **globalns)
        cls._get_root_field().type_ = evaluate_any_forward_refs_if_possible(prev_type, **globalns)
        cls.set_orig_model(evaluate_any_forward_refs_if_possible(cls.get_orig_model(), **globalns))
        if ROOT_KEY in cls.__annotations__:
            cls.__annotations__[ROOT_KEY] = evaluate_any_forward_refs_if_possible(
                cls.__annotations__[ROOT_KEY], **globalns)

        cls._clean_type_caches()

        cls._recursively_set_allow_none(cls._get_root_field())

        cls._prepare_cls_members_to_mimic_model(cls)

        prev_visited_classes.add(cls)

        # Propagate update_forward_refs to parent models but retaining the
        # same calling module. This is needed to ensure the correct
        # context is used to resolve forward references in complex
        # inheritance hierarchies.
        #
        # We explicitly call `update_forward_refs` on immediate parent
        # classes (`__bases__`) instead of relying solely on
        # `super().update_forward_refs()`. This is because `super()`
        # inside this classmethod resolves relative to `Model` in the MRO,
        # silently bypassing custom logic on any intermediate `Model`
        # subclasses. Explicitly propagating through `__bases__` ensures
        # that class-level setups are correctly applied to all parents
        # exactly once, efficiently preventing redundant updates.
        for base in cls.__bases__:
            if is_model_subclass(base) and base is not Model:
                # Merge the current class's own module namespace into
                # localns before propagating, so that pydantic-generated
                # parametrized base classes (which have
                # __module__='omnipy.data.model' rather than the defining
                # module) can still resolve forward refs that only exist
                # in the defining module's namespace.

                extra_ns: dict[str, Any] = {}
                extra_ns.update(**own_module_ns)
                extra_ns.update(**localns)

                base.update_forward_refs(
                    calling_module=calling_module,
                    prev_visited_classes=prev_visited_classes,
                    **extra_ns,
                )

        cls.__name__ = remove_forward_ref_notation(cls.__name__)
        cls.__qualname__ = remove_forward_ref_notation(cls.__qualname__)

    def validate_content(self) -> None:
        """Re-validate the current :attr:`content` value in place.

        Raises:
            ValidationError: If the current content no longer satisfies the
                model's declared type.
        """
        self._validate_and_set_value(self.content)

    def _validate_and_set_value(
        self,
        new_content: object,
        reset_solution: ContextManager[None] | None = None,
        lazy_snapshot_if_possible: bool = False,
    ) -> None:

        old_content_id = id(self.content)

        def _set_new_content(content: object) -> None:
            if id(content) != old_content_id:
                self.content = content  # type: ignore[assignment]

        self._generic_validate_content(
            new_content=new_content,
            outer_reset_solution=reset_solution,
            post_validation_func=_set_new_content,
            lazy_snapshot_if_possible=lazy_snapshot_if_possible,
        )

    def _prepare_reset_solution_take_snapshot_if_needed(
        self,
        /,
    ) -> ResetSolutionTuple:
        snapshot_taken = False
        if self.config.model.interactive:
            # TODO: Lazy snapshotting causes unneeded double validation for data that is later
            #       validated for snapshot. Perhaps add a dirty flag to snapshot that can be used
            #       to determine if re-validation is needed? This can also help avoid equality
            #       tests, which might be expensive for large data structures.
            needs_pre_validation = (not self.has_snapshot()
                                    or not self.content_validated_according_to_snapshot())
            if needs_pre_validation:
                internal_reset_solution = self._get_reset_solution()
                with internal_reset_solution:
                    self._validate_and_set_value(
                        self.content, reset_solution=internal_reset_solution)
                    snapshot_taken = True

        return ResetSolutionTuple(
            reset_solution=self._get_reset_solution(),
            snapshot_taken=snapshot_taken,
        )

    def _get_reset_solution(self) -> ContextManager[None]:
        if self.config.model.interactive and self.has_snapshot():
            return self._get_revert_to_snapshot_reset_solution()
        else:
            return nothing()

    def _get_revert_to_snapshot_reset_solution(self) -> ContextManager[None]:
        prev_deepcopy_content_ids = SetDeque[int]()

        def _setup():
            prev_deepcopy_content_ids.extend(self.snapshot_holder.get_deepcopy_content_ids())

        def _handle_exception():
            new_deepcopy_content_ids = SetDeque[int](
                self.snapshot_holder.get_deepcopy_content_ids())
            new_deepcopy_content_ids.extend(prev_deepcopy_content_ids)
            self.snapshot_holder.schedule_deepcopy_content_ids_for_deletion(
                *new_deepcopy_content_ids)
            # self.content = self.snapshot_holder.get_snapshot_deepcopy(self)
            self.content = deepcopy(self.snapshot)

        return setup_and_teardown_callback_context(
            setup_func=_setup,
            exception_func=_handle_exception,
        )

    def _generic_validate_content(
        self,
        /,
        new_content: object,
        outer_reset_solution: ContextManager[None] | None = None,
        post_validation_func: Callable[[_RootT], None] | None = None,
        lazy_snapshot_if_possible: bool = False,
    ) -> None:
        keep_alive_old_content = self.content  # To ensure old content ids are not reused

        inner_reset_solution: ContextManager[None]
        if outer_reset_solution:
            inner_reset_solution = nothing()
        else:
            validating_self = new_content is self.content
            reset_solution_tuple = self._prepare_reset_solution_take_snapshot_if_needed()
            if validating_self and reset_solution_tuple.snapshot_taken:
                return
            inner_reset_solution = reset_solution_tuple.reset_solution

        with (inner_reset_solution):
            validated_content = self._validate_content_from_value(new_content)

            if validated_content is new_content:
                validated_content = copy(validated_content)

            if post_validation_func:
                post_validation_func(validated_content)
        del inner_reset_solution

        del new_content
        if self.has_snapshot() or not lazy_snapshot_if_possible:
            self._take_snapshot_of_validated_content()

        del keep_alive_old_content

    def _validate_content_from_value(
        self,
        value: object,
    ) -> _RootT:
        _, value = prepare_value_for_validation_if_dataset_or_model(value)

        values, _, validation_error = pyd.validate_model(self.__class__, {ROOT_KEY: value})
        if validation_error:
            raise validation_error

        return values[ROOT_KEY]

    @property
    def snapshot(self) -> _RootT:
        """Return the validated snapshot currently tracked for this model.

        Returns:
            The snapshot value stored for the current model instance.

        Raises:
            AssertionError: If no snapshot has been taken yet.
        """
        snapshot_wrapper = self._get_snapshot_wrapper()
        assert snapshot_wrapper.id == id(self)
        return snapshot_wrapper.snapshot

    def has_snapshot(self) -> bool:
        """Check whether this model currently has a stored snapshot.

        Returns:
            ``True`` if interactive snapshot state exists for this model.
        """
        return self in self.snapshot_holder

    def _get_snapshot_wrapper(self) -> IsSnapshotWrapper[IsModel, _RootT]:
        assert self.has_snapshot(), 'No snapshot taken yet'
        return self.snapshot_holder[self]

    def snapshot_taken_of_same_model(self, model: 'Model') -> bool:
        """Check whether the stored snapshot was taken from ``model`` itself.

        Args:
            model: Model instance to compare against the snapshot origin.

        Returns:
            ``True`` if the snapshot was recorded from the same object identity.
        """
        snapshot_wrapper = self._get_snapshot_wrapper()
        return snapshot_wrapper.taken_of_same_obj(model)

    def snapshot_differs_from_model(self, model: 'Model') -> bool:
        """Check whether the stored snapshot differs from another model's content.

        Args:
            model: Model whose current content should be compared with the
                snapshot.

        Returns:
            ``True`` if the snapshot content differs from ``model.content``.
        """
        snapshot_wrapper = self._get_snapshot_wrapper()
        return snapshot_wrapper.differs_from(model.content)

    def content_validated_according_to_snapshot(self) -> bool:
        """Report whether current content still matches the validated snapshot.

        Returns:
            ``True`` when the current content is still represented by the stored
            snapshot and does not need re-validation.
        """
        needs_validation = self.snapshot_differs_from_model(self) \
            or not self.snapshot_taken_of_same_model(self)
        return not needs_validation

    def _take_snapshot_of_validated_content(self) -> None:
        if self.config.model.interactive:
            with self.deepcopy_context(self.snapshot_holder.take_snapshot_setup,
                                       self.snapshot_holder.take_snapshot_teardown):
                self.snapshot_holder.take_snapshot(self)

    @classmethod
    def _parse_data(cls, data: Any) -> _RootT:
        return data

    # TODO: See if it is possible to support general mappings similarly to iterables (in Model)
    #       (note: this is an old TODO, it is unclear what exactly is not supported...)
    @pyd.root_validator(pre=True)
    def _generous_iterable_support(cls, root_obj: dict_t[str, _RootT | None]) -> Any:
        if ROOT_KEY in root_obj:
            value = root_obj[ROOT_KEY]
            outer_type = cls.outer_type()
            if (lenient_issubclass(outer_type, Iterable)
                    and not lenient_isinstance(value, outer_type)  # type: ignore[arg-type]
                    and is_non_str_byte_iterable(value)
                    # Leave the types below for pydantic to handle
                    and not pyd.sequence_like(value)
                    # Also, exclude mappings
                    and not isinstance(value, Mapping)):
                return {ROOT_KEY: (_ for _ in value)}
        return root_obj

    @pyd.root_validator
    def _parse_root_object(cls, root_obj: dict_t[str, _RootT | None]) -> Any:
        assert ROOT_KEY in root_obj
        value = root_obj[ROOT_KEY]
        value = parse_none_according_to_model(value, root_model=cls)

        config = cls.data_class_creator.config  # type: ignore[attr-defined]
        with hold_and_reset_prev_attrib_value(config.model,
                                              'dynamically_convert_elements_to_models'):
            config.model.dynamically_convert_elements_to_models = False
            return {ROOT_KEY: cls._parse_data(value)}

    # TODO: Rename Model.content to Model.content as it may be a single value, while "content"
    #       implies a countable collection of values
    @property
    def content(self) -> _RootT:
        """Access the parsed root value stored by the model.

        Returns:
            The current validated root value.
        """
        return cast(_RootT, self.__dict__.get(ROOT_KEY))

    @content.setter
    def content(self, value: _RootT) -> None:
        """Set the root value without triggering automatic validation.

        Args:
            value: New root value to assign directly.

        Note:
            Unlike :meth:`__init__`, :meth:`from_data`, and :meth:`from_json`,
            direct assignment does not validate the value automatically. Call
            :meth:`validate_content` when you need the assignment checked.
        """
        super().__setattr__(ROOT_KEY, value)

    def to(self, model_cls: type[_OtherModelT]) -> _OtherModelT:
        """Convert this model into another model class by reparsing its data.

        Args:
            model_cls: Destination model class.

        Returns:
            A new instance of ``model_cls`` initialized from this model.
        """
        return model_cls(self)

    def do(self, placeholder: F) -> Any:
        """Apply a placeholder-style callable to this model.

        Args:
            placeholder: Callable placeholder from Omnipy's ``F`` helper.

        Returns:
            Whatever value ``placeholder`` returns for this model instance.
        """
        return placeholder(self)

    def dict(self, *args, **kwargs) -> dict_t[str, object]:
        return {ROOT_KEY: self.to_data()}

    # TODO: Improve typing of to_data/from_data. Should be limited to JSON types at least, but also
    #       `_RootT` for simple models (without submodels). Handling Submodels is tricky, and may
    #       not be possible, e.g. `Model[list[Model[int]]().to_data()` should be type `list[int]`.
    #       A possibility is to support manually providing proper to_data, e.g. through
    #       Generic Mixin class, e.g.:
    #       ```python
    #       class MyModel(Model[list[Model[int]]], ModelData[list[int]]):
    #          ...
    #       ```
    def to_data(self) -> object:
        """Serialize the model into raw Python data.

        Returns:
            The wrapped value converted to plain data, including recursive
            conversion of nested Omnipy models.
        """
        return super().dict(by_alias=True)[ROOT_KEY]

    def _empty_from_data(self, value: object) -> None:
        @contextmanager
        def _reset_to_default(*args, **kwds):
            self.content = self._get_default_value_from_model(self.full_type())
            yield

        self._validate_and_set_value(
            value, reset_solution=_reset_to_default(), lazy_snapshot_if_possible=True)

    def from_data(self, data: Any) -> None:
        """Parse raw Python data into this existing model instance.

        Args:
            data: Raw data to validate and store as the model's content.

        Raises:
            ValidationError: If ``data`` cannot be parsed as this model's type.
        """
        if self.content == self._get_default_value_from_model(self.full_type()):
            self._empty_from_data(data)
        else:
            self._validate_and_set_value(data)

    def absorb_and_replace(self, other: 'Model'):
        """Replace this model's content with data parsed from another model.

        Args:
            other: Source model whose serialized data should be absorbed.
        """
        self.from_data(other.to_data())

    def to_json(self, pretty=True) -> str:
        """Serialize the model to JSON.

        Args:
            pretty: When ``True``, return indented human-readable JSON.

        Returns:
            JSON representation of the model content.
        """
        json_content = pyd.BaseModel.json(self)
        if pretty:
            return self._pretty_print_json(json.loads(json_content))
        else:
            return json_content

    def from_json(self, json_content: str) -> None:
        """Parse JSON into this existing model instance.

        Args:
            json_content: JSON document to parse.

        Raises:
            ValidationError: If the JSON content does not match the model type.
        """
        new_model = self.parse_raw(json_content, proto=pyd.Protocol.json)
        self.content = new_model.content

    @classmethod
    @functools.cache
    def inner_type(cls, with_args: bool = False) -> TypeForm:
        """Return the inner validated root type for this model class.

        Args:
            with_args: When ``True``, preserve type arguments such as ``list[int]``.

        Returns:
            The inner root type used after pydantic normalization.
        """
        return cls._get_root_type(outer=False, with_args=with_args)

    @classmethod
    @functools.cache
    def outer_type(cls, with_args: bool = False) -> TypeForm:
        """Return the declared outer root type for this model class.

        Args:
            with_args: When ``True``, preserve type arguments such as ``list[int]``.

        Returns:
            The outer root type exposed by the model.
        """
        return cls._get_root_type(outer=True, with_args=with_args)

    @classmethod
    @functools.cache
    def full_type(cls) -> type[_RootT]:
        """Return the model's full declared root type including type arguments.

        Returns:
            The complete concrete type bound to this model.
        """
        return cast(type[_RootT], cls.outer_type(with_args=True))

    @classmethod
    @functools.cache
    def is_nested_type(cls) -> bool:
        """Check whether this model wraps a nested or transformed root type.

        Returns:
            ``True`` when the inner validated type differs from the declared
            outer type.
        """
        return not cls.inner_type(with_args=True) == cls.outer_type(with_args=True)

    @classmethod
    def _clean_type_caches(cls):
        cls._get_root_type.cache_clear()
        cls.outer_type.cache_clear()
        cls.inner_type.cache_clear()
        cls.full_type.cache_clear()
        cls.is_nested_type.cache_clear()

    @classmethod
    def _get_root_field(cls) -> pyd.ModelField:
        return cast(pyd.ModelField, cls.__fields__.get(ROOT_KEY))

    @classmethod
    @functools.cache
    def _get_root_type(cls, outer: bool, with_args: bool) -> TypeForm:
        root_field = cls._get_root_field()
        root_type = root_field.outer_type_ if outer else root_field.type_

        orig_model = cls.get_orig_model()
        if orig_model != Undefined:
            if not is_optional(root_type) and is_optional(orig_model):
                if outer:
                    root_type = Optional[root_type]
                else:
                    root_type = Optional[root_field.outer_type_]

        return root_type if with_args else ensure_plain_type(root_type)

    # @classmethod
    # def create_from_json(cls, data: str | tuple[str]):
    #     if isinstance(data, tuple):
    #         data = data[0]
    #
    #     obj = cls()
    #     obj.from_json(data)
    #     return obj
    #
    # def __reduce__(self):
    #     return self.__class__.create_from_json, (self.to_json(),)

    @classmethod
    def to_json_schema(cls, pretty=True) -> str:
        """Render the model's JSON schema.

        Args:
            pretty: When ``True``, return indented human-readable JSON.

        Returns:
            JSON schema for the model with Omnipy's ``orig_model`` metadata
            removed.
        """
        schema = cls.schema()
        if 'orig_model' in schema:
            del schema['orig_model']

        if pretty:
            return cls._pretty_print_json(schema)
        else:
            return json.dumps(schema)

    @staticmethod
    def _pretty_print_json(json_content: Any) -> str:
        return json.dumps(json_content, indent=2)

    def _check_for_root_key(self) -> None:
        if ROOT_KEY not in self.__dict__:
            raise TypeError('The Model class requires the specific model to be specified in as '
                            'a type hierarchy within brackets either directly, e.g.:\n'
                            '\t"model = Model[list[int]]([1,2,3])"\n'
                            'or indirectly in a subclass definition, e.g.:\n'
                            '\t"class MyNumberList(Model[list[int]]): ..."')

    def __setattr__(self, attr: str, value: Any) -> None:
        """Set model attributes while protecting Omnipy's root-value invariants.

        ``content`` assignments are handled specially so Omnipy can keep
        snapshot bookkeeping in sync. For wrapped non-Omnipy pydantic models,
        unknown attributes are delegated to the underlying content object.

        Args:
            attr: Attribute name to assign.
            value: Value to assign.

        Raises:
            RuntimeError: If attempting to assign an unsupported extra
                attribute on a normal Omnipy model.
        """
        if attr in ['__module__'] + list(self.__dict__.keys()) and attr not in [ROOT_KEY]:
            super().__setattr__(attr, value)
        else:
            match (attr):
                case 'content':
                    content_prop = getattr(self.__class__, attr)
                    old_content_id = id(content_prop.__get__(self))
                    is_new_content = id(value) != old_content_id

                    if is_new_content:
                        content_prop.__set__(self, value)

                        if self.config.model.interactive and self.has_snapshot():
                            self.snapshot_holder.schedule_deepcopy_content_ids_for_deletion(
                                old_content_id)
                case 'repr_state':
                    prop = getattr(self.__class__, attr)
                    prop.__set__(self, value)
                case _:
                    if self._is_non_omnipy_pydantic_model():
                        self._special_method(
                            '__setattr__',
                            MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
                            attr,
                            value)
                    else:
                        raise RuntimeError('Model does not allow setting of extra attributes')

    def _special_method(  # noqa: C901
            self, name: str, info: MethodInfo, *args: object, **kwargs: object) -> object:

        if info.state_changing:

            def _call_special_method_and_return_self_if_inplace(*inner_args: object,
                                                                **inner_kwargs: object) -> object:
                return_val = self._call_special_method(name, *inner_args, **inner_kwargs)

                # In-place operators should return self, which here includes the wrapping Model obj
                # The following is to avoid _convert_to_model_if_reasonable() to be called below,
                # which would otherwise create a new Model instance and return it
                if id(return_val) == id(self.content):  # in-place operator, e.g. model += 1
                    return_val = self

                return return_val

            reset_solution = self._prepare_reset_solution_take_snapshot_if_needed().reset_solution
            with reset_solution:
                ret = _call_special_method_and_return_self_if_inplace(*args, **kwargs)
                if ret is NotImplemented:
                    return ret

                self._validate_and_set_value(
                    new_content=self.content,
                    reset_solution=reset_solution,
                )

        elif name == '__iter__' and isinstance(self, Iterable) and not hasattr(self, 'keys'):
            _per_element_model_generator = self._get_convert_full_element_model_generator(
                cast(Iterable, self.content),  # level_up_type_arg_idx=0,
            )
            return _per_element_model_generator()
        else:
            ret = self._call_special_method(name, *args, **kwargs)
            if ret is NotImplemented:
                return ret

            if info.state_changing:
                self.validate_content()

        if id(ret) != id(self) and info.returns_same_type:
            level_up = False
            if name == '__getitem__':
                assert len(args) == 1
                if not isinstance(args[0], slice) and not is_non_str_byte_iterable(args[0]):
                    level_up = True

            # We can do this with some ease of mind as all the methods except '__getitem__' with
            # integer argument are supposed to possibly return a result of the same type.
            ret = self._convert_to_model_if_reasonable(
                ret,
                level_up=level_up,
                raise_validation_errors=(info.returns_same_type == YesNoMaybe.YES),
            )

        return ret

    def _call_special_method(  # noqa: C901
            self,
            name: str,
            *args: object,
            **kwargs: object,
    ) -> object:
        content = self.content

        has_add_method = self._content_obj_hasattr('__add__')
        has_radd_method = self._content_obj_hasattr('__radd__')
        has_iadd_method = self._content_obj_hasattr('__iadd__')

        if name == '__add__' and has_add_method:

            def _add(other) -> object:
                # try:
                #     return content.__add__(self.__class__(other).content)
                # except ValidationError:
                return content.__add__(other)  # type: ignore[operator]

            # return _add_new_other_model(*args, **kwargs)
            method = _add
            return self._call_single_arg_method_with_model_converted_other_first(
                name, method, *args, model_converted_other_method=None, **kwargs)

        elif name == '__radd__' and (has_radd_method or has_add_method):

            def _radd(other) -> object:
                if has_radd_method:
                    ret = content.__radd__(other)  # type: ignore[attr-defined]
                    if ret is NotImplemented and has_add_method:
                        return content.__add__(other)  # type: ignore[operator]
                    return ret
                else:
                    return content.__add__(other)  # type: ignore[operator]

            def _radd_model_converted_other(other) -> object:
                other_content = self.__class__(other).content
                if has_radd_method:
                    ret = content.__radd__(other_content)  # type: ignore[attr-defined]
                    if ret is NotImplemented and has_add_method:
                        return other_content.__add__(content)  # type: ignore[operator]
                    return ret
                else:
                    return other_content.__add__(content)  # type: ignore[operator]

            method = _radd
            model_converted_other_method = _radd_model_converted_other
            return self._call_single_arg_method_with_model_converted_other_first(
                name,
                method,
                *args,
                model_converted_other_method=model_converted_other_method,
                **kwargs,
            )

        elif name == '__iadd__' and (has_iadd_method or has_add_method):

            def _iadd(other) -> object:
                if has_iadd_method:
                    ret = content.__iadd__(other)  # type: ignore[attr-defined]
                    if ret is NotImplemented and has_add_method:
                        return content.__add__(other)  # type: ignore[operator]
                    return ret
                else:
                    return content.__add__(other)  # type: ignore[operator]

            method = _iadd
            return self._call_single_arg_method_with_model_converted_other_first(
                name, method, *args, model_converted_other_method=None, **kwargs)
        else:
            try:
                method = cast(Callable, self._getattr_from_content_obj(name))
            except AttributeError as e:
                if name in ('__int__', '__float__', '__complex__'):
                    raise ValueError from e
                if name == '__len__':
                    raise TypeError(f"object of type '{self.__class__.__name__}' has no len()")
                else:
                    return NotImplemented

            if name == '__hash__' and method is None:
                raise TypeError(f'unhashable type: {self.__class__.__name__}')

            if name in ['__setitem__', '__setattr__']:
                key, value = args
                _, value = prepare_value_for_validation_if_dataset_or_model(value)
                args = (key, value)

                self_convert_args_if_failure = False
            else:
                self_convert_args_if_failure = True

            if name == '__getitem__' and is_model_instance(content):
                # If propagating a __getitem__ to a nested model, propagate
                # also the `dynamically_convert_elements_to_models` setting
                # as it is activated only at the innermost level (when
                # content is no longer a Model.
                reset_dyn_convert_els_to_models = False
            else:
                reset_dyn_convert_els_to_models = True

            return self._call_method(
                method,
                self_convert_args_if_failure,
                reset_dyn_convert_els_to_models,
                *args,
                **kwargs,
            )

    def _call_single_arg_method_with_model_converted_other_first(
        self,
        name: str,
        method: Callable,
        *args: object,
        model_converted_other_method: Callable | None = None,
        **kwargs: object,
    ):
        if len(args) != 1:
            raise TypeError(f'expected 1 argument, got {len(args)}')

        if len(kwargs) > 0:
            raise TypeError(f'method {name} takes no keyword arguments')

        arg = args[0]

        try:
            try:
                if model_converted_other_method:
                    return model_converted_other_method(arg)
                else:
                    return method(self.__class__(arg).content, **kwargs)
            except (ValidationError, TypeError):
                # TODO: Add debug logging for hidden validation and other exceptions e.g. when
                #       concatenating `Model[int](123) + '234.'` (gives TypeError:
                #       unsupported operand type(s) for +: 'Model[int]' and 'str'). ?
                #       `Model[int](123) + '234'` works fine, returns `Model[int]('357')`.
                return method(arg)
        except TypeError:
            return NotImplemented

    def _call_method(  # noqa: C901
        self,
        method: Callable,
        self_convert_args_if_failure: bool,
        reset_dyn_convert_els_to_models: bool,
        *args: object,
        **kwargs: object,
    ):
        with hold_and_reset_prev_attrib_value(
                self.config.model,
                'dynamically_convert_elements_to_models',
        ):
            if reset_dyn_convert_els_to_models:
                self.config.model.dynamically_convert_elements_to_models = False

            try:
                ret = method(*args, **kwargs)
                # TODO: Do not call methods with model_converted_args where
                #       it does not make sense, e.g. by adding a field
                #       possibly_self_type_as_input in `MethodInfo`
            except TypeError as type_exc:
                if not self_convert_args_if_failure:
                    raise
                try:
                    ret = self._call_method_with_model_converted_args(method, *args, **kwargs)
                except ValidationError:
                    raise type_exc

            if ret is NotImplemented:
                if self_convert_args_if_failure:
                    try:
                        ret = self._call_method_with_model_converted_args(method, *args, **kwargs)
                    except ValidationError:
                        pass

            return ret

    def _call_method_with_model_converted_args(
        self,
        method: Callable,
        *args: object,
        **kwargs: object,
    ):
        model_args = [self.__class__(arg).content for arg in args]
        return method(*model_args, **kwargs)

    def _get_convert_full_element_model_generator(
        self,
        elements: Iterable,
    ) -> Callable[..., Generator]:
        def _convert_full_element_model_generator(elements=elements):
            for el in elements:
                yield self._convert_to_model_if_reasonable(el, level_up=True)

        return _convert_full_element_model_generator

    def _get_convert_element_value_model_generator(self,
                                                   elements: Iterable) -> Callable[..., Generator]:
        def _convert_element_value_model_generator(elements=elements):
            for el in elements:
                yield (
                    el[0],
                    self._convert_to_model_if_reasonable(el[1], level_up=True),
                )

        return _convert_element_value_model_generator

    def _convert_to_model_if_reasonable(  # noqa: C901
        self,
        ret: Mapping[_KeyT, _ValT] | Iterable[_ValT] | _ReturnT | _RootT,
        level_up: bool = False,
        raise_validation_errors: bool = False,
    ) -> 'Model[_KeyT] | Model[_ValT] | Model[tuple[_KeyT, _ValT]] | Model[_ReturnT] | Model[_RootT] | _ReturnT':  # noqa: E501
        from omnipy.data._typing.helpers import all_model_type_variants

        if level_up and not self.config.model.dynamically_convert_elements_to_models:
            ...
        else:
            for type_to_check in all_model_type_variants(self):
                plain_type_to_check = ensure_plain_type(type_to_check)
                if plain_type_to_check in (ForwardRef, TypeVar, None):
                    continue

                if level_up:  # from above: dynamically_convert_elements_to_models == True
                    type_args = get_args(type_to_check)
                    if type_args:
                        # Assuming last type argument is the type of value of the container
                        value_arg_type = type_args[-1]

                        for level_up_type_to_check in all_type_variants(value_arg_type):
                            level_up_type_to_check = self._fix_tuple_type_from_args(
                                level_up_type_to_check)
                            # Only non-Models content considered for dynamic conversion
                            if not is_model_instance(ret) and self._is_instance_or_literal(
                                    ret,
                                    ensure_plain_type(level_up_type_to_check),
                                    level_up_type_to_check,
                            ):
                                try:
                                    return Model[level_up_type_to_check](ret)  # type: ignore
                                except ValidationError:
                                    if raise_validation_errors:
                                        raise
                                except TypeError:
                                    pass

                else:
                    if self._is_instance_or_literal(
                            ret,
                            plain_type_to_check,
                            type_to_check,
                    ):
                        try:
                            return self.__class__(ret)
                        except ValidationError:
                            if raise_validation_errors:
                                raise
                        except TypeError:
                            pass

        return cast(_ReturnT, ret)

    @staticmethod
    def _is_instance_or_literal(obj: object, plain_type: type, raw_type: type | GenericAlias):
        if plain_type is Literal:
            args = get_args(raw_type)
            for arg in args:
                if obj == arg:
                    return True
            return False
        else:
            return lenient_isinstance(obj, plain_type)

    def _fix_tuple_type_from_args(
        self, level_up_type_to_check: type | GenericAlias | tuple[type | GenericAlias, ...]
    ) -> type | GenericAlias:
        if isinstance(level_up_type_to_check, tuple):
            match len(level_up_type_to_check):
                case 1:
                    return level_up_type_to_check[0]
                case _:
                    return tuple[level_up_type_to_check]  # type: ignore[valid-type]
        else:
            return level_up_type_to_check

    if not TYPE_CHECKING:

        def __getattr__(self, attr: str) -> Any:
            """Proxy missing attributes and methods to the wrapped content object.

            Omnipy uses this hook to expose operations of the wrapped root value
            while still validating state-changing calls and converting returned
            elements back into models when appropriate.

            Args:
                attr: Attribute name requested on the model.

            Returns:
                The proxied attribute or wrapped method from the underlying
                content object.

            Raises:
                AttributeError: If the wrapped content object does not define
                    ``attr``.
            """
            if self._is_non_omnipy_pydantic_model() and self._content_obj_hasattr(attr):
                self._validate_and_set_value(self.content)

            content_attr = self._getattr_from_content_obj(attr)

            if inspect.isroutine(content_attr):
                method_info = self.__class__._get_special_methods_info_dict().get(attr)
                is_read_only_method = (
                    method_info and not method_info.state_changing
                    or attr in ('items', 'values', 'keys'))

                if not is_read_only_method:
                    reset_solution = \
                        self._prepare_reset_solution_take_snapshot_if_needed().reset_solution
                    new_content_attr: Callable = cast(Callable,
                                                      self._getattr_from_content_obj(attr))

                    def _validate_content(ret: Any):
                        self._validate_and_set_value(self.content, reset_solution=reset_solution)
                        return self._convert_to_model_if_reasonable(
                            ret,
                            level_up=False,
                            raise_validation_errors=False,
                        )

                    content_attr = add_callback_after_call(new_content_attr,
                                                           _validate_content,
                                                           reset_solution)

            if attr in ('values', 'items'):
                match attr:
                    case 'values':
                        _model_generator = self._get_convert_full_element_model_generator(())
                    case 'items':
                        _model_generator = self._get_convert_element_value_model_generator(())

                content_attr = add_callback_after_call(
                    cast(Callable, content_attr),
                    _model_generator,
                    no_context,
                )

            return content_attr

    def _is_non_omnipy_pydantic_model(self) -> bool:
        return is_non_omnipy_pydantic_model(self.content)

    def _content_obj_hasattr(self, attr) -> object:
        return hasattr(self.content, attr)

    def _getattr_from_content_obj(self, attr) -> object:
        return getattr(self.content, attr)

    def _getattr_from_content_cls(self, attr) -> object:
        return getattr(self.content.__class__, attr)

    # def _get_real_content(self) -> object:
    #     if is_model_instance(self.content):
    #         return self.content.content
    #     else:
    #         return self.content

    def __eq__(self, other: object) -> bool:
        """Compare two models by concrete class and wrapped content.

        Args:
            other: Object to compare with this model.

        Returns:
            ``True`` when ``other`` is the same concrete model class and its
            content compares equal.
        """
        if is_model_instance(other):
            return (self.__class__ == other.__class__ and all_equals(self.content, other.content))
            # and self.to_data() == other.to_data()  # last line is just in case
        else:
            return False

    def __bool__(self):
        if self.content:
            return True
        else:
            return False

    def __call__(self, *args: object, **kwargs: object) -> object:
        if not self._content_obj_hasattr('__call__'):
            raise TypeError(f"'{self.__class__.__name__}' object is not callable")
        return self._special_method(
            '__call__',
            MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
            *args,
            **kwargs)

    def __repr_args__(self):
        """Provide the root value to pydantic's representation machinery.

        Returns:
            Representation arguments describing the wrapped content.
        """
        return [(None, self.content)]


def prepare_value_for_validation_if_dataset_or_model(value: object,) -> tuple[bool, object]:
    if is_dataset_instance(value):
        return True, value.to_data()
    if is_model_instance(value):
        return True, value.to_data()
    elif is_non_omnipy_pydantic_model(value):
        return True, cast(pyd.BaseModel, value).dict(by_alias=True)
    return False, value


def is_model_instance(__obj: object) -> 'TypeIs[Model]':
    """Check whether an object is an Omnipy model instance.

    Args:
        __obj: Object to test.

    Returns:
        ``True`` when ``__obj`` is an instance of :class:`Model`.
    """
    return lenient_isinstance(__obj, Model) \
        and not is_none_type(__obj)  # Consequence of _ModelMetaclass hack


@functools.cache
def is_model_subclass(__cls: TypeForm) -> 'TypeIs[type[Model]]':
    """Check whether a type is an Omnipy model subclass.

    Args:
        __cls: Type expression to test.

    Returns:
        ``True`` when ``__cls`` is a subclass of :class:`Model`.
    """
    return lenient_issubclass(__cls, Model) \
        and not is_none_type(__cls)  # Consequence of _ModelMetaclass hack


def obj_or_model_content_isinstance(
    __obj: object,
    __class_or_tuple: type[_ClassOrTupleT] | tuple[type[_ClassOrTupleT], ...],
) -> TypeIs[_ClassOrTupleT]:
    """Check a plain object or a model's content against a target type.

    Args:
        __obj: Plain object or model instance to inspect.
        __class_or_tuple: Accepted type or tuple of accepted types.

    Returns:
        ``True`` when ``__obj`` itself, or ``__obj.content`` for a model,
        matches ``__class_or_tuple``.
    """
    return isinstance(__obj.content if is_model_instance(__obj) else __obj, __class_or_tuple)


def is_pure_pydantic_model(obj: object):
    """Check whether an object is a direct ``pydantic.BaseModel`` subclass instance.

    Args:
        obj: Object to test.

    Returns:
        ``True`` when the object's immediate base class is exactly
        ``pydantic.BaseModel``.
    """
    return type(obj).__bases__ == (pyd.BaseModel,)


def is_non_omnipy_pydantic_model(obj: object):
    """Check whether an object is a pydantic model outside Omnipy's wrappers.

    Args:
        obj: Object to test.

    Returns:
        ``True`` when ``obj`` is a pydantic or generic pydantic model instance
        that is neither an Omnipy :class:`Model` nor an Omnipy
        :class:`~omnipy.data.dataset.Dataset`.
    """
    mro = type(obj).__mro__
    return mro[0] != pyd.BaseModel \
        and (pyd.BaseModel in mro or pyd.GenericModel in mro) \
        and Model not in mro \
        and Dataset not in mro


# TODO: Remove parse_none_according_to_model after upgrade to pydantic v2


# Partial workaround of https://github.com/pydantic/pydantic/issues/3836 and similar bugs,
# together with hacks setting allow_none=True (_ModelMetaclass and _recursively_set_allow_none).
# See series of relevant tests in test_model.py starting with  test_list_of_none_variants().
def parse_none_according_to_model(value, root_model):  # IsModel
    """Convert ``None`` values according to a model's nested type rules.

    This helper works around pydantic v1 limitations around nested ``None``
    handling. It walks the declared model type and injects ``None`` or nested
    model wrappers where Omnipy's type semantics allow them.

    Args:
        value: Candidate value that may contain ``None`` entries.
        root_model: Model class whose root type should govern the conversion.

    Returns:
        The original value or a transformed structure with ``None`` values
        normalized according to ``root_model``.

    Raises:
        OmnipyNoneIsNotAllowedError: If ``None`` appears where the model type
            does not allow it.
    """
    outer_type = root_model.outer_type(with_args=True)
    plain_outer_type = root_model.outer_type(with_args=False)
    outer_args = get_args(outer_type)

    if is_model_subclass(outer_type):
        return _parse_none_in_model(outer_type, value)

    if root_model.is_nested_type():
        inner_val_type = root_model.inner_type(with_args=True)

        # Mutable sequences or variable tuples
        if _outer_type_and_value_are_of_types(plain_outer_type, value, (MutableSequence, tuple)):
            return _parse_none_in_mutable_sequence_or_tuple(plain_outer_type, inner_val_type, value)

        # Mappings
        if _outer_type_and_value_are_of_types(plain_outer_type, value, Mapping) and outer_args:
            return _parse_none_in_mapping(plain_outer_type, outer_args, inner_val_type, value)

        if lenient_isinstance(outer_type, TypeVar):
            return _parse_none_in_typevar(inner_val_type)

        if value is None:
            raise OmnipyNoneIsNotAllowedError()

    else:
        union_variants = _split_outer_type_to_union_variants(outer_args)
        flattened_union_variants = _flatten_two_level_tuple(union_variants)

        if any(is_model_subclass(tp_) or _supports_none(tp_) for tp_ in flattened_union_variants):

            # Fixed tuples
            if _outer_type_and_value_are_of_types(plain_outer_type, value, tuple) and outer_args:
                return _parse_none_in_fixed_tuple(plain_outer_type, union_variants, value)

            # Unions
            if is_union(plain_outer_type):
                return _parse_none_in_union(flattened_union_variants, value)

    return value


def _parse_none_in_model(outer_type, value):
    # Not exactly sure which is the best solution. Both seem to work. The latter option should be
    # more general, but potentially slower
    #
    # return outer_type(value) if value is None else value

    return outer_type(value) if type(value) is not outer_type else value


def _split_outer_type_to_union_variants(outer_type_args):
    return tuple(split_to_union_variants(_) for _ in outer_type_args)


def _flatten_two_level_tuple(two_level_tuple):
    return tuple(el for first_level_tuple in two_level_tuple for el in first_level_tuple)


def _supports_none(type_: TypeForm) -> bool:
    return is_none_type(type_) or is_optional(type_) or type_ in (object, Any)


def _outer_type_and_value_are_of_types(plain_outer_type, value, *types):
    return any(
        lenient_issubclass(plain_outer_type, type_) and lenient_isinstance(value, type_)
        for type_ in types)


def _parse_none_in_mutable_sequence_or_tuple(plain_outer_type, inner_val_type, value):
    inner_val_union_types = split_to_union_variants(inner_val_type)

    if any(is_model_subclass(_) or _supports_none(_) for _ in inner_val_union_types):
        return plain_outer_type(
            _parse_none_in_types(inner_val_union_types) if val is None else val for val in value)
    return value


def _parse_none_in_mapping(plain_outer_type, outer_type_args, inner_val_type, value):
    inner_val_union_types = split_to_union_variants(inner_val_type)

    inner_key_type = outer_type_args[0] if lenient_issubclass(
        plain_outer_type, Mapping) and outer_type_args else Undefined
    inner_key_union_types = split_to_union_variants(inner_key_type)

    if any(
            is_model_subclass(_) or _supports_none(_)
            for _ in chain(inner_key_union_types, inner_val_union_types)):
        return plain_outer_type({
            _parse_none_in_types(inner_key_union_types) if key is None else key:
                _parse_none_in_types(inner_val_union_types) if val is None else val
            for key, val in value.items()
        })
    return value


def _parse_none_in_typevar(inner_val_type):
    inner_val_union_types = split_to_union_variants(inner_val_type)

    return _parse_none_in_types(inner_val_union_types)


def _parse_none_in_fixed_tuple(plain_outer_type, tuple_of_union_variant_types, value):
    return plain_outer_type(
        _parse_none_in_types(tuple_of_union_variant_types[i]) if val is None else val
        for i, val in enumerate(value))


def _parse_none_in_union(flattened_union_variant_types, value):
    if value is None:
        return _parse_none_in_types(flattened_union_variant_types)
    else:
        return value


def _parse_none_in_types(inner_union_types: tuple[TypeForm]) -> object:
    for type_ in inner_union_types:
        if is_model_subclass(type_):
            model = type_
            return model(parse_none_according_to_model(None, model))
        elif _supports_none(type_):
            return None
    raise OmnipyNoneIsNotAllowedError()
