from collections import defaultdict
import inspect
import types
from typing import DefaultDict, Dict, List, Protocol, Type

from omnipy.util.helpers import (generic_aware_issubclass_ignore_args,
                                 get_bases,
                                 transfer_generic_args_to_cls)


class IsMixin(Protocol):
    def __init__(self, **kwargs: object) -> None:
        ...


class DynamicMixinAcceptor:
    # Constants
    WITH_MIXINS_CLS_PREFIX = 'WithMixins'

    # Declarations needed by mypy
    _orig_class: Type
    _orig_init_signature: inspect.Signature
    _mixin_classes: List[Type]
    _init_params_per_mixin_cls: DefaultDict[str, DefaultDict[str, inspect.Parameter]]

    def __class_getitem__(cls, item):
        return super().__class_getitem__(item)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if DynamicMixinAcceptor in get_bases(cls) and cls.__init__ is object.__init__:
            raise TypeError(
                'Dynamic mixin acceptor class is required to define a __init__() method.')

        cls._orig_init_signature = inspect.signature(cls.__init__)
        cls._mixin_classes = []
        cls._init_params_per_mixin_cls = defaultdict(defaultdict)

    @classmethod
    def _get_mixin_init_kwarg_params(cls) -> Dict[str, inspect.Parameter]:
        return {
            key: param for param_dict in cls._init_params_per_mixin_cls.values() for key,
            param in param_dict.items()
        }

    @property
    def _mixin_init_kwarg_params(self) -> Dict[str, inspect.Parameter]:
        return self._get_mixin_init_kwarg_params()

    @classmethod
    def _get_mixin_init_kwarg_params_including_bases(cls) -> Dict[str, inspect.Parameter]:
        all_mixin_init_kwarg_params: Dict[str, inspect.Parameter] = {}

        base_list = list(cls.__mro__)
        skip_bases = {'DynamicMixinAcceptor'}

        for base in base_list:
            if base.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX):
                skip_bases.add(base.__name__[:-len(cls.WITH_MIXINS_CLS_PREFIX)])

        cleaned_base_list = [
            base for base in base_list
            if issubclass(base, DynamicMixinAcceptor) and base.__name__ not in skip_bases
        ]

        for base in cleaned_base_list:
            all_mixin_init_kwarg_params |= dict(base._get_mixin_init_kwarg_params().items())

        return all_mixin_init_kwarg_params

    @property
    def _mixin_init_kwarg_params_including_bases(self) -> Dict[str, inspect.Parameter]:
        return self._get_mixin_init_kwarg_params_including_bases()

    @classmethod
    def accept_mixin(cls, mixin_cls: Type) -> None:
        cls._accept_mixin(mixin_cls, update=True)

    @classmethod
    def _accept_mixin(cls, mixin_cls: Type, update: bool):
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
                        '(except for the "self" param)')
                if param.kind == param.KEYWORD_ONLY:
                    cls._init_params_per_mixin_cls[mixin_cls.__name__][key] = param

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
            val for (key, val) in cls._get_mixin_init_kwarg_params_including_bases().items()
            if key not in orig_init_param_dict
        ]

        updated_params = init_params + only_mixin_params + opt_var_keyword_param
        return cls._orig_init_signature.replace(parameters=updated_params)

    @classmethod
    def reset_mixins(cls):
        cls._mixin_classes.clear()
        cls._init_params_per_mixin_cls.clear()
        cls.__init__.__signature__ = cls._orig_init_signature

    def __new__(cls, *args, **kwargs):
        if not cls.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX):
            cls_with_mixins = cls._create_subcls_inheriting_from_mixins_and_orig_cls()
            obj = super(cls, cls_with_mixins).__new__(cls_with_mixins, *args, **kwargs)

        else:
            obj = object.__new__(cls)

        cls._update_cls_init_signature_with_kwargs_all_mixin_kwargs()
        return obj

    @classmethod
    def _create_subcls_inheriting_from_mixins_and_orig_cls(cls):

        # TODO: Refactor this, and possibly elsewhere in class

        def __init__(self, *args, **kwargs):
            # print(f'__init__ for obj of class: {self.__class__.__name__}')
            cls.__init__(self, *args, **kwargs)
            mixin_kwargs_defaults = {}

            for base in cls_with_mixins.__mro__:
                if base == cls \
                        or base.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX) \
                        or base.__init__ is object.__init__:
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
                        elif param.kind in (param.POSITIONAL_ONLY,
                                            param.POSITIONAL_OR_KEYWORD,
                                            param.VAR_POSITIONAL):
                            contains_positional = True

                if contains_positional:
                    # print(f'Calling... {base.__name__}(args={args}, kwargs={mixin_kwargs})')
                    base.__init__(self, *args, **mixin_kwargs)
                else:
                    # print(f'Calling... {base.__name__}(kwargs={mixin_kwargs})')
                    base.__init__(self, **mixin_kwargs)

        cls_bases = list(get_bases(cls))
        if not cls.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX):
            cls_bases = list(cls._mixin_classes) + cls_bases

        cls_bases_with_mixins = []

        for cls_base in cls_bases:

            if cls._is_true_acceptor_subclass(cls_base):
                cls_new_base = cls_base._create_subcls_inheriting_from_mixins_and_orig_cls()
                cls_base = transfer_generic_args_to_cls(cls_new_base, cls_base)

            cls_bases_with_mixins.append(cls_base)

        def fill_ns(ns):
            ns |= dict(__init__=__init__)
            return ns

        cls_with_mixins = types.new_class(
            f'{cls.__name__}{cls.WITH_MIXINS_CLS_PREFIX}',
            tuple([cls] + cls_bases_with_mixins),
            {},
            fill_ns,
        )
        cls_with_mixins.__module__ = cls.__module__

        cls_with_mixins._orig_class = cls
        cls_with_mixins._orig_init_signature = inspect.signature(cls.__init__)

        for mixin_cls in cls._mixin_classes:
            cls_with_mixins._accept_mixin(mixin_cls, update=False)

        return cls_with_mixins

    @staticmethod
    def _is_true_acceptor_subclass(cls):
        if cls == DynamicMixinAcceptor:
            return False
        return generic_aware_issubclass_ignore_args(cls, DynamicMixinAcceptor)
