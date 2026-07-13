"""Tests for data type checks."""

from typing import Generic, Literal

import pytest
from typing_extensions import TypeVar

from omnipy import Dataset, Model
from omnipy.data.model import (is_model_instance,
                               is_model_subclass,
                               is_non_omnipy_pydantic_model,
                               is_pure_pydantic_model,
                               obj_or_model_content_isinstance)
import omnipy.util.pydantic as pyd

from .helpers.models import PydanticParentModel


def test_is_model_instance() -> None:
    assert not is_model_instance(123)
    assert is_model_instance(Model[int](123))
    assert not is_model_instance(None)
    assert is_model_instance(Model[None](None))
    assert not is_model_instance(PydanticParentModel)


def test_is_model_subclass() -> None:
    assert not is_model_subclass(int)
    assert is_model_subclass(Model[int])

    class A:
        ...

    class MyModel(Model[list[int]]):
        ...

    assert not is_model_subclass(A)
    assert is_model_subclass(MyModel)


def test_obj_or_model_content_isinstance_for_regular_objects() -> None:
    assert obj_or_model_content_isinstance(123, int)
    assert obj_or_model_content_isinstance('abc', str)
    assert obj_or_model_content_isinstance([1, 2, 3], list)

    assert not obj_or_model_content_isinstance(123, list)
    assert not obj_or_model_content_isinstance('abc', int)
    assert not obj_or_model_content_isinstance([1, 2, 3], str)

    assert obj_or_model_content_isinstance(123, (list, int))
    assert obj_or_model_content_isinstance('abc', (int, str))
    assert obj_or_model_content_isinstance([1, 2, 3], (str, list))

    assert obj_or_model_content_isinstance(123, list | int)
    assert obj_or_model_content_isinstance('abc', int | str)
    assert obj_or_model_content_isinstance([1, 2, 3], str | list)

    with pytest.raises(TypeError):
        obj_or_model_content_isinstance('abc', Literal['abc'])  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        obj_or_model_content_isinstance([1, 2, 3], list[int])


def test_obj_or_model_content_isinstance_for_models() -> None:
    assert obj_or_model_content_isinstance(Model[int](123), int)
    assert obj_or_model_content_isinstance(Model[str]('abc'), str)
    assert obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), list)

    assert not obj_or_model_content_isinstance(Model[int](123), list)
    assert not obj_or_model_content_isinstance(Model[str]('abc'), int)
    assert not obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), str)

    assert obj_or_model_content_isinstance(Model[int](123), (list, int))
    assert obj_or_model_content_isinstance(Model[str]('abc'), (int, str))
    assert obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), (str, list))

    assert obj_or_model_content_isinstance(Model[int](123), list | int)
    assert obj_or_model_content_isinstance(Model[str]('abc'), int | str)
    assert obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), str | list)

    with pytest.raises(TypeError):
        assert obj_or_model_content_isinstance(
            Model[Literal['abc']]('abc'),
            Literal['abc'],  # type: ignore[arg-type]
        )

    with pytest.raises(TypeError):
        assert obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), list[int])


def test_all_model_type_variants() -> None:
    from omnipy.data._typing.helpers import all_model_type_variants

    class MyModel(Model[list[int] | float | Model[list[str] | list[int]]]):
        ...

    variants = all_model_type_variants(MyModel)
    assert variants == (list[int], float, Model[list[str] | list[int]])


def test_all_dataset_type_variants() -> None:
    from omnipy.data._typing.helpers import all_dataset_type_variants
    from omnipy.data.dataset import Dataset

    class MyDataset(Dataset[Model[list[int] | float | Model[str] | Dataset[Model[list[int]]]]]):
        ...

    variants = all_dataset_type_variants(MyDataset)
    assert variants == (list[int], float, Model[str], Dataset[Model[list[int]]])


def test_is_pydantic_model() -> None:
    class PydanticModel(pyd.BaseModel):
        ...

    T = TypeVar('T')

    class GenericPydanticModel(pyd.GenericModel, Generic[T]):
        ...

    class Mixin:
        ...

    class MultiInheritModel(pyd.BaseModel, Mixin):
        ...

    class PydanticModelSubclass(PydanticModel):
        ...

    class OmnipyModel(Model[int]):
        ...

    class OmnipyModelSubclass(Model[int]):
        ...

    class MultiInheritOmnipyAndPydanticModel(Model[int], pyd.BaseModel):
        ...

    class MultiInheritOmnipyAndGenericPydanticModel(Model[int], pyd.GenericModel, Generic[T]):
        ...

    assert is_pure_pydantic_model(PydanticModel())
    assert not is_pure_pydantic_model(pyd.BaseModel())
    assert not is_pure_pydantic_model(GenericPydanticModel())
    assert not is_pure_pydantic_model(MultiInheritModel())
    assert not is_pure_pydantic_model(PydanticModelSubclass())
    assert not is_pure_pydantic_model(OmnipyModel())
    assert not is_pure_pydantic_model(OmnipyModelSubclass())
    assert not is_pure_pydantic_model(MultiInheritOmnipyAndPydanticModel())
    assert not is_pure_pydantic_model(MultiInheritOmnipyAndGenericPydanticModel())
    assert not is_pure_pydantic_model(Model[PydanticModel]())
    assert not is_pure_pydantic_model(Dataset[Model[PydanticModel]]())
    assert not is_pure_pydantic_model('model')

    assert is_non_omnipy_pydantic_model(PydanticModel())
    assert not is_non_omnipy_pydantic_model(pyd.BaseModel())
    assert is_non_omnipy_pydantic_model(GenericPydanticModel())
    assert is_non_omnipy_pydantic_model(MultiInheritModel())
    assert is_non_omnipy_pydantic_model(PydanticModelSubclass())
    assert not is_non_omnipy_pydantic_model(OmnipyModel())
    assert not is_non_omnipy_pydantic_model(OmnipyModelSubclass())
    assert not is_non_omnipy_pydantic_model(MultiInheritOmnipyAndPydanticModel())
    assert not is_non_omnipy_pydantic_model(MultiInheritOmnipyAndGenericPydanticModel())
    assert not is_non_omnipy_pydantic_model(Model[PydanticModel]())
    assert not is_non_omnipy_pydantic_model(Dataset[Model[PydanticModel]]())
    assert not is_non_omnipy_pydantic_model('model')
