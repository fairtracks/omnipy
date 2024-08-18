from enum import IntEnum
from typing import Generic, NamedTuple

from typing_extensions import TypeVar

T = TypeVar('T')


class TypeVarStore(Generic[T]):
    def __init__(self, t: T) -> None:
        raise ValueError()


class Params:
    params: dict[str, object]

    def __class_getitem__(cls, params: dict[str, object] = {}) -> 'Params':
        cls.params = params
        return cls


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
    '__bool__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
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
}


def get_special_methods_info_dict() -> dict[str, MethodInfo]:
    return _SPECIAL_METHODS_INFO_DICT
