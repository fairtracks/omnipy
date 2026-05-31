"""General-purpose helper functions shared across Omnipy.

This module collects small utilities for mapping normalization, dataclass merging,
type introspection, forward-reference resolution, import inspection, newline-aware
text handling, and other reusable runtime helpers. Several helpers intentionally
favor graceful fallbacks for dynamic Python edge cases, such as unresolved forward
references, parameterized generics, optional values, empty inputs, and array-like
equality results.
"""

import asyncio
from collections.abc import Hashable, Iterable
from dataclasses import asdict
import functools
from importlib.abc import Loader
from importlib.machinery import FileFinder, ModuleSpec
from importlib.metadata import distribution
import inspect
from inspect import getmodule, isclass
from keyword import iskeyword, issoftkeyword
import locale as pkg_locale
import operator
import sys
from types import GenericAlias, ModuleType, NoneType, UnionType
from typing import _AnnotatedAlias  # type: ignore[attr-defined]
from typing import _LiteralGenericAlias  # type: ignore[attr-defined]
from typing import _UnionGenericAlias  # type: ignore[attr-defined]
from typing import (_SpecialForm,
                    Any,
                    Callable,
                    cast,
                    Concatenate,
                    ForwardRef,
                    get_args,
                    get_origin,
                    Literal,
                    Mapping,
                    overload,
                    ParamSpec,
                    TypeAlias,
                    TypeGuard,
                    Union)

from cachebox import cached, LRUCache
from typing_extensions import TypeVar

from omnipy.shared.protocols.util import IsDataclass
from omnipy.shared.typedefs import LocaleType, TypeForm
import omnipy.util.pydantic as pyd

_KeyT = TypeVar('_KeyT', bound=Hashable)
_ValueT = TypeVar('_ValueT')
_ObjT = TypeVar('_ObjT', bound=object)
_DataclassT = TypeVar('_DataclassT', bound=IsDataclass)
_P = ParamSpec('_P')
_RetT = TypeVar('_RetT')

Dictable: TypeAlias = Mapping[_KeyT, Any] | Iterable[tuple[_KeyT, Any]]


def sorted_dict_hash(d: dict) -> tuple:
    """Return a deterministic tuple representation of a dictionary.

    Args:
        d: Dictionary whose keys must be sortable with ``sorted()``.

    Returns:
        A tuple of ``(key, value)`` pairs ordered by key.
    """
    return tuple((k, d[k]) for k in sorted(d.keys()))


def as_dictable(obj: object) -> Dictable | None:
    """Return ``obj`` when it can be treated as mapping input.

    Args:
        obj: Candidate mapping or iterable of ``(key, value)`` pairs.

    Returns:
        ``obj`` cast to ``Dictable`` when supported, otherwise ``None``.

    Notes:
        Iterable inputs are validated eagerly. Single-pass iterators may therefore
        be consumed by the tuple-pair check.
    """
    def _is_iterable_of_tuple_pairs(obj_inner: object) -> bool:
        return isinstance(obj_inner, Iterable) and \
            all(isinstance(el, tuple) and len(el) == 2 for el in obj_inner)

    if isinstance(obj, Mapping) or _is_iterable_of_tuple_pairs(obj):
        return cast(Dictable, obj)
    else:
        return None


def create_merged_dict(dictable_1: Dictable[_KeyT],
                       dictable_2: Dictable[_KeyT]) -> dict[_KeyT, Any]:
    """Merge two mapping-like inputs into a new dictionary.

    Args:
        dictable_1: Base mapping or iterable of key-value pairs.
        dictable_2: Mapping or iterable whose values override ``dictable_1``.

    Returns:
        A new dictionary containing keys from both inputs.
    """
    merged_dict = cast(
        dict[_KeyT, Any],
        dictable_1 if isinstance(dictable_1, dict) else dict(dictable_1),
    )
    dict_2 = cast(
        dict[_KeyT, Any],
        dictable_2 if isinstance(dictable_2, dict) else dict(dictable_2),
    )
    merged_dict |= dict_2
    return merged_dict


