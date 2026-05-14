from typing import Callable, cast

from omnipy.util.helpers import generate_job_slug
from omnipy.util.mixin import WITH_MIXINS_CLS_SUFFIX


class NameJobBaseMixin:
    def __init__(self, *, name: str | None = None):
        self._name: str | None = name

        if self._name is not None:
            self._check_not_empty_string('name', self._name)
        else:
            if hasattr(self, '_job_func'):
                self._job_func: Callable
                self._name = self._job_func.__name__

        # TODO: When job state machine is implemented, check using that to see if in job state
        self._unique_name = self._generate_unique_name() if hasattr(self, 'create_job') else None

    @staticmethod
    def _check_not_empty_string(param_name: str, param: str) -> None:
        if len(param) == 0:
            raise ValueError('Empty strings not allowed for parameter "{}"'.format(param_name))

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def unique_name(self) -> str | None:
        return self._unique_name

    def _generate_unique_name(self) -> str | None:
        if self._name is None:
            return None

        job_cls_name = self.__class__.__name__
        if job_cls_name.endswith(WITH_MIXINS_CLS_SUFFIX):
            job_cls_name = job_cls_name[:-len(WITH_MIXINS_CLS_SUFFIX)]

        return generate_job_slug(job_cls_name, self._name)

    def _regenerate_unique_name(self) -> None:
        self._unique_name = self._generate_unique_name()


class NameJobMixin:
    def regenerate_unique_name(self) -> None:
        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)
        self_as_name_job_base_mixin._regenerate_unique_name()
