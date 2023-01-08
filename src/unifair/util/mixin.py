from collections import defaultdict
import inspect
from typing import DefaultDict, Dict, List, Protocol, Type


class IsMixin(Protocol):
    def __init__(self, **kwargs: object) -> None:
        ...


class DynamicMixinAcceptorFactory(type):
    def __new__(mcs, name, bases, namespace):
        cls = type.__new__(mcs, name, bases, namespace)

        if any(base.__name__ == 'DynamicMixinAcceptor' for base in cls.__bases__):
            cls._init_cls_from_metaclass()

        return cls


class DynamicMixinAcceptor(metaclass=DynamicMixinAcceptorFactory):

    # Declarations needed by mypy
    _orig_class: Type
    _orig_init_signature: inspect.Signature
    _mixin_classes: List[Type]
    _init_params_per_mixin_cls: DefaultDict[str, DefaultDict[str, inspect.Parameter]]

    @classmethod
    def _init_cls_from_metaclass(cls):
        if '__init__' not in cls.__dict__:
            raise TypeError('Mixin acceptor class is required to define a __init__() method.')

        cls._orig_class = cls
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
    def accept_mixin(cls, mixin_cls: Type) -> None:
        # prepend for last mixin to potentially overwrite the others
        cls._mixin_classes.insert(0, mixin_cls)

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

    def __new__(cls, *outer_args, **outer_kwargs):
        cls_with_mixins = cls._create_subcls_inheriting_from_mixins_and_orig_cls()
        return object.__new__(cls_with_mixins)

    @classmethod
    def _create_subcls_inheriting_from_mixins_and_orig_cls(cls):
        def _initialize_mixin_and_update_kwargs_with_defaults(self, kwargs, mixin_cls):
            mixin_kwargs = {}

            for key, param in self._init_params_per_mixin_cls[mixin_cls.__name__].items():
                if key in kwargs:
                    mixin_kwargs[key] = kwargs[key]
                elif param.default:
                    kwargs[key] = param.default

            mixin_cls.__init__(self, **mixin_kwargs)

            return kwargs

        def __init__(self, *args, **kwargs):
            for mixin_cls in self._mixin_classes:
                kwargs = _initialize_mixin_and_update_kwargs_with_defaults(self, kwargs, mixin_cls)

            self._orig_class.__init__(self, *args, **kwargs)

        cls_with_mixins = DynamicMixinAcceptorFactory(
            f'{cls.__name__}WithMixins',
            tuple(list(cls._mixin_classes) + [cls]),
            dict(__init__=__init__),
        )
        cls_with_mixins._update_cls_init_signature_with_kwargs_for_all_mixins()  # noqa

        return cls_with_mixins