def first_key_in_mapping(mapping: Mapping[_KeyT, Any],) -> _KeyT:
    """Return the first key yielded by a mapping.

    Args:
        mapping: Mapping to inspect.

    Returns:
        The first key produced by ``mapping.keys()``.

    Raises:
        KeyError: If the mapping is empty.
    """
    for _key in mapping.keys():
        return _key
    raise KeyError('Mapping is empty, no first key.')


def first_value_in_mapping(mapping: Mapping[Any, _ValueT],) -> _ValueT:
    """Return the first value yielded by a mapping.

    Args:
        mapping: Mapping to inspect.

    Returns:
        The first value produced by ``mapping.values()``.

    Raises:
        ValueError: If the mapping is empty.
    """
    for _val in mapping.values():
        return _val
    raise ValueError('Mapping is empty, no first value.')


def merge_dataclasses(dataclass: _DataclassT, other_dict: dict[str, Any]) -> _DataclassT:
    """Create a new dataclass instance with selected field overrides.

    Args:
        dataclass: Source dataclass instance.
        other_dict: Replacement values keyed by dataclass field name.

    Returns:
        A new instance of the same dataclass type.
    """
    return dataclass.__class__(**(asdict(dataclass) | other_dict))


def remove_none_vals(**kwargs: object) -> dict[object, object]:
    """Drop keyword arguments whose value is ``None``.

    Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
        A dictionary containing only non-``None`` values.
    """
    return {key: obj for key, obj in kwargs.items() if obj is not None}


def get_datetime_format(locale: LocaleType | None = None) -> str:
    """Return the locale-dependent date-time format string.

    Args:
        locale: Locale passed to ``locale.setlocale``.

    Returns:
        The current locale's ``D_T_FMT`` format, or a conservative fallback on
        platforms without ``nl_langinfo``.

    Notes:
        This function changes the process-wide locale as a side effect.
    """
    pkg_locale.setlocale(pkg_locale.LC_ALL, locale)

    if hasattr(pkg_locale, 'nl_langinfo'):  # noqa
        datetime_format = pkg_locale.nl_langinfo(pkg_locale.D_T_FMT)
    else:
        datetime_format = '%a %b %e %X %Y'
    return datetime_format


async def resolve(obj):
    """Await ``obj`` when needed and otherwise return it unchanged.

    Args:
        obj: Awaitable or plain value.

    Returns:
        The awaited result for awaitables, or ``obj`` itself.
    """
    return await obj if inspect.isawaitable(obj) else obj


def repr_max_len(data: object, max_len: int = 200):
    """Return ``repr(data)`` truncated to at most ``max_len`` characters.

    Args:
        data: Object to represent.
        max_len: Maximum number of repr characters before truncation.

    Returns:
        The full repr when short enough, otherwise a truncated repr with ``...``.
    """
    repr_str = repr(data)
    return f'{repr_str[:max_len]}...' if len(repr_str) > max_len else repr_str


def get_parametrized_type(obj: object):
    """Return a generic instance's recorded type when available.

    Args:
        obj: Object that may carry ``__orig_class__``.

    Returns:
        ``obj.__orig_class__`` for parametrized generic instances, otherwise
        ``type(obj)``.
    """
    return getattr(obj, '__orig_class__', type(obj))


def generic_aware_issubclass_ignore_args(cls, cls_or_tuple):
    """Run ``issubclass`` while tolerating parametrized generic aliases.

    Args:
        cls: Candidate class or parametrized generic alias.
        cls_or_tuple: Superclass or tuple of superclasses.

    Returns:
        ``True`` when ``cls`` is a subclass of ``cls_or_tuple``.

    Notes:
        When ``issubclass`` rejects a parametrized generic, the helper retries
        with the generic origin and ignores its type arguments.
    """
    try:
        return issubclass(cls, cls_or_tuple)
    except TypeError:
        return issubclass(get_origin(cls), cls_or_tuple)


