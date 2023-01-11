from collections import defaultdict
import inspect
from typing import DefaultDict, Dict, List, Protocol, Type

from omnipy.util.helpers import create_merged_dict


class IsMixin(Protocol):
    def __init__(self, **kwargs: object) -> None:
        ...


class DynamicMixinAcceptorFactory(type):
    def __new__(mcs, name, bases, namespace):
        cls = type.__new__(mcs, name, bases, namespace)

        if name != 'DynamicMixinAcceptor':
            cls._init_cls_from_metaclass(bases)

        return cls


class DynamicMixinAcceptor(metaclass=DynamicMixinAcceptorFactory):
    # Constants
    WITH_MIXINS_CLS_PREFIX = 'WithMixins'

    # Declarations needed by mypy
    _orig_class: Type
    _orig_init_signature: inspect.Signature
    _mixin_classes: List[Type]
    _init_params_per_mixin_cls: DefaultDict[str, DefaultDict[str, inspect.Parameter]]

    @classmethod
    def _init_cls_from_metaclass(cls, bases):
        if any(base.__name__ == 'DynamicMixinAcceptor' for base in bases):
            if '__init__' not in cls.__dict__:
                raise TypeError('Mixin acceptor class is required to define a __init__() method.')

        cls._orig_init_signature = inspect.signature(cls.__init__)
        cls._mixin_classes = []
        cls._init_params_per_mixin_cls = defaultdict(defaultdict)

        for base in bases:
            if hasattr(base, '_mixin_classes'):
                for mixin_class in base._mixin_classes:
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
    def accept_mixin(cls, mixin_cls: Type) -> None:
        cls._mixin_classes.append(mixin_cls)

        if '__init__' in mixin_cls.__dict__:
            cls._store_init_signature_params_for_mixin(mixin_cls)
            cls._update_cls_init_signature_with_kwargs_for_all_mixins()

    @classmethod
    def _store_init_signature_params_for_mixin(cls, mixin_cls):
        for key, param in inspect.signature(mixin_cls.__init__).parameters.items():
            if key != 'self':
                if param.kind != param.KEYWORD_ONLY:
                    raise AttributeError(
                        'All params in the signature of the __init__() method in a dynamic '
                        'mixin class must be keyword-only (except for the "self" param)')
                cls._init_params_per_mixin_cls[mixin_cls.__name__][key] = param

    @classmethod
    def _update_cls_init_signature_with_kwargs_for_all_mixins(cls):
        orig_init_param_dict = cls._orig_init_signature.parameters

        init_params = list(orig_init_param_dict.values())
        if init_params[-1].kind != inspect.Parameter.VAR_KEYWORD:
            raise AttributeError('Mixin acceptor class is required to define a catch-all "kwargs"'
                                 ' parameter as the last parameter of its __init__() method.')

        var_keyword_param = init_params[-1]
        init_params = init_params[:-1]
        only_mixin_params = [
            val for (key, val) in cls._get_mixin_init_kwarg_params().items()
            if key not in orig_init_param_dict
        ]

        updated_params = init_params + only_mixin_params + [var_keyword_param]
        updated_init_signature = cls._orig_init_signature.replace(parameters=updated_params)

        cls.__init__.__signature__ = updated_init_signature

    def __new__(cls, *args, **kwargs):
        if not cls.__name__.endswith(cls.WITH_MIXINS_CLS_PREFIX):
            cls_with_mixins = cls._create_subcls_inheriting_from_mixins_and_orig_cls()
            return object.__new__(cls_with_mixins)
        else:
            return object.__new__(cls)

    @classmethod
    def _create_subcls_inheriting_from_mixins_and_orig_cls(cls):
        def _initialize_mixins(self, kwargs):
            for mixin_cls in self._mixin_classes:
                mixin_kwargs = {}

                for key, param in self._init_params_per_mixin_cls[mixin_cls.__name__].items():
                    if key in kwargs:
                        mixin_kwargs[key] = kwargs[key]

                mixin_cls.__init__(self, **mixin_kwargs)

        def _check_mixin_kwarg_defaults_and_return_if_not_in_kwargs(self, kwargs):
            orig_init_param_dict = cls._orig_init_signature.parameters

            kwarg_new_param_default = {}
            kwarg_new_param_default_mixin_name = {}

            for mixin_cls in self._mixin_classes:
                for key, param in self._init_params_per_mixin_cls[mixin_cls.__name__].items():
                    if param.default is not param.empty:
                        if key in orig_init_param_dict and \
                                param.default != orig_init_param_dict[key].default:
                            raise AttributeError(
                                f'Default value for keyword argument "{key}" differs between '
                                f'__init__() methods of mixin class "{mixin_cls.__name__}" '
                                f'and original class "{self._orig_class.__name__}": '
                                f'{param.default} != {orig_init_param_dict[key].default}')
                        elif key in kwarg_new_param_default and \
                                param.default != kwarg_new_param_default[key]:
                            raise AttributeError(
                                f'Default value for keyword argument "{key}" differs between '
                                f'__init__() methods of mixin classes "{mixin_cls.__name__}" and'
                                f'"{kwarg_new_param_default_mixin_name[key]}": '
                                f'{param.default} != {kwarg_new_param_default[key]}')
                        else:
                            kwarg_new_param_default[key] = param.default
                            kwarg_new_param_default_mixin_name[key] = mixin_cls.__name__

            return {
                key: param_default for key,
                param_default in kwarg_new_param_default.items() if key not in kwargs
            }

        def __init__(self, *args, **kwargs):
            mixin_kwargs_defaults = \
                _check_mixin_kwarg_defaults_and_return_if_not_in_kwargs(self, kwargs)

            self._orig_class.__init__(self,
                                      *args,
                                      **create_merged_dict(kwargs, mixin_kwargs_defaults))
            _initialize_mixins(self, kwargs)

        cls_with_mixins = DynamicMixinAcceptorFactory(
            f'{cls.__name__}{cls.WITH_MIXINS_CLS_PREFIX}',
            tuple(list(reversed(cls._mixin_classes)) + [cls]),
            dict(__init__=__init__),
        )

        cls_with_mixins._orig_class = cls
        cls_with_mixins._orig_init_signature = inspect.signature(cls.__init__)

        cls_with_mixins._update_cls_init_signature_with_kwargs_for_all_mixins()  # noqa

        return cls_with_mixins
