from typing import Optional

from inflection import underscore
from slugify import slugify

from omnipy.modules.prefect import generate_slug
from omnipy.util.mixin import DynamicMixinAcceptor


class NameJobBaseMixin:
    def __init__(self, *, name: Optional[str] = None):
        self._name: Optional[str] = name

        if self._name is not None:
            self._check_not_empty_string('name', self._name)
        else:
            if hasattr(self, '_job_func'):
                self._name = self._job_func.__name__

        # TODO: When job state machine is implemented, check using that to see if in job state
        self._unique_name = self._generate_unique_name() if hasattr(self, 'create_job') else None

    @staticmethod
    def _check_not_empty_string(param_name: str, param: str) -> None:
        if len(param) == 0:
            raise ValueError('Empty strings not allowed for parameter "{}"'.format(param_name))

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_name(self) -> str:
        return self._unique_name

    def _generate_unique_name(self) -> str:
        if self._name is None:
            return None

        class_name = self.__class__.__name__
        if class_name.endswith(DynamicMixinAcceptor.WITH_MIXINS_CLS_PREFIX):
            class_name = class_name[:-len(DynamicMixinAcceptor.WITH_MIXINS_CLS_PREFIX)]

        class_name_snake_case = underscore(class_name)
        return slugify(f'{class_name_snake_case}-{self._name}-{generate_slug(2)}')

    def _regenerate_unique_name(self) -> None:
        self._unique_name = self._generate_unique_name()


class NameJobMixin:
    def regenerate_unique_name(self) -> None:
        self._regenerate_unique_name()


#
# class NameFuncJobBaseMixin:
#     def __init__(self, *, name: Optional[str] = None):
#         self._name = name if name is not None else self._job_func.__name__