def transfer_generic_args_to_cls(to_cls, from_generic_type):
    """Apply generic arguments from one type to another class when possible.

    Args:
        to_cls: Target class or generic alias factory.
        from_generic_type: Source type whose arguments should be reused.

    Returns:
        ``to_cls`` specialized with the source arguments, or ``to_cls`` unchanged
        if specialization is unsupported.
    """
    try:
        return to_cls[get_args(from_generic_type)]
    except (TypeError, AttributeError):
        return to_cls


@overload
def ensure_plain_type(  # pyright: ignore [reportOverlappingOverload]
        in_type: ForwardRef) -> ForwardRef:
    ...


@overload
def ensure_plain_type(in_type: TypeVar) -> TypeVar:
    ...


@overload
def ensure_plain_type(in_type: type | GenericAlias | UnionType) -> type:
    ...


@overload
def ensure_plain_type(in_type: _SpecialForm) -> _SpecialForm:
    ...


@overload
def ensure_plain_type(in_type: _LiteralGenericAlias | _UnionGenericAlias | _AnnotatedAlias) -> type:
    ...


def ensure_plain_type(in_type: TypeForm) -> ForwardRef | TypeVar | type | _SpecialForm | NoneType:
    """Normalize a type form to its plain runtime representative when possible.

    Args:
        in_type: Type expression, including unions, generics, and forward refs.

    Returns:
        The generic origin for parametrized types, ``types.UnionType`` for
        ``typing.Union``, ``None`` for ``NoneType``, or the original value when it
        is already plain.
    """

    if in_type == NoneType:
        return None

    origin = get_origin(in_type)
    if origin == Union:
        return UnionType  # pyright: ignore [reportReturnType]
    else:
        return cast(type | ForwardRef | TypeVar, origin if get_args(in_type) else in_type)


def evaluate_any_forward_refs_if_possible(in_type: TypeForm,
                                          calling_module: str | None = None,
                                          **localns) -> TypeForm:
    """Resolve forward references recursively when enough namespace data exists.

    Args:
        in_type: Type expression that may contain forward references.
        calling_module: Module name used as global namespace lookup.
        **localns: Extra symbols available during forward-reference evaluation.

    Returns:
        A resolved type expression when evaluation succeeds, otherwise the input
        expression or a partially resolved variant.

    Notes:
        Unresolvable names are left untouched instead of raising ``NameError``.
    """
    if not calling_module:
        calling_module = get_calling_module_name() if 'ForwardRef' in str(in_type) else None

    if isinstance(in_type, ForwardRef):
        if calling_module and calling_module in sys.modules:
            globalns = sys.modules[calling_module].__dict__.copy()
        else:
            globalns = {}
        try:
            return cast(
                type | GenericAlias,
                in_type._evaluate(
                    globalns, localns if localns else locals(), recursive_guard=frozenset()))
        except NameError:
            pass
    else:
        origin = get_origin(in_type)
        args = get_args(in_type)
        if origin and args:
            new_args = tuple(
                evaluate_any_forward_refs_if_possible(arg, calling_module, **localns)
                for arg in args)
            if origin == UnionType:
                return functools.reduce(operator.or_, new_args)
            else:
                return origin[new_args]
    return in_type


def get_default_if_typevar(typ_: type[_ObjT] | TypeForm | TypeVar) -> type[_ObjT] | TypeForm:
    """Return a ``TypeVar`` default value, or the input type unchanged.

    Args:
        typ_: Concrete type, type form, or ``TypeVar``.

    Returns:
        The default bound value for a ``TypeVar`` with ``__default__`` support, or
        ``typ_`` when it is not a ``TypeVar``.

    Raises:
        TypeError: If ``typ_`` is a ``TypeVar`` without a default.
    """
    if isinstance(typ_, TypeVar):
        if hasattr(typ_, '__default__'):
            return typ_.__default__
        else:
            raise TypeError(f'The TypeVar "{typ_.__name__}" needs to specify a default value. '
                            f'This requires Python 3.13, but is supported in earlier versions '
                            f'of Python by importing TypeVar from the library '
                            f'"typing-extensions".')
    return typ_


