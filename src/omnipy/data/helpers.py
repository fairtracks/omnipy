"""Helper types and utilities shared across Omnipy's data layer internals."""

from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from enum import IntEnum
import os
import sys
from textwrap import dedent
from typing import Any, ContextManager, ForwardRef, Generic, get_args, get_origin, NamedTuple

from typing_extensions import TypeIs, TypeVar

from omnipy.data._data_class_creator import DataClassBase
from omnipy.shared.typedefs import TypeForm
from omnipy.util.helpers import format_classname_with_params, is_package_editable, is_union

__all__ = [
    'TypeVarStore',
    'TypeVarStore1',
    'TypeVarStore2',
    'TypeVarStore3',
    'TypeVarStore4',
    'DoubleTypeVarStore',
    'YesNoMaybe',
    'MethodInfo',
    'SPECIAL_METHODS_INFO_DICT',
    'ResetSolutionTuple',
    'cleanup_name_qualname_and_module',
    'build_own_module_and_global_namespace_for_forward_refs',
    'PendingData',
    'FailedData',
]

_T = TypeVar('_T')
_U = TypeVar('_U')

if is_package_editable('omnipy'):  # Only define environment variables when developing
    os.environ['OMNIPY_MACRO_TYPEVAR_STORE_MARKER_SUMMARY'] = dedent("""\
        Distinct single-type-variable marker used when multiple stores are needed.""")


class TypeVarStore(Generic[_T]):
    """Sentinel generic used to expose a single type variable in helper type plumbing."""
    def __init__(self, t: _T) -> None:
        raise ValueError()


class DoubleTypeVarStore(Generic[_T, _U]):
    """Sentinel generic used to expose one of two type variables to internal helpers."""
    def __init__(self, t: _T | _U) -> None:
        raise ValueError()


class TypeVarStore1(TypeVarStore[_T], Generic[_T]):
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # {{TYPEVAR_STORE_MARKER_SUMMARY}}
    """Distinct single-type-variable marker used when multiple stores are needed."""

    ...


class TypeVarStore2(TypeVarStore[_T], Generic[_T]):
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # {{TYPEVAR_STORE_MARKER_SUMMARY}}
    """Distinct single-type-variable marker used when multiple stores are needed."""

    ...


class TypeVarStore3(TypeVarStore[_T], Generic[_T]):
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # {{TYPEVAR_STORE_MARKER_SUMMARY}}
    """Distinct single-type-variable marker used when multiple stores are needed."""

    ...


class TypeVarStore4(TypeVarStore[_T], Generic[_T]):
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # {{TYPEVAR_STORE_MARKER_SUMMARY}}
    """Distinct single-type-variable marker used when multiple stores are needed."""

    ...


class YesNoMaybe(IntEnum):
    """Tri-state answer used when Omnipy infers special-method behavior."""

    NO = 0
    YES = 1
    MAYBE = 2


class MethodInfo(NamedTuple):
    """Metadata describing how a Python special method behaves for wrapped data classes.

    Attributes:
        state_changing: Whether calling the method mutates the wrapped object.
        returns_same_type: Whether the method is expected to return the same data-class type.
    """

    state_changing: bool
    returns_same_type: YesNoMaybe


# Ordered after their order in the Python documentation
# (https://docs.python.org/3.10/reference/datamodel.html)
SPECIAL_METHODS_INFO_DICT: dict[str, MethodInfo] = {
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
    '__next__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
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
    '__str__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    '__bytes__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # - Used to implement operator.index() - always integer -----------------
    '__index__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # - Rounding operations - mostly integers -------------------------------
    '__round__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__trunc__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__floor__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    '__ceil__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.MAYBE),
    # - Context managers -------------------------------------------------------
    '__enter__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
    '__exit__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
    # - Buffer protocol --------------------------------------------------------
    '__buffer__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
    '__release_buffer__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
    # - Annotations ---------------------------------------------------------
    # '__annotations__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # '__annotate__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # - Hash and other standard methods -------------------------------------
    '__hash__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # - Coroutines ----------------------------------------------------------
    '__await__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # - Asynchronous iterators ------------------------------------------------
    '__aiter__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    '__anext__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # - Asynchronous context managers ----------------------------------------
    '__aenter__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
    '__aexit__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
    # - Copy protocol --------------------------------------------------------
    '__copy__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.YES),
    '__deepcopy__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.YES),
    '__replace__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.YES),
    # - Str methods --------------------------------------------------------
    # __format__ returns a str, which might sometimes match the model, but
    # if e.g. `Model[str]` and `dynamically_convert_elements_to_models=True`
    # we do not want to return a Model[str] object.
    '__format__': MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO),
    # - Other --------------------------------------------------------
    '__delattr__': MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
}

