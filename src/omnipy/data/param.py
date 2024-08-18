from dataclasses import dataclass
from typing import Callable, Generic, get_args, ParamSpec, Protocol

from typing_extensions import TypeVar

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