def all_type_variants(
    in_type: type | GenericAlias | UnionType | _UnionGenericAlias
) -> tuple[type | GenericAlias, ...]:
    """Return a flat tuple of all direct variants in a union-like type.

    Args:
        in_type: Type or union expression.

    Returns:
        ``get_args(in_type)`` for unions, otherwise a one-item tuple containing
        ``in_type``.
    """
    if is_union(in_type):
        return get_args(in_type)
    else:
        return (cast(type | GenericAlias, in_type),)


def is_iterable(obj: Iterable[_ObjT] | _ObjT) -> TypeGuard[Iterable[_ObjT]]:
    """Return whether ``obj`` can be iterated over.

    Args:
        obj: Value to test.

    Returns:
        ``True`` when ``iter(obj)`` succeeds.

    Notes:
        Strings and bytes count as iterables here. Use
        ``is_non_str_byte_iterable()`` when that is undesirable.
    """
    try:
        iter(obj)  # type: ignore[arg-type]
        return True
    except TypeError:
        return False


def is_non_str_byte_iterable(
        obj: Iterable[_ObjT] | _ObjT | str | bytes) -> TypeGuard[Iterable[_ObjT]]:
    """Return whether ``obj`` is iterable but not ``str`` or ``bytes``.

    Args:
        obj: Value to test.

    Returns:
        ``True`` for non-string, non-bytes iterables.
    """
    return is_iterable(obj) and not type(obj) in (str, bytes)


def ensure_non_str_byte_iterable(value):
    """Wrap scalars in a tuple while leaving non-string iterables unchanged.

    Args:
        value: Iterable or scalar value.

    Returns:
        ``value`` itself when it is a non-string iterable, otherwise a one-item
        tuple containing ``value``.

    Notes:
        ``str`` and ``bytes`` are treated as scalar values and therefore wrapped.
    """
    return value if is_non_str_byte_iterable(value) else (value,)


def takes_input_params_from(
    func: Callable[Concatenate[Any, _P], Any]
) -> Callable[[Callable[Concatenate[Any, _P], _RetT]], Callable[Concatenate[Any, _P], _RetT]]:
    """Copy a callable parameter signature for static typing purposes.

    Args:
        func: Callable whose input parameters should be mirrored.

    Returns:
        An identity decorator that preserves the input signature of ``func`` in
        type annotations.
    """
    return lambda _: _


def has_items(obj: object) -> bool:
    """Return whether ``obj`` reports a positive length.

    Args:
        obj: Value that may implement ``__len__``.

    Returns:
        ``True`` when ``obj`` has ``__len__`` and its length is greater than zero.
    """
    return hasattr(obj, '__len__') \
        and obj.__len__() > 0  # pyright: ignore [reportAttributeAccessIssue]


def get_first_item(iterable: Iterable[object]) -> object:
    """Return the first iterated item from a non-empty iterable.

    Args:
        iterable: Iterable expected to contain at least one item.

    Returns:
        The first yielded item.

    Raises:
        AssertionError: If ``iterable`` is empty according to ``has_items()``.
    """
    assert has_items(iterable)
    for item in iterable:
        return item


def split_to_union_variants(type_: TypeForm) -> tuple[TypeForm]:
    """Return a union's direct variants or a singleton containing ``type_``.

    Args:
        type_: Type expression to split.

    Returns:
        A tuple of union members, or ``(type_,)`` when the input is not a union.
    """
    return get_args(type_) if is_union(type_) else (type_,)


