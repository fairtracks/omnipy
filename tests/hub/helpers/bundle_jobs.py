"""Jobs run from job bundles in the job bundle tests."""

from omnipy import Dataset, LinearFlowTemplate, Model, TaskTemplate
from omnipy.data._data_class_creator import DataClassBase


@TaskTemplate()
def add(a: int, b: int) -> int:
    return a + b


@TaskTemplate()
def echo_text(text: str) -> str:
    return text


@TaskTemplate()
def double_values(data: Dataset[Model[int]]) -> Dataset[Model[int]]:
    return Dataset[Model[int]]({key: val.content * 2 for key, val in data.items()})


@TaskTemplate()
def count_items(items: Model[list[int]]) -> int:
    return len(items.content)


@TaskTemplate()
def dynamic_conversion_setting() -> bool:
    return DataClassBase.data_class_creator.config.model.dynamically_convert_elements_to_models


@TaskTemplate()
def unpersistable() -> object:
    return object()


@TaskTemplate()
def plus_one(number: int) -> int:
    return number + 1


@LinearFlowTemplate(plus_one, plus_one)
def plus_two(number: int) -> int: ...
