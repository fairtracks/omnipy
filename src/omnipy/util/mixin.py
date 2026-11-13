"""Dynamic mixin composition utilities for runtime-generated subclasses.

This module lets selected classes accept mixins after definition time. It keeps
constructor signatures in sync with accepted mixins and creates runtime
subclasses that combine the original class with the requested mixin bases.
"""

from collections import defaultdict
from collections.abc import Callable, Mapping
import inspect
import types
from typing import Self

from typing_extensions import get_original_bases

from omnipy.util.helpers import generic_aware_issubclass_ignore_args, transfer_generic_args_to_cls

WITH_MIXINS_CLS_SUFFIX = 'WithMixins'


def strip_mixins_suffix(cls_name: str) -> str:
    """Remove the generated mixin subclass suffix from a class name.

    Args:
        cls_name: Class name to normalize.

    Returns:
        The original class name when the generated suffix is present, otherwise
        ``cls_name`` unchanged.
    """
    if cls_name.endswith(WITH_MIXINS_CLS_SUFFIX):
        return cls_name[: -len(WITH_MIXINS_CLS_SUFFIX)]

    return cls_name


RECEIVES_UNCLAIMED_KWARGS_ATTR = '_receives_unclaimed_kwargs'
"""Class attribute marking a mixin whose ``__init__`` receives the unclaimed keyword arguments.

Such a mixin declares ``__init__(self, **kwargs)`` and gets the keyword arguments that neither the
original class nor any other mixin declares. Without such a mixin, they are ignored.
"""


