from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from enum import IntEnum
from typing import ContextManager, ForwardRef, Generic, get_args, get_origin, NamedTuple

from typing_extensions import TypeVar

from omnipy.data._data_class_creator import DataClassBase
from omnipy.shared.typedefs import TypeForm
from omnipy.util.helpers import format_classname_with_params, is_union

__all__ = [
    'TypeVarStore1',
    'TypeVarStore2',
    'TypeVarStore3',
    'TypeVarStore4',
    'DoubleTypeVarStore',
    'PendingData',
    'FailedData',
]

_T = TypeVar('_T')
_U = TypeVar('_U')


class TypeVarStore(Generic[_T]):
    def __init__(self, t: _T) -> None:
        raise ValueError()


class DoubleTypeVarStore(Generic[_T, _U]):
    def __init__(self, t: _T | _U) -> None:
        raise ValueError()


class TypeVarStore1(TypeVarStore[_T], Generic[_T]):
    ...


class TypeVarStore2(TypeVarStore[_T], Generic[_T]):
    ...


class TypeVarStore3(TypeVarStore[_T], Generic[_T]):
    ...


class TypeVarStore4(TypeVarStore[_T], Generic[_T]):
    ...


class YesNoMaybe(IntEnum):
    NO = 0
    YES = 1
    MAYBE = 2


class MethodInfo(NamedTuple):
    state_changing: bool
    returns_same_type: YesNoMaybe


# Ordered after their order in the Python documentation
# (https://docs.python.org/3.10/reference/datamodel.html)
_SPECIAL_METHODS_INFO_DICT: dict[str, MethodInfo] = {
    # 3.3.1. Basic customization ############################################
    # '__bool__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # 3.3.7. Emulating container types ######################################
    '__len__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    '__length_hint__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    '__getitem__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__setitem__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
    '__delitem__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
    '__missing__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    '__iter__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    '__reversed__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    '__contains__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # 3.3.8. Emulating numeric types ########################################
    # - Binary arithmetic ---------------------------------------------------
    '__add__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.YES),
    '__sub__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__mul__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__matmul__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__truediv__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__floordiv__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__mod__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__divmod__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__pow__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__lshift__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rshift__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__and__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__xor__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__or__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    # - Binary arithmetic (right-hand side) ---------------------------------
    '__radd__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.YES),
    '__rsub__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rmul__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rmatmul__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rtruediv__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rfloordiv__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rmod__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rdivmod__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rpow__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rlshift__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rrshift__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rand__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__rxor__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__ror__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    # - Binary arithmetic (in-place, e.g. '=+') -----------------------------
    '__iadd__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.YES),
    '__isub__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__imul__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__imatmul__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__itruediv__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__ifloordiv__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__imod__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__ipow__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__ilshift__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__irshift__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__iand__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__ixor__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    '__ior__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.MAYBE),
    # - Unary arithmetic operations (e.g. -x) -------------------------------
    '__neg__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__pos__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__abs__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__invert__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    # - Converting to the appropriate type ----------------------------------
    '__complex__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    '__int__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    '__float__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # - Used to implement operator.index() - always integer -----------------
    '__index__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # - Rounding operations - mostly integers -------------------------------
    '__round__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__trunc__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__floor__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__ceil__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    # - Hash and other standard methods ----------------------------------
    '__hash__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
}


def get_special_methods_info_dict() -> dict[str, MethodInfo]:
    return _SPECIAL_METHODS_INFO_DICT


validate_cls_counts: defaultdict[str, int] = defaultdict(int)


class ResetSolutionTuple(NamedTuple):
    reset_solution: ContextManager[None]
    snapshot_taken: bool


def debug_get_sorted_validate_counts() -> dict[str, int]:
    return dict(reversed(sorted(validate_cls_counts.items(), key=lambda item: item[1])))


def debug_get_total_validate_count() -> int:
    return sum(val for key, val in validate_cls_counts.items())


def cleanup_name_qualname_and_module(
    cls: type[DataClassBase],
    model_or_dataset: type[DataClassBase],
    orig_model: TypeForm,
) -> None:
    def _display_as_type(model: TypeForm):
        if isinstance(model, str):  # ForwardRef
            return model
        elif isinstance(model, ForwardRef):
            return model.__forward_arg__
        elif isinstance(model, tuple):
            return ', '.join(_display_as_type(arg) for arg in model)
        elif is_union(model):
            return ' | '.join(_display_as_type(arg) for arg in get_args(model))
        elif len(get_args(model)) > 0:
            return (f'{_display_as_type(get_origin(model))}'
                    f"[{', '.join(_display_as_type(arg) for arg in get_args(model))}]")
        elif isinstance(model, TypeVar):
            return str(model)
        else:
            with suppress(AttributeError):
                return model.__name__  # type:ignore[union-attr]
            return str(model)

    params_str = _display_as_type(orig_model)

    model_or_dataset.__name__ = format_classname_with_params(cls.__name__, params_str)
    model_or_dataset.__qualname__ = format_classname_with_params(cls.__qualname__, params_str)
    model_or_dataset.__module__ = cls.__module__


# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()


@dataclass(frozen=True, kw_only=True)
class PendingData:
    job_name: str
    job_unique_name: str = ''


@dataclass(frozen=True, kw_only=True)
class FailedData:
    job_name: str
    job_unique_name: str = ''
    exception: BaseException