@cached(LRUCache(128))
def is_union(cls_or_type: type | UnionType | None | object) -> bool:
    """Return whether ``cls_or_type`` represents a union expression.

    Args:
        cls_or_type: Type or object to inspect.

    Returns:
        ``True`` for ``typing.Union`` and ``|`` unions.
    """
    union_types = [Union, UnionType]
    return cls_or_type in union_types or get_origin(cls_or_type) in union_types


@cached(LRUCache(128))
def is_optional(cls_or_type: type | UnionType | None | object) -> bool:
    """Return whether ``cls_or_type`` is a union that includes ``None``.

    Args:
        cls_or_type: Type or object to inspect.

    Returns:
        ``True`` when the input is optional in the ``X | None`` sense.
    """
    return is_union(cls_or_type) and any(pyd.is_none_type(arg) for arg in get_args(cls_or_type))


def is_literal_type(value: Any) -> bool:
    """Return whether ``value`` is a ``typing.Literal`` specialization."""
    return get_origin(value) is Literal


def is_type_specialization(value: Any) -> bool:
    """Return whether ``value`` is a specialization of ``type[...]``."""
    return get_origin(value) is type


@functools.cache
def is_strict_subclass(
        __cls: type,
        __class_or_tuple: type | UnionType | tuple[type | UnionType | tuple[Any, ...], ...]
) -> bool:
    """Return whether ``__cls`` is a proper subclass of the given parent type.

    Args:
        __cls: Candidate subclass.
        __class_or_tuple: Parent class or tuple accepted by ``issubclass``.

    Returns:
        ``True`` when ``__cls`` is a subclass but not equal to the parent itself.
    """
    if issubclass(__cls, __class_or_tuple):
        if isinstance(__class_or_tuple, Iterable):
            return __cls not in __class_or_tuple
        else:
            return __cls != __class_or_tuple
    return False


def is_unreserved_identifier(identifier: str) -> bool:
    """Return whether a string is a valid non-keyword Python identifier.

    Args:
        identifier: Candidate identifier.

    Returns:
        ``True`` when the string is an identifier and neither a hard nor soft
        keyword.
    """
    return identifier.isidentifier() and not iskeyword(identifier) and not issoftkeyword(identifier)


def remove_forward_ref_notation(type_str: str):
    """Strip ``ForwardRef('...')`` wrappers from a rendered type string.

    Args:
        type_str: String representation that may contain forward-ref notation.

    Returns:
        The string with the wrapper removed.
    """
    return type_str.replace("ForwardRef('", '').replace("')", '')


def format_classname_with_params(cls_name: str, params_str: str) -> str:
    """Format a class name together with rendered generic parameters.

    Args:
        cls_name: Base class name.
        params_str: Already rendered generic parameter string.

    Returns:
        A string on the form ``ClassName[param]``.
    """
    return f'{cls_name}[{params_str}]'


def _is_internal_module(module: ModuleType, imported_modules: list[ModuleType]):
    return module not in imported_modules and module.__name__.startswith('omnipy')


def recursive_module_import_new(root_path: list[str],
                                imported_modules: dict[str, ModuleType],
                                excluded_set: set[str]):
    """Import modules discovered under ``root_path`` into ``imported_modules``.

    Args:
        root_path: Package search paths passed to ``pkgutil.walk_packages``.
        imported_modules: Destination mapping updated in place by module name.
        excluded_set: Module names whose entire subtrees should be skipped.

    Notes:
        Importing modules executes their import-time side effects.
    """

    import pkgutil

    module_finder: FileFinder
    module_name: str
    _is_pkg: bool

    cur_excluded_prefix = ''

    for module_finder, module_name, _is_pkg in pkgutil.walk_packages(root_path):  # type: ignore
        # print(f'{module_name}: {_is_pkg}')
        if cur_excluded_prefix and module_name.startswith(cur_excluded_prefix):
            continue
        else:
            cur_excluded_prefix = ''

        if module_name in excluded_set:
            cur_excluded_prefix = f'{module_name}.'
            continue

        module_spec: ModuleSpec | None = module_finder.find_spec(module_name)
        if module_spec:
            loader: Loader | None = module_spec.loader
            if loader:
                imported_modules[module_name] = loader.load_module(module_name)


