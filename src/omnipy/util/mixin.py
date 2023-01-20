import types
from collections import defaultdict
import inspect
from typing import Any, cast, DefaultDict, Dict, List, Protocol, Tuple, Type

from omnipy.util.helpers import transfer_generic_args_to_cls, generic_aware_issubclass, get_bases


class IsMixin(Protocol):
    def __init__(self, **kwargs: object) -> None:
        ...


class DynamicMixinAcceptorMeta(type):
    def __new__(mcs: Type['DynamicMixinAcceptorMeta'],
                name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any]) -> Type['DynamicMixinAcceptor']:
        try:
            cls: type = type.__new__(mcs, name, bases, namespace)
        except TypeError:

            def fill_ns(ns):
                ns |= namespace
                return ns

            cls = types.new_class(
                name,
                bases,
                {},
                fill_ns,
            )

        cls = cast(Type['DynamicMixinAcceptor'], cls)
        if name != 'DynamicMixinAcceptor':
            cls._init_cls_from_metaclass(bases)

        return cls


class DynamicMixinAcceptor(metaclass=DynamicMixinAcceptorMeta):
    # Constants
    WITH_MIXINS_CLS_PREFIX = 'WithMixins'

    # Declarations needed by mypy
    _orig_class: Type
    _orig_init_signature: inspect.Signature
    _mixin_classes: List[Type]
    _init_params_per_mixin_cls: DefaultDict[str, DefaultDict[str, inspect.Parameter]]

    def __class_getitem__(cls, item):
        # if not cls.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX):
        #     cls_with_mixins = cls._create_subcls_inheriting_from_mixins_and_orig_cls()
        #     obj = super(cls, cls_with_mixins).__class_getitem__(item)
        # else:
        #     obj = super().__class_getitem__(item)
        #
        # cls._update_cls_init_signature_with_kwargs_for_all_mixins()
        return super().__class_getitem__(item)

    @classmethod
    def _init_cls_from_metaclass(
        cls,
        bases: Tuple[type, ...],
    ) -> None:
        if DynamicMixinAcceptor in get_bases(cls) and not hasattr(cls, '__init__'):
            raise TypeError('Mixin acceptor class is required to define a __init__() method.')

        cls._orig_init_signature = inspect.signature(cls.__init__)
        cls._mixin_classes = []
        cls._init_params_per_mixin_cls = defaultdict(defaultdict)

        # cls._copy_mixin_classes_from_bases(bases)

    @classmethod
    def _copy_mixin_classes_from_bases(cls, bases: Tuple[type, ...]) -> None:
        for base in bases:
            if issubclass(base, DynamicMixinAcceptor) \
                    and base != DynamicMixinAcceptor \
                    and not base.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX):
                cls._copy_mixin_classes_from_mixin_acceptor_base(base)

    @classmethod
    def _copy_mixin_classes_from_mixin_acceptor_base(
        cls,
        base: Type['DynamicMixinAcceptor'],
    ) -> None:
        for mixin_class in base._mixin_classes:
            cls._copy_mixin_class_from_mixin_acceptor_base(base, mixin_class)

    @classmethod
    def _copy_mixin_class_from_mixin_acceptor_base(
        cls,
        base: Type['DynamicMixinAcceptor'],
        mixin_class: Type,
    ) -> None:
        if mixin_class.__name__ not in cls._init_params_per_mixin_cls:
            cls._mixin_classes.append(mixin_class)
            cls._init_params_per_mixin_cls[mixin_class.__name__] = \
                base._init_params_per_mixin_cls[mixin_class.__name__]

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
    def _get_mixin_init_kwarg_params_with_all_bases(cls) -> Dict[str, inspect.Parameter]:
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
    def _mixin_init_kwarg_params_with_all_bases(self) -> Dict[str, inspect.Parameter]:
        return self._get_mixin_init_kwarg_params_with_all_bases()

    @classmethod
    def accept_mixin(cls, mixin_cls: Type) -> None:
        cls._accept_mixin(mixin_cls, update=True)

    @classmethod
    def _accept_mixin(cls, mixin_cls: Type, update: bool):
        cls._mixin_classes.append(mixin_cls)

        if '__init__' in mixin_cls.__dict__:
            cls._store_init_signature_params_for_mixin(mixin_cls)

            if update:
                cls._update_cls_init_signature_with_kwargs_for_all_mixins()

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
    def _update_cls_init_signature_with_kwargs_for_all_mixins(cls):
        orig_init_param_dict = cls._orig_init_signature.parameters

        init_params = list(orig_init_param_dict.values())
        opt_var_keyword_param = []

        if init_params[-1].kind == inspect.Parameter.VAR_KEYWORD:
            opt_var_keyword_param = [init_params[-1]]
            init_params = init_params[:-1]

        # if init_params[-1].kind != inspect.Parameter.VAR_KEYWORD:
        #     raise AttributeError('Mixin acceptor class is required to define a catch-all "kwargs"'
        #                          ' parameter as the last parameter of its __init__() method.')

        only_mixin_params = [
            val for (key, val) in cls._get_mixin_init_kwarg_params_with_all_bases().items()
            if key not in orig_init_param_dict
        ]

        updated_params = init_params + only_mixin_params + opt_var_keyword_param
        updated_init_signature = cls._orig_init_signature.replace(parameters=updated_params)

        cls.__init__.__signature__ = updated_init_signature
        if hasattr(cls, '_orig_class'):
            cls._orig_class.__init____signature__ = updated_init_signature

    @classmethod
    def reset_mixins(cls):
        cls._mixin_classes.clear()
        cls._init_params_per_mixin_cls.clear()
        cls.__init__.__signature__ = cls._orig_init_signature

    #
    # def __new__(cls, *args, **kwargs):
    #     if not cls.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX):
    #         cls_with_mixins = cls._create_subcls_inheriting_from_mixins_and_orig_cls()
    #         # obj = object.__new__(cls_with_mixins)
    #         return cls_with_mixins.__new__(cls_with_mixins, *args, **kwargs)
    #     else:
    #         return super().__new__(cls)

    def __new__(cls, *args, **kwargs):
        if not cls.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX):
            cls_with_mixins = cls._create_subcls_inheriting_from_mixins_and_orig_cls()
            obj = super(cls, cls_with_mixins).__new__(cls_with_mixins, *args, **kwargs)

        else:
            super_new = super().__new__
            if super_new is object.__new__:
                obj = super().__new__(cls)
            else:
                obj = super().__new__(cls, *args, **kwargs)

        cls._update_cls_init_signature_with_kwargs_for_all_mixins()
        return obj

    @classmethod
    def _create_subcls_inheriting_from_mixins_and_orig_cls(cls):
        def _initialize_mixins(self, **kwargs):
            mixin_kwargs_defaults = {}

            for mixin_cls in cls_with_mixins._mixin_classes:
                mixin_kwargs = {}

                mixin_cls_name = mixin_cls.__name__
                if mixin_cls_name.endswith(cls.WITH_MIXINS_CLS_PREFIX):
                    mixin_cls_name = mixin_cls._orig_class.__name__

                for key, param in cls._init_params_per_mixin_cls[mixin_cls_name].items():
                    if key in kwargs:
                        mixin_kwargs[key] = kwargs[key]
                    elif key in mixin_kwargs_defaults:
                        mixin_kwargs[key] = mixin_kwargs_defaults[key]
                    else:
                        mixin_kwargs[key] = param.default
                        mixin_kwargs_defaults[key] = param.default

                mixin_cls.__init__(self, **mixin_kwargs)

        # def _check_mixin_kwarg_defaults_and_return_if_not_in_kwargs(self, kwargs):
        #     orig_init_param_dict = cls._orig_init_signature.parameters
        #
        #     kwarg_new_param_default = {}
        #     kwarg_new_param_default_mixin_name = {}
        #
        #     for mixin_cls in cls._mixin_classes:
        #         for key, param in self._init_params_per_mixin_cls[mixin_cls.__name__].items():
        #             if param.default is not param.empty:
        #                 # if key in orig_init_param_dict and \
        #                 #         param.default != orig_init_param_dict[key].default:
        #                 #     raise AttributeError(
        #                 #         f'Default value for keyword argument "{key}" differs between '
        #                 #         f'__init__() methods of mixin class "{mixin_cls.__name__}" '
        #                 #         f'and original class "{self._orig_class.__name__}": '
        #                 #         f'{param.default} != {orig_init_param_dict[key].default}')
        #                 # elif key in kwarg_new_param_default and \
        #                 #         param.default != kwarg_new_param_default[key]:
        #                 #     raise AttributeError(
        #                 #         f'Default value for keyword argument "{key}" differs between '
        #                 #         f'__init__() methods of mixin classes "{mixin_cls.__name__}" and'
        #                 #         f'"{kwarg_new_param_default_mixin_name[key]}": '
        #                 #         f'{param.default} != {kwarg_new_param_default[key]}')
        #                 # else:
        #                 kwarg_new_param_default[key] = param.default
        #                 kwarg_new_param_default_mixin_name[key] = mixin_cls.__name__
        #
        #     return {
        #         key: param_default for key,
        #         param_default in kwarg_new_param_default.items() if key not in kwargs
        #     }
        # def __init__(self, *args, **kwargs):
        #     cls.__init__(self, *args, **kwargs)
        #     mixin_kwargs_defaults = {}
        #
        #     all_mixin_classes = {}
        #     all_std_mro_classes = []
        #
        #     all_mro_classes = cls_with_mixins.__mro__
        #     for mro_cls in all_mro_classes:
        #         if hasattr(mro_cls, '_mixin_classes'):
        #             for mixin_cls in mro_cls._mixin_classes:
        #                 all_mixin_classes[mixin_cls.__name__] = mixin_cls
        #
        #     for mro_cls in all_mro_classes:
        #         if mro_cls.__name__ not in all_mixin_classes \
        #                 and mro_cls != cls \
        #                 and not mro_cls.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX) \
        #                 and mro_cls.__init__ is not object.__init__:
        #             all_std_mro_classes.append(mro_cls)
        #
        #     for mixin_cls in all_mixin_classes.values():
        #         if '__init__' in mixin_cls.__dict__:
        #             mixin_kwargs = {}
        #
        #             for key, param in inspect.signature(mixin_cls.__init__).parameters.items():
        #                 if key != 'self':
        #                     if param.kind == param.KEYWORD_ONLY:
        #                         if key in kwargs:
        #                             mixin_kwargs[key] = kwargs[key]
        #                         elif key in mixin_kwargs_defaults:
        #                             mixin_kwargs[key] = mixin_kwargs_defaults[key]
        #                         else:
        #                             mixin_kwargs_defaults[key] = param.default
        #
        #             mixin_cls.__init__(self, **mixin_kwargs)
        #
        #     for std_mro_class in all_std_mro_classes:
        #         std_mro_class.__init__(self, *args, **kwargs)

        def __init__(self, *args, **kwargs):
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
        mixin_classes = []

        for cls_base in cls_bases:
            # if cls_base in cls._mixin_classes:

            if cls._is_true_acceptor_subclass(cls_base):
                cls_new_base = cls_base._create_subcls_inheriting_from_mixins_and_orig_cls()
                cls_base = transfer_generic_args_to_cls(cls_new_base, cls_base)
            # mixin_classes.append(cls_base)

            cls_bases_with_mixins.append(cls_base)

            # if cls_base.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX):
            #     mixin_classes.append(cls_base)

        # cls_generic_params: Tuple = get_parameters(cls)

        cls_with_mixins = DynamicMixinAcceptorMeta(
            f'{cls.__name__}{cls.WITH_MIXINS_CLS_PREFIX}',
            tuple([cls] + cls_bases_with_mixins),
            dict(__init__=__init__),
        )

        cls_with_mixins._orig_class = cls
        cls_with_mixins._orig_init_signature = inspect.signature(cls.__init__)

        for mixin_cls in cls._mixin_classes:
            cls_with_mixins._accept_mixin(mixin_cls, update=False)

        # cls_with_mixins._update_cls_init_signature_with_kwargs_for_all_mixins()  # noqa

        return cls_with_mixins

    @staticmethod
    def _is_true_acceptor_subclass(cls):
        if cls == DynamicMixinAcceptor:
            return False
        return generic_aware_issubclass(cls, DynamicMixinAcceptor)