validate_cls_counts: defaultdict[str, int] = defaultdict(int)


class ResetSolutionTuple(NamedTuple):
    """Result from internal reset handling during snapshot-aware operations.

    Attributes:
        reset_solution: Context manager that applies the chosen reset strategy.
        snapshot_taken: Whether a fresh snapshot was captured before the operation.
    """

    reset_solution: ContextManager[None]
    snapshot_taken: bool


def debug_get_sorted_validate_counts() -> dict[str, int]:
    """Return validation-call counts sorted from highest to lowest for debugging."""

    return dict(reversed(sorted(validate_cls_counts.items(), key=lambda item: item[1])))


def debug_get_total_validate_count() -> int:
    """Return the total number of tracked validation calls for debugging."""

    return sum(val for key, val in validate_cls_counts.items())


def cleanup_name_qualname_and_module(
    cls: type[DataClassBase],
    model_or_dataset: type[DataClassBase],
    orig_model: TypeForm,
) -> None:
    """Normalize generated class identity metadata for parametrized data classes.

    Omnipy dynamically creates specialized model and dataset classes. This helper keeps the
    generated class name, qualified name, and module aligned with the originating class so those
    classes display predictably in errors, debugging output, and introspection tools.

    Args:
        cls: The original generic data-class type being specialized.
        model_or_dataset: The generated specialized class whose metadata should be updated.
        orig_model: The type parameter representation used to build the specialized class name.
    """
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


def build_own_module_and_global_namespace_for_forward_refs(
    own_class: type,
    calling_module: str | None,
    **localns: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build own-module and global namespaces for fwd reference resolution

    Build global namespaces for forward reference resolution by merging:

    1. The model's own defining module namespace — so forward refs
       declared inside the model (e.g. JsonScalar in
       tables/models.py) are always resolvable even when
       update_forward_refs is triggered from a different module.

    2. The calling module's namespace on top — so forward refs
       that point to types available at the call site (e.g.
       NestedDataset in datasets.py) are resolved correctly.

    3. Any explicitly passed localns with the highest priority.

    Returns:
        A tuple of (own_module_namespace, global_namespace) to be used for
        forward reference resolution.
    """
    def _module_loaded(module_name: str | None) -> TypeIs[str]:
        return module_name is not None and module_name in sys.modules

    own_module = getattr(own_class, '__module__', None)
    own_module_ns = (sys.modules[own_module].__dict__ if _module_loaded(own_module) else {})

    calling_module_ns = (
        sys.modules[calling_module].__dict__ if _module_loaded(calling_module) else {})

    globalns: dict[str, Any] = {}
    globalns.update(own_module_ns)
    globalns.update(calling_module_ns)
    globalns.update(localns)

    return own_module_ns, globalns


@dataclass(frozen=True, kw_only=True)
class PendingData:
    """Marker payload for dataset items whose producing task has not completed yet.

    Attributes:
        job_name: Human-readable task name.
        job_unique_name: Optional unique task identifier when available.
    """

    job_name: str
    job_unique_name: str = ''


@dataclass(frozen=True, kw_only=True)
class FailedData:
    """Marker payload for dataset items whose producing task failed.

    Attributes:
        job_name: Human-readable task name.
        job_unique_name: Optional unique task identifier when available.
        exception: The captured task failure.
    """

    job_name: str
    job_unique_name: str = ''
    exception: BaseException
