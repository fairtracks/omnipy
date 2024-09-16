from collections import defaultdict
from contextlib import suppress
from enum import IntEnum
import functools
import os
import shutil
from typing import ContextManager, ForwardRef, Generic, get_args, get_origin, NamedTuple

from pydantic.typing import is_none_type
from pydantic.utils import lenient_isinstance, lenient_issubclass
from typing_extensions import TypeVar

from omnipy.api.typedefs import TypeForm
from omnipy.data.data_class_creator import DataClassBase
from omnipy.util.helpers import format_classname_with_params, is_union

T = TypeVar('T')
U = TypeVar('U')


class TypeVarStore(Generic[T]):
    def __init__(self, t: T) -> None:
        raise ValueError()


class DoubleTypeVarStore(Generic[T, U]):
    def __init__(self, t: T | U) -> None:
        raise ValueError()


class TypeVarStore1(TypeVarStore[T], Generic[T]):
    ...


class TypeVarStore2(TypeVarStore[T], Generic[T]):
    ...


class TypeVarStore3(TypeVarStore[T], Generic[T]):
    ...


class TypeVarStore4(TypeVarStore[T], Generic[T]):
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


INTERACTIVE_MODULES = [
    '__main__',
    'IPython.lib.pretty',
    'IPython.core.interactiveshell',
    '_pydevd_bundle.pydevd_asyncio_utils',
    '_pydevd_bundle.pydevd_exec2',
]
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
                return model.__name__
            return str(model)

    params_str = _display_as_type(orig_model)

    model_or_dataset.__name__ = format_classname_with_params(cls.__name__, params_str)
    model_or_dataset.__qualname__ = format_classname_with_params(cls.__qualname__, params_str)
    model_or_dataset.__module__ = cls.__module__


def get_terminal_size() -> os.terminal_size:
    from omnipy.hub.runtime import runtime

    shutil_terminal_size = shutil.get_terminal_size()
    columns = runtime.config.data.terminal_size_columns if runtime else shutil_terminal_size.columns
    lines = runtime.config.data.terminal_size_lines if runtime else shutil_terminal_size.lines

    return os.terminal_size((columns, lines))


def waiting_for_terminal_repr(new_value: bool | None = None) -> bool:
    from omnipy.hub.runtime import runtime
    if runtime is None:
        return False

    if new_value is not None:
        runtime.objects.waiting_for_terminal_repr = new_value
        return new_value
    else:
        return runtime.objects.waiting_for_terminal_repr


def is_model_instance(__obj: object) -> bool:
    from omnipy.data.model import Model
    return lenient_isinstance(__obj, Model) \
        and not is_none_type(__obj)  # Consequence of _ModelMetaclass hack


@functools.cache
def is_model_subclass(__cls: TypeForm) -> bool:
    from omnipy.data.model import Model
    return lenient_issubclass(__cls, Model) \
        and not is_none_type(__cls)  # Consequence of _ModelMetaclass hack


def obj_or_model_contents_isinstance(__obj: object, __class_or_tuple: type) -> bool:
    return isinstance(__obj.contents if is_model_instance(__obj) else __obj, __class_or_tuple)


# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()
