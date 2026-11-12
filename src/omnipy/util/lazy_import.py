"""Helpers for modules that expose lazily imported names."""

from collections.abc import Mapping, MutableMapping
from importlib import import_module


def resolve_lazy_export(
    name: str,
    module_name: str,
    package: str | None,
    namespace: MutableMapping[str, object],
    exports: Mapping[str, str],
) -> object:
    """Import a declared export and cache it in the calling module's namespace.

    Pass the exporting module's ``__name__``, ``__package__`` and ``globals()``.
    Module paths can be absolute or relative to ``package``.
    """
    if name not in exports:
        raise AttributeError(f'module {module_name!r} has no attribute {name!r}')
    module = import_module(exports[name], package)
    value = getattr(module, name)
    namespace[name] = value
    return value