def recursive_module_import(module: ModuleType,
                            imported_modules: list[ModuleType] = []) -> dict[str, object]:
    """Recursively merge attributes from Omnipy base-class modules.

    Args:
        module: Module whose class hierarchy should be inspected.
        imported_modules: Visited modules used to avoid repeated imports.

    Returns:
        A merged module namespace including relevant internal base-class modules.
    """
    module_vars = vars(module)
    imported_modules.append(module)

    for obj in module_vars.values():
        if isclass(obj):
            for base_cls in obj.__bases__:
                base_cls_module = getmodule(base_cls)
                if base_cls_module and _is_internal_module(base_cls_module, imported_modules):
                    module_vars = create_merged_dict(
                        recursive_module_import(base_cls_module, imported_modules),
                        module_vars,
                    )

    return module_vars


def get_calling_module_name() -> str | None:
    """Return the first caller module name found above the helper frame.

    Returns:
        The detected module name, or ``None`` when inspection cannot resolve one.
    """
    stack = inspect.stack()
    start_frame_index = 2
    while len(stack) > start_frame_index:
        grandparent_frame = stack[start_frame_index][0]
        module = inspect.getmodule(grandparent_frame)
        if module is not None:
            return module.__name__
        start_frame_index += 1


def called_from_omnipy_tests() -> bool:
    """Return whether the current call stack originates from Omnipy tests.

    Returns:
        ``True`` when a stack frame belongs to a module under ``tests`` inside the
        Omnipy repository.
    """
    stack = inspect.stack()
    for index in range(len(stack)):
        frame = stack[index][0]
        module = inspect.getmodule(frame)
        if module is not None \
                and module.__name__.startswith('tests') \
                and module.__file__ is not None \
                and ("omnipy/tests" in module.__file__ or ("/omnipy/" in module.__file__ and "/tests/" in module.__file__)):
            return True
    return False


@functools.cache
def is_package_editable(package_name):
    """Check if package is installed in editable mode using metadata."""
    try:
        dist = distribution(package_name)
        # Get the location where package is installed
        if dist.read_text('direct_url.json'):
            import json
            direct_url = json.loads(dist.read_text('direct_url.json'))  # pyright: ignore
            return direct_url.get('dir_info', {}).get('editable', False)
        return False
    except Exception:
        return False


def get_event_loop_and_check_if_loop_is_running() -> tuple[asyncio.AbstractEventLoop | None, bool]:
    """Get the current event loop and whether it is already running.

    Returns:
        A tuple of ``(loop, is_running)``. ``loop`` is ``None`` when no current
        loop exists in the active thread.
    """
    loop_is_running: bool
    loop: asyncio.AbstractEventLoop | None = None

    try:
        loop = asyncio.get_running_loop()
        loop_is_running = loop.is_running()
    except RuntimeError:
        loop_is_running = False

    return loop, loop_is_running


def split_all_content_to_lines(content: str) -> list[str]:
    """Split text into newline-preserving logical lines.

    Args:
        content: Full text content.

    Returns:
        A list like ``splitlines(keepends=True)`` with an added trailing empty
        string when ``content`` is empty or ends with a newline.

    Notes:
        The extra empty string keeps line-oriented consumers aligned with repr-like
        content that omits the final newline character.
    """
    all_content_lines_stripped = content.splitlines(keepends=False)
    all_content_lines = content.splitlines(keepends=True)

    if len(all_content_lines) == 0 \
            or all_content_lines[-1] != all_content_lines_stripped[-1]:
        # If no content or the last line ends with a newline, we add an
        # empty line. This is needed as the last newline is excluded
        # from self.content (in line with typical repr output).
        all_content_lines.append('')

    return all_content_lines


