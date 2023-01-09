from typing import Optional

from inflection import underscore
from prefect.utilities.names import generate_slug
from slugify import slugify


class NameJobConfigMixin:
    def __init__(self, *, name: Optional[str] = None):

        self._name: Optional[str] = name

        if self._name is not None:
            self._check_not_empty_string('name', self._name)

        self._unique_name = None

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


class NameJobMixin:
    def __init__(self, *, name: Optional[str] = None):
        self._name: Optional[str] = name
        self._generate_unique_name()

    def _generate_unique_name(self):
        if self._name is None:
            return None
        class_name_snake_case = underscore(self.__class__.__name__)
        self._unique_name = slugify(f'{class_name_snake_case}-{self._name}-{generate_slug(2)}')

    def regenerate_unique_name(self) -> None:
        self._generate_unique_name()


class NameTaskConfigMixin:
    def __init__(self, *, name: Optional[str] = None):
        self._name = name if name is not None else self._task_func.__name__


class NameLinearFlowConfigMixin:
    def __init__(self, *, name: Optional[str] = None):
        self._name = name if name is not None else self._linear_flow_func.__name__


class NameDagFlowConfigMixin:
    def __init__(self, *, name: Optional[str] = None):
        self._name = name if name is not None else self._dag_flow_func.__name__


class NameFuncFlowConfigMixin:
    def __init__(self, *, name: Optional[str] = None):
        self._name = name if name is not None else self._func_flow_func.__name__