class DynamicMixinAcceptor:
    """Base class for classes that accept mixins dynamically.

    Subclasses register mixin classes through :meth:`accept_mixin`, after which
    instance creation returns a generated subclass inheriting from both the
    original class and its accepted mixins.

    A mixin can be accepted as optional. An optional mixin is only added to an instance when
    one of its keyword arguments is given with a value other than its default, or when its
    activation function returns ``True`` at instance creation.
    """

    # Declarations needed by mypy
    _orig_class: type
    _orig_init_signature: inspect.Signature
    _mixin_classes: list[type]
    _optional_mixins: dict[type, Callable[[], bool] | None]
    _init_params_per_mixin_cls: defaultdict[type, defaultdict[str, inspect.Parameter]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if DynamicMixinAcceptor in get_original_bases(cls) and cls.__init__ is object.__init__:
            raise TypeError(
                'Dynamic mixin acceptor class is required to define a __init__() method.'
            )

        cls._orig_init_signature = inspect.signature(cls.__init__)
        cls._mixin_classes = []
        cls._optional_mixins = {}
        cls._init_params_per_mixin_cls = defaultdict(defaultdict)

    @classmethod
    def _get_mixin_init_kwarg_params(cls) -> dict[str, inspect.Parameter]:
        return {
            key: param
            for param_dict in cls._init_params_per_mixin_cls.values()
            for key, param in param_dict.items()
        }

    @property
    def _mixin_init_kwarg_params(self) -> dict[str, inspect.Parameter]:
        return self._get_mixin_init_kwarg_params()

    @classmethod
    def _get_mixin_init_kwarg_params_including_bases(cls) -> dict[str, inspect.Parameter]:
        all_mixin_init_kwarg_params: dict[str, inspect.Parameter] = {}

        base_list = list(cls.__mro__)
        skip_bases = {'DynamicMixinAcceptor'}

        for base in base_list:
            if base.__name__.endswith(WITH_MIXINS_CLS_SUFFIX):
                skip_bases.add(base.__name__[: -len(WITH_MIXINS_CLS_SUFFIX)])

        cleaned_base_list = [
            base
            for base in base_list
            if issubclass(base, DynamicMixinAcceptor) and base.__name__ not in skip_bases
        ]

        for base in cleaned_base_list:
            all_mixin_init_kwarg_params |= dict(base._get_mixin_init_kwarg_params().items())

        return all_mixin_init_kwarg_params

    @property
    def _mixin_init_kwarg_params_including_bases(self) -> dict[str, inspect.Parameter]:
        return self._get_mixin_init_kwarg_params_including_bases()

    @property
    def _optional_mixin_init_kwarg_params_including_bases(self) -> dict[str, inspect.Parameter]:
        """Keyword parameters of the optional mixins of this object, by name."""
        optional_params: dict[str, inspect.Parameter] = {}
        for base in type(self).__mro__:
            if issubclass(base, DynamicMixinAcceptor) and '_optional_mixins' in base.__dict__:
                for mixin_cls in base._optional_mixins:
                    optional_params |= base._init_params_per_mixin_cls.get(mixin_cls, {})
        return optional_params

    @classmethod
    def accept_mixin(
        cls,
        mixin_cls: type,
        *,
        optional: bool = False,
        activate_if: Callable[[], bool] | None = None,
    ) -> None:
        """Register a mixin class for dynamic composition.

        Args:
            mixin_cls: Mixin class whose ``__init__`` keyword-only parameters
                should be merged into the acceptor signature.
            optional: If ``True``, the mixin is only added to instances created with one of its
                keyword arguments set to a value other than its default, or when
                ``activate_if`` returns ``True``.
            activate_if: For optional mixins, a function called at instance creation that
                activates the mixin when it returns ``True``.
        """
        if optional:
            cls._optional_mixins[mixin_cls] = activate_if
        cls._accept_mixin(mixin_cls, update=True)

    @classmethod
    def _accept_mixin(cls, mixin_cls: type, update: bool):
        cls._mixin_classes.append(mixin_cls)

        if '__init__' in mixin_cls.__dict__:
            cls._store_init_signature_params_for_mixin(mixin_cls)

            if update:
                cls._update_cls_init_signature_with_kwargs_all_mixin_kwargs()

    @classmethod
    def _store_init_signature_params_for_mixin(cls, mixin_cls):
        for key, param in inspect.signature(mixin_cls.__init__).parameters.items():
            if key != 'self':
                if param.kind not in (param.KEYWORD_ONLY, param.VAR_KEYWORD):
                    raise AttributeError(
                        'All params in the signature of the __init__() method in a dynamic '
                        'mixin class must be keyword-only or var-keyword '
                        f'(except for the "self" param). Failing param: {param.name}'
                    )
                if param.kind == param.KEYWORD_ONLY:
                    cls._init_params_per_mixin_cls[mixin_cls][key] = param

    @classmethod
    def _update_cls_init_signature_with_kwargs_all_mixin_kwargs(cls):
        updated_init_signature = cls._get_updated_cls_init_signature_with_all_mixin_kwargs()

        cls.__init__.__signature__ = updated_init_signature
        if hasattr(cls, '_orig_class'):
            cls._orig_class.__init____signature__ = updated_init_signature

    @classmethod
    def _get_updated_cls_init_signature_with_all_mixin_kwargs(cls):
        orig_init_param_dict = cls._orig_init_signature.parameters
        init_params = list(orig_init_param_dict.values())
        opt_var_keyword_param = []

        if init_params[-1].kind == inspect.Parameter.VAR_KEYWORD:
            opt_var_keyword_param = [init_params[-1]]
            init_params = init_params[:-1]

        only_mixin_params = [
            val
            for (key, val) in cls._get_mixin_init_kwarg_params_including_bases().items()
            if key not in orig_init_param_dict
        ]

        updated_params = init_params + only_mixin_params + opt_var_keyword_param
        return cls._orig_init_signature.replace(parameters=updated_params)

    @classmethod
    def reset_mixins(cls):
        """Clear all accepted mixins and restore the original init signature."""
        cls._mixin_classes.clear()
        cls._optional_mixins.clear()
        cls._init_params_per_mixin_cls.clear()
        cls.__init__.__signature__ = cls._orig_init_signature

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls.__name__.endswith(WITH_MIXINS_CLS_SUFFIX):
            cls_with_mixins = cls._create_subcls_inheriting_from_mixins_and_orig_cls(kwargs)
            obj = super(cls, cls_with_mixins).__new__(cls_with_mixins, *args, **kwargs)

        else:
            obj = object.__new__(cls)

        cls._update_cls_init_signature_with_kwargs_all_mixin_kwargs()
        return obj

    @classmethod
    def _is_mixin_active(cls, mixin_cls: type, kwargs: Mapping[str, object]) -> bool:
        if mixin_cls not in cls._optional_mixins:
            return True

        activate_if = cls._optional_mixins[mixin_cls]
        if activate_if is not None and activate_if():
            return True

        for key, param in cls._init_params_per_mixin_cls.get(mixin_cls, {}).items():
            if key in kwargs and (param.default is param.empty or kwargs[key] != param.default):
                return True
        return False

    @classmethod
    def _create_subcls_inheriting_from_mixins_and_orig_cls(  # noqa: C901
        cls, kwargs: Mapping[str, object] | None = None
    ) -> type[Self]:

        # TODO: Refactor this, and possibly elsewhere in class

        if kwargs is None:
            kwargs = {}

        active_mixin_classes = [
            mixin_cls for mixin_cls in cls._mixin_classes if cls._is_mixin_active(mixin_cls, kwargs)
        ]

        def __init__(self, *args, **kwargs):  # noqa: C901
            # print(f'__init__ for obj of class: {self.__class__.__name__}')
            cls.__init__(self, *args, **kwargs)
            mixin_kwargs_defaults = {}

            # Keyword arguments declared by the original class or by any accepted mixin, active or
            # not. The rest is passed to a mixin marked to receive unclaimed keyword arguments.
            claimed_keys = {
                key
                for key, param in inspect.signature(cls.__init__).parameters.items()
                if param.kind not in (param.VAR_KEYWORD, param.VAR_POSITIONAL)
            }
            unclaimed_kwargs = {key: val for key, val in kwargs.items() if key not in claimed_keys}

            for base in cls_with_mixins.__mro__:
                if (
                    base == cls
                    or base.__name__.endswith(WITH_MIXINS_CLS_SUFFIX)
                    or base.__init__ is object.__init__
                ):
                    continue

                if base.__dict__.get(RECEIVES_UNCLAIMED_KWARGS_ATTR, False):
                    base.__init__(self, **unclaimed_kwargs)
                    continue

                mixin_kwargs = {}
                contains_positional = False

                for key, param in inspect.signature(base.__init__).parameters.items():
                    if key != 'self':
                        if param.kind == param.KEYWORD_ONLY:
                            if key in kwargs:
                                mixin_kwargs[key] = kwargs[key]
                            elif key in mixin_kwargs_defaults:
                                mixin_kwargs[key] = mixin_kwargs_defaults[key]
                            else:
                                mixin_kwargs_defaults[key] = param.default
                        elif param.kind in (
                            param.POSITIONAL_ONLY,
                            param.POSITIONAL_OR_KEYWORD,
                            param.VAR_POSITIONAL,
                        ):
                            contains_positional = True

                if contains_positional:
                    # print(f'Calling... {base.__name__}(args={args}, kwargs={mixin_kwargs})')
                    base.__init__(self, *args, **mixin_kwargs)
                else:
                    # print(f'Calling... {base.__name__}(kwargs={mixin_kwargs})')
                    base.__init__(self, **mixin_kwargs)

        cls_bases = list(get_original_bases(cls))
        if not cls.__name__.endswith(WITH_MIXINS_CLS_SUFFIX):
            cls_bases = active_mixin_classes + cls_bases

        cls_bases_with_mixins = []

        for cls_base in cls_bases:
            if cls._is_true_acceptor_subclass(cls_base):
                cls_new_base = cls_base._create_subcls_inheriting_from_mixins_and_orig_cls(kwargs)
                cls_base = transfer_generic_args_to_cls(cls_new_base, cls_base)

            cls_bases_with_mixins.append(cls_base)

        def fill_ns(ns):
            ns |= dict(__init__=__init__)
            return ns

        cls_with_mixins: type[Self] = types.new_class(
            f'{cls.__name__}{WITH_MIXINS_CLS_SUFFIX}',
            tuple([cls] + cls_bases_with_mixins),
            {},
            fill_ns,
        )
        cls_with_mixins.__module__ = cls.__module__

        cls_with_mixins._orig_class = cls
        cls_with_mixins._orig_init_signature = inspect.signature(cls.__init__)

        for mixin_cls in active_mixin_classes:
            cls_with_mixins._accept_mixin(mixin_cls, update=False)
            if mixin_cls in cls._optional_mixins:
                cls_with_mixins._optional_mixins[mixin_cls] = cls._optional_mixins[mixin_cls]

        return cls_with_mixins

    @staticmethod
    def _is_true_acceptor_subclass(cls):
        if cls == DynamicMixinAcceptor:
            return False
        return generic_aware_issubclass_ignore_args(cls, DynamicMixinAcceptor)