def strip_newline(line: str) -> str:
    """Remove a trailing newline from a single line of text.

    Args:
        line: String expected to contain at most one logical line.

    Returns:
        The line without its newline terminator.

    Raises:
        AssertionError: If ``line`` contains more than one logical line.
    """
    line_stripped = line.splitlines()
    assert len(line_stripped) <= 1, \
        f'Expected a single line, but got {len(line_stripped)} lines: {line_stripped}'
    if len(line_stripped) == 0:
        return ''
    else:
        return line_stripped[0]


def strip_and_split_newline(line: str) -> tuple[str, str]:
    """Split a line into its content and trailing newline sequence.

    Args:
        line: String expected to contain a single logical line.

    Returns:
        A ``(content, newline)`` tuple.
    """
    line_stripped = strip_newline(line)
    newline = line[len(line_stripped):]
    return line_stripped, newline


def strip_newlines(lines: Iterable[str]) -> list[str]:
    """Strip trailing newlines from each input line.

    Args:
        lines: Iterable of single-line strings.

    Returns:
        A list of newline-free line contents.
    """
    return [strip_newline(line) for line in lines]


def extract_newline(line: str) -> str:
    """Return only the trailing newline sequence from a single line.

    Args:
        line: String expected to contain a single logical line.

    Returns:
        The trailing newline sequence, or an empty string.
    """
    return strip_and_split_newline(line)[1]


def max_newline_stripped_width(lines: list[str]) -> int:
    """Return the longest visible line width after stripping newlines.

    Args:
        lines: Lines that may include newline terminators.

    Returns:
        The maximum character width excluding trailing newline sequences.
    """
    return max((len(strip_newline(line)) for line in lines), default=0)


def all_equals(first, second) -> bool:
    """Collapse scalar or vectorized equality results into a single boolean.

    Args:
        first: First value or array-like object.
        second: Second value or array-like object.

    Returns:
        ``True`` when all element-wise comparisons are true, or when the scalar
        comparison is true.

    Notes:
        Supports numpy- and pandas-style comparison objects exposing ``all()``.
    """
    equals = first == second
    if is_iterable(equals):
        if hasattr(equals, 'all') and callable(getattr(equals, 'all')):
            # Works for both pandas and numpy
            return equals.all(None)  # pyright: ignore [reportAttributeAccessIssue]
        else:
            return all(equals)
    else:
        return equals


NumberT = TypeVar('NumberT', float, int)


def min_or_none(*args: NumberT | None) -> NumberT | None:
    """Return the smallest non-``None`` argument.

    Args:
        *args: Numbers or ``None`` values.

    Returns:
        The minimum non-``None`` value, or ``None`` when no numbers are provided.
    """
    filtered_args = [arg for arg in args if arg is not None]
    return min(filtered_args) if filtered_args else None


def max_or_none(*args: NumberT | None) -> NumberT | None:
    """Return the largest non-``None`` argument.

    Args:
        *args: Numbers or ``None`` values.

    Returns:
        The maximum non-``None`` value, or ``None`` when no numbers are provided.
    """
    filtered_args = [arg for arg in args if arg is not None]
    return max(filtered_args) if filtered_args else None


def get_job_name_slug(job_cls_name: str, job_name: str):
    import inflection

    job_cls_name_slug = inflection.underscore(job_cls_name).replace('_', '-')
    job_name_slug = inflection.underscore(job_name).replace('_', '-')
    return f'{job_cls_name_slug}-{job_name_slug}'


def generate_run_slug():
    import coolname

    return coolname.generate_slug(3)


def get_full_job_slug(job_cls_name: str, job_name: str, job_run_slug: str):
    return f'{get_job_name_slug(job_cls_name, job_name)}-{job_run_slug}'
