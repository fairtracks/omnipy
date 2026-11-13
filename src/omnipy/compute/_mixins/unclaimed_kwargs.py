"""Mixin keeping job keyword arguments that no loaded job mixin declares.

Plugins add job keyword arguments through optional job mixins, and plugins are loaded lazily.
A template may therefore be created with keyword arguments whose mixin is not loaded yet, for
example ``tes_image`` before the TES engine has been loaded. Such keyword arguments are kept on
the template and passed on again when the template is applied, refined or revised. When a job is
created at apply and a keyword argument is still not claimed by any mixin, a warning is logged.
"""

from collections.abc import Mapping, Set
import logging
import os
from types import MappingProxyType

from omnipy.util.mixin import RECEIVES_UNCLAIMED_KWARGS_ATTR

SILENCE_UNCLAIMED_KWARGS_WARNING_ENV_VAR = 'OMNIPY_SILENCE_UNUSED_JOB_KEYWORDS'
"""Environment variable that silences the warning about unused job keyword arguments when set to
``1``. Engines that run jobs remotely set it where the submitting side has already handled them.
"""

_logger = logging.getLogger(__name__)


def _freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(val) for key, val in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(val) for val in value)
    if isinstance(value, Set):
        return frozenset(_freeze(val) for val in value)
    return value


class UnclaimedKwargsJobBaseMixin:
    """Keep the keyword arguments of a job that no loaded job mixin declares."""

    def __init__(self, **unclaimed_kwargs: object) -> None:
        self._unclaimed_kwargs: MappingProxyType[str, object] = MappingProxyType(
            {key: _freeze(val) for key, val in unclaimed_kwargs.items()}
        )

        is_applied_job = getattr(self, '_from_apply', False)
        silenced = os.environ.get(SILENCE_UNCLAIMED_KWARGS_WARNING_ENV_VAR) == '1'
        if self._unclaimed_kwargs and is_applied_job and not silenced:
            name = getattr(self, '_name', None)
            keys = ', '.join(f'"{key}"' for key in self._unclaimed_kwargs)
            _logger.warning(
                f'Job "{name}" ignores keyword arguments not used by any loaded job mixin: '
                f'{keys}. They may be misspelled, or belong to a plugin that is not loaded '
                'for the current engine.'
            )

    @property
    def unclaimed_kwargs(self) -> MappingProxyType[str, object]:
        """Keyword arguments that no loaded job mixin declares.

        Returns:
            MappingProxyType[str, object]: Read-only mapping of the unclaimed keyword arguments,
                with mutable values converted to read-only equivalents.
        """
        return self._unclaimed_kwargs


setattr(UnclaimedKwargsJobBaseMixin, RECEIVES_UNCLAIMED_KWARGS_ATTR, True)
