from typing import NamedTuple


class MethodInfo(NamedTuple):
    state_changing: bool
    maybe_returns_same_type: bool


# Ordered after their order in the Python documentation
# (https://docs.python.org/3.10/reference/datamodel.html)
SPECIAL_METHODS_INFO: dict[str, MethodInfo] = {
    # 3.3.1. Basic customization ############################################
    '__bool__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    # 3.3.7. Emulating container types ######################################
    '__len__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    '__length_hint__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    '__getitem__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__setitem__': MethodInfo(state_changing=True, maybe_returns_same_type=False),
    '__delitem__': MethodInfo(state_changing=True, maybe_returns_same_type=False),
    '__missing__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    '__iter__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    '__reversed__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    '__contains__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    # 3.3.8. Emulating numeric types ########################################
    # - Binary arithmetic ---------------------------------------------------
    '__add__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__sub__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__mul__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__matmul__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__truediv__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__floordiv__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__mod__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__divmod__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__pow__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__lshift__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rshift__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__and__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__xor__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__or__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    # - Binary arithmetic (right-hand side) ---------------------------------
    '__radd__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rsub__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rmul__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rmatmul__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rtruediv__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rfloordiv__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rmod__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rdivmod__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rpow__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rlshift__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rrshift__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rand__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__rxor__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__ror__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    # - Binary arithmetic (in-place, e.g. '=+') -----------------------------
    '__iadd__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__isub__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__imul__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__imatmul__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__itruediv__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__ifloordiv__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__imod__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__ipow__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__ilshift__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__irshift__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__iand__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__ixor__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    '__ior__': MethodInfo(state_changing=True, maybe_returns_same_type=True),
    # - Unary arithmetic operations (e.g. -x) -------------------------------
    '__neg__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__pos__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__abs__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__invert__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    # - Converting to the appropriate type ----------------------------------
    '__complex__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    '__int__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    '__float__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    # - Used to implement operator.index() - always integer -----------------
    '__index__': MethodInfo(state_changing=False, maybe_returns_same_type=False),
    # - Rounding operations - mostly integers -------------------------------
    '__round__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__trunc__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__floor__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
    '__ceil__': MethodInfo(state_changing=False, maybe_returns_same_type=True),
}
