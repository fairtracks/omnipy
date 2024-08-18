from dataclasses import dataclass
from typing import Any, Callable, cast, Generic, get_args, ParamSpec, Protocol

from typing_extensions import TypeVar

from omnipy import Model

ParamsT = TypeVar('ParamsT')
ParamsP = ParamSpec('ParamsP')


class Conf(Protocol[ParamsT]):
    settings: ParamsT


def conf(param_cls: Callable[ParamsP, ParamsT]) -> Callable[ParamsP, type[Conf[ParamsT]]]:
    def _conf(*args: ParamsP.args, **kwargs: ParamsP.kwargs) -> type[Conf[ParamsT]]:
        # Factory for new _Conf classes. Needed to allow the classes to have individual settings
        class _Conf(Conf[ParamsT]):
            settings = param_cls(**kwargs)

        return _Conf

    return _conf


class ParamModelMixin(Generic[ParamsT]):
    @dataclass
    class Params:
        ...

    @classmethod
    def _get_conf_settings(cls) -> ParamsT:
        conf_t = get_args(get_args(cls.full_type())[-1])[0]
        if isinstance(conf_t, TypeVar):
            conf_t = conf(cls.Params)()
        return conf_t.settings


ConfT = TypeVar('ConfT', bound=type[Conf])


class ConfHolder(Generic[ConfT]):
    def __init__(self, conf: ConfT) -> None:
        raise ValueError()


class MyModel(Model[int | ConfHolder[ConfT]], ParamModelMixin['MyModel.Params'], Generic[ConfT]):
    @dataclass
    class Params:
        add: int = 123

    @classmethod
    def _parse_data(cls, data: int) -> int:
        conf_settings = cls._get_conf_settings()
        # reveal_type(settings)
        # reveal_type(settings.add)
        return data + conf_settings.add


my_conf = conf(MyModel.Params)
print('my_conf = conf(MyModel.Params):', my_conf, type(my_conf))
# reveal_type(my_conf)

MyConf = my_conf(add=23)
print('MyConf = my_conf(add=23):', MyConf, type(MyConf))
# reveal_type(MyConf)

settings = MyConf.settings
print('settings = MyConf.settings:', settings, type(settings))
# reveal_type(settings)

add = MyConf.settings.add
print('add = MyConf.settings.add:', add, type(add))
# reveal_type(add)

aa: MyModel[my_conf(add=33)] = MyModel[my_conf(add=33)](123)
print('MyModel[my_conf(add=33)](123):', aa, type(aa))
# reveal_type(aa)

MyNewConf = conf(MyModel.Params)(add=100)
bb = MyModel[MyNewConf](123)
print('MyNewConf = conf(MyModel.Params)(add=100); MyModel[MyNewConf](123):', bb, type(bb))
# reveal_type(bb)

abc = bb + 12
print('MyModel[MyNewConf](123) + 12:', abc, type(abc))
# reveal_type(abc)

cc = MyModel(123)
print('MyModel(123):', cc, type(cc))
# reveal_type(cc)

config = conf(MyModel.Params)


class MyAddTenModel(MyModel[config(add=10)]):
    ...


dd = MyAddTenModel(123)
print('MyAddTenModel(123):', dd, type(dd))
# reveal_type(dd)

# Variant of https://github.com/python/typing/issues/270#issuecomment-555966301
#
# T = TypeVar("T")
# P = ParamSpec('P')
#
# class copy_paramspec(Generic[P]):
#     def __init__(self, target: Callable[P, Any]) -> None:
#         ...
#
#     def __call__(self, wrapped: Callable[..., T]) -> Callable[P, T]:
#         return wrapped
