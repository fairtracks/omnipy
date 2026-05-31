"""Mixins for assigning stable display names and unique names to jobs."""

from typing import Callable, cast

from omnipy.util.helpers import generate_run_slug, get_full_job_slug
from omnipy.util.mixin import strip_mixins_suffix


class NameJobBaseMixin:
    """Provide base support for job names and generated unique names."""
    def __init__(self, *, name: str | None = None):
        self._name: str | None = name

        if self._name is not None:
            self._check_not_empty_string('name', self._name)
        else:
            if hasattr(self, '_job_func'):
                self._job_func: Callable
                self._name = self._job_func.__name__

        # TODO: When job state machine is implemented, check using that to see if in job state
        self._unique_run_slug, self._unique_full_job_slug = (
            self._generate_unique_slugs() if hasattr(self, 'create_job') else (None, None))

    @staticmethod
    def _check_not_empty_string(param_name: str, param: str) -> None:
        if len(param) == 0:
            raise ValueError('Empty strings not allowed for parameter "{}"'.format(param_name))

    @property
    def name(self) -> str | None:
        """{{ISUNIQUELYNAMEDJOB_NAME_SUMMARY}}

        {{ISUNIQUELYNAMEDJOB_NAME_DETAILS}}"""

        return self._name

    @property
    def unique_name(self) -> str | None:
        return self._unique_full_job_slug

    @property
    def unique_run_slug(self) -> str | None:
        return self._unique_run_slug

    def _generate_unique_slugs(self) -> tuple[str, str] | tuple[None, None]:
        if self._name is None:
            return None, None

        job_cls_name = strip_mixins_suffix(self.__class__.__name__)

        unique_run_slug = generate_run_slug()
        unique_full_job_slug = get_full_job_slug(job_cls_name, self._name, unique_run_slug)
        return unique_run_slug, unique_full_job_slug

    def _regenerate_unique_slugs(self) -> None:
        self._unique_run_slug, self._unique_full_job_slug = self._generate_unique_slugs()


class NameJobMixin:
    """Expose public helpers for refreshing generated job names."""
    def regenerate_unique_name(self) -> None:
        """{{ISUNIQUELYNAMEDJOB_REGENERATE_UNIQUE_NAME_SUMMARY}}

        {{ISUNIQUELYNAMEDJOB_REGENERATE_UNIQUE_NAME_DETAILS}}"""

        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)
        self_as_name_job_base_mixin._regenerate_unique_slugs()
