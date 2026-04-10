from typing import Literal

import pytest

from omnipy import Model
from omnipy.data.typechecks import (is_model_instance,
                                    is_model_subclass,
                                    obj_or_model_content_isinstance)

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
    from omnipy.data.typechecks import all_model_type_variants

    class MyModel(Model[Model[int | float] | Model[str] | list[int]]):
        ...

    variants = all_model_type_variants(MyModel, double_model_unions_as_variants=False)
    assert variants == (int | float, str, list[int])

    variants = all_model_type_variants(MyModel, double_model_unions_as_variants=True)
    assert variants == (int, float, str, list[int])


def test_all_dataset_type_variants() -> None:
    from omnipy.data.dataset import Dataset
    from omnipy.data.typechecks import all_dataset_type_variants

    class MyDataset(Dataset[Model[Model[int] | float] | Model[str] | Dataset[Model[list[int]]]]):
        ...

    variants = all_dataset_type_variants(MyDataset)
    assert variants == (int, float, str, Dataset[Model[list[int]]])
