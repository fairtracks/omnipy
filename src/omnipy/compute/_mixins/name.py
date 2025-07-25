from typing import Callable, cast

from inflection import underscore

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
        from slugify import slugify

        from omnipy.components.prefect.lazy_import import generate_slug

        if self._name is None:
            return None

        class_name = self.__class__.__name__
        if class_name.endswith(WITH_MIXINS_CLS_SUFFIX):
            class_name = class_name[:-len(WITH_MIXINS_CLS_SUFFIX)]

        class_name_snake_case = underscore(class_name)
        return slugify(f'{class_name_snake_case}-{self._name}-{generate_slug(2)}')

    def _regenerate_unique_name(self) -> None:
        self._unique_name = self._generate_unique_name()


class NameJobMixin:
    def regenerate_unique_name(self) -> None:
        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)
        self_as_name_job_base_mixin._regenerate_unique_name()
